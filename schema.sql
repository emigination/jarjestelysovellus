CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    password TEXT
);
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location TEXT,
    owner_id INTEGER REFERENCES users
);