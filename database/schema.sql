-- Vahan Dashboard Database Schema
-- Vehicle Registration Data Management System

-- Main vehicle registrations table
CREATE TABLE IF NOT EXISTS vehicle_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    year INTEGER NOT NULL,
    quarter TEXT NOT NULL CHECK (quarter IN ('Q1', 'Q2', 'Q3', 'Q4')),
    month INTEGER CHECK (month BETWEEN 1 AND 12),
    vehicle_type TEXT NOT NULL CHECK (vehicle_type IN ('2W', '3W', '4W')),
    manufacturer TEXT NOT NULL,
    model TEXT,
    fuel_type TEXT CHECK (fuel_type IN ('Petrol', 'Diesel', 'Electric', 'CNG', 'Hybrid')),
    registrations INTEGER NOT NULL CHECK (registrations >= 0),
    state_code TEXT DEFAULT 'ALL',
    region TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Manufacturer master table for data consistency
CREATE TABLE IF NOT EXISTS manufacturers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    vehicle_type TEXT NOT NULL,
    country TEXT,
    established_year INTEGER,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicle type master table
CREATE TABLE IF NOT EXISTS vehicle_types (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT
);

-- Growth metrics table for pre-calculated analytics
CREATE TABLE IF NOT EXISTS growth_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('manufacturer', 'vehicle_type', 'overall')),
    entity_name TEXT NOT NULL,
    metric_type TEXT NOT NULL CHECK (metric_type IN ('yoy', 'qoq', 'mom')),
    period TEXT NOT NULL, -- Format: YYYY-QX or YYYY-MM or YYYY
    current_value INTEGER NOT NULL,
    previous_value INTEGER,
    growth_rate REAL,
    growth_absolute INTEGER,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Market share snapshots
CREATE TABLE IF NOT EXISTS market_share (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT NOT NULL,
    vehicle_type TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    registrations INTEGER NOT NULL,
    market_share_percent REAL NOT NULL,
    rank_position INTEGER,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_registrations_date ON vehicle_registrations(date);
CREATE INDEX IF NOT EXISTS idx_registrations_year_quarter ON vehicle_registrations(year, quarter);
CREATE INDEX IF NOT EXISTS idx_registrations_vehicle_type ON vehicle_registrations(vehicle_type);
CREATE INDEX IF NOT EXISTS idx_registrations_manufacturer ON vehicle_registrations(manufacturer);
CREATE INDEX IF NOT EXISTS idx_registrations_composite ON vehicle_registrations(vehicle_type, manufacturer, year, quarter);

CREATE INDEX IF NOT EXISTS idx_growth_entity ON growth_metrics(entity_type, entity_name);
CREATE INDEX IF NOT EXISTS idx_growth_period ON growth_metrics(period, metric_type);

CREATE INDEX IF NOT EXISTS idx_market_share_period ON market_share(period, vehicle_type);

-- Insert master data for vehicle types
INSERT OR IGNORE INTO vehicle_types (code, name, description, category) VALUES
('2W', 'Two Wheeler', 'Motorcycles, Scooters, Mopeds', 'Personal Transport'),
('3W', 'Three Wheeler', 'Auto Rickshaws, Goods Carriers', 'Commercial Transport'),
('4W', 'Four Wheeler', 'Cars, SUVs, Commercial Vehicles', 'Personal & Commercial Transport');

-- Insert sample manufacturer data
INSERT OR IGNORE INTO manufacturers (name, vehicle_type, country, established_year) VALUES
-- 2W Manufacturers
('Hero MotoCorp', '2W', 'India', 1984),
('Honda Motorcycle', '2W', 'Japan', 1948),
('TVS Motor', '2W', 'India', 1978),
('Bajaj Auto', '2W', 'India', 1945),
('Yamaha', '2W', 'Japan', 1955),
('Royal Enfield', '2W', 'India', 1901),
('Suzuki', '2W', 'Japan', 1909),

-- 4W Manufacturers
('Maruti Suzuki', '4W', 'India', 1981),
('Hyundai', '4W', 'South Korea', 1967),
('Tata Motors', '4W', 'India', 1945),
('Mahindra', '4W', 'India', 1945),
('Kia', '4W', 'South Korea', 1944),
('Toyota', '4W', 'Japan', 1937),
('Honda Cars', '4W', 'Japan', 1948),
('Volkswagen', '4W', 'Germany', 1937),

-- 3W Manufacturers
('Bajaj Auto', '3W', 'India', 1945),
('TVS Motor', '3W', 'India', 1978),
('Mahindra', '3W', 'India', 1945),
('Piaggio', '3W', 'Italy', 1884),
('Atul Auto', '3W', 'India', 1986);
