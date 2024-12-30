-- Delete all existing records from the tables
DELETE FROM
    doctor_locations;

DELETE FROM
    doctors;

DELETE FROM
    locations;

DELETE FROM
    appointments;

DELETE FROM
    availability;

-- Insert doctors
INSERT INTO
    doctors (id, first_name, last_name)
VALUES
    (0, 'Jane', 'Wright'),
    (1, 'Joseph', 'Lister');

-- Insert locations
INSERT INTO
    locations (id, address)
VALUES
    (0, '1 Park St'),
    (1, '2 University Ave');

-- Associate doctors with locations
INSERT INTO
    doctor_locations (id, doctor_id, location_id)
VALUES
    (0, 0, 0),
    -- doctor_id=0, location_id=0
    (1, 1, 0),
    -- doctor_id=1, location_id=0
    (2, 1, 1);

-- doctor_id=1, location_id=1
-- Insert availability slots for doctor-location associations
INSERT INTO
    availability (
        id,
        doctor_location_id,
        start_time,
        end_time,
        day_of_week
    )
VALUES
    -- Availability for doctor_id=0, location_id=0
    (
        0,
        0,
        '2025-01-01T09:00:00',
        '2025-01-01T10:00:00',
        'Thursday'
    ),
    -- Availability for doctor_id=1, location_id=0
    (
        1,
        1,
        '2025-01-01T11:00:00',
        '2025-01-01T12:00:00',
        'Wednesday'
    ),
    -- Availability for doctor_id=1, location_id=1
    (
        2,
        2,
        '2025-01-01T12:00:00',
        '2025-01-01T12:30:00',
        'Wednesday'
    );

-- Insert appointments for doctor-location associations
INSERT INTO
    appointments (
        id,
        doctor_location_id,
        start_time,
        end_time,
        day_of_week
    )
VALUES
    -- Appointment for doctor_id=0, location_id=0
    (
        0,
        0,
        '2025-01-01T09:00:00',
        '2025-01-01T09:30:00',
        'Wednesday'
    ),
    -- Appointment for doctor_id=1, location_id=1
    (
        1,
        2,
        '2025-01-01T11:00:00',
        '2025-01-01T11:30:00',
        'Wednesday'
    ),
    -- Appointment for doctor_id=1, location_id=1
    (
        2,
        2,
        '2025-01-02T14:00:00',
        '2025-01-02T14:30:00',
        'Thursday'
    );