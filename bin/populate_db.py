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
        # r = requests.post(f"{base_url}/cities", json={"name": "Legoland1", 
        #     "population": 1, "county_id": 3})
        # print(r.status_code)
        # print(r.text)

def delete_city(city_id, base_url):
    r = requests.delete(f"{base_url}/cities/{city_id}")
    print(r.status_code)
    print(r.text)

if __name__ == "__main__":
    populate_countries(sys.argv[1])
    populate_counties(sys.argv[1])
    populate_cities(sys.argv[1])

    #delete_city(1, sys.argv[1])

