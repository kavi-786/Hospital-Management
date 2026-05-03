CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- Users Table (Handles all logins: Admin, Doctor, Nurse, Ambulance, Store, Patient)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Doctor', 'Nurse', 'Ambulance', 'Store', 'Patient') NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Doctors Table
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    availability_status BOOLEAN DEFAULT TRUE,
    image VARCHAR(255),  -- ✅ NEW COLUMN
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- Patients Table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    blood_group VARCHAR(5),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Appointments Table
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status ENUM('Pending', 'Accepted', 'Rejected', 'Completed') DEFAULT 'Pending',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- Prescriptions Table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    diagnosis TEXT NOT NULL,
    medicines TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE CASCADE
);

-- Medicines / Medical Store Stock
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    stock_quantity INT DEFAULT 0,
    price DECIMAL(10, 2),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Emergency / Ambulance Requests
CREATE TABLE IF NOT EXISTS emergency_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT, -- Can be null if requested by non-registered user
    location TEXT NOT NULL,
    status ENUM('Pending', 'Dispatched', 'Resolved') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

-- Nurse Assignments (Assigned Patients)
CREATE TABLE IF NOT EXISTS nurse_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nurse_user_id INT NOT NULL,
    patient_id INT NOT NULL,
    status VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (nurse_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Insert Default Admin
-- Password is 'admin123' (hashed using Werkzeug generate_password_hash)
-- Example hash for 'admin123': pbkdf2:sha256:600000$examplehash...
-- You should run the application and create an admin, or we can insert a predefined hash.
-- Hashed 'admin123' -> scrypt:32768:8:1$YlG4k3dZ4hWv$95a285d8... (Werkzeug 3.0 format)
INSERT IGNORE INTO users (username, password_hash, role, name) 
VALUES ('admin', 'scrypt:32768:8:1$F3xT7N8VzM4Qk2Jb$5f235b2a0c4f83b19b674b8e8f80459378627448d3c11d0442347101887b419a4a7541656eb28b9cc822c9f53835c249a421b8f596324d9c4fb2bb607149a463', 'Admin', 'Super Admin');
