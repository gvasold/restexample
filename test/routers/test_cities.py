"""Test endpoints defined in routers/cities.
"""
import pytest
from cities.crud import create_city
from cities.schemas import CityCreate


def test_get(client, cities):
    "Test unparametrized request to /cities."
    response = client.get("/cities")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    assert results[0]["id"] == 1
    assert results[1]["id"] == 10

    # check response format
    c1 = results[0]
    assert c1["id"] == 1
    assert c1["name"] == "City 1"
    assert c1["link"] == "http://testserver/cities/1"


def test_get_with_invalid_params(client, cities):
    "Test invalid parameters."
    # start= must be 1 or greater.
    response = client.get("/cities?start=0")
    assert response.status_code == 422

    # size must be 1 or greater
    response = client.get("/cities?size=0")
    assert response.status_code == 422

    # minpop must be 1 or greater
    response = client.get("/cities?minpop=0")
    assert response.status_code == 422

    # maxpop must be 1 or greater
    response = client.get("/cities?maxpop=0")
    assert response.status_code == 422


def test_get_with_paging(client, cities):
    "Test if explicit paging works."
    response = client.get("/cities?start=41&size=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5
    assert result[0]["id"] == 36


def test_get_with_param_q(client, cities):
    "Test if ?q= works"
    response = client.get("/cities?q=ty+5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 11
    assert result[0]["name"] == "City 5"
    assert result[1]["name"] == "City 50"


def test_get_with_param_country(client, cities):
    "Test if country= works"
    response = client.get("/cities?country=Country+2&size=100")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 21


def test_get_with_param_county(client, cities):
    "Test if county= works"
    response = client.get("/cities?county=County+2&size=100")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 10


def test_head(client, cities):
    "Test a head_request against /cities"
    response = client.head("/cities/")
    assert response.status_code == 200


def test_options_counties(client, cities):
    "Test the OPTIONS method against /cities."
    response = client.options("/cities")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "POST" in allowed
    assert "OPTIONS" in allowed


def test_post(client, cities):
    "Test POST to create a new City."
    response = client.post(
        "/cities/", json={"name": "FooBar", "population": 1000, "county_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "FooBar"
    assert response.json()["population"] == 1000
    assert response.json()["county"]["id"] == 1
    assert response.json()["county"]["name"] == "County 1"
    assert response.json()["county"]["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"


def test_post_with_id(client, cities):
    "Test POST to create a new City with a pre defined id."
    response = client.post(
        "/cities/", json={"id": 999, "name": "FooBar", "population": 99, "county_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 999
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"] == "http://testserver/cities/999"
    assert response.json()["county"]["id"] == 1
    assert response.json()["county"]["name"] == "County 1"
    assert response.json()["county"]["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"


def test_post_with_existing_id(client, cities):
    "POST with an exisiting id must raise Error."
    response = client.post(
        "/cities/", json={"id": 1, "name": "FooBar", "population": 99, "county_id": 1}
    )
    assert response.status_code == 400


def test_post_with_non_existing_county_id(client, cities):
    "POST with county_id without county must raise Error."
    response = client.post(
        "/cities/", json={"name": "FooBar", "population": 77, "county_id": 9999}
    )
    assert response.status_code == 400
