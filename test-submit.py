#!/usr/bin/env python3
import requests
import json
import hmac
import hashlib

API_KEY = "sk_live_pKv2B0Q-F5Btkn3l0f1DOzCyYHRI8QTaCtH5wdxVqX8"
HMAC_SECRET = "whsec_NNqLGHAaS8oOrCvgkFBegwj1Ry3lvJ_6pQ1QJKs8j50"
API_URL = "http://localhost/api/v1/submit"

data = {
    "comment_id": "test_comment_001",
    "text": "Đây là comment test để kiểm tra hệ thống",
    "metadata": {
        "author": "Test User",
        "source": "manual_test"
    }
}

# Calculate HMAC signature
body = json.dumps(data).encode('utf-8')
signature = hmac.new(
    HMAC_SECRET.encode('utf-8'),
    body,
    hashlib.sha256
).hexdigest()

print("Submitting job to VietCMS...")
try:
    response = requests.post(
        API_URL,
        data=body,
        headers={
            "X-API-Key": API_KEY,
            "X-Hub-Signature-256": f"sha256={signature}",
            "Content-Type": "application/json"
        },
        timeout=10
    )
    response.raise_for_status()
    result = response.json()
    
    print(f"Success! Job submitted")
    print(f"Job ID: {result.get('job_id')}")
    print(f"Status: {result.get('status')}")
    print(f"\nWait 5 seconds for processing...")
    print(f"\nCheck worker logs: docker logs vietcms-moderation-moderation-worker-1 --tail 50")
    print(f"Check webhook logs: docker logs vietcms-dispatcher --tail 50")
    print(f"Check demo backend: docker logs vietcms-demo-website --tail 50")
    
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")

