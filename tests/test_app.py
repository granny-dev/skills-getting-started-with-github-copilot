from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # each test should start with fresh copy of the in-memory data
    # simplest approach: reassign activities dictionary contents
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        }
    })
    yield


def test_get_activities():
    # Arrange: nothing special, fixture has set up activities

    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_success():
    # Arrange
    email = "test@mergington.edu"
    url = "/activities/Chess%20Club/signup?email=" + email

    # Act
    resp = client.post(url)

    # Assert
    assert resp.status_code == 200
    assert resp.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    # Arrange
    email = "dup@mergington.edu"
    url = "/activities/Chess%20Club/signup?email=" + email
    client.post(url)  # initial signup

    # Act
    resp = client.post(url)  # duplicate request

    # Assert
    assert resp.status_code == 400
    assert "already signed up" in resp.json()["detail"]


def test_signup_nonexistent_activity():
    # Arrange
    url = "/activities/Nope/signup?email=foo@bar.com"

    # Act
    resp = client.post(url)

    # Assert
    assert resp.status_code == 404


def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    url = "/activities/Chess%20Club/participants?email=" + email

    # Act
    resp = client.delete(url)

    # Assert
    assert resp.status_code == 200
    assert f"Removed {email}" in resp.json()["message"]
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_found():
    # Arrange
    url = "/activities/Chess%20Club/participants?email=nosuch@foo.com"

    # Act
    resp = client.delete(url)

    # Assert
    assert resp.status_code == 404


def test_unregister_activity_not_found():
    # Arrange
    url = "/activities/NoClub/participants?email=foo@bar.com"

    # Act
    resp = client.delete(url)

    # Assert
    assert resp.status_code == 404
