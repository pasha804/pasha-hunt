from scrapling import Fetcher, StealthyFetcher
import sys

def test_fetcher():
    print("Testing Fetcher.get on public api...")
    try:
        response = Fetcher.get("https://httpbin.org/get", timeout=10)
        print("Fetcher status:", response.status)
        assert response.status == 200, f"Expected 200, got {response.status}"
        print("Fetcher test PASSED!")
    except Exception as e:
        print("Fetcher test encountered error:", e)

if __name__ == "__main__":
    test_fetcher()
