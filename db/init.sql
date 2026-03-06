-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Seed some initial data
INSERT INTO users (name, email) VALUES
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com'),
    ('Bob Johnson', 'bob@example.com')
ON CONFLICT (email) DO NOTHING;

-- Create events table (ACLED conflict events for South Sudan)
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    event_id_cnty VARCHAR(50) UNIQUE NOT NULL,
    event_date DATE NOT NULL,
    year INTEGER NOT NULL,
    time_precision INTEGER,
    disorder_type VARCHAR(255),
    event_type VARCHAR(255),
    sub_event_type VARCHAR(255),
    actor1 VARCHAR(500),
    assoc_actor_1 VARCHAR(500),
    inter1 VARCHAR(255),
    actor2 VARCHAR(500),
    assoc_actor_2 VARCHAR(500),
    inter2 VARCHAR(255),
    interaction VARCHAR(500),
    civilian_targeting VARCHAR(255),
    iso INTEGER,
    region VARCHAR(255),
    country VARCHAR(255),
    admin1 VARCHAR(255),
    admin2 VARCHAR(255),
    admin3 VARCHAR(255),
    location VARCHAR(255),
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    geo_precision INTEGER,
    source VARCHAR(255),
    source_scale VARCHAR(255),
    notes TEXT,
    fatalities INTEGER DEFAULT 0,
    tags VARCHAR(500),
    timestamp BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
