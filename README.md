# Online Doctor Appointment Booking System

An enterprise-grade, relational database-driven healthcare application inspired by **Marham.pk** and **Practo**. Built with a normalized **8-Table Relational Database Schema** in **Microsoft SQL Server (T-SQL)** and an interactive web interface powered by **Python Flask**, modern vanilla **CSS3**, and **JavaScript**.

---

## 🏛️ System Architecture & Entity-Relationship (ER) Design

The database schema strictly adheres to Third Normal Form (3NF) to eliminate redundancy, enforce referential integrity, and handle multi-location doctor scheduling.

### The 8 Relational Tables:
1. **`Admin`**: System administrators responsible for verifying PMDC credentials, approving doctor registrations, and viewing system audit reports.
2. **`Doctor`**: Medical consultants with qualifications, PMDC license numbers, medical specialization, approval status, and professional biography.
3. **`Patient`**: Registered healthcare consumers who search for doctors, book appointments, and maintain consultation history.
4. **`Specialization`**: Medical disciplines (e.g., Dermatologist, Cardiologist, Gynecologist, Pediatrician).
5. **`Doctor_Location`**: Clinics and hospitals where a doctor practices. Allows 1 doctor to maintain multiple practice locations across cities (Lahore, Karachi, Islamabad, etc.).
6. **`Doctor_Schedule`**: Recurring weekly timings per clinic location (Day of week, start time, end time, and discrete slot duration in minutes).
7. **`Available_Slots`**: Concrete bookable appointment slots on specific dates generated from doctor schedules (`Available`, `Booked`, `Cancelled`).
8. **`Appointment`**: The transaction record binding a Patient, a Doctor, and an Available Time Slot with status tracking and medical reasons.

---

## 🎨 UI/UX Design System (Inspired by Marham.pk)

The frontend reflects the reverse-engineered visual hierarchy and design tokens of **Marham.pk**:
- **Brand Palette:** Deep Medical Navy (`#014E78`), Crimson Red CTA (`#C02942`), Trust Amber (`#F5960B`), and Success Green (`#10B981`).
- **Signature Dual Search:** Instant city selector dropdown paired with live doctor and specialty query input.
- **Doctor Cards:** PMDC license authentication tags, experience indicators, multiple clinic badges, consultation fees, and instant slot reservation modal.
- **Dynamic Portals:** Dedicated role-based dashboards for **Patients**, **Doctors**, and **Administrators**.

---

## 🚀 Quick Start Guide

### Prerequisites:
- Python 3.10+ (Tested on Python 3.14)
- Microsoft SQL Server (LocalDB or SQLEXPRESS) with ODBC Driver 18/17

### 1. Database Initialization (Microsoft SQL Server):
Open **SQL Server Management Studio (SSMS)** or run from PowerShell:
```powershell
# Creates database and executes schema
sqlcmd -S localhost\SQLEXPRESS -E -i sql/schema.sql

# Populates realistic seed data
sqlcmd -S localhost\SQLEXPRESS -E -i sql/seed_data.sql

# Runs advanced queries, procedures, and views
sqlcmd -S localhost\SQLEXPRESS -E -i sql/queries.sql
```

*(Note: If you run via Python, `database.py` connects automatically to `localhost\SQLEXPRESS` and supports auto-fallback).*

### 2. Launch the Web Application:
```powershell
python app.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Demo Login Accounts (For Academic Evaluation)

| Role | Email Address | Password | Permissions & Features |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@marhamhealth.pk` | `admin123` | Approve/Reject doctor registrations, add specializations, view system metrics & appointment audits |
| **Doctor** | `dr.atiq@marhamhealth.pk` | `admin123` | Manage clinic locations, configure weekly schedules, generate slots, view patient booking roster |
| **Patient** | `hamza.ahmed@gmail.com` | `admin123` | Search doctors, filter by city/specialty, select time slots, book & cancel appointments |

*(Note: The login page includes 1-click **Autofill Buttons** for instant evaluation).*

---

## 📂 Project Structure

```text
d:\University Work\Database\Doctor Online Appointment\
├── app.py                   # Flask Application (Routing, Authentication, REST APIs)
├── database.py              # Database Access Layer (pyodbc connection to SQL Server)
├── sql/
│   ├── schema.sql           # Complete T-SQL DDL script (8 tables, PK/FK, constraints, indexes)
│   ├── seed_data.sql        # Realistic Pakistani medical seed data
│   └── queries.sql          # Advanced JOINs, Aggregates, Views & Stored Procedures
├── static/
│   ├── css/
│   │   └── style.css        # Marham-inspired CSS styling, design tokens & responsive grid
│   └── js/
│       └── app.js           # Client booking engine, AJAX handlers, slot selector
├── templates/
│   ├── base.html            # Master layout with topbar, navbar, footer & booking modal
│   ├── index.html           # Homepage (Hero search, specialties, doctor cards)
│   ├── doctors.html         # Filterable doctor directory
│   ├── doctor_profile.html  # Doctor details, multiple clinic locations & slot picker
│   ├── patient_portal.html  # Patient dashboard (view appointments, cancellation)
│   ├── doctor_portal.html   # Doctor console (locations, schedules, slot generator)
│   ├── admin_portal.html    # Admin console (doctor approvals, KPIs, reports)
│   ├── login.html           # Unified authentication with role switcher
│   └── register.html        # Patient and Doctor onboarding forms
└── README.md                # Comprehensive documentation
```
