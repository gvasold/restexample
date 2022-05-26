"""Test endpoints for counties.
"""
import pytest
from cities.crud import create_county
from cities.schemas import CountyCreate


def test_get(client, counties):
    "Test unparametrized request to /counties"
    response = client.get("/counties")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 20
    assert results[0]["id"] == 1
    assert results[1]["id"] == 10

    # check response format
    c1 = results[0]
    assert c1["id"] == 1
    assert c1["name"] == "County 1"
    assert c1["link"] == "http://testserver/counties/1"


def test_get_with_paging(client, counties):
    "Test if explicit paging works."
    response = client.get("/counties?start=40&size=5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 5
    assert result[0]["id"] == 36


def test_get_with_param_q(client, counties):
    "Test if ?q= works"
    response = client.get("/counties?q=ty+5")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 11
    assert result[0]["name"] == "County 5"
    assert result[1]["name"] == "County 50"


def test_head(client, counties):
    "Test a head_request against /counties"
    response = client.head("/counties")
    assert response.status_code == 200


def test_options_counties(client, counties):
    "Test the OPTIONS method against /counties."
    response = client.options("/counties")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "POST" in allowed
    assert "OPTIONS" in allowed


def test_get_with_id(client, cities):
    "Test if county/<id> works."
    response = client.get("/counties/1")
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == 1
    assert result["name"] == "County 1"

    assert len(result["cities"]) == 9
    assert result["cities"][0]["id"] == 1
    assert result["cities"][0]["name"] == "City 1"
    assert result["cities"][0]["link"] == "http://testserver/cities/1"


def test_get_with_non_existing_id(client, counties):
    "Requesting a non existing county must return 404."
    response = client.get("/counties/98765")
    assert response.status_code == 404


def test_options_with_id(client, counties):
    "Test the OPTIONS method against /counties/<id>)."
    response = client.options("/counties/1")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "PUT" in allowed
    assert "OPTIONS" in allowed


def test_post(client, countries):
    "Test POST to create a new County."
    response = client.post("/counties", json={"name": "FooBar", "country_id": 1})
    assert response.status_code == 201
    assert response.json()["name"] == "FooBar"
    assert response.json()["id"]
    assert response.json()["link"]
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county


def test_post_with_id(client, countries):
    "Test POST to create a new County with a pre defined id."
    response = client.post(
        "/counties", json={"id": 99, "name": "FooBar", "country_id": 1}
    )
    assert response.status_code == 201
    assert response.json()["id"] == 99
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"] == "http://testserver/counties/99"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county


def test_post_with_existing_id(client, counties):
    "POST with an exisiting id must raise Error."
    response = client.post(
        "/counties", json={"id": 1, "name": "FooBar", "country_id": 1}
    )
    assert response.status_code == 400


def test_post_with_non_exisiting_country_id(client, counties):
    "POST with country_id without country must raise Error."
    response = client.post("/counties", json={"name": "FooBar", "country_id": 9999})
    assert response.status_code == 400


def test_put_update(client, cities):
    "Test put to update an existing county."
    response = client.put("/counties/1", json={"name": "BarFoo", "country_id": 1})
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "BarFoo"
    assert response.json()["link"] == "http://testserver/counties/1"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert len(response.json()["cities"]) == 9
    city1 = response.json()["cities"][0]
    assert city1["id"] == 1
    assert city1["name"] == "City 1"
    assert city1["link"] == "http://testserver/cities/1"

def test_put_update_fail(client, counties):
    "Updating an existing county with a non existing country_id must fail."
    response = client.put(
        "/counties/1", json={"name": "BarFoo", "country_id": 99999}
    )
    assert response.status_code == 400


def test_put_create(client, counties):
    "Test put to update an existing county."
    response = client.put("/counties/9123", json={"name": "Foo", "country_id": 1})
    assert response.status_code == 201
    assert response.json()["id"] == 9123
    assert response.json()["name"] == "Foo"
    assert response.json()["link"] == "http://testserver/counties/9123"
    assert response.json()["country"]["id"] == 1
    assert response.json()["country"]["name"] == "Country 1"
    assert response.json()["country"]["link"] == "http://testserver/countries/1"
    assert not response.json()["cities"]  # No cities for new county

def test_put_create_fail(client, cities):
    "Creating a new county via put with a non existing country_id must fail."
    response = client.put(
        "/counties/98765", json={"name": "BarFoo", "country_id": 99999}
    )
    assert response.status_code == 400


def test_delete(client, counties):
    "Delete is not implemented for counties."
    response = client.delete("/counties/1")
    assert response.status_code == 405
