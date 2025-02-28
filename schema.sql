CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    spotify_id VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    profile_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_artists (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    artist_name VARCHAR(100),
    artist_id VARCHAR(50), 
    popularity INT,
    followers INT,
    spotify_url TEXT,
    image_url TEXT
);

CREATE TABLE user_genres (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    genre_name VARCHAR(100)
);
