-- Create the traffic violations table
CREATE TABLE traffic_violations (
    id INTEGER PRIMARY KEY,
    violation_time DATETIME,
    district TEXT,
    violation_type TEXT,
    vehicle_type TEXT,
    plate_number TEXT
);

-- Create indexes for better query performance
CREATE INDEX idx_district ON traffic_violations(district);
CREATE INDEX idx_violation_type ON traffic_violations(violation_type);
CREATE INDEX idx_violation_time ON traffic_violations(violation_time);
