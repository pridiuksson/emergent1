import pytest
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in environment")

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BACKEND_URL}/")
    assert response.status_code == 200
    assert response.json() == {"message": "Mixtape Generator API"}

def test_generate_playlist_simple_themes():
    """Test playlist generation with simple themes"""
    themes = ["rock", "pop", "hip hop"]
    
    for theme in themes:
        response = requests.post(
            f"{BACKEND_URL}/api/generate-playlist",
            json={"theme": theme, "count": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "playlist" in data
        assert "message" in data
        assert len(data["playlist"]) <= 5
        
        # Verify each song has required fields
        for song in data["playlist"]:
            assert "title" in song
            assert "artist" in song
            assert "videoId" in song
            assert "thumbnail" in song
            assert isinstance(song["videoId"], str)
            assert song["videoId"] != ""

def test_generate_playlist_invalid_count():
    """Test playlist generation with invalid count"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock", "count": 100}  # Count too high
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["playlist"]) <= 15  # Should be limited to 15

def test_generate_playlist_empty_theme():
    """Test playlist generation with empty theme"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "", "count": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["playlist"]) > 0  # Should still return songs

def test_generate_playlist_special_characters():
    """Test playlist generation with special characters"""
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock!@#$%^&*()", "count": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["playlist"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
