"""Test endpoints for countries.
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
    response = client.get("/countries?start=40&size=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5
    assert result[0]["id"] == 36


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
    response = client.head("/countries")
    assert response.status_code == 200

def test_options_countries(client, countries):
    "Test the OPTIONS method against /countries."
    response = client.options("/countries")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers['Allow'].split(',')]
    assert len(allowed) == 4
    assert 'GET' in allowed
    assert 'HEAD' in allowed
    assert 'POST' in allowed
    assert 'OPTIONS' in allowed

def test_get_with_id(client, counties):
    "Test if client/<id> works."
    response = client.get("/countries/1")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["name"] == "Country 1"

    assert len(result["counties"]) == 9
    assert result["counties"][0]["id"] == 1
    assert result["counties"][0]["name"] == "County 1"
    assert result["counties"][0]["link"] == "http://testserver/counties/1"

def test_get_with_non_existing_id(client, counties):
    "Requesting a non existing country must return 404."
    response = client.get("/countries/98765")
    assert response.status_code == 404

def test_options_with_id(client, countries):
    "Test the OPTIONS method against /countries(<id>)."
    response = client.options("/countries/1")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers['Allow'].split(',')]
    assert len(allowed) == 4
    assert 'GET' in allowed
    assert 'HEAD' in allowed
    assert 'PUT' in allowed
    assert 'OPTIONS' in allowed


def test_post(client):
    "Test POST to create a new Country."
    response = client.post("/countries", json={"name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["id"]
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"]
    assert not response.json()["counties"] #empty list


def test_post_with_id(client):
    "Test POST to create a new Country with a pre defined id."
    response = client.post("/countries", json={"id": 99, "name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["id"] == 99
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"] == "http://testserver/countries/99"
    assert not response.json()["counties"] #empty list


def test_post_with_existing_id(client, countries):
    "POST with an exisiting id must raise Error."
    response = client.post("/countries", json={"id": 1, "name": "FooBar"})
    assert response.status_code == 400


def test_put_update(client, counties):
    "Test put to update an existing country."
    response = client.put("/countries/1", json={"name": "BarFoo"})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "BarFoo"
    assert response.json()["link"] == "http://testserver/countries/1"
    assert len(response.json()["counties"]) == 9
    county1 = response.json()["counties"][0]
    assert county1["id"] == 1
    assert county1["name"] == "County 1"
    assert county1["link"] == "http://testserver/counties/1"


def test_put_create(client, countries):
    "Test put to update an existing country."
    response = client.put("/countries/9123", json={"name": "Foo"})
    assert response.status_code == 201
    assert response.json()["id"] == 9123
    assert response.json()["name"] == "Foo"
    assert response.json()["link"] == "http://testserver/countries/9123"
    assert not response.json()["counties"] #empty list


def test_delete(client, countries):
    "Delete is not implemented for countries."
    response = client.delete("/countries/1")
    assert response.status_code == 405

