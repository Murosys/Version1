CREATE DATABASE IF NOT EXISTS murosys_database DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE murosys_database;

CREATE TABLE IF NOT EXISTS users (
	id int NOT NULL AUTO_INCREMENT,
  	username varchar(50) NOT NULL,
  	password varchar(100) NOT NULL,
  	email varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS listening_history(
	endTime varchar(100),
    artistName varchar(50),
    trackName varchar(100),
    msPlayed int
);

select * from listening_history limit 5;