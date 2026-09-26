import sys
import time
import json
import urllib.request
import urllib.error

def run_smoke_tests(base_url="http://localhost"):
    print(f"=== Starting Smoke Tests against {base_url} ===")
    
    # Test 1: Public Health Check via Nginx
    health_url = f"{base_url}/health"
    print(f"1. Testing Health Endpoint: {health_url}")
    try:
        req = urllib.request.Request(health_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert data.get("status") == "UP", f"Expected UP, got {data.get('status')}"
            print("   --> PASSED: Health status is UP")
    except Exception as e:
        print(f"   --> FAILED: {e}")
        return False

    # Test 2: OpenAPI Specification
    docs_url = f"{base_url}/openapi.json"
    print(f"2. Testing OpenAPI Schema Endpoint: {docs_url}")
    try:
        req = urllib.request.Request(docs_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert "openapi" in data, "OpenAPI key not in response"
            print(f"   --> PASSED: Schema title '{data.get('info', {}).get('title')}' verified")
    except Exception as e:
        print(f"   --> FAILED: {e}")
        return False

    # Test 3: Public Jobs List API
    jobs_url = f"{base_url}/api/jobs"
    print(f"3. Testing Jobs API: {jobs_url}")
    try:
        req = urllib.request.Request(jobs_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert isinstance(data, list), "Expected list of jobs"
            print(f"   --> PASSED: Successfully retrieved {len(data)} active jobs")
    except Exception as e:
        print(f"   --> FAILED: {e}")
        return False

    # Test 4: Frontend HTML Shell
    frontend_url = f"{base_url}/"
    print(f"4. Testing Frontend SPA Ingress: {frontend_url}")
    try:
        req = urllib.request.Request(frontend_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode()
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert "root" in body, "Expected #root in HTML template"
            print("   --> PASSED: Frontend SPA index loaded successfully")
    except Exception as e:
        print(f"   --> FAILED: {e}")
        return False

    # Test 5: Authentication API (Login with seeded admin)
    login_url = f"{base_url}/api/auth/login"
    print(f"5. Testing Auth Login API: {login_url}")
    try:
        payload = json.dumps({"email": "admin@placement.edu", "password": "Admin@123"}).encode("utf-8")
        req = urllib.request.Request(login_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            assert resp.status == 200, f"Expected 200, got {resp.status}"
            assert "access_token" in data, "No access_token returned"
            assert data.get("role") == "ADMIN", f"Expected ADMIN, got {data.get('role')}"
            print("   --> PASSED: Authentication succeeded, JWT token received")
    except Exception as e:
        print(f"   --> FAILED: {e}")
        return False

    print("=== All 5 Smoke Tests PASSED Successfully ===")
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
    success = run_smoke_tests(target)
    sys.exit(0 if success else 1)
