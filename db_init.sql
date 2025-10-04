-- Database initialization untuk Tsunami Detection
-- File ini akan dijalankan otomatis saat container PostgreSQL pertama kali dibuat

-- Create database jika belum ada
-- CREATE DATABASE IF NOT EXISTS tsunami_db;

-- Use database
-- \c tsunami_db;

-- Create user jika belum ada
-- CREATE USER IF NOT EXISTS tsunami_user WITH ENCRYPTED PASSWORD 'tsunami_secure_pass_2024';

-- Grant privileges
-- GRANT ALL PRIVILEGES ON DATABASE tsunami_db TO tsunami_user;

-- Create tables untuk logging dan monitoring
CREATE TABLE IF NOT EXISTS wave_detections (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tanggal DATE NOT NULL,
    jam TIME NOT NULL,
    frame_number INTEGER,
    puncak_ombak_y INTEGER,
    status_ombak VARCHAR(50),
    jumlah_garis_terdeteksi INTEGER,
    extreme_count INTEGER DEFAULT 0,
    alert_sent BOOLEAN DEFAULT FALSE,
    camera_location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tsunami_alerts (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL, -- 'TSUNAMI', 'EARTHQUAKE', 'TEST'
    message TEXT,
    recipient VARCHAR(100),
    delivery_status VARCHAR(50), -- 'SENT', 'FAILED', 'PENDING'
    extreme_count INTEGER,
    camera_location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS earthquake_events (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    earthquake_time TIMESTAMP WITH TIME ZONE,
    magnitude DECIMAL(3,1),
    depth INTEGER,
    location VARCHAR(255),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    tsunami_potential BOOLEAN DEFAULT FALSE,
    alert_sent BOOLEAN DEFAULT FALSE,
    source VARCHAR(50) DEFAULT 'BMKG',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    log_level VARCHAR(20), -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    component VARCHAR(50), -- 'WAVE_DETECTION', 'ALERT_SYSTEM', 'EARTHQUAKE_MONITOR'
    message TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes untuk performance
CREATE INDEX IF NOT EXISTS idx_wave_detections_timestamp ON wave_detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_wave_detections_status ON wave_detections(status_ombak);
CREATE INDEX IF NOT EXISTS idx_tsunami_alerts_timestamp ON tsunami_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_tsunami_alerts_type ON tsunami_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_earthquake_events_timestamp ON earthquake_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_earthquake_events_magnitude ON earthquake_events(magnitude);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_logs_level ON system_logs(log_level);

-- Create views untuk reporting
CREATE OR REPLACE VIEW daily_wave_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_detections,
    COUNT(CASE WHEN status_ombak = 'EXTREME' THEN 1 END) as extreme_count,
    COUNT(CASE WHEN status_ombak = '4 m (SANGAT TINGGI)' THEN 1 END) as very_high_count,
    COUNT(CASE WHEN status_ombak = '2,5 m (TINGGI)' THEN 1 END) as high_count,
    COUNT(CASE WHEN alert_sent = TRUE THEN 1 END) as alerts_sent,
    MAX(puncak_ombak_y) as max_wave_height,
    MIN(puncak_ombak_y) as min_wave_height,
    AVG(puncak_ombak_y) as avg_wave_height
FROM wave_detections 
GROUP BY DATE(timestamp)
ORDER BY date DESC;

CREATE OR REPLACE VIEW recent_alerts AS
SELECT 
    ta.*,
    CASE 
        WHEN ta.timestamp > NOW() - INTERVAL '1 hour' THEN 'RECENT'
        WHEN ta.timestamp > NOW() - INTERVAL '1 day' THEN 'TODAY'
        ELSE 'OLDER'
    END as recency
FROM tsunami_alerts ta
ORDER BY ta.timestamp DESC;

-- Grant permissions pada tables dan views
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO tsunami_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO tsunami_user;
GRANT SELECT ON daily_wave_summary TO tsunami_user;
GRANT SELECT ON recent_alerts TO tsunami_user;

-- Insert sample data untuk testing (optional)
-- INSERT INTO wave_detections (tanggal, jam, frame_number, puncak_ombak_y, status_ombak, jumlah_garis_terdeteksi, camera_location)
-- VALUES 
--     (CURRENT_DATE, CURRENT_TIME, 1, 200, 'NORMAL', 5, 'Test Camera Location'),
--     (CURRENT_DATE, CURRENT_TIME, 2, 150, 'RENDAH', 3, 'Test Camera Location');

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Tsunami Detection Database initialized successfully!';
    RAISE NOTICE 'Tables created: wave_detections, tsunami_alerts, earthquake_events, system_logs';
    RAISE NOTICE 'Views created: daily_wave_summary, recent_alerts';
END $$;