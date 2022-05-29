"""Test endpoints defined in routers/country.
"""
from cities.routers.country import get_image_file_for, parse_accept_header
# pylint: disable=W0613


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
    "Test the OPTIONS method against /countries/<id>)."
    response = client.options("/countries/1")
    assert response.status_code == 204
    allowed = [x.strip() for x in response.headers["Allow"].split(",")]
    assert len(allowed) == 4
    assert "GET" in allowed
    assert "HEAD" in allowed
    assert "PUT" in allowed
    assert "OPTIONS" in allowed


def test_post_with_id(client):
    "Test POST to create a new Country with a pre defined id."
    response = client.post("/countries/", json={"id": 99, "name": "FooBar"})
    assert response.status_code == 201
    assert response.json()["id"] == 99
    assert response.json()["name"] == "FooBar"
    assert response.json()["link"] == "http://testserver/countries/99"
    assert not response.json()["counties"]  # empty list


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


def test_put_update_new_id_must_fail(client, counties):
    "Updates must not replace the id."
    response = client.put("/countries/1", json={"id": 9999, "name": "BarFoo"})
    assert response.status_code == 400


def test_put_create(client, countries):
    "Test put to update an existing country."
    response = client.put("/countries/9123", json={"name": "Foo"})
    assert response.status_code == 201
    assert response.json()["id"] == 9123
    assert response.json()["name"] == "Foo"
    assert response.json()["link"] == "http://testserver/countries/9123"
    assert not response.json()["counties"]  # empty list


def test_delete(client, countries):
    "Delete is not implemented for countries."
    response = client.delete("/countries/1")
    assert response.status_code == 405


def test_patch_name(client, countries):
    "Test if patching name works."
    response = client.patch("/countries/1", json={"name": "Foo"})
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Foo"


def test_patch_non_existing(client, counties):
    "Patching a non existing country leads to 404."
    response = client.patch("/countries/987654", json={"name": "Foo"})
    assert response.status_code == 404


def test_parse_accept_header():
    "Function should return the first matching content type."
    result = parse_accept_header(
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    )
    assert result is None

    assert parse_accept_header("image/svg+xml") == "image/svg+xml"
    assert parse_accept_header("image/png") == "image/png"
    assert parse_accept_header("image/jpeg") == "image/jpeg"
    assert parse_accept_header("image/gif") == "image/gif"


def test_get_image_file_for():
    "Should return path to the image file."
    assert "1.png" in get_image_file_for(1, "image/png")
    assert "2.jpg" in get_image_file_for(2, "image/jpeg")
    assert "3.gif" in get_image_file_for(3, "image/gif")
    assert "4.svg" in get_image_file_for(4, "image/svg+xml")
