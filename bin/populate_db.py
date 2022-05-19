#!/usr/bin/env python
import csv
import requests
import sys


def populate_countries(base_url):
    "Push lines from countries.csv to data base."
    with open("countries.csv", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        success_counter = 0
        for row in reader:
            country_id = int(row["id"])
            del row["id"]
            r = requests.put(f"{base_url}/countries/{country_id}", json=row)
            if r.status_code >= 400:
                raise Exception(f"Error {r.status_code}: {r.text}")
            else:
                success_counter += 1
        print(f"Created {success_counter} countries")


def populate_counties(base_url):
    "Push lines from counties.csv to data base."
    with open("counties.csv", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        success_counter = 0
        for row in reader:
            county_id = int(row["id"])
            row["country_id"] = int(row["country_id"])
            r = requests.put(f"{base_url}/counties/{county_id}", json=row)
            if r.status_code >= 400:
                raise Exception(f"Error {r.status_code}: {r.text}")
            else:
                success_counter += 1
        print(f"Created {success_counter} counties")

def populate_cities(base_url):
    "Push lines from cities.csv to data base."
    with open("cities.csv", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        success_counter = 0
        for row in reader:
            row["id"] = int(row["id"])
            row["population"] = int(row["population"])
            row["county_id"] = int(row["county_id"])
            r = requests.put(f"{base_url}/cities/{row['id']}", json=row)
            if r.status_code >= 400:
                raise Exception(f"Error {r.status_code}: {r.text}")
            else:
                success_counter += 1
        print(f"Created {success_counter} cities")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        base_url = 'http://127.0.0.1:8000'
    else:
        base_url = sys.argv[1]
    populate_countries(base_url)
    populate_counties(base_url)
    populate_cities(base_url)

