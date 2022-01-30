DROP TABLE IF EXISTS 
    user,
    post,
    labels,
    trip;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    current_trip INTEGER,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    trip INTEGER NOT NULL,
    post_date DATE NOT NULL,
    amount NUMERIC NOT NULL,
    title TEXT NOT NULL,
    label INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (label) REFERENCES labels (label_id)
);

CREATE TABLE labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label_name TEXT NOT NULL,
    user INTEGER NO NULL,
    FOREIGN KEY (user) REFERENCES user (id)
);

CREATE TABLE trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_name TEXT NOT NULL,
    user INTEGER NO NULL,
    FOREIGN KEY (user) REFERENCES user (id)
);