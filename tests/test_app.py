import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activity state before each test."""
    original = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app, follow_redirects=False)


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_root_redirects(client):
    response = client.get("/")
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9
    assert "Chess Club" in data


def test_get_activities_shape(client):
    response = client.get("/activities")
    chess = response.json()["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]
    assert "new@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_unknown_activity(client):
    response = client.post("/activities/Unknown Activity/signup?email=new@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate(client):
    client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    response = client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    assert "michael@mergington.edu" in response.json()["message"]
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity(client):
    response = client.delete("/activities/Unknown Activity/signup?email=michael@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_enrolled(client):
    response = client.delete("/activities/Chess Club/signup?email=nobody@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
