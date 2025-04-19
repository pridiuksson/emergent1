import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackendAPITester:
    def __init__(self):
        # Get the backend URL from environment variable
        load_dotenv()
        self.base_url = os.getenv('REACT_APP_BACKEND_URL', 'http://localhost:8001')
        self.tests_run = 0
        self.tests_passed = 0
        logger.info(f"Testing backend at: {self.base_url}")

    def run_test(self, name, method, endpoint, expected_status=200, data=None):
        """Run a single API test"""
        self.tests_run += 1
        url = f"{self.base_url}/{endpoint}"
        
        try:
            logger.info(f"\n🔍 Testing {name} at {url}")
            
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            
            status_match = response.status_code == expected_status
            
            if status_match:
                self.tests_passed += 1
                logger.info(f"✅ {name} - Status: {response.status_code}")
                logger.info(f"Response: {response.json()}")
                return True, response.json()
            else:
                logger.error(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False, None

        except Exception as e:
            logger.error(f"❌ {name} - Error: {str(e)}")
            return False, None

    def test_root_endpoint(self):
        """Test the root endpoint"""
        return self.run_test(
            "Root Endpoint",
            "GET",
            "api",
            200
        )

def main():
    tester = BackendAPITester()
    
    # Test root endpoint
    tester.test_root_endpoint()
    
    # Print summary
    logger.info(f"\n📊 Test Summary:")
    logger.info(f"Tests Passed: {tester.tests_passed}/{tester.tests_run}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    main()