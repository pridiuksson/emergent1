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
        
        self.tests_run += 1
        logger.info(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                logger.info(f"✅ Passed - Status: {response.status_code}")
                return True, response.json()
            else:
                logger.error(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                return False, None

        except Exception as e:
            logger.error(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )

    def test_generate_playlist(self, theme):
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
    if root_success:
        logger.info(f"Root endpoint response: {root_response}")
    
    # Test playlist generation with different themes
    themes = ["rock", "pop", "hip hop"]
    for theme in themes:
        success, response = tester.test_generate_playlist(theme)
        if success:
            playlist = response.get('playlist', [])
            logger.info(f"\nGenerated playlist for theme '{theme}':")
            logger.info(f"Number of songs: {len(playlist)}")
            if playlist:
                logger.info("Sample song:")
                logger.info(f"Title: {playlist[0]['title']}")
                logger.info(f"Artist: {playlist[0]['artist']}")
                logger.info(f"Video ID: {playlist[0]['videoId']}")
    
    # Print final results
    logger.info(f"\n📊 Tests Summary:")
    logger.info(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()