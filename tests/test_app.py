"""
Tests for the Mergington High School Activities API
Uses the AAA (Arrange-Act-Assert) pattern with pytest
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(original)
    yield


client = TestClient(app)


def test_get_activities_returns_all_activities():
    """Test that GET /activities returns all activities"""
    # Arrange - activities are set up by the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_includes_description_and_participants():
    """Test that activities include description, schedule, and participants"""
    # Arrange - activities are set up by the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    chess = response.json()["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "participants" in chess
    assert "max_participants" in chess


def test_signup_for_activity_success():
    """Test that a student can sign up for an activity"""
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]


def test_signup_for_nonexistent_activity_returns_404():
    """Test that signing up for a nonexistent activity returns 404"""
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_duplicate_student_returns_400():
    """Test that signing up the same student twice returns 400"""
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_unregister_from_activity_success():
    """Test that a student can unregister from an activity"""
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_nonexistent_activity_returns_404():
    """Test that unregistering from a nonexistent activity returns 404"""
    # Arrange
    email = "student@mergington.edu"
    activity_name = "Nonexistent Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404


def test_unregister_student_not_signed_up_returns_400():
    """Test that unregistering a student not signed up returns 400"""
    # Arrange
    email = "notsignedup@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"].lower()
