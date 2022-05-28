"""Test endpoints defined in routers/countries.
"""
import pytest
from cities.crud import create_country
from cities.schemas import CountryCreate


def test_get(client, countries):
    "Test unparametrized request to /countries"
    response = client.get("/countries")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    assert results[0]["id"] == 1
    assert results[1]["id"] == 10

    # check response format
    c1 = results[0]
    assert c1["id"] == 1
    assert c1["name"] == "Country 1"
    assert c1["link"] == "http://testserver/countries/1"


def test_get_with_paging(client, countries):
    "Test if explicit paging works."
    response = client.get("/countries?start=41&size=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5
    assert result[0]["id"] == 36


def test_get_with_invalid_params(client, countries):
    "Test invalid parameters."
    # start= must be 1 or greater.
    response = client.get("/countries?start=0")
    assert response.status_code == 422

    # size must be 1 or greater
    response = client.get("/countries?size=0")
    assert response.status_code == 422


def test_get_with_param_q(client, countries):
    "Test if ?q= works"
    response = client.get("/countries?q=try+5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 11
    assert result[0]["name"] == "Country 5"
    assert result[1]["name"] == "Country 50"


def test_head(client, countries):
    "Test a head_request against /countries"
    response = client.head("/countries/")
    assert response.status_code == 200


def test_options_countries(client, countries):
    "Test the OPTIONS method against /countries."
    response = client.options("/countries/")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "POST" in allowed
    assert "OPTIONS" in allowed


def test_post(client):
    "Test POST to create a new Country."
    response = client.post("/countries/", json={"name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"]
    assert not response.json()["counties"]  # empty list


def test_post_with_existing_id(client, countries):
    "POST with an exisiting id must raise Error."
    response = client.post("/countries/", json={"id": 1, "name": "FooBar"})
    assert response.status_code == 400
