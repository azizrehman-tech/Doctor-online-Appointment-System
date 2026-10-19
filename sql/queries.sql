-- ==========================================================
-- ONLINE DOCTOR APPOINTMENT BOOKING SYSTEM
-- Advanced SQL Operations & Reporting Queries
-- Academic Demonstration for University Database Evaluation
-- ==========================================================

USE DoctorAppointmentDB;
GO

-- 1. JOIN QUERY: Search approved doctors with their specialization, hospital, and city
SELECT 
    d.doctor_id,
    d.name AS DoctorName,
    s.name AS Specialization,
    d.qualification,
    d.license_no,
    loc.location_name AS HospitalOrClinic,
    loc.city,
    loc.contact_no
FROM dbo.Doctor d
INNER JOIN dbo.Specialization s ON d.specialization_id = s.specialization_id
INNER JOIN dbo.Doctor_Location loc ON d.doctor_id = loc.doctor_id
WHERE d.status = 'Approved'
ORDER BY loc.city, s.name, d.name;
GO

-- 2. MULTI-TABLE JOIN: Full Appointment Roster with Patient, Doctor, Location, and Time Slot
SELECT 
    a.appointment_id,
    a.booking_date,
    a.status AS AppointmentStatus,
    p.name AS PatientName,
    p.phone AS PatientPhone,
    d.name AS DoctorName,
    s.name AS Specialization,
    loc.location_name AS ClinicLocation,
    loc.city,
    sl.slot_date,
    CONVERT(VARCHAR(5), sl.start_time, 108) + ' - ' + CONVERT(VARCHAR(5), sl.end_time, 108) AS SlotTime,
    a.reason
FROM dbo.Appointment a
INNER JOIN dbo.Patient p ON a.patient_id = p.patient_id
INNER JOIN dbo.Doctor d ON a.doctor_id = d.doctor_id
INNER JOIN dbo.Specialization s ON d.specialization_id = s.specialization_id
INNER JOIN dbo.Available_Slots sl ON a.slot_id = sl.slot_id
INNER JOIN dbo.Doctor_Schedule sch ON sl.schedule_id = sch.schedule_id
INNER JOIN dbo.Doctor_Location loc ON sch.doctor_location_id = loc.doctor_location_id
ORDER BY sl.slot_date DESC, sl.start_time ASC;
GO

-- 3. AGGREGATION & GROUP BY: Appointment counts & active doctor statistics by city
SELECT 
    loc.city,
    COUNT(DISTINCT d.doctor_id) AS TotalApprovedDoctors,
    COUNT(DISTINCT loc.doctor_location_id) AS TotalClinics,
    COUNT(a.appointment_id) AS TotalAppointmentsBooked
FROM dbo.Doctor_Location loc
INNER JOIN dbo.Doctor d ON loc.doctor_id = d.doctor_id
LEFT JOIN dbo.Appointment a ON d.doctor_id = a.doctor_id
WHERE d.status = 'Approved'
GROUP BY loc.city
ORDER BY TotalAppointmentsBooked DESC;
GO

-- 4. SUBQUERY: Find doctors who have available slots in the next 3 days
SELECT 
    d.doctor_id,
    d.name,
    d.qualification,
    s.name AS Specialization
FROM dbo.Doctor d
JOIN dbo.Specialization s ON d.specialization_id = s.specialization_id
WHERE d.doctor_id IN (
    SELECT DISTINCT loc.doctor_id
    FROM dbo.Doctor_Location loc
    JOIN dbo.Doctor_Schedule sch ON loc.doctor_location_id = sch.doctor_location_id
    JOIN dbo.Available_Slots sl ON sch.schedule_id = sl.schedule_id
    WHERE sl.slot_status = 'Available'
      AND sl.slot_date >= CAST(GETDATE() AS DATE)
);
GO

-- 5. STORED PROCEDURE: Book an Appointment Transactionally (Prevents Double-Booking)
IF OBJECT_ID('dbo.sp_BookAppointment', 'P') IS NOT NULL 
    DROP PROCEDURE dbo.sp_BookAppointment;
GO

CREATE PROCEDURE dbo.sp_BookAppointment
    @PatientId INT,
    @SlotId INT,
    @DoctorId INT,
    @Reason NVARCHAR(500),
    @NewAppointmentId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;

    BEGIN TRY
        -- Check if slot is available
        IF NOT EXISTS (
            SELECT 1 FROM dbo.Available_Slots 
            WHERE slot_id = @SlotId AND slot_status = 'Available'
        )
        BEGIN
            RAISERROR('Selected time slot is no longer available.', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END

        -- Insert Appointment
        INSERT INTO dbo.Appointment (patient_id, slot_id, doctor_id, booking_date, status, reason)
        VALUES (@PatientId, @SlotId, @DoctorId, GETDATE(), 'Confirmed', @Reason);

        SET @NewAppointmentId = SCOPE_IDENTITY();

        -- Mark slot as Booked
        UPDATE dbo.Available_Slots
        SET slot_status = 'Booked'
        WHERE slot_id = @SlotId;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- 6. VIEW: Patient-facing Doctor Directory View
IF OBJECT_ID('dbo.vw_DoctorDirectory', 'V') IS NOT NULL 
    DROP VIEW dbo.vw_DoctorDirectory;
GO

CREATE VIEW dbo.vw_DoctorDirectory AS
SELECT 
    d.doctor_id,
    d.name AS DoctorName,
    d.license_no,
    d.qualification,
    s.specialization_id,
    s.name AS SpecializationName,
    loc.doctor_location_id,
    loc.location_name,
    loc.city,
    loc.address,
    loc.contact_no,
    d.bio
FROM dbo.Doctor d
INNER JOIN dbo.Specialization s ON d.specialization_id = s.specialization_id
INNER JOIN dbo.Doctor_Location loc ON d.doctor_id = loc.doctor_id
WHERE d.status = 'Approved';
GO
