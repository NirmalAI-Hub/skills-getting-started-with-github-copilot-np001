"""
Pytest configuration and fixtures for the Activities API tests.

This module defines reusable fixtures for testing the FastAPI application,
including test data and a TestClient instance.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for the FastAPI app.
    
    Returns:
        TestClient: A test client for making requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """
    Fixture that provides sample test data for activities.
    
    Returns:
        dict: A dictionary of test activities with varying participant counts.
    """
    return {
        "Test Activity Zero": {
            "description": "Activity with no participants",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 10,
            "participants": []
        },
        "Test Activity One": {
            "description": "Activity with one participant",
            "schedule": "Tuesdays, 3:00 PM - 4:00 PM",
            "max_participants": 15,
            "participants": ["alice@example.com"]
        },
        "Test Activity Two": {
            "description": "Activity with two participants",
            "schedule": "Wednesdays, 3:00 PM - 4:00 PM",
            "max_participants": 20,
            "participants": ["bob@example.com", "charlie@example.com"]
        }
    }


@pytest.fixture
def test_email():
    """
    Fixture that provides a standard test email address.
    
    Returns:
        str: A test email address.
    """
    return "test@example.com"


@pytest.fixture
def another_test_email():
    """
    Fixture that provides a second test email address for multi-user scenarios.
    
    Returns:
        str: Another test email address.
    """
    return "another@example.com"


@pytest.fixture
def test_activity_name():
    """
    Fixture that provides a standard test activity name.
    
    Returns:
        str: A test activity name.
    """
    return "Test Activity One"
