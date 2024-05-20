CREATE TABLE captchas (
    picture bytea NOT NULL,
    val     varchar(5) UNIQUE,
    suffix  varchar(7) UNIQUE
);

CREATE TABLE users (
    id             serial PRIMARY KEY,
    username       varchar(16) UNIQUE NOT NULL,
    ugroup         varchar(16),
    weight         smallint,
    registered     timestamp,
    last_visit     timestamp,
    password_hash  varchar(128),
    description    varchar(500) DEFAULT NULL,
    last_published timestamp DEFAULT NULL
);

CREATE TABLE accounts (
    id        serial PRIMARY KEY,
    address   varchar(128) UNIQUE,
    swap      varchar(128),
    requested timestamp,
    user_id   integer REFERENCES users(id) UNIQUE
);

CREATE TABLE sessions (
    suffix  varchar(13) UNIQUE NOT NULL,
    brkey   varchar(32),
    logedin timestamp,
    expire  timestamp,
    user_id integer REFERENCES users(id)
);

CREATE TABLE avatars (
    picture bytea NOT NULL,
    user_id integer REFERENCES users(id) UNIQUE
);
