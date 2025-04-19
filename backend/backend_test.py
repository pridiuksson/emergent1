import requests
import pytest
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMixtapeAPI:
    def __init__(self):
        self.base_url = "https://c5c05f74-9ce7-4946-abe7-d7e2823838ee.preview.emergentagent.com"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        logger.info(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                logger.info(f"✅ Passed - Status: {response.status_code}")
            else:
                logger.error(f"❌ Failed - Expected {expected_status}, got {response.status_code}")

            return success, response.json() if success else {}

        except Exception as e:
            logger.error(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_generate_playlist(self, theme="rock"):
        """Test playlist generation"""
        return self.run_test(
            "Generate Playlist",
            "POST",
            "api/generate-playlist",
            200,
            data={"theme": theme, "count": 10}
        )

def main():
    tester = TestMixtapeAPI()
    
    # Test root endpoint
    root_success, root_response = tester.test_root_endpoint()
    assert root_success, "Root endpoint test failed"
    assert "message" in root_response, "Root endpoint response missing message"

    # Test playlist generation with different themes
    themes = ["rock", "pop", "hip hop"]
    for theme in themes:
        success, response = tester.test_generate_playlist(theme)
        assert success, f"Playlist generation failed for theme: {theme}"
        assert "playlist" in response, "Response missing playlist data"
        assert len(response["playlist"]) > 0, "Playlist is empty"
        
        # Verify playlist item structure
        first_song = response["playlist"][0]
        assert all(key in first_song for key in ["title", "artist", "videoId", "thumbnail"]), \
            "Playlist item missing required fields"

    logger.info(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()