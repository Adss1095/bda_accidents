CREATE DATABASE IF NOT EXISTS road_safety;
USE road_safety;

CREATE EXTERNAL TABLE IF NOT EXISTS accidents (
    accident_id STRING, accident_date STRING, accident_time STRING,
    district STRING, severity STRING, weather_condition STRING,
    road_surface STRING, vehicle_type STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data/road_accidents'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Accidents by district
SELECT district, COUNT(*) AS accident_count FROM accidents
GROUP BY district ORDER BY accident_count DESC;

-- By severity
SELECT severity, COUNT(*) AS total FROM accidents GROUP BY severity ORDER BY total DESC;

-- By weather
SELECT weather_condition, COUNT(*) AS total FROM accidents
GROUP BY weather_condition ORDER BY total DESC;

-- By road surface
SELECT road_surface, COUNT(*) AS total FROM accidents
GROUP BY road_surface ORDER BY total DESC;

-- By vehicle type
SELECT vehicle_type, COUNT(*) AS total FROM accidents
GROUP BY vehicle_type ORDER BY total DESC;

-- By hour of day
SELECT CAST(SUBSTR(accident_time, 1, 2) AS INT) AS hour, COUNT(*) AS total
FROM accidents GROUP BY CAST(SUBSTR(accident_time, 1, 2) AS INT) ORDER BY hour;
