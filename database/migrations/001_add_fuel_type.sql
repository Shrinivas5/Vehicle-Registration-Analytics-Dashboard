-- Migration: Add fuel type tracking
-- Date: 2024-01-01

ALTER TABLE vehicle_registrations ADD COLUMN fuel_type TEXT CHECK (fuel_type IN ('Petrol', 'Diesel', 'Electric', 'CNG', 'Hybrid'));

-- Update existing records with sample fuel type data
UPDATE vehicle_registrations 
SET fuel_type = CASE 
    WHEN vehicle_type = '2W' THEN 
        CASE (ABS(RANDOM()) % 10)
            WHEN 0,1,2,3,4,5,6 THEN 'Petrol'
            WHEN 7,8 THEN 'Electric'
            ELSE 'CNG'
        END
    WHEN vehicle_type = '4W' THEN 
        CASE (ABS(RANDOM()) % 10)
            WHEN 0,1,2,3 THEN 'Petrol'
            WHEN 4,5,6 THEN 'Diesel'
            WHEN 7,8 THEN 'CNG'
            ELSE 'Electric'
        END
    ELSE 'CNG'
END
WHERE fuel_type IS NULL;
