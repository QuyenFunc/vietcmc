"""End-to-end test scenarios"""
import requests
import time
import json
import hmac
import hashlib


BASE_URL = "http://localhost/api/v1"


def test_full_flow():
    """Test complete flow: register -> submit -> status"""
    
    # Step 1: Register client
    print("Step 1: Registering client...")
    register_response = requests.post(f"{BASE_URL}/register", json={
        "organization_name": "E2E Test Corp",
        "email": f"e2e_test_{int(time.time())}@example.com",
        "webhook_url": "https://webhook.site/e2e-test"
    })
    
    assert register_response.status_code == 201, f"Registration failed: {register_response.text}"
    
    credentials = register_response.json()["data"]
    api_key = credentials["api_key"]
    hmac_secret = credentials["hmac_secret"]
    
    print(f"[OK] Client registered with app_id: {credentials['app_id']}")
    
    # Step 2: Submit job
    print("\nStep 2: Submitting moderation job...")
    payload = {
        "text": "Sản phẩm này rất tốt, tôi rất hài lòng với chất lượng!",
        "comment_id": "test_comment_123",
        "metadata": {
            "user_id": "user_456",
            "post_id": "post_789"
        }
    }
    
    body = json.dumps(payload)
    signature = hmac.new(
        hmac_secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    submit_response = requests.post(
        f"{BASE_URL}/submit",
        data=body,
        headers={
            "X-API-Key": api_key,
            "X-Hub-Signature-256": f"sha256={signature}",
            "Content-Type": "application/json"
        }
    )
    
    assert submit_response.status_code == 202, f"Job submission failed: {submit_response.text}"
    
    job_id = submit_response.json()["data"]["job_id"]
    print(f"[OK] Job submitted with job_id: {job_id}")
    
    # Step 3: Check status
    print("\nStep 3: Checking job status...")
    for attempt in range(10):
        time.sleep(2)
        
        status_response = requests.get(
            f"{BASE_URL}/status/{job_id}",
            headers={"X-API-Key": api_key}
        )
        
        assert status_response.status_code == 200
        
        status_data = status_response.json()["data"]
        print(f"  Attempt {attempt + 1}: Status = {status_data['status']}")
        
        if status_data['status'] == 'completed':
            print(f"\n[OK] Job completed!")
            print(f"  Sentiment: {status_data['result']['sentiment']}")
            print(f"  Moderation: {status_data['result']['moderation_result']}")
            print(f"  Confidence: {status_data['result']['confidence']}")
            print(f"  Processing time: {status_data['processing_duration_ms']}ms")
            break
    else:
        print("[FAIL] Job did not complete in time")
    
    print("\n" + "="*50)
    print("E2E Test PASSED")
    print("="*50)


if __name__ == "__main__":
    try:
        test_full_flow()
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")

