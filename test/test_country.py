"""Test endpoints for countries.
"""
import pytest
from cities.crud import create_country
from cities.schemas import CountryCreate


def test_post(client):
    "Test POST to create a new Country."
    response = client.post("/countries", json={"name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["name"] == "FooBar"

def test_post_with_id(client):
    "Test POST to create a new Country with a pre defined id."
    response = client.post("/countries", json={"id":99, "name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["id"] == 99
    assert response.json()["name"] == "FooBar"