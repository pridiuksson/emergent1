import pytest
import requests
import json

BACKEND_URL = "https://c5c05f74-9ce7-4946-abe7-d7e2823838ee.preview.emergentagent.com"

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get(f"{BACKEND_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Mixtape Generator API"

def test_generate_playlist():
    """Test playlist generation with different themes"""
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
        
        # Verify playlist data
        playlist = data["playlist"]
        assert isinstance(playlist, list)
        assert len(playlist) <= 5  # Should respect count parameter
        
        # Check each song has required fields
        for song in playlist:
            assert "title" in song
            assert "artist" in song
            assert "videoId" in song
            assert "thumbnail" in song
            
            # Verify data types
            assert isinstance(song["title"], str)
            assert isinstance(song["artist"], str)
            assert isinstance(song["videoId"], str)
            assert isinstance(song["thumbnail"], str)
            
            # Verify thumbnail URL format
            assert song["thumbnail"].startswith("http")

def test_error_handling():
    """Test error handling with invalid requests"""
    
    # Test missing theme
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"count": 5}
    )
    assert response.status_code in [400, 422]  # FastAPI validation error
    
    # Test invalid count
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock", "count": "invalid"}
    )
    assert response.status_code in [400, 422]  # FastAPI validation error
    
    # Test count exceeding limit
    response = requests.post(
        f"{BACKEND_URL}/api/generate-playlist",
        json={"theme": "rock", "count": 20}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["playlist"]) <= 15  # Should be capped at 15

if __name__ == "__main__":
    print("Testing root endpoint...")
    test_root_endpoint()
    print("✅ Root endpoint test passed")
    
    print("\nTesting playlist generation...")
    test_generate_playlist()
    print("✅ Playlist generation tests passed")
    
    print("\nTesting error handling...")
    test_error_handling()
    print("✅ Error handling tests passed")
    
    print("\n🎉 All backend tests passed!")