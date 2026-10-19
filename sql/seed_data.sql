-- ==========================================================
-- ONLINE DOCTOR APPOINTMENT BOOKING SYSTEM
-- Seed Data Script (Microsoft SQL Server / T-SQL)
-- Realistic Sample Data inspired by Marham.pk
-- ==========================================================

USE DoctorAppointmentDB;
GO

-- 1. Insert Admins
INSERT INTO dbo.Admin (name, email, password, phone, role, is_active)
VALUES 
('System Admin', 'admin@marhamhealth.pk', 'admin123', '+92 300 1234567', 'SuperAdmin', 1),
('Dr. Tariq Mahmood (Medical Director)', 'tariq.admin@marhamhealth.pk', 'admin123', '+92 321 7654321', 'MedicalDirector', 1);

-- 2. Insert Specializations
INSERT INTO dbo.Specialization (name, description)
VALUES 
('Dermatologist', 'Skin, hair, nail care, acne treatment, aesthetic procedures, and laser therapies.'),
('Gynecologist', 'Women reproductive health, obstetrics, maternity care, and fertility treatment.'),
('Cardiologist', 'Heart and cardiovascular conditions, hypertension, echocardiography, and angiograms.'),
('Pediatrician', 'Child healthcare, vaccinations, pediatric development, and newborn care.'),
('Orthopedic Surgeon', 'Bone, joint, spinal problems, sports injuries, fractures, and joint replacement.'),
('Neurologist', 'Brain, spinal cord, neuropathy, migraines, epilepsy, and nervous system disorders.'),
('Gastroenterologist', 'Digestive tract, liver diseases, endoscopy, colonoscopy, and stomach disorders.'),
('General Physician', 'Primary family medicine, fever, infectious diseases, and chronic condition management.'),
('Psychiatrist', 'Mental health disorders, anxiety, depression, cognitive therapy, and counseling.'),
('ENT Specialist', 'Ear, nose, throat conditions, sinus problems, hearing loss, and tonsillitis.');

-- 3. Insert Doctors
-- Note: Doctors are initially linked to Specialization IDs and approved by Admin ID 1
INSERT INTO dbo.Doctor (name, email, phone, password, qualification, license_no, specialization_id, approved_by_admin_id, status, bio)
VALUES 
('Assoc. Prof. Dr. Mohammad Atiq Ur Rehman', 'dr.atiq@marhamhealth.pk', '+92 300 8472911', 'admin123', 'MBBS, FCPS (Dermatology), Diploma in Aesthetic Medicine (USA)', 'PMDC-41829-P', 1, 1, 'Approved', 'Over 16 years of extensive experience treating dermatological diseases, hair loss, laser skincare, and aesthetic treatments in Lahore.'),
('Dr. Jawaryiah Kanwal', 'dr.jawaryiah@marhamhealth.pk', '+92 321 9918234', 'admin123', 'MBBS, MCPS, FCPS (Obstetrics & Gynecology)', 'PMDC-58201-P', 2, 1, 'Approved', 'Renowned Consultant Obstetrician and Gynecologist with 12+ years expertise in high-risk pregnancies, infertility, and laparoscopic surgery.'),
('Prof. Dr. Sajjad Naseer', 'dr.sajjad@marhamhealth.pk', '+92 333 4519283', 'admin123', 'MBBS, FCPS (Cardiology), FACC (USA), FSCAI', 'PMDC-29184-P', 3, 1, 'Approved', 'Senior Interventional Cardiologist with 22 years of clinical excellence managing ischemic heart diseases, angioplasty, and cardiac rehab.'),
('Dr. Subheen Fatima', 'dr.subheen@marhamhealth.pk', '+92 345 6712390', 'admin123', 'MBBS, DCH, FCPS (Pediatrics)', 'PMDC-62910-P', 4, 1, 'Approved', 'Compassionate Child Specialist and Neonatologist dedicated to pediatric immunization, growth monitoring, and newborn critical care.'),
('Dr. Usman Javaid', 'dr.usman@marhamhealth.pk', '+92 302 8847123', 'admin123', 'MBBS, MS (Orthopedic Surgery), Fellowship Arthroscopy (UK)', 'PMDC-48392-P', 5, 1, 'Approved', 'Specialized Consultant Orthopedic Surgeon handling complex joint replacements, arthroscopic sports injuries, and spine traumas.'),
('Dr. Mahum Imran', 'dr.mahum@marhamhealth.pk', '+92 312 9018471', 'admin123', 'MBBS, FCPS (Neurology)', 'PMDC-73192-P', 6, 1, 'Approved', 'Consultant Neurologist specializing in headache management, stroke rehabilitation, movement disorders, and neuro-diagnostics.'),
('Dr. Muhammad Awais Latif', 'dr.awais@marhamhealth.pk', '+92 334 5192847', 'admin123', 'MBBS, MRCP (UK), FCPS (Gastroenterology)', 'PMDC-51029-P', 7, 1, 'Approved', 'Advanced therapeutic endoscopist and hepatologist managing liver cirrhosis, GERD, and gastrointestinal diseases.'),
('Dr. Farhan Ali (Pending Approval)', 'dr.farhan@marhamhealth.pk', '+92 322 1199334', 'admin123', 'MBBS, FCPS (General Medicine)', 'PMDC-89201-P', 8, NULL, 'Pending', 'General Physician applicant awaiting PMDC verification credentials check.');

-- 4. Insert Doctor Locations (Hospitals & Clinics)
INSERT INTO dbo.Doctor_Location (doctor_id, location_name, address, city, state, country, contact_no)
VALUES 
-- Dr. Atiq (Lahore)
(1, 'Shalamar Hospital', 'Shalamar Link Road, Moghalpura', 'Lahore', 'Punjab', 'Pakistan', '+92 42 111 205 205'),
(1, 'Cosmetique Clinic', '190 DD, Phase 4, DHA', 'Lahore', 'Punjab', 'Pakistan', '+92 42 3574 6565'),

-- Dr. Jawaryiah Kanwal (Lahore & Rawalpindi)
(2, 'Doctors Hospital & Medical Center', '152-G/1, Canal Bank, Johar Town', 'Lahore', 'Punjab', 'Pakistan', '+92 42 3530 2701'),
(2, 'PAF Hospital', 'Main Margalla Road, Sector E-9', 'Islamabad', 'Federal Capital', 'Pakistan', '+92 51 9507 777'),

-- Prof. Dr. Sajjad Naseer (Karachi)
(3, 'South City Hospital', 'Street 3, Block 3, Clifton', 'Karachi', 'Sindh', 'Pakistan', '+92 21 3586 2301'),
(3, 'National Institute of Cardiovascular Diseases (NICVD)', 'Rafiqui Shaheed Road', 'Karachi', 'Sindh', 'Pakistan', '+92 21 9920 1271'),

-- Dr. Subheen Fatima (Islamabad)
(4, 'Shifa International Hospital', 'Pitras Bukhari Road, Sector H-8/4', 'Islamabad', 'Federal Capital', 'Pakistan', '+92 51 8463 000'),

-- Dr. Usman Javaid (Lahore)
(5, 'Surgimed Hospital', '1-Zafar Ali Road, Gulberg V', 'Lahore', 'Punjab', 'Pakistan', '+92 42 3571 4411'),

-- Dr. Mahum Imran (Karachi)
(6, 'Aga Khan University Hospital', 'Stadium Road', 'Karachi', 'Sindh', 'Pakistan', '+92 21 111 911 911'),

-- Dr. Awais Latif (Multan)
(7, 'Nishtar Medical Complex', 'Nishtar Road', 'Multan', 'Punjab', 'Pakistan', '+92 61 9200 231');

-- 5. Insert Doctor Schedules
INSERT INTO dbo.Doctor_Schedule (doctor_location_id, day_of_week, start_time, end_time, slot_duration)
VALUES 
-- Dr. Atiq at Shalamar Hospital
(1, 'Monday', '10:00:00', '13:00:00', 30),
(1, 'Wednesday', '10:00:00', '13:00:00', 30),
(1, 'Friday', '10:00:00', '13:00:00', 30),

-- Dr. Atiq at Cosmetique
(2, 'Tuesday', '17:00:00', '20:00:00', 20),
(2, 'Thursday', '17:00:00', '20:00:00', 20),

-- Dr. Jawaryiah at Doctors Hospital
(3, 'Monday', '16:00:00', '19:00:00', 20),
(3, 'Thursday', '16:00:00', '19:00:00', 20),

-- Prof. Sajjad at South City Hospital
(5, 'Monday', '11:00:00', '14:00:00', 30),
(5, 'Wednesday', '11:00:00', '14:00:00', 30),

-- Dr. Subheen at Shifa International
(7, 'Tuesday', '09:00:00', '12:00:00', 20),
(7, 'Thursday', '09:00:00', '12:00:00', 20),

-- Dr. Usman at Surgimed
(8, 'Monday', '15:00:00', '18:00:00', 30),
(8, 'Wednesday', '15:00:00', '18:00:00', 30);

-- 6. Insert Available Slots for the next few days
-- Note: Dates will be populated for current week
DECLARE @today DATE = CAST(GETDATE() AS DATE);
DECLARE @tomorrow DATE = DATEADD(DAY, 1, @today);
DECLARE @dayAfter DATE = DATEADD(DAY, 2, @today);
DECLARE @dayThree DATE = DATEADD(DAY, 3, @today);

-- Slots for Dr. Atiq (Schedule 1 & 2)
INSERT INTO dbo.Available_Slots (schedule_id, slot_date, start_time, end_time, slot_status)
VALUES 
(1, @today, '10:00:00', '10:30:00', 'Booked'),
(1, @today, '10:30:00', '11:00:00', 'Available'),
(1, @today, '11:00:00', '11:30:00', 'Available'),
(1, @today, '11:30:00', '12:00:00', 'Available'),
(1, @tomorrow, '10:00:00', '10:30:00', 'Available'),
(1, @tomorrow, '10:30:00', '11:00:00', 'Available'),
(1, @dayAfter, '10:00:00', '10:30:00', 'Available'),

-- Slots for Dr. Jawaryiah (Schedule 6)
(6, @today, '16:00:00', '16:20:00', 'Booked'),
(6, @today, '16:20:00', '16:40:00', 'Available'),
(6, @today, '16:40:00', '17:00:00', 'Available'),
(6, @tomorrow, '16:00:00', '16:20:00', 'Available'),
(6, @tomorrow, '16:20:00', '16:40:00', 'Available'),

-- Slots for Prof. Sajjad Naseer (Schedule 8)
(8, @today, '11:00:00', '11:30:00', 'Available'),
(8, @today, '11:30:00', '12:00:00', 'Booked'),
(8, @today, '12:00:00', '12:30:00', 'Available'),
(8, @tomorrow, '11:00:00', '11:30:00', 'Available'),

-- Slots for Dr. Subheen (Schedule 10)
(10, @tomorrow, '09:00:00', '09:20:00', 'Available'),
(10, @tomorrow, '09:20:00', '09:40:00', 'Available'),

-- Slots for Dr. Usman (Schedule 12)
(12, @dayAfter, '15:00:00', '15:30:00', 'Available'),
(12, @dayAfter, '15:30:00', '16:00:00', 'Available');

-- 7. Insert Patients
INSERT INTO dbo.Patient (name, email, phone, password, date_of_birth, gender, address)
VALUES 
('Hamza Ahmed', 'hamza.ahmed@gmail.com', '+92 331 4455667', 'admin123', '1995-04-12', 'Male', 'House 42, Sector Y, DHA Phase 3, Lahore'),
('Ayesha Malik', 'ayesha.malik@yahoo.com', '+92 300 9876543', 'admin123', '1998-09-23', 'Female', 'Apartment 12-B, Askari 11, Lahore'),
('Bilal Khan', 'bilal.khan@outlook.com', '+92 321 5566778', 'admin123', '1987-11-05', 'Male', 'Street 7, F-8/2, Islamabad'),
('Zainab Fatima', 'zainab.f@gmail.com', '+92 345 1122334', 'admin123', '2001-02-18', 'Female', 'House 88, Khayaban-e-Shamsheer, DHA Phase 5, Karachi');

-- 8. Insert Appointments
INSERT INTO dbo.Appointment (patient_id, slot_id, doctor_id, booking_date, status, reason)
VALUES 
(1, 1, 1, DATEADD(HOUR, -5, GETDATE()), 'Confirmed', 'Severe acne breakout and eczema consultation on facial skin.'),
(2, 8, 2, DATEADD(HOUR, -2, GETDATE()), 'Confirmed', 'Routine prenatal checkup and ultrasound scan review.'),
(3, 14, 3, DATEADD(DAY, -1, GETDATE()), 'Confirmed', 'Post-stent cardiac evaluation, chest tightness on exertion.');
GO
