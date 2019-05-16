/*
tables.sql
CS304 SP19 Final Project
Julia Klugherz, Karina Lin, Katherine Gao

*/

use c9;

drop table if exists uploadblob;
drop table if exists incident;
drop table if exists user;


create table user(
	BNUM		integer primary key,
	name 		varchar(100),
	email 		varchar(30),
	isAdmin 	Boolean,
	role 		enum ('facstaff', 'student')
)
ENGINE = InnoDB;

create table incident(
	reportID 		        integer auto_increment primary key,
	reporterID 		        integer,
	reportedID 		        integer,
	advocateID		        integer,
	location 		        varchar(30),
	category		        enum('racism', 'sexism', 'ableism', 'sexual harassment', 'other'),
	dateOfIncident 		    date,
	anonymousToAll   	    Boolean,
	anonymousToReported 	Boolean,
    description		        varchar(100),
    foreign key (reporterID) references user(BNUM),
    foreign key (reportedID) references user(BNUM),
    foreign key (advocateID) references user(BNUM)
)
ENGINE = InnoDB;

create table uploadblob(
	reportID integer primary key,
	file blob,
	foreign key (reportID) references incident(reportID)
	on delete cascade 
)
ENGINE = InnoDB;
