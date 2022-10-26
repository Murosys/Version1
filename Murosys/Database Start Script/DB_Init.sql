CREATE DATABASE IF NOT EXISTS murosys_database DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE murosys_database;


CREATE TABLE IF NOT EXISTS users (
	id int NOT NULL AUTO_INCREMENT,
  	username varchar(50) NOT NULL,
  	`password` varchar(100) NOT NULL,
  	email varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

drop table listening_history;
CREATE TABLE IF NOT EXISTS listening_history(
	endTime varchar(100),
    artistName varchar(50),
    trackName varchar(100),
    msPlayed int
);

drop table recommendations;
CREATE TABLE IF NOT EXISTS recommendations(
	trackName varchar(100),
    artistName varchar(50)
);

drop table songs;
CREATE TABLE IF NOT EXISTS songs(
	id varchar(100),
    `name` varchar(50),
    popularity int,
    duration_ms int,
    explicit int,
    artists varchar(100),
    id_artists varchar(200),
    release_date varchar(100),
    danceability double,
    energy double,
    `key` int,
    loudness double,
    `mode` int,
    speechiness double,
    acousticness double,
    instrumentalness double,
    liveliness double,
    valence double,
    tempo double,
    time_signature int
);

select * from recommendations limit 5;
INSERT INTO recommendations VALUES ("hotline bling", "drake");
INSERT INTO recommendations VALUES ("sticky", "drake");
select count(*) from listening_history;