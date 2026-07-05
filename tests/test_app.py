from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


client = TestClient(app_module.app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def restore_activities():
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    app_module.activities.clear()
    app_module.activities.update(deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_existing_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_rejects_duplicate_student():
    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": "emma@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_adds_new_student_to_activity():
    email = "new.student@mergington.edu"

    response = client.post(
        "/activities/Programming%20Class/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Programming Class"
    }
    assert email in app_module.activities["Programming Class"]["participants"]


def test_unregister_removes_student_from_activity():
    email = "alex@mergington.edu"

    response = client.delete(
        "/activities/Basketball/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Basketball"
    }
    assert email not in app_module.activities["Basketball"]["participants"]
