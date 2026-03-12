"""Tests for the High School Management System API

Tests cover GET /activities, signup functionality, participant deletion,
and error handling with proper reset of in-memory state.
"""

import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


# Store the initial state of activities for reset between tests
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities state before each test.

    This fixture ensures that in-memory state doesn't leak between tests.
    The autouse=True parameter automatically applies it to all tests.
    """
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the FastAPI app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_activities_count = len(INITIAL_ACTIVITIES)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == expected_activities_count
        assert "Chess Club" in response.json()
        assert "Programming Class" in response.json()


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_successful_signup(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_participant_count = len(
            activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()[
            "message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]
                   ) == initial_participant_count + 1

    def test_signup_duplicate_error(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_participant_count = len(
            activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
        assert len(activities[activity_name]
                   ["participants"]) == initial_participant_count

    def test_signup_unknown_activity_error(self, client):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestDeleteParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_successful_delete_participant(self, client):
        # Arrange
        activity_name = "Soccer Team"
        email = "alex@mergington.edu"  # Existing participant
        initial_participant_count = len(
            activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()[
            "message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]
                   ) == initial_participant_count - 1

    def test_delete_non_existent_participant_error(self, client):
        # Arrange
        activity_name = "Basketball Club"
        email = "nonexistent@mergington.edu"
        initial_participant_count = len(
            activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
        assert len(activities[activity_name]
                   ["participants"]) == initial_participant_count
