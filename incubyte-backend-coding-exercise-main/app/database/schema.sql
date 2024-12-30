-- Initialize the database by dropping any existing tables
-- and then creating new empty tables for doctors, locations, 
-- their relationships, availabilities, and appointments.
-- 1. Drop existing tables if they already exist (to start fresh)
DROP TABLE IF EXISTS doctors;

DROP TABLE IF EXISTS locations;

DROP TABLE IF EXISTS doctor_locations;

DROP TABLE IF EXISTS availability;

DROP TABLE IF EXISTS appointments;

-- 2. Create a table for storing doctors
CREATE TABLE doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

-- 3. Create a table for storing locations
CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  address TEXT NOT NULL
);

-- 4. Create a join table between doctors and locations
CREATE TABLE doctor_locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id),
  FOREIGN KEY (location_id) REFERENCES locations (id)
);

-- 5. Create a table for availability slots
CREATE TABLE availability (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_location_id INTEGER NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  day_of_week TEXT NOT NULL,
  FOREIGN KEY (doctor_location_id) REFERENCES doctor_locations (id)
);

-- 6. Create a table for actual booked appointments
CREATE TABLE appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_location_id INTEGER NOT NULL,
  start_time DATETIME NOT NULL,
  end_time DATETIME NOT NULL,
  day_of_week TEXT NOT NULL,
  FOREIGN KEY (doctor_location_id) REFERENCES doctor_locations (id)
);