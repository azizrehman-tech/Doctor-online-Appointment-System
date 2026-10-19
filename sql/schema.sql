-- ==========================================================
-- ONLINE DOCTOR APPOINTMENT BOOKING SYSTEM
-- Relational Database Schema (Microsoft SQL Server / T-SQL)
-- 8-Table Normalized Schema based on Project ER Diagram
-- ==========================================================

USE DoctorAppointmentDB;
GO

-- Drop tables in reverse foreign-key order if they exist
IF OBJECT_ID('dbo.Appointment', 'U') IS NOT NULL DROP TABLE dbo.Appointment;
IF OBJECT_ID('dbo.Available_Slots', 'U') IS NOT NULL DROP TABLE dbo.Available_Slots;
IF OBJECT_ID('dbo.Doctor_Schedule', 'U') IS NOT NULL DROP TABLE dbo.Doctor_Schedule;
IF OBJECT_ID('dbo.Doctor_Location', 'U') IS NOT NULL DROP TABLE dbo.Doctor_Location;
IF OBJECT_ID('dbo.Doctor', 'U') IS NOT NULL DROP TABLE dbo.Doctor;
IF OBJECT_ID('dbo.Specialization', 'U') IS NOT NULL DROP TABLE dbo.Specialization;
IF OBJECT_ID('dbo.Patient', 'U') IS NOT NULL DROP TABLE dbo.Patient;
IF OBJECT_ID('dbo.Admin', 'U') IS NOT NULL DROP TABLE dbo.Admin;
GO

-- 1. Admin Table
CREATE TABLE dbo.Admin (
    admin_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    phone NVARCHAR(30) NULL,
    role NVARCHAR(50) DEFAULT 'SuperAdmin',
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 2. Specialization Table
CREATE TABLE dbo.Specialization (
    specialization_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    description NVARCHAR(500) NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 3. Doctor Table
CREATE TABLE dbo.Doctor (
    doctor_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    phone NVARCHAR(30) NULL,
    password NVARCHAR(255) NOT NULL,
    qualification NVARCHAR(200) NOT NULL, -- e.g. MBBS, FCPS, MD
    license_no NVARCHAR(100) NOT NULL UNIQUE, -- PMDC / PMC Registration number
    specialization_id INT NOT NULL,
    approved_by_admin_id INT NULL,
    status NVARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    bio NVARCHAR(1000) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Doctor_Specialization FOREIGN KEY (specialization_id) 
        REFERENCES dbo.Specialization(specialization_id),
    CONSTRAINT FK_Doctor_Admin FOREIGN KEY (approved_by_admin_id) 
        REFERENCES dbo.Admin(admin_id)
);
GO

-- 4. Doctor_Location Table (Clinics & Hospitals where Doctor practices)
CREATE TABLE dbo.Doctor_Location (
    doctor_location_id INT IDENTITY(1,1) PRIMARY KEY,
    doctor_id INT NOT NULL,
    location_name NVARCHAR(200) NOT NULL,
    address NVARCHAR(300) NOT NULL,
    city NVARCHAR(100) NOT NULL,
    state NVARCHAR(100) NULL,
    country NVARCHAR(100) DEFAULT 'Pakistan',
    contact_no NVARCHAR(50) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_DoctorLocation_Doctor FOREIGN KEY (doctor_id) 
        REFERENCES dbo.Doctor(doctor_id) ON DELETE CASCADE
);
GO

-- 5. Doctor_Schedule Table (Weekly Recurring Timing per Location)
CREATE TABLE dbo.Doctor_Schedule (
    schedule_id INT IDENTITY(1,1) PRIMARY KEY,
    doctor_location_id INT NOT NULL,
    day_of_week NVARCHAR(20) NOT NULL CHECK (day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')),
    start_time TIME(0) NOT NULL,
    end_time TIME(0) NOT NULL,
    slot_duration INT NOT NULL DEFAULT 15 CHECK (slot_duration > 0), -- In minutes
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_DoctorSchedule_DoctorLocation FOREIGN KEY (doctor_location_id) 
        REFERENCES dbo.Doctor_Location(doctor_location_id) ON DELETE CASCADE,
    CONSTRAINT CHK_Schedule_Time CHECK (start_time < end_time)
);
GO

-- 6. Available_Slots Table (Individual Bookable Time Slots)
CREATE TABLE dbo.Available_Slots (
    slot_id INT IDENTITY(1,1) PRIMARY KEY,
    schedule_id INT NOT NULL,
    slot_date DATE NOT NULL,
    start_time TIME(0) NOT NULL,
    end_time TIME(0) NOT NULL,
    slot_status NVARCHAR(20) DEFAULT 'Available' CHECK (slot_status IN ('Available', 'Booked', 'Cancelled')),
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_AvailableSlots_Schedule FOREIGN KEY (schedule_id) 
        REFERENCES dbo.Doctor_Schedule(schedule_id) ON DELETE CASCADE,
    CONSTRAINT CHK_Slot_Time CHECK (start_time < end_time)
);
GO

-- 7. Patient Table
CREATE TABLE dbo.Patient (
    patient_id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(150) NOT NULL UNIQUE,
    phone NVARCHAR(30) NULL,
    password NVARCHAR(255) NOT NULL,
    date_of_birth DATE NULL,
    gender NVARCHAR(20) NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    address NVARCHAR(300) NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 8. Appointment Table (Booking linking Patient, Slot, and Doctor)
CREATE TABLE dbo.Appointment (
    appointment_id INT IDENTITY(1,1) PRIMARY KEY,
    patient_id INT NOT NULL,
    slot_id INT NOT NULL,
    doctor_id INT NOT NULL,
    booking_date DATETIME DEFAULT GETDATE(),
    status NVARCHAR(50) DEFAULT 'Confirmed' CHECK (status IN ('Pending', 'Confirmed', 'Completed', 'Cancelled')),
    reason NVARCHAR(500) NULL,
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Appointment_Patient FOREIGN KEY (patient_id) 
        REFERENCES dbo.Patient(patient_id),
    CONSTRAINT FK_Appointment_Slot FOREIGN KEY (slot_id) 
        REFERENCES dbo.Available_Slots(slot_id),
    CONSTRAINT FK_Appointment_Doctor FOREIGN KEY (doctor_id) 
        REFERENCES dbo.Doctor(doctor_id)
);
GO

-- Indexes for Query Performance & Lookups
CREATE INDEX IX_Doctor_Specialization ON dbo.Doctor(specialization_id);
CREATE INDEX IX_DoctorLocation_City ON dbo.Doctor_Location(city);
CREATE INDEX IX_DoctorLocation_DoctorId ON dbo.Doctor_Location(doctor_id);
CREATE INDEX IX_AvailableSlots_DateStatus ON dbo.Available_Slots(slot_date, slot_status);
CREATE INDEX IX_Appointment_Patient ON dbo.Appointment(patient_id);
CREATE INDEX IX_Appointment_Doctor ON dbo.Appointment(doctor_id);
GO
