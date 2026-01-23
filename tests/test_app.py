"""
Tests for the FastAPI application endpoints
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    yield
    # Reset participants to initial state
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = ["alex@mergington.edu"]
    activities["Tennis Club"]["participants"] = ["james@mergington.edu"]
    activities["Art Studio"]["participants"] = ["isabella@mergington.edu"]
    activities["Drama Club"]["participants"] = ["lucas@mergington.edu", "mia@mergington.edu"]
    activities["Science Bowl"]["participants"] = ["noah@mergington.edu"]
    activities["Debate Team"]["participants"] = ["ava@mergington.edu", "ethan@mergington.edu"]


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that getting activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9
    
    def test_get_activities_contains_required_fields(self, client):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client, reset_activities):
        """Test that duplicate signups are rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client, reset_activities):
        """Test unregistering a participant not in the activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test the complete flow of signup and unregister"""
        email = "testuser@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        assert email in activities["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            "/activities/Programming%20Class/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        assert email not in activities["Programming Class"]["participants"]
    
    def test_multiple_signups_same_activity(self, client, reset_activities):
        """Test multiple different participants signing up for same activity"""
        emails = ["user1@mergington.edu", "user2@mergington.edu", "user3@mergington.edu"]
        
        for email in emails:
            response = client.post(
                "/activities/Gym%20Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all were added
        for email in emails:
            assert email in activities["Gym Class"]["participants"]
