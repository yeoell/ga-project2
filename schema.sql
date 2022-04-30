DROP TABLE IF EXISTS recipes;

CREATE TABLE recipes (
    id serial PRIMARY KEY,
    name varchar(50) NOT NULL,
    image_url varchar(200),
);