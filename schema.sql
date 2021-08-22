CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE,
    password TEXT
);
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location_id INTEGER REFERENCES items,
    location TEXT,
    dimensions TEXT,
    year INTEGER
);
CREATE TABLE owners (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);
CREATE TABLE viewers (
    id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    tag TEXT,
    item_id INTEGER REFERENCES items ON DELETE CASCADE
);