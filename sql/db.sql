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

CREATE TABLE friends (
    author_id integer REFERENCES users(id),
    friend_id integer REFERENCES users(id),
    CONSTRAINT author_friend_uni UNIQUE (author_id, friend_id)
);

CREATE TABLE followers (
    author_id   integer REFERENCES users(id),
    follower_id integer REFERENCES users(id),
    CONSTRAINT author_follower_uni UNIQUE (author_id, follower_id)
);

CREATE TABLE blockers (
    target_id  integer REFERENCES users(id),
    blocker_id integer REFERENCES users(id),
    CONSTRAINT target_blocker_uni UNIQUE (target_id, blocker_id)
);

CREATE TABLE albums (
    id        serial        PRIMARY KEY,
    title     varchar(100),
    created   timestamp,
    changed   timestamp,
    suffix    varchar(8)    UNIQUE,
    state     varchar(10),
    volume    integer       DEFAULT 0,
    author_id integer       REFERENCES users(id),
    CONSTRAINT author_title_uni UNIQUE (author_id, title)
);

CREATE TABLE pictures (
    uploaded timestamp,
    picture  bytea,
    filename varchar(128),
    width    integer,
    height   integer,
    format   varchar(6),
    volume   integer,
    suffix   varchar(14)   UNIQUE,
    album_id integer       REFERENCES albums(id)
);

CREATE TABLE articles (
    id        serial PRIMARY KEY,
    title     varchar(100),
    slug      varchar(128) UNIQUE,
    suffix    varchar(16)  UNIQUE,
    html      text         DEFAULT NULL,
    summary   varchar(512) DEFAULT NULL,
    meta      varchar(180) DEFAULT NULL,
    published timestamp    DEFAULT NULL,
    edited    timestamp,
    state     varchar(10),
    commented boolean      DEFAULT TRUE,
    viewed    integer      DEFAULT 0,
    author_id integer REFERENCES users(id)
);

CREATE TABLE paragraphs (
    num        integer DEFAULT 0,
    mdtext     text,
    article_id integer REFERENCES articles(id),
    CONSTRAINT article_num_uni UNIQUE (article_id, num)
);

CREATE TABLE labels (
    id serial PRIMARY KEY,
    label varchar(32) UNIQUE
);

CREATE TABLE als (
    article_id integer REFERENCES articles(id),
    label_id integer REFERENCES labels(id),
    CONSTRAINT art_label_uni UNIQUE (article_id, label_id)
);

CREATE TABLE aliases (
    url       text,
    created   timestamp,
    clicked   integer       DEFAULT 0,
    suffix    varchar(10)   UNIQUE,
    author_id integer       REFERENCES users(id),
    CONSTRAINT author_url_uni UNIQUE (author_id, url)
);

CREATE TABLE likes (
    article_id integer REFERENCES articles(id),
    user_id    integer REFERENCES users(id),
    CONSTRAINT article_l_user_uni UNIQUE (article_id, user_id)
);

CREATE TABLE dislikes (
    article_id integer REFERENCES articles(id),
    user_id    integer REFERENCES users(id),
    CONSTRAINT article_d_user_uni UNIQUE (article_id, user_id)
);

CREATE TABLE announces (
    headline  varchar(50),
    body      text         DEFAULT NULL,
    html      text         DEFAULT NULL,
    suffix    varchar(6)   UNIQUE,
    pub       boolean      DEFAULT FALSE,
    adm       boolean      DEFAULT FALSE,
    published timestamp,
    author_id integer REFERENCES users(id)
);

CREATE TABLE messages (
    id                   serial     PRIMARY KEY,
    sent                 timestamp,
    received             timestamp,
    body                 text       DEFAULT NULL,
    html                 text       DEFAULT NULL,
    postponed            boolean    DEFAULT FALSE,
    removed_by_sender    boolean    DEFAULT FALSE,
    removed_by_recipient boolean    DEFAULT FALSE,
    sender_id            integer REFERENCES users(id),
    recipient_id         integer REFERENCES users(id)
);

CREATE TABLE commentaries (
    id         serial     PRIMARY KEY,
    created    timestamp,
    deleted    boolean    DEFAULT FALSE,
    admined    boolean    DEFAULT FALSE,
    html       text       DEFAULT NULL,
    author_id  integer REFERENCES users(id),
    article_id integer REFERENCES articles(id),
    parent_id  integer REFERENCES commentaries(id)
);
