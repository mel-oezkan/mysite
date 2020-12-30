-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS meet;
DROP TABLE IF EXISTS participant;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  realName TEXT NOT NULL,
  chatId INTEGER DEFAULT 0,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE meet (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  study_subject TEXT NOT NULL,
  datum TEXT NOT NULL,
  from_time TEXT NOT NULL,
  to_time TEXT NOT NULL,
  place TEXT NOT NULL,
  current_participants INTEGER DEFAULT 0,
  max_participants INTEGER DEFAULT 1,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE participant (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participant_id INTEGER NOT NULL,
    meet_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    study_subject TEXT NOT NULL,
    from_time TEXT NOT NULL,
    to_time TEXT NOT NULL,
    FOREIGN KEY (participant_id) REFERENCES user (id),
    FOREIGN KEY (meet_id) REFERENCES meet (id)
);


