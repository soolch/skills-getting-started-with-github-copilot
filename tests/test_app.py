"""
Tests for the FastAPI application
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test"""
    original_activities = {
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
        },
        "Basketball Club": {
            "description": "Team-based basketball practice and competitive games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in tournaments",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "sarah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore various art mediums and create visual masterpieces",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["ava@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop public speaking and argumentation skills through structured debates",
            "schedule": "Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on projects",
            "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
            "max_participants": 24,
            "participants": ["ethan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original_activities)


class TestActivities:
    """Test getting activities"""
    
    def test_get_activities(self, client):
        """Test that activities endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        assert len(data) == 9
    
    def test_activities_have_required_fields(self, client):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Test signup functionality"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_already_registered(self, client):
        """Test signing up a student already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregister:
    """Test unregister functionality"""
    
    def test_unregister_participant(self, client):
        """Test removing a participant from an activity"""
        # Verify participant exists
        activities_before = client.get("/activities").json()
        assert "michael@mergington.edu" in activities_before["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert "michael@mergington.edu" not in activities_after["Chess Club"]["participants"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistering a student not registered for activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a nonexistent activity"""
        response = client.post(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRoot:
    """Test root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static files"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
