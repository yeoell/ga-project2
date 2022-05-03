DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    id serial PRIMARY KEY,
    name text NOT NULL,
    image_url varchar(200)
);

CREATE TABLE users(
    id SERIAL PRIMARY KEY, 
    email TEXT, 
    first_name TEXT, 
    last_name TEXT,
    password_hash TEXT
);

CREATE TABLE recipe_detail(
    id SERIAL PRIMARY KEY, 
    ingredients TEXT, 
    method TEXT
);