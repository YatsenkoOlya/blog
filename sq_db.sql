--CREATE TABLE IF NOT EXISTS mainmenu (
--id integer PRIMARY KEY AUTOINCREMENT,
--title text NOT NULL,
--url text NOT NULL
--);

CREATE TABLE IF NOT EXISTS posts (
id integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL,
text text NOT NULL,
url text NOT NULL,
time integer NOT NULL,
id_user integer NOT NULL,
id_topics integer NOT NULL
);

--CREATE TABLE IF NOT EXISTS users (
--id integer PRIMARY KEY AUTOINCREMENT,
--name text NOT NULL,
--email text NOT NULL,
--psw text NOT NULL,
--avatar BLOB DEFAULT NULL,
--time integer NOT NULL,
--is_admin integer NOT NULL
--);
CREATE TABLE IF NOT EXISTS authors (
id integer PRIMARY KEY AUTOINCREMENT,
login text NOT NULL
);

--CREATE TABLE IF NOT EXISTS posts_files (
--id_file integer PRIMARY KEY AUTOINCREMENT,
--id_post text,
--p_file BLOB NOT NULL,
--FOREIGN KEY (id_post) REFERENCES posts(id)
--);

CREATE TABLE IF NOT EXISTS topics (
id_topics integer PRIMARY KEY AUTOINCREMENT,
title text NOT NULL
);

CREATE TABLE IF NOT EXISTS comments (
id_comments integer PRIMARY KEY AUTOINCREMENT,
text text NOT NULL,
id_user integer NOT NULL,
id_post integer NOT NULL
);