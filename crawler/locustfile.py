from locust import HttpUser, task, between
import json

class ScanUser(HttpUser):
    wait_time = between(0.1, 0.2)  # Simulate 5 RPS
    
    @task
    def scan_endpoint(self):
        # Test URLs with different characteristics
        test_urls = [
            "https://example.com",
            "https://github.com",
            "https://stackoverflow.com"
        ]
        
        for url in test_urls:
            payload = {"url": url}
            with self.client.post(
                "/scan",
                json=payload,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        # Verify response structure
                        assert "scan_time_ms" in data
                        assert "cookies" in data
                        assert "cookie_banner_detected" in data
                    except (json.JSONDecodeError, AssertionError) as e:
                        response.failure(f"Invalid response format: {str(e)}")
                else:
                    response.failure(f"Got status code {response.status_code}")

# Run with:
# locust -f locustfile.py --host=http://localhost:8000 --users 5 --spawn-rate 5 --run-time 2m --headless 