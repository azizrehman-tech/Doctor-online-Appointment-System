"""
Online Doctor Appointment Booking System - Web Application
Built with Python Flask, connected to Microsoft SQL Server via pyodbc.
UI/UX heavily inspired by Marham.pk with rich aesthetics, real-time filters, and multi-portal support.
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import database
import datetime

app = Flask(__name__)
app.secret_key = "marham_doctor_booking_secure_secret_key_2026"

# Inject current year and common helpers to all templates
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.datetime.now().year,
        "current_date": datetime.date.today().strftime("%Y-%m-%d"),
        "logged_user": session.get("user")
    }

# ==========================================================
# PUBLIC WEB VIEWS
# ==========================================================

@app.route("/")
def index():
    specialties = database.get_specializations()
    cities = database.get_cities()
    # Featured top doctors
    featured_doctors = database.search_doctors()[:8]
    return render_template("index.html", 
                           specialties=specialties, 
                           cities=cities, 
                           doctors=featured_doctors)

@app.route("/doctors")
def doctors_list():
    city = request.args.get("city", "")
    specialty = request.args.get("specialty", "")
    query = request.args.get("q", "")
    
    specialties = database.get_specializations()
    cities = database.get_cities()
    doctors = database.search_doctors(city=city, specialty=specialty, query=query)
    
    return render_template("doctors.html", 
                           doctors=doctors, 
                           specialties=specialties, 
                           cities=cities,
                           selected_city=city, 
                           selected_specialty=specialty, 
                           search_query=query)

@app.route("/doctor/<int:doctor_id>")
def doctor_profile(doctor_id):
    doctor = database.get_doctor_details(doctor_id)
    if not doctor:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("index"))
    
    # Selected date for slot booking (defaults to today)
    selected_date = request.args.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    available_slots = database.get_available_slots_by_doctor(doctor_id, selected_date)
    
    return render_template("doctor_profile.html", 
                           doctor=doctor, 
                           selected_date=selected_date, 
                           slots=available_slots)

# ==========================================================
# PORTALS (PATIENT, DOCTOR, ADMIN)
# ==========================================================

@app.route("/portal/patient")
def patient_portal():
    user = session.get("user")
    if not user or user.get("role") != "patient":
        flash("Please log in as a Patient to access your patient dashboard.", "warning")
        return redirect(url_for("login_view", role="patient"))
    
    appointments = database.get_patient_appointments(user["id"])
    return render_template("patient_portal.html", appointments=appointments, patient=user)

@app.route("/portal/doctor")
def doctor_portal():
    user = session.get("user")
    if not user or user.get("role") != "doctor":
        flash("Please log in as a Doctor to access your professional dashboard.", "warning")
        return redirect(url_for("login_view", role="doctor"))
    
    doctor = database.get_doctor_details(user["id"])
    appointments = database.get_doctor_appointments(user["id"])
    return render_template("doctor_portal.html", doctor=doctor, appointments=appointments)

@app.route("/portal/admin")
def admin_portal():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        flash("Admin authentication required.", "danger")
        return redirect(url_for("login_view", role="admin"))
    
    data = database.get_admin_dashboard_data()
    specialties = database.get_specializations()
    return render_template("admin_portal.html", stats=data, specialties=specialties)

# ==========================================================
# AUTHENTICATION (LOGIN / REGISTER / LOGOUT)
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login_view():
    default_role = request.args.get("role", "patient")
    if request.method == "POST":
        role = request.form.get("role", "patient")
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        with database.get_db() as (conn, cur, is_sql):
            if role == "patient":
                cur.execute("SELECT patient_id, name, email, password, phone FROM Patient WHERE email = ?", [email])
                row = cur.fetchone()
                if row and row[3] == password:
                    session["user"] = {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "phone": row[4],
                        "role": "patient"
                    }
                    flash(f"Welcome back, {row[1]}!", "success")
                    return redirect(url_for("patient_portal"))
            elif role == "doctor":
                cur.execute("SELECT doctor_id, name, email, password, status, license_no FROM Doctor WHERE email = ?", [email])
                row = cur.fetchone()
                if row and row[3] == password:
                    session["user"] = {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "status": row[4],
                        "license_no": row[5],
                        "role": "doctor"
                    }
                    flash(f"Welcome, {row[1]}!", "success")
                    return redirect(url_for("doctor_portal"))
            elif role == "admin":
                cur.execute("SELECT admin_id, name, email, password, role FROM Admin WHERE email = ?", [email])
                row = cur.fetchone()
                if row and row[3] == password:
                    session["user"] = {
                        "id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "admin_role": row[4],
                        "role": "admin"
                    }
                    flash(f"Logged in as Administrator ({row[1]})", "success")
                    return redirect(url_for("admin_portal"))

        flash("Invalid email or password credentials. Please try again.", "danger")
    
    return render_template("login.html", active_role=default_role)

@app.route("/register", methods=["GET", "POST"])
def register_view():
    role = request.args.get("role", "patient")
    specialties = database.get_specializations()
    
    if request.method == "POST":
        role = request.form.get("role", "patient")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        
        if role == "patient":
            dob = request.form.get("date_of_birth") or None
            gender = request.form.get("gender") or None
            address = request.form.get("address") or None
            ok, msg = database.register_patient(name, email, phone, password, dob, gender, address)
            if ok:
                session["user"] = {"id": msg, "name": name, "email": email, "phone": phone, "role": "patient"}
                flash("Registration successful! Welcome to Marham Health.", "success")
                return redirect(url_for("patient_portal"))
            else:
                flash(msg, "danger")
        elif role == "doctor":
            qualification = request.form.get("qualification")
            license_no = request.form.get("license_no")
            specialization_id = int(request.form.get("specialization_id", 1))
            bio = request.form.get("bio")
            ok, msg = database.register_doctor(name, email, phone, password, qualification, license_no, specialization_id, bio)
            if ok:
                session["user"] = {"id": msg, "name": name, "email": email, "status": "Pending", "license_no": license_no, "role": "doctor"}
                flash("Doctor registration submitted! Your profile is pending administrative review.", "info")
                return redirect(url_for("doctor_portal"))
            else:
                flash(msg, "danger")

    return render_template("register.html", active_role=role, specialties=specialties)

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("index"))

# ==========================================================
# REST API ENDPOINTS
# ==========================================================

@app.route("/api/cities")
def api_cities():
    return jsonify(database.get_cities())

@app.route("/api/specialties")
def api_specialties():
    return jsonify(database.get_specializations())

@app.route("/api/doctors/search")
def api_search_doctors():
    city = request.args.get("city")
    specialty = request.args.get("specialty")
    q = request.args.get("q")
    results = database.search_doctors(city=city, specialty=specialty, query=q)
    return jsonify(results)

@app.route("/api/doctor/<int:doctor_id>/slots")
def api_doctor_slots(doctor_id):
    date_str = request.args.get("date", datetime.date.today().strftime("%Y-%m-%d"))
    slots = database.get_available_slots_by_doctor(doctor_id, date_str)
    return jsonify(slots)

@app.route("/api/appointments/book", methods=["POST"])
def api_book_appointment():
    data = request.get_json() or request.form
    slot_id = data.get("slot_id")
    doctor_id = data.get("doctor_id")
    reason = data.get("reason", "Consultation")
    
    user = session.get("user")
    patient_id = None
    if user and user.get("role") == "patient":
        patient_id = user["id"]
    else:
        # If guest booking, create a quick patient account or find existing by email
        patient_name = data.get("patient_name")
        patient_email = data.get("patient_email")
        patient_phone = data.get("patient_phone")
        if not (patient_name and patient_email):
            return jsonify({"success": False, "message": "Patient name and email are required to book an appointment."}), 400
        
        with database.get_db() as (conn, cur, is_sql):
            cur.execute("SELECT patient_id FROM Patient WHERE email = ?", [patient_email])
            row = cur.fetchone()
            if row:
                patient_id = row[0]
            else:
                ok, pid = database.register_patient(patient_name, patient_email, patient_phone, "admin123")
                patient_id = pid
                # auto login
                session["user"] = {"id": pid, "name": patient_name, "email": patient_email, "role": "patient"}

    if not (slot_id and doctor_id and patient_id):
        return jsonify({"success": False, "message": "Missing booking parameters."}), 400

    success, result = database.book_appointment(patient_id, int(slot_id), int(doctor_id), reason)
    if success:
        return jsonify({
            "success": True, 
            "message": "Your appointment has been successfully confirmed!",
            "appointment_id": result
        })
    else:
        return jsonify({"success": False, "message": result}), 400

@app.route("/api/appointments/<int:appointment_id>/cancel", methods=["POST"])
def api_cancel_appointment(appointment_id):
    user = session.get("user")
    patient_id = user["id"] if (user and user.get("role") == "patient") else None
    
    success, msg = database.cancel_appointment(appointment_id, patient_id=patient_id)
    return jsonify({"success": success, "message": msg})

@app.route("/api/admin/doctor/<int:doctor_id>/status", methods=["POST"])
def api_admin_doctor_status(doctor_id):
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json() or request.form
    new_status = data.get("status")
    if new_status not in ["Approved", "Rejected"]:
        return jsonify({"success": False, "message": "Invalid status value."}), 400
    
    database.update_doctor_status(doctor_id, new_status, admin_id=user["id"])
    return jsonify({"success": True, "message": f"Doctor status updated to {new_status}."})

@app.route("/api/doctor/location/add", methods=["POST"])
def api_add_location():
    user = session.get("user")
    if not user or user.get("role") != "doctor":
        return jsonify({"success": False, "message": "Doctor authorization required."}), 403
    
    data = request.get_json() or request.form
    database.add_doctor_location(
        doctor_id=user["id"],
        location_name=data.get("location_name"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state", ""),
        contact_no=data.get("contact_no", "")
    )
    return jsonify({"success": True, "message": "New practice location added successfully!"})

@app.route("/api/doctor/schedule/add", methods=["POST"])
def api_add_schedule():
    user = session.get("user")
    if not user or user.get("role") != "doctor":
        return jsonify({"success": False, "message": "Doctor authorization required."}), 403
    
    data = request.get_json() or request.form
    sched_id = database.add_doctor_schedule(
        doctor_location_id=int(data.get("doctor_location_id")),
        day_of_week=data.get("day_of_week"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        slot_duration=int(data.get("slot_duration", 20))
    )
    return jsonify({"success": True, "schedule_id": sched_id, "message": "Weekly schedule configured!"})

@app.route("/api/doctor/slots/generate", methods=["POST"])
def api_generate_slots():
    user = session.get("user")
    if not user or user.get("role") != "doctor":
        return jsonify({"success": False, "message": "Doctor authorization required."}), 403
    
    data = request.get_json() or request.form
    schedule_id = int(data.get("schedule_id"))
    target_date = data.get("slot_date")
    count = database.generate_slots_for_schedule(schedule_id, target_date)
    return jsonify({"success": True, "count": count, "message": f"Generated {count} bookable time slots for {target_date}."})

@app.route("/api/admin/specialization/add", methods=["POST"])
def api_add_specialization():
    user = session.get("user")
    if not user or user.get("role") != "admin":
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    data = request.get_json() or request.form
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return jsonify({"success": False, "message": "Specialization name is required."}), 400
    
    database.add_specialization(name, description)
    return jsonify({"success": True, "message": f"Specialization '{name}' added successfully."})

if __name__ == "__main__":
    print("\n========================================================")
    print(" [ONLINE DOCTOR APPOINTMENT BOOKING SYSTEM]")
    print(" [DATABASE] Connected to Microsoft SQL Server: DoctorAppointmentDB")
    print(" [SERVER] Running at: http://127.0.0.1:5000")
    print("========================================================\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
