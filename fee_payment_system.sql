-- Create database
CREATE DATABASE IF NOT EXISTS fee_system;
USE fee_system;

-- Users table (for both admin and students)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'student') NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    class VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    parent_name VARCHAR(100),
    parent_phone VARCHAR(20),
    address TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Fee categories
CREATE TABLE fee_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- Fee structure
CREATE TABLE fee_structure (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    class VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    due_date DATE NOT NULL,
    FOREIGN KEY (category_id) REFERENCES fee_categories(id),
    UNIQUE KEY (category_id, class, academic_year)
);

-- Student fees allocation
CREATE TABLE student_fees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    fee_structure_id INT NOT NULL,
    status ENUM('pending', 'partial', 'paid') DEFAULT 'pending',
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (fee_structure_id) REFERENCES fee_structure(id),
    UNIQUE KEY (student_id, fee_structure_id)
);

-- Payments
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_fee_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method ENUM('cash', 'card', 'upi', 'bank_transfer') NOT NULL,
    transaction_id VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (student_fee_id) REFERENCES student_fees(id) ON DELETE CASCADE
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, password, full_name, role, email) 
VALUES ('admin', '$2b$12$LsgIQBJdZ/NlRszB.kKqYOhS2I5jYy5IYHRUkwO8YoHCXzGh5nNNy', 'System Administrator', 'admin', 'admin@example.com');

-- Insert sample fee categories
INSERT INTO fee_categories (name, description) VALUES 
('Tuition Fee', 'Regular monthly tuition fee'),
('Development Fee', 'Annual development charges'),
('Library Fee', 'Annual library membership fee'),
('Sports Fee', 'Annual sports facilities fee'),
('Examination Fee', 'Term examination charges');