"""Provides a connect_db() function with returns a database connector for the cities database.

Also contains utily function to create the database from the csv file cities.csv.
 """
import csv
import os
import sqlite3


def read_csv(csv_file):
    "Split up the csv file into cities, counties and countries."
    cities = []
    counties = []
    countries = []
    with open(csv_file, encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # check if country already exists or create it otherwise
            matching_countries = [
                country for country in countries if country[1] == row["bundesland"]
            ]
            if matching_countries:
                country_id, country = matching_countries[0]
            else:
                country_id = len(countries) + 1
                country = row["bundesland"]
                countries.append([country_id, country])
            # check if county already exists or create it otherwise
            matching_counties = [
                county for county in counties if county[1] == row["bezirk"]
            ]
            if matching_counties:
                county_id, county, _ = matching_counties[0]
            else:
                county_id = len(counties) + 1
                county = row["bezirk"]
                counties.append([county_id, county, country_id])
            # every cities is only included once in the csv file
            cities.append(
                [len(cities) + 1, row["stadt"], int(row["einwohner"]), county_id]
            )
    return cities, counties, countries


def create_schema(conn):
    "Create the database schema."
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE countries (
        id integer primary key,
        name varchar)"""
    )
    cursor.execute(
        """CREATE TABLE counties (
        id integer primary key,
        name varchar,
        country_id integer REFERENCES countries(id))"""
    )
    cursor.execute(
        """CREATE TABLE cities (
        id integer primary key,
        name varchar,
        population integer,
        county_id integer REFERENCES counties(id))"""
    )
    conn.commit()


def create_db(db_file, csv_file):
    "Create the sqlite3 data base from csv file."
    cities, counties, countries = read_csv(csv_file)
    conn = sqlite3.connect(db_file)
    create_schema(conn)
    cursor = conn.cursor()
    cursor.executemany("INSERT INTO countries values(?, ?)", countries)
    cursor.executemany("INSERT INTO counties values(?, ?, ?)", counties)
    cursor.executemany("INSERT INTO cities values(?, ?, ?, ?)", cities)
    conn.commit()
    conn.close()


def connect_db(db_file):
    """Return a sqlite3 connection object.

    Creates the database if necessary.
    """
    if not os.path.exists(db_file):
        create_db(db_file, "data/cities.csv")
    return sqlite3.connect(db_file)
    
 DATABASE_URL, connect_args={"check_same_thread": False}

if __name__ == "__main__":
    connect_db("data/cities.db")
