import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
    """
    create table if not exists airlines(
        id serial primary key,
        ticker varchar unique,
        name varchar not null
    )
    """,
    """
    create table if not exists airports(
        id serial primary key,
        airport_code varchar unique,
        airport_name varchar not null,
        city varchar not null,
        state varchar not null,
        country varchar not null,
        latitude float not null,
        longitude float not null
    )
    """,
    """
    create table if not exists flights(
        id serial primary key,
        year numeric(4) not null,
        month int not null,
        day int not null,
        airline_ticker varchar REFERENCES airlines(ticker),
        flight_number int not null,
        tail_number varchar not null,
        starting_airport varchar REFERENCES airports(airport_code),
        destination_airport varchar not null,
        departure_time int not null
    )
    """,
    """
    create table if not exists users(
        user_id serial primary key,
        name varchar not null,
        mail varchar(30) not null,
        password varchar not null,
        phone_number char(11) not null,
        affiliation varchar not null
    )
    """
]


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
