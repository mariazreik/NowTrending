-- Set schema as default for this session
SET search_path TO student;

CREATE TABLE student.twitter_hashflags (
    id SERIAL PRIMARY KEY,
    hashtag VARCHAR(255) NOT NULL UNIQUE,  -- Added UNIQUE constraint on 'hashtag'
    starting_timestamp_ms TIMESTAMP NOT NULL,
    ending_timestamp_ms TIMESTAMP NOT NULL,
    asset_url TEXT,
    is_hashfetti_enabled BOOLEAN,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE student.twitter_trends (
    id SERIAL PRIMARY KEY,  -- Auto-incremented unique identifier
    trend_name VARCHAR(255) NOT NULL UNIQUE,  -- ✅ Make trend_name unique
    position INT NOT NULL,  
    meta_description TEXT,  
    domain_context VARCHAR(255),  
    url TEXT,  
    impression_id VARCHAR(255),  
    related_terms TEXT[],  
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

