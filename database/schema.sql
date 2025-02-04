-- Set schema as default for this session
SET search_path TO student;


-- Creates Twitter Hashlags table
CREATE TABLE IF NOT EXISTS student.twitter_hashflags (
    id SERIAL PRIMARY KEY,
    hashtag VARCHAR(255) NOT NULL UNIQUE,  -- Added UNIQUE constraint on 'hashtag'
    starting_timestamp_ms TIMESTAMP NOT NULL,
    ending_timestamp_ms TIMESTAMP NOT NULL,
    asset_url TEXT,
    is_hashfetti_enabled BOOLEAN,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Creates the Twitter Trends table
CREATE TABLE IF NOT EXISTS student.twitter_trend (
    id SERIAL PRIMARY KEY,  -- Auto-incremented unique identifier
    trend_name VARCHAR(255) NOT NULL,  -- ✅ Make trend_name unique
    position INT NOT NULL,  
    meta_description TEXT,  
    domain_context VARCHAR(255),  
    url TEXT,  
    impression_id VARCHAR(255),  
    related_terms TEXT[],  
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_id VARCHAR(255) NOT NULL,
    CONSTRAINT unique_trend_per_location UNIQUE (trend_name, location_id)  -- ✅ Ensures uniqueness per location
);

-- A table to map the trends to the locations
CREATE TABLE IF NOT EXISTS student.twitter_locations (
    location_id VARCHAR(255) PRIMARY KEY,  
    country_name VARCHAR(255) NOT NULL
);


-- Creates the Google Trends tables
-- Table for storing Google Trends keywords separately
CREATE TABLE IF NOT EXISTS student.google_locations (
    id SERIAL PRIMARY KEY,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    message TEXT DEFAULT 'OK',
    country TEXT NOT NULL,
    lastUpdate TIMESTAMP,
    scrapedAt TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Separate table for keywords
CREATE TABLE IF NOT EXISTS student.google_trend (
    id SERIAL PRIMARY KEY,
    google_location_id INT REFERENCES student.google_locations(id) ON DELETE CASCADE,
    keyword TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
