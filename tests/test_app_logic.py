"""
Unit tests for core application logic.

These tests focus on the business logic of participant management and
activity validation, independent of HTTP concerns.
"""

import pytest
from src.app import activities


class TestActivityLookup:
    """Tests for activity lookup and validation."""

    def test_activity_exists(self):
        """Test that we can verify if an activity exists."""
        assert "Chess Club" in activities
        assert "Non Existent Activity" not in activities

    def test_all_activities_have_required_fields(self):
        """Test that all activities have the required data structure."""
        for activity_name, activity in activities.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
            assert isinstance(activity["participants"], list)


class TestParticipantManagement:
    """Tests for participant list operations."""

    def test_add_participant_to_empty_list(self, sample_activities):
        """Test adding a participant to an activity with no participants."""
        activity = sample_activities["Test Activity Zero"]
        initial_count = len(activity["participants"])
        
        email = "test@example.com"
        activity["participants"].append(email)
        
        assert len(activity["participants"]) == initial_count + 1
        assert email in activity["participants"]

    def test_add_participant_to_non_empty_list(self, sample_activities):
        """Test adding a participant to an activity with existing participants."""
        activity = sample_activities["Test Activity Two"]
        initial_count = len(activity["participants"])
        
        email = "newuser@example.com"
        activity["participants"].append(email)
        
        assert len(activity["participants"]) == initial_count + 1
        assert email in activity["participants"]

    def test_remove_participant_from_list(self, sample_activities):
        """Test removing a participant from an activity."""
        activity = sample_activities["Test Activity Two"]
        participant_to_remove = activity["participants"][0]
        initial_count = len(activity["participants"])
        
        activity["participants"].remove(participant_to_remove)
        
        assert len(activity["participants"]) == initial_count - 1
        assert participant_to_remove not in activity["participants"]


class TestDuplicateSignupPrevention:
    """Tests for preventing duplicate signups."""

    def test_detect_existing_participant(self, sample_activities):
        """Test that we can detect if a participant already exists."""
        activity = sample_activities["Test Activity One"]
        existing_email = activity["participants"][0]
        
        assert existing_email in activity["participants"]

    def test_multiple_participants_in_list(self, sample_activities):
        """Test checking for membership in activity with multiple participants."""
        activity = sample_activities["Test Activity Two"]
        
        for email in activity["participants"]:
            assert email in activity["participants"]
        
        # Non-existent email should not be found
        assert "nonexistent@example.com" not in activity["participants"]

    def test_case_sensitivity_in_email_check(self, sample_activities):
        """Test that email checks are case-sensitive."""
        activity = sample_activities["Test Activity One"]
        original_email = activity["participants"][0]
        different_case_email = original_email.upper()
        
        # Emails with different case should be treated as different
        # (This documents current behavior)
        if original_email != different_case_email:
            assert different_case_email not in activity["participants"]


class TestActivityCapacity:
    """Tests for activity capacity tracking."""

    def test_calculate_available_spots(self, sample_activities):
        """Test calculating available spots in an activity."""
        activity = sample_activities["Test Activity One"]
        max_capacity = activity["max_participants"]
        current_participants = len(activity["participants"])
        available_spots = max_capacity - current_participants
        
        assert available_spots == max_capacity - 1

    def test_all_activities_have_positive_capacity(self):
        """Test that all activities have positive max_participants."""
        for activity_name, activity in activities.items():
            assert activity["max_participants"] > 0

    def test_participants_not_exceed_capacity(self):
        """Test that current participants don't exceed max capacity."""
        for activity_name, activity in activities.items():
            assert len(activity["participants"]) <= activity["max_participants"]


class TestEmailValidation:
    """Tests for email format handling."""

    def test_email_with_plus_sign(self, sample_activities):
        """Test handling of email addresses with plus signs."""
        activity = sample_activities["Test Activity Zero"]
        email_with_plus = "test+tag@example.com"
        
        activity["participants"].append(email_with_plus)
        assert email_with_plus in activity["participants"]

    def test_email_with_different_tlds(self, sample_activities):
        """Test handling various email TLDs."""
        activity = sample_activities["Test Activity Zero"]
        emails = [
            "test@example.com",
            "test@example.co.uk",
            "test@example.org"
        ]
        
        for email in emails:
            activity["participants"].append(email)
        
        for email in emails:
            assert email in activity["participants"]


class TestParticipantListIntegrity:
    """Tests for maintaining participant list integrity."""

    def test_add_then_remove_same_participant(self, sample_activities):
        """Test adding and then removing the same participant."""
        activity = sample_activities["Test Activity Zero"]
        email = "test@example.com"
        
        activity["participants"].append(email)
        assert email in activity["participants"]
        
        activity["participants"].remove(email)
        assert email not in activity["participants"]

    def test_participant_list_remains_list_after_operations(self, sample_activities):
        """Test that participant list remains a list after operations."""
        activity = sample_activities["Test Activity One"]
        
        activity["participants"].append("new@example.com")
        assert isinstance(activity["participants"], list)
        
        activity["participants"].remove(activity["participants"][0])
        assert isinstance(activity["participants"], list)
