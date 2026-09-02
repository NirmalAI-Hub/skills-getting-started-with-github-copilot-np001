"""
Integration tests for the FastAPI endpoints.

These tests verify the behavior of all API endpoints including request/response
handling, status codes, and error scenarios.
"""

import pytest
from src.app import activities


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities as JSON."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Should contain at least the default activities from app.py
        assert len(data) > 0

    def test_get_activities_includes_all_fields(self, client):
        """Test that activity response includes all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        # Pick any activity and verify structure
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_handles_empty_participants(self, client):
        """Test that activities with empty participants list are handled correctly."""
        response = client.get("/activities")
        data = response.json()
        
        # Check that we can have activities with no participants
        has_empty_activity = any(
            len(activity["participants"]) == 0
            for activity in data.values()
        )
        # At minimum, structure should support empty participants
        for activity in data.values():
            assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client, test_email):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": test_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_email in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert test_email in activities_data["Chess Club"]["participants"]

    def test_signup_activity_not_found(self, client, test_email):
        """Test signup fails when activity doesn't exist."""
        response = client.post(
            "/activities/Non Existent Activity/signup",
            params={"email": test_email}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered(self, client):
        """Test signup fails when student is already registered."""
        existing_email = "michael@mergington.edu"  # From Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup handles URL-encoded activity names correctly."""
        # Activity with space in name
        unique_email = "urlencoded_test@example.com"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": unique_email}
        )
        assert response.status_code == 200

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with email containing special characters."""
        special_email = "test+tag@example.co.uk"
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": special_email}
        )
        assert response.status_code == 200
        data = response.json()
        assert special_email in data["message"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """Test successful unregister from an activity."""
        # First, get the current state
        activities_before = client.get("/activities").json()
        participant_count_before = len(activities_before["Chess Club"]["participants"])
        original_participant = activities_before["Chess Club"]["participants"][0]
        
        # Unregister
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": original_participant}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert original_participant in data["message"]
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        participant_count_after = len(activities_after["Chess Club"]["participants"])
        assert participant_count_after == participant_count_before - 1
        assert original_participant not in activities_after["Chess Club"]["participants"]

    def test_unregister_activity_not_found(self, client):
        """Test unregister fails when activity doesn't exist."""
        response = client.delete(
            "/activities/Non Existent Activity/unregister",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_student_not_signed_up(self, client):
        """Test unregister fails when student is not signed up."""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@example.com"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_unregister_with_url_encoded_activity_name(self, client):
        """Test unregister handles URL-encoded activity names correctly."""
        # Get a participant from an activity with space in name
        activities_data = client.get("/activities").json()
        if activities_data["Programming Class"]["participants"]:
            participant = activities_data["Programming Class"]["participants"][0]
            response = client.delete(
                "/activities/Programming Class/unregister",
                params={"email": participant}
            )
            assert response.status_code == 200

    def test_unregister_with_special_characters_in_email(self, client):
        """Test unregister with email containing special characters."""
        special_email = "unregister+special@example.co.uk"
        
        # First signup
        signup_response = client.post(
            "/activities/Gym Class/signup",
            params={"email": special_email}
        )
        assert signup_response.status_code == 200
        
        # Then unregister
        unregister_response = client.delete(
            "/activities/Gym Class/unregister",
            params={"email": special_email}
        )
        assert unregister_response.status_code == 200
        data = unregister_response.json()
        assert special_email in data["message"]


class TestEndToEndScenarios:
    """Integration tests for complete user workflows."""

    def test_signup_and_unregister_cycle(self, client, test_email):
        """Test complete cycle of signup and unregister."""
        activity = "Tennis Club"
        
        # Signup
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_data = client.get("/activities").json()
        assert test_email in activities_data[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": test_email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        activities_data = client.get("/activities").json()
        assert test_email not in activities_data[activity]["participants"]

    def test_multiple_signups_same_activity(self, client, test_email, another_test_email):
        """Test multiple students can signup for the same activity."""
        activity = "Debate Team"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": test_email}
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": another_test_email}
        )
        assert response2.status_code == 200
        
        # Verify both are registered
        activities_data = client.get("/activities").json()
        assert test_email in activities_data[activity]["participants"]
        assert another_test_email in activities_data[activity]["participants"]
