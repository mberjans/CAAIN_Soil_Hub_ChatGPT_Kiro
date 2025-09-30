-- Mobile Location Database Schema
-- TICKET-008_farm-location-input-11.2: Add mobile-specific location features and capabilities

-- Field Boundaries Table
CREATE TABLE IF NOT EXISTS field_boundaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    field_name VARCHAR(200) NOT NULL,
    points JSONB NOT NULL, -- Array of GPS points with lat/lng/accuracy/timestamp
    area_acres DECIMAL(10,4),
    perimeter_meters DECIMAL(10,2),
    point_count INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT field_boundaries_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT field_boundaries_area_positive CHECK (area_acres >= 0),
    CONSTRAINT field_boundaries_perimeter_positive CHECK (perimeter_meters >= 0),
    CONSTRAINT field_boundaries_point_count_positive CHECK (point_count >= 0)
);

-- Field Photos Table
CREATE TABLE IF NOT EXISTS field_photos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    field_id VARCHAR(100),
    photo_data BYTEA NOT NULL, -- Binary photo data
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy DECIMAL(8, 2), -- GPS accuracy in meters
    notes TEXT,
    file_type VARCHAR(50) DEFAULT 'image/jpeg',
    captured_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT field_photos_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT field_photos_latitude_range CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT field_photos_longitude_range CHECK (longitude >= -180 AND longitude <= 180),
    CONSTRAINT field_photos_accuracy_positive CHECK (accuracy >= 0),
    CONSTRAINT field_photos_file_type_valid CHECK (file_type IN ('image/jpeg', 'image/png', 'image/webp', 'image/gif'))
);

-- Voice Notes Table
CREATE TABLE IF NOT EXISTS voice_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    field_id VARCHAR(100),
    audio_data BYTEA NOT NULL, -- Binary audio data
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    accuracy DECIMAL(8, 2), -- GPS accuracy in meters
    duration DECIMAL(8, 2), -- Audio duration in seconds
    notes TEXT,
    file_type VARCHAR(50) DEFAULT 'audio/webm',
    recorded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT voice_notes_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT voice_notes_latitude_range CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT voice_notes_longitude_range CHECK (longitude >= -180 AND longitude <= 180),
    CONSTRAINT voice_notes_accuracy_positive CHECK (accuracy >= 0),
    CONSTRAINT voice_notes_duration_positive CHECK (duration >= 0),
    CONSTRAINT voice_notes_file_type_valid CHECK (file_type IN ('audio/webm', 'audio/mp4', 'audio/wav', 'audio/ogg'))
);

-- Offline Sync Queue Table
CREATE TABLE IF NOT EXISTS offline_sync_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    data_type VARCHAR(20) NOT NULL, -- 'boundary', 'photo', 'voice_note'
    data JSONB NOT NULL, -- The actual data to sync
    created_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP, -- When the data was synced
    sync_attempts INTEGER DEFAULT 0,
    last_sync_error TEXT,
    
    -- Constraints
    CONSTRAINT offline_sync_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT offline_sync_data_type_valid CHECK (data_type IN ('boundary', 'photo', 'voice_note')),
    CONSTRAINT offline_sync_attempts_positive CHECK (sync_attempts >= 0)
);

-- Field Mapping Sessions Table
CREATE TABLE IF NOT EXISTS field_mapping_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    field_name VARCHAR(200) NOT NULL,
    start_latitude DECIMAL(10, 8) NOT NULL,
    start_longitude DECIMAL(11, 8) NOT NULL,
    points JSONB DEFAULT '[]'::jsonb, -- Array of GPS points
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT field_mapping_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT field_mapping_start_latitude_range CHECK (start_latitude >= -90 AND start_latitude <= 90),
    CONSTRAINT field_mapping_start_longitude_range CHECK (start_longitude >= -180 AND start_longitude <= 180)
);

-- Mobile Location Statistics Table
CREATE TABLE IF NOT EXISTS mobile_location_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    total_boundaries INTEGER DEFAULT 0,
    total_photos INTEGER DEFAULT 0,
    total_voice_notes INTEGER DEFAULT 0,
    total_area_mapped DECIMAL(12, 4) DEFAULT 0,
    last_activity TIMESTAMP,
    offline_sync_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT mobile_stats_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT mobile_stats_totals_positive CHECK (
        total_boundaries >= 0 AND 
        total_photos >= 0 AND 
        total_voice_notes >= 0 AND 
        total_area_mapped >= 0 AND 
        offline_sync_count >= 0
    )
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_field_boundaries_user_id ON field_boundaries(user_id);
CREATE INDEX IF NOT EXISTS idx_field_boundaries_created_at ON field_boundaries(created_at);
CREATE INDEX IF NOT EXISTS idx_field_boundaries_field_name ON field_boundaries(field_name);

CREATE INDEX IF NOT EXISTS idx_field_photos_user_id ON field_photos(user_id);
CREATE INDEX IF NOT EXISTS idx_field_photos_field_id ON field_photos(field_id);
CREATE INDEX IF NOT EXISTS idx_field_photos_captured_at ON field_photos(captured_at);
CREATE INDEX IF NOT EXISTS idx_field_photos_location ON field_photos(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_voice_notes_user_id ON voice_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_voice_notes_field_id ON voice_notes(field_id);
CREATE INDEX IF NOT EXISTS idx_voice_notes_recorded_at ON voice_notes(recorded_at);
CREATE INDEX IF NOT EXISTS idx_voice_notes_location ON voice_notes(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_offline_sync_user_id ON offline_sync_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_offline_sync_data_type ON offline_sync_queue(data_type);
CREATE INDEX IF NOT EXISTS idx_offline_sync_created_at ON offline_sync_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_offline_sync_synced_at ON offline_sync_queue(synced_at);

CREATE INDEX IF NOT EXISTS idx_field_mapping_user_id ON field_mapping_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_field_mapping_active ON field_mapping_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_field_mapping_started_at ON field_mapping_sessions(started_at);

CREATE INDEX IF NOT EXISTS idx_mobile_stats_user_id ON mobile_location_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_mobile_stats_last_activity ON mobile_location_stats(last_activity);

-- Triggers for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_field_boundaries_updated_at 
    BEFORE UPDATE ON field_boundaries 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_mobile_stats_updated_at 
    BEFORE UPDATE ON mobile_location_stats 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update mobile location statistics
CREATE OR REPLACE FUNCTION update_mobile_location_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- Update stats when new boundary is created
    IF TG_TABLE_NAME = 'field_boundaries' AND TG_OP = 'INSERT' THEN
        INSERT INTO mobile_location_stats (user_id, total_boundaries, total_area_mapped, last_activity)
        VALUES (NEW.user_id, 1, NEW.area_acres, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            total_boundaries = mobile_location_stats.total_boundaries + 1,
            total_area_mapped = mobile_location_stats.total_area_mapped + NEW.area_acres,
            last_activity = NOW(),
            updated_at = NOW();
    END IF;
    
    -- Update stats when new photo is created
    IF TG_TABLE_NAME = 'field_photos' AND TG_OP = 'INSERT' THEN
        INSERT INTO mobile_location_stats (user_id, total_photos, last_activity)
        VALUES (NEW.user_id, 1, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            total_photos = mobile_location_stats.total_photos + 1,
            last_activity = NOW(),
            updated_at = NOW();
    END IF;
    
    -- Update stats when new voice note is created
    IF TG_TABLE_NAME = 'voice_notes' AND TG_OP = 'INSERT' THEN
        INSERT INTO mobile_location_stats (user_id, total_voice_notes, last_activity)
        VALUES (NEW.user_id, 1, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            total_voice_notes = mobile_location_stats.total_voice_notes + 1,
            last_activity = NOW(),
            updated_at = NOW();
    END IF;
    
    -- Update stats when offline sync is completed
    IF TG_TABLE_NAME = 'offline_sync_queue' AND TG_OP = 'UPDATE' AND NEW.synced_at IS NOT NULL AND OLD.synced_at IS NULL THEN
        INSERT INTO mobile_location_stats (user_id, offline_sync_count, last_activity)
        VALUES (NEW.user_id, 1, NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            offline_sync_count = mobile_location_stats.offline_sync_count + 1,
            last_activity = NOW(),
            updated_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for automatic stats updates
CREATE TRIGGER update_stats_field_boundaries
    AFTER INSERT ON field_boundaries
    FOR EACH ROW EXECUTE FUNCTION update_mobile_location_stats();

CREATE TRIGGER update_stats_field_photos
    AFTER INSERT ON field_photos
    FOR EACH ROW EXECUTE FUNCTION update_mobile_location_stats();

CREATE TRIGGER update_stats_voice_notes
    AFTER INSERT ON voice_notes
    FOR EACH ROW EXECUTE FUNCTION update_mobile_location_stats();

CREATE TRIGGER update_stats_offline_sync
    AFTER UPDATE ON offline_sync_queue
    FOR EACH ROW EXECUTE FUNCTION update_mobile_location_stats();

-- Views for common queries
CREATE OR REPLACE VIEW user_mobile_activity_summary AS
SELECT 
    u.id as user_id,
    u.username,
    COALESCE(ms.total_boundaries, 0) as total_boundaries,
    COALESCE(ms.total_photos, 0) as total_photos,
    COALESCE(ms.total_voice_notes, 0) as total_voice_notes,
    COALESCE(ms.total_area_mapped, 0) as total_area_mapped,
    COALESCE(ms.offline_sync_count, 0) as offline_sync_count,
    ms.last_activity,
    COUNT(DISTINCT fb.id) as active_boundaries,
    COUNT(DISTINCT fp.id) as recent_photos,
    COUNT(DISTINCT vn.id) as recent_voice_notes
FROM users u
LEFT JOIN mobile_location_stats ms ON u.id = ms.user_id
LEFT JOIN field_boundaries fb ON u.id = fb.user_id AND fb.created_at > NOW() - INTERVAL '30 days'
LEFT JOIN field_photos fp ON u.id = fp.user_id AND fp.captured_at > NOW() - INTERVAL '7 days'
LEFT JOIN voice_notes vn ON u.id = vn.user_id AND vn.recorded_at > NOW() - INTERVAL '7 days'
GROUP BY u.id, u.username, ms.total_boundaries, ms.total_photos, ms.total_voice_notes, 
         ms.total_area_mapped, ms.offline_sync_count, ms.last_activity;

-- Function to clean up old mapping sessions
CREATE OR REPLACE FUNCTION cleanup_old_mapping_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete mapping sessions older than 24 hours that are still active
    DELETE FROM field_mapping_sessions 
    WHERE is_active = TRUE AND started_at < NOW() - INTERVAL '24 hours';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ language 'plpgsql';

-- Function to get field mapping statistics
CREATE OR REPLACE FUNCTION get_field_mapping_stats(user_uuid UUID)
RETURNS TABLE (
    total_sessions INTEGER,
    active_sessions INTEGER,
    completed_sessions INTEGER,
    total_area_mapped DECIMAL,
    average_session_duration INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_sessions,
        COUNT(*) FILTER (WHERE is_active = TRUE)::INTEGER as active_sessions,
        COUNT(*) FILTER (WHERE is_active = FALSE)::INTEGER as completed_sessions,
        COALESCE(SUM(area_acres), 0) as total_area_mapped,
        COALESCE(AVG(completed_at - started_at), INTERVAL '0') as average_session_duration
    FROM field_mapping_sessions fms
    LEFT JOIN field_boundaries fb ON fms.id = fb.id
    WHERE fms.user_id = user_uuid;
END;
$$ language 'plpgsql';

-- Comments for documentation
COMMENT ON TABLE field_boundaries IS 'Stores GPS-tracked field boundaries recorded from mobile devices';
COMMENT ON TABLE field_photos IS 'Stores field photos with automatic geotagging from mobile cameras';
COMMENT ON TABLE voice_notes IS 'Stores voice notes with geotagging for field annotations';
COMMENT ON TABLE offline_sync_queue IS 'Queue for synchronizing offline data collected on mobile devices';
COMMENT ON TABLE field_mapping_sessions IS 'Active field mapping sessions for GPS boundary recording';
COMMENT ON TABLE mobile_location_stats IS 'Statistics for mobile location feature usage';

COMMENT ON COLUMN field_boundaries.points IS 'JSON array of GPS points with latitude, longitude, accuracy, and timestamp';
COMMENT ON COLUMN field_photos.photo_data IS 'Binary image data captured from mobile camera';
COMMENT ON COLUMN voice_notes.audio_data IS 'Binary audio data recorded from mobile microphone';
COMMENT ON COLUMN offline_sync_queue.data IS 'JSON data to be synchronized when connection is restored';
COMMENT ON COLUMN field_mapping_sessions.points IS 'JSON array of GPS points collected during mapping session';