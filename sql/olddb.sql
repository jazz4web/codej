DROP TABLE permissions;
ALTER TABLE users DROP permissions;
ALTER TABLE users DROP sessions;
ALTER TABLE users ADD ugroup varchar(16);
ALTER TABLE users ADD weight smallint;
UPDATE users SET ugroup = 'Писатели';
UPDATE users SET weight = 100;
UPDATE users SET ugroup = 'Администраторы' WHERE username = 'webmaster';
UPDATE users SET weight = 255 WHERE username = 'webmaster';

CREATE TABLE sessions (
    suffix  varchar(13) UNIQUE NOT NULL,
    brkey   varchar(32),
    logedin timestamp,
    expire  timestamp,
    user_id integer REFERENCES users(id)
);

CREATE TABLE settings(
    indexpage varchar(16) DEFAULT NULL,
    dgroup    varchar(16) DEFAULT NULL,
    counters  text,
    robots    text
);

INSERT INTO settings (indexpage, dgroup, counters, robots)
  VALUES (NULL, NULL, NULL, NULL);
