DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS trip;
DROP TABLE IF EXISTS currency;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE post (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    trip INTEGER NOT NULL,
    post_date DATE NOT NULL,
    currency TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    title TEXT NOT NULL,
    label INTEGER NOT NULL,
    FOREIGN KEY (author_id) REFERENCES user (id),
    FOREIGN KEY (label) REFERENCES labels (label_id),
    FOREIGN KEY (currency) REFERENCES currency (currency_id),
    FOREIGN KEY (trip) REFERENCES currency (trip_id)
);

CREATE TABLE labels (
    label_id INTEGER PRIMARY KEY AUTOINCREMENT,
    label_name TEXT UNIQUE NOT NULL,
    user INTEGER NO NULL,
    FOREIGN KEY (user) REFERENCES user (id)
);

CREATE TABLE trip (
    trip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_name TEXT UNIQUE NOT NULL,
    user INTEGER NO NULL,
    FOREIGN KEY (user) REFERENCES user (id)
);

CREATE TABLE currency (
    currency_id INTEGER PRIMARY KEY AUTOINCREMENT,
    currency_name TEXT UNIQUE NOT NULL,
    symbol TEXT NOT NULL
);

INSERT INTO currency (currency_name, symbol) VALUES ('Dolar', 'U$');
INSERT INTO currency (currency_name, symbol) VALUES ('Euro', '€');
INSERT INTO currency (currency_name, symbol) VALUES ('Real', 'R$');