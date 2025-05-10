drop database if exists life;
create database life;
use life;

-- Table: country
create table country (
    country_id int auto_increment primary key,
    country_name varchar(100) not null,
    region varchar(100) not null
);

-- Table: quality
create table quality (
    qol_id int auto_increment primary key,
    qol_index decimal(10, 2) not null,  
    stability int not null,
    rights int not null,
    health int not null,
    safety int not null,
    climate int not null,
    costs int not null,
    popularity int not null,
    country_id int not null,
    foreign key (country_id) references country (country_id)
);

-- Table: happiness
create table happiness (
    happiness_id int auto_increment primary key,
    happiness float not null,
    log_gdp float not null,
    social_support float not null,
    healthy_life_expectancy float not null,
    freedom float not null,
    generosity float not null,
    perceptions_of_corruption float not null,
    country_id int not null,
    foreign key (country_id) references country (country_id)
);