import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    """
    create table if not exists airlines(
        id serial primary key,
        ticker VARCHAR unique,
        name VARCHAR not null
    )
    """,
    """
    create table if not exists airports(
        id serial primary key,
        airport_code VARCHAR unique,
        airport_name VARCHAR not null,
        city VARCHAR not null,
        state VARCHAR not null,
        country VARCHAR not null,
        latitude VARCHAR not null,
        longitude VARCHAR not null
    )
    """,
    """
    create table if not exists flights(
        id serial primary key,
        date DATE not null DEFAULT CURRENT_DATE,
        airline_ticker VARCHAR REFERENCES airlines(ticker) ON DELETE CASCADE ON UPDATE CASCADE,
        flight_number VARCHAR not null,
        tail_number VARCHAR not null,
        starting_airport VARCHAR REFERENCES airports(airport_code)  ON DELETE CASCADE ON UPDATE CASCADE,
        destination_airport varchar REFERENCES airports(airport_code) ON DELETE CASCADE ON UPDATE CASCADE,
        scheduled_departure VARCHAR (5) NOT NULL,
        scheduled_arrival VARCHAR (5) NOT NULL,
        distance  VARCHAR NOT NULL
    )
    """,
    """
    create table if not exists users(
        user_id serial primary key,
        nick_name varchar(20) unique not null,
        mail varchar(30) unique not null,
        password varchar not null,
        name varchar not null,
        surname varchar not null, 
        phone varchar(15) not null,
        GENDER varchar(1) not null,
        user_description varchar not null,
        is_admin BOOLEAN NOT NULL DEFAULT FALSE
    )
    """,
    """
    create table if not exists feedback(
        id serial primary key,
        nick_name varchar(20) REFERENCES users(nick_name) ON DELETE CASCADE ON UPDATE CASCADE,
        type VARCHAR not null,
        class VARCHAR not null,
        satisfaction VARCHAR(1)  not null,
        online_support VARCHAR(1) not null,
        checking_service VARCHAR(1) not null,
        baggage_handling VARCHAR(1) not null,
        cleanliness VARCHAR(1) not null,
        airline_ticker VARCHAR REFERENCES airlines(ticker) ON DELETE CASCADE ON UPDATE CASCADE
    )
    """
]

# insert into airlines (ticker,name) values('THY','Turkish Airlines');
# insert into airlines (ticker,name) values('UA','United Air Lines Inc.');
# insert into airlines (ticker,name) values('AA','American Airlines Inc.');
# insert into airlines (ticker,name) values('US','US Airways Inc.');

# insert into airports (airport_code,airport_name,city,state,country,latitude,longitude) values ('ABE','Lehigh Valley International Airport','Allentown','PA','USA','40.65236','-75.4404');
# insert into airports (airport_code,airport_name,city,state,country,latitude,longitude) values ('ABI','Abilene Regional Airport','Abilene','TX','USA','32.41132','-99.6819');
# insert into airports (airport_code,airport_name,city,state,country,latitude,longitude) values ('ABQ','Albuquerque International Sunport','Albuquerque','NM','USA','35.04022','-106.60919');
# insert into airports (airport_code,airport_name,city,state,country,latitude,longitude) values ('ABR','Aberdeen Regional Airport','Aberdeen','SD','USA','45.44906','-98.42183');
# insert into airports (airport_code,airport_name,city,state,country,latitude,longitude) values ('ABY','Southwest Georgia Regional Airport','Albany','GA','USA','31.53552','-84.19447');


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
