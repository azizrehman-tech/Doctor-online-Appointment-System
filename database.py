"""
Database connection and abstraction layer for Online Doctor Appointment Booking System.
Supports Microsoft SQL Server (via pyodbc) with automatic SQLite fallback for maximum portability.
"""

import os
import sqlite3
import datetime
from contextlib import contextmanager

USE_SQL_SERVER = True
SQL_SERVER_CONN_STR = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=DoctorAppointmentDB;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

SQLITE_DB_PATH = os.path.join(os.path.dirname(__file__), "doctor_appointment.db")

def test_sql_server():
    try:
        import pyodbc
        conn = pyodbc.connect(SQL_SERVER_CONN_STR, timeout=3)
        conn.close()
        return True
    except Exception as e:
        print(f"[Database] SQL Server connection unavailable: {e}. Falling back to SQLite.")
        return False

# Detect engine on import
_has_sql_server = test_sql_server()

@contextmanager
def get_db():
    """Context manager yielding (connection, cursor, is_sql_server)"""
    if _has_sql_server:
        import pyodbc
        conn = pyodbc.connect(SQL_SERVER_CONN_STR)
        cursor = conn.cursor()
        try:
            yield conn, cursor, True
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            yield conn, cursor, False
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

def row_to_dict(cursor, row):
    """Converts a database row into a standard Python dict"""
    if row is None:
        return None
    if isinstance(row, sqlite3.Row):
        return dict(row)
    # pyodbc row
    columns = [col[0] for col in cursor.description]
    res = {}
    for col, val in zip(columns, row):
        if isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
            res[col] = str(val)
        else:
            res[col] = val
    return res

def rows_to_dicts(cursor, rows):
    return [row_to_dict(cursor, r) for r in rows]

# ==========================================================
# PUBLIC API & QUERY FUNCTIONS
# ==========================================================

def get_specializations():
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT specialization_id, name, description FROM Specialization ORDER BY name")
        return rows_to_dicts(cur, cur.fetchall())

def get_cities():
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT DISTINCT city FROM Doctor_Location WHERE city IS NOT NULL AND city != '' ORDER BY city")
        rows = cur.fetchall()
        return [r[0] for r in rows]

def search_doctors(city=None, specialty=None, query=None):
    with get_db() as (conn, cur, is_sql):
        sql = """
            SELECT 
                d.doctor_id, d.name AS doctor_name, d.qualification, d.license_no, d.bio, d.status,
                s.specialization_id, s.name AS specialization_name,
                loc.doctor_location_id, loc.location_name, loc.city, loc.address, loc.contact_no,
                (SELECT COUNT(*) FROM Available_Slots sl 
                 JOIN Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
                 WHERE sch.doctor_location_id = loc.doctor_location_id AND sl.slot_status = 'Available'
                ) AS available_slots_count
            FROM Doctor d
            INNER JOIN Specialization s ON d.specialization_id = s.specialization_id
            LEFT JOIN Doctor_Location loc ON d.doctor_id = loc.doctor_id
            WHERE d.status = 'Approved'
        """
        params = []
        if city and city.lower() != 'all':
            sql += " AND LOWER(loc.city) = LOWER(?)"
            params.append(city)
        if specialty and specialty.lower() != 'all':
            sql += " AND (LOWER(s.name) = LOWER(?) OR s.specialization_id = ?)"
            params.extend([specialty, specialty if specialty.isdigit() else -1])
        if query:
            q_like = f"%{query}%"
            sql += " AND (d.name LIKE ? OR s.name LIKE ? OR loc.location_name LIKE ? OR d.qualification LIKE ?)"
            params.extend([q_like, q_like, q_like, q_like])
            
        sql += " ORDER BY d.name ASC"
        cur.execute(sql, params)
        return rows_to_dicts(cur, cur.fetchall())

def get_doctor_details(doctor_id):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            SELECT d.*, s.name AS specialization_name
            FROM Doctor d
            INNER JOIN Specialization s ON d.specialization_id = s.specialization_id
            WHERE d.doctor_id = ?
        """, [doctor_id])
        doctor = row_to_dict(cur, cur.fetchone())
        if not doctor:
            return None

        # Fetch locations
        cur.execute("""
            SELECT * FROM Doctor_Location WHERE doctor_id = ? ORDER BY location_name
        """, [doctor_id])
        locations = rows_to_dicts(cur, cur.fetchall())

        # For each location fetch schedules & available slots
        for loc in locations:
            cur.execute("""
                SELECT * FROM Doctor_Schedule WHERE doctor_location_id = ? ORDER BY day_of_week
            """, [loc['doctor_location_id']])
            loc['schedules'] = rows_to_dicts(cur, cur.fetchall())

            # Fetch slots
            cur.execute("""
                SELECT sl.*, sch.day_of_week
                FROM Available_Slots sl
                JOIN Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
                WHERE sch.doctor_location_id = ?
                ORDER BY sl.slot_date ASC, sl.start_time ASC
            """, [loc['doctor_location_id']])
            loc['slots'] = rows_to_dicts(cur, cur.fetchall())

        doctor['locations'] = locations
        return doctor

def get_available_slots_by_doctor(doctor_id, date_str=None):
    with get_db() as (conn, cur, is_sql):
        sql = """
            SELECT sl.slot_id, sl.slot_date, sl.start_time, sl.end_time, sl.slot_status,
                   sch.day_of_week, loc.location_name, loc.city, loc.doctor_location_id
            FROM Available_Slots sl
            JOIN Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
            JOIN Doctor_Location loc ON sch.doctor_location_id = loc.doctor_location_id
            WHERE loc.doctor_id = ? AND sl.slot_status = 'Available'
        """
        params = [doctor_id]
        if date_str:
            sql += " AND sl.slot_date = ?"
            params.append(date_str)
        sql += " ORDER BY sl.slot_date ASC, sl.start_time ASC"
        cur.execute(sql, params)
        return rows_to_dicts(cur, cur.fetchall())

def book_appointment(patient_id, slot_id, doctor_id, reason):
    with get_db() as (conn, cur, is_sql):
        # 1. Check if slot is available
        cur.execute("SELECT slot_status FROM Available_Slots WHERE slot_id = ?", [slot_id])
        row = cur.fetchone()
        if not row or row[0] != 'Available':
            return False, "This time slot is no longer available. Please select another slot."

        # 2. Insert appointment
        if is_sql:
            cur.execute("""
                INSERT INTO Appointment (patient_id, slot_id, doctor_id, booking_date, status, reason)
                OUTPUT INSERTED.appointment_id
                VALUES (?, ?, ?, GETDATE(), 'Confirmed', ?)
            """, [patient_id, slot_id, doctor_id, reason])
            appt_id = cur.fetchone()[0]
        else:
            cur.execute("""
                INSERT INTO Appointment (patient_id, slot_id, doctor_id, booking_date, status, reason)
                VALUES (?, ?, ?, datetime('now'), 'Confirmed', ?)
            """, [patient_id, slot_id, doctor_id, reason])
            appt_id = cur.lastrowid

        # 3. Mark slot as Booked
        cur.execute("UPDATE Available_Slots SET slot_status = 'Booked' WHERE slot_id = ?", [slot_id])
        return True, appt_id

def cancel_appointment(appointment_id, patient_id=None):
    with get_db() as (conn, cur, is_sql):
        sql = "SELECT slot_id, patient_id FROM Appointment WHERE appointment_id = ?"
        cur.execute(sql, [appointment_id])
        row = cur.fetchone()
        if not row:
            return False, "Appointment not found."
        
        slot_id = row[0]
        owner_id = row[1]
        if patient_id and owner_id != patient_id:
            return False, "Unauthorized cancellation request."

        # Update appointment status
        cur.execute("UPDATE Appointment SET status = 'Cancelled' WHERE appointment_id = ?", [appointment_id])
        # Free up the slot so it can be re-booked
        cur.execute("UPDATE Available_Slots SET slot_status = 'Available' WHERE slot_id = ?", [slot_id])
        return True, "Appointment successfully cancelled. The time slot is now open."

def get_patient_appointments(patient_id):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            SELECT 
                a.appointment_id, a.booking_date, a.status, a.reason,
                d.doctor_id, d.name AS doctor_name, d.qualification,
                s.name AS specialization_name,
                loc.location_name, loc.city, loc.address,
                sl.slot_date, sl.start_time, sl.end_time
            FROM Appointment a
            JOIN Doctor d ON a.doctor_id = d.doctor_id
            JOIN Specialization s ON d.specialization_id = s.specialization_id
            JOIN Available_Slots sl ON a.slot_id = sl.slot_id
            JOIN Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
            JOIN Doctor_Location loc ON sch.doctor_location_id = loc.doctor_location_id
            WHERE a.patient_id = ?
            ORDER BY sl.slot_date DESC, sl.start_time DESC
        """, [patient_id])
        return rows_to_dicts(cur, cur.fetchall())

def get_doctor_appointments(doctor_id):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            SELECT 
                a.appointment_id, a.booking_date, a.status, a.reason,
                p.patient_id, p.name AS patient_name, p.phone AS patient_phone, p.email AS patient_email, p.gender,
                loc.location_name, loc.city,
                sl.slot_date, sl.start_time, sl.end_time
            FROM Appointment a
            JOIN Patient p ON a.patient_id = p.patient_id
            JOIN Available_Slots sl ON a.slot_id = sl.slot_id
            JOIN Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
            JOIN Doctor_Location loc ON sch.doctor_location_id = loc.doctor_location_id
            WHERE a.doctor_id = ?
            ORDER BY sl.slot_date DESC, sl.start_time ASC
        """, [doctor_id])
        return rows_to_dicts(cur, cur.fetchall())

def add_doctor_location(doctor_id, location_name, address, city, state, contact_no):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            INSERT INTO Doctor_Location (doctor_id, location_name, address, city, state, country, contact_no)
            VALUES (?, ?, ?, ?, ?, 'Pakistan', ?)
        """, [doctor_id, location_name, address, city, state, contact_no])
        return True

def add_doctor_schedule(doctor_location_id, day_of_week, start_time, end_time, slot_duration=20):
    with get_db() as (conn, cur, is_sql):
        if is_sql:
            cur.execute("""
                INSERT INTO Doctor_Schedule (doctor_location_id, day_of_week, start_time, end_time, slot_duration)
                OUTPUT INSERTED.schedule_id
                VALUES (?, ?, ?, ?, ?)
            """, [doctor_location_id, day_of_week, start_time, end_time, slot_duration])
            sched_id = cur.fetchone()[0]
        else:
            cur.execute("""
                INSERT INTO Doctor_Schedule (doctor_location_id, day_of_week, start_time, end_time, slot_duration)
                VALUES (?, ?, ?, ?, ?)
            """, [doctor_location_id, day_of_week, start_time, end_time, slot_duration])
            sched_id = cur.lastrowid
        return sched_id

def generate_slots_for_schedule(schedule_id, target_date_str):
    """Generates discrete time slots for a given schedule on target_date"""
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT start_time, end_time, slot_duration FROM Doctor_Schedule WHERE schedule_id = ?", [schedule_id])
        sch = cur.fetchone()
        if not sch:
            return 0
        
        start_t_str, end_t_str, duration = str(sch[0]), str(sch[1]), int(sch[2])
        # Parse times
        st = datetime.datetime.strptime(start_t_str.split('.')[0][:5], "%H:%M")
        et = datetime.datetime.strptime(end_t_str.split('.')[0][:5], "%H:%M")
        
        count = 0
        current = st
        while current + datetime.timedelta(minutes=duration) <= et:
            slot_start = current.strftime("%H:%M:%S")
            current += datetime.timedelta(minutes=duration)
            slot_end = current.strftime("%H:%M:%S")
            
            # Check if slot already exists
            cur.execute("""
                SELECT 1 FROM Available_Slots 
                WHERE schedule_id = ? AND slot_date = ? AND start_time = ?
            """, [schedule_id, target_date_str, slot_start])
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO Available_Slots (schedule_id, slot_date, start_time, end_time, slot_status)
                    VALUES (?, ?, ?, ?, 'Available')
                """, [schedule_id, target_date_str, slot_start, slot_end])
                count += 1
        return count

def get_admin_dashboard_data():
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT COUNT(*) FROM Doctor WHERE status = 'Approved'")
        total_doctors = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM Doctor WHERE status = 'Pending'")
        pending_doctors = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM Patient")
        total_patients = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM Appointment")
        total_appointments = cur.fetchone()[0]

        # Pending doctors list
        cur.execute("""
            SELECT d.*, s.name AS specialization_name
            FROM Doctor d
            JOIN Specialization s ON d.specialization_id = s.specialization_id
            WHERE d.status = 'Pending'
            ORDER BY d.created_at DESC
        """)
        pending_list = rows_to_dicts(cur, cur.fetchall())

        # Recent appointments
        cur.execute("""
            SELECT a.appointment_id, a.booking_date, a.status, a.reason,
                   p.name AS patient_name, d.name AS doctor_name, s.name AS specialization_name,
                   sl.slot_date, sl.start_time
            FROM Appointment a
            JOIN Patient p ON a.patient_id = p.patient_id
            JOIN Doctor d ON a.doctor_id = d.doctor_id
            JOIN Specialization s ON d.specialization_id = s.specialization_id
            JOIN Available_Slots sl ON a.slot_id = sl.slot_id
            ORDER BY a.booking_date DESC
        """)
        recent_appointments = rows_to_dicts(cur, cur.fetchmany(10))

        return {
            "total_doctors": total_doctors,
            "pending_doctors": pending_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "pending_list": pending_list,
            "recent_appointments": recent_appointments
        }

def update_doctor_status(doctor_id, status, admin_id=1):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            UPDATE Doctor 
            SET status = ?, approved_by_admin_id = ?
            WHERE doctor_id = ?
        """, [status, admin_id if status == 'Approved' else None, doctor_id])
        return True

def add_specialization(name, description):
    with get_db() as (conn, cur, is_sql):
        cur.execute("""
            INSERT INTO Specialization (name, description) VALUES (?, ?)
        """, [name, description])
        return True

def register_patient(name, email, phone, password, dob=None, gender=None, address=None):
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT patient_id FROM Patient WHERE email = ?", [email])
        if cur.fetchone():
            return False, "An account with this email address already exists."
        if is_sql:
            cur.execute("""
                INSERT INTO Patient (name, email, phone, password, date_of_birth, gender, address)
                OUTPUT INSERTED.patient_id
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [name, email, phone, password, dob, gender, address])
            pid = cur.fetchone()[0]
        else:
            cur.execute("""
                INSERT INTO Patient (name, email, phone, password, date_of_birth, gender, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [name, email, phone, password, dob, gender, address])
            pid = cur.lastrowid
        return True, pid

def register_doctor(name, email, phone, password, qualification, license_no, specialization_id, bio):
    with get_db() as (conn, cur, is_sql):
        cur.execute("SELECT doctor_id FROM Doctor WHERE email = ? OR license_no = ?", [email, license_no])
        if cur.fetchone():
            return False, "A doctor with this email or PMDC license already exists."
        if is_sql:
            cur.execute("""
                INSERT INTO Doctor (name, email, phone, password, qualification, license_no, specialization_id, status, bio)
                OUTPUT INSERTED.doctor_id
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
            """, [name, email, phone, password, qualification, license_no, specialization_id, bio])
            did = cur.fetchone()[0]
        else:
            cur.execute("""
                INSERT INTO Doctor (name, email, phone, password, qualification, license_no, specialization_id, status, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)
            """, [name, email, phone, password, qualification, license_no, specialization_id, bio])
            did = cur.lastrowid
        return True, did
