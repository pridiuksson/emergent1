import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL')

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BACKEND_URL}/api")
    assert response.status_code == 200
    assert response.json()["message"] == "Mixtape Generator API"

def test_generate_playlist_rock():
    """Test generating a rock playlist"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock", "count": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "playlist" in data
    assert len(data["playlist"]) == 5
    assert all(isinstance(song, dict) for song in data["playlist"])
    assert all(
        all(key in song for key in ["title", "artist", "videoId", "thumbnail"])
        for song in data["playlist"]
    )

def test_generate_playlist_pop():
    """Test generating a pop playlist"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "pop", "count": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert "playlist" in data
    assert len(data["playlist"]) == 3

def test_generate_playlist_invalid_count():
    """Test generating a playlist with invalid count"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock", "count": 20}  # Should be limited to 15
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["playlist"]) <= 15  # Count should be capped at 15

def test_generate_playlist_empty_theme():
    """Test generating a playlist with empty theme"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "", "count": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "playlist" in data
    assert len(data["playlist"]) == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
