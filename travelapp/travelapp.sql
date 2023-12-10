-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS itinerary;
DROP TABLE IF EXISTS places;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  bio TEXT
);

CREATE TABLE itinerary (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	itinerary_name TEXT NOT NULL,
  country TEXT NOT NULL,
	FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE places (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	itinerary_id INTEGER NOT NULL,
	place TEXT NOT NULL,
  state TEXT,
	lat TEXT,
	lon TEXT,
	FOREIGN KEY (itinerary_id) REFERENCES itinerary (id)
);

CREATE TABLE posts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
