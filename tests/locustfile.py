from locust import HttpUser, task, between
import json
import hmac
import hashlib
import random


class ModerationUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Register a client on start"""
        response = self.client.post("/api/v1/register", json={
            "organization_name": f"Load Test {random.randint(1000, 9999)}",
            "email": f"load{random.randint(1000, 9999)}@test.com",
            "webhook_url": "https://webhook.site/test"
        })
        
        if response.status_code == 201:
            data = response.json()["data"]
            self.api_key = data["api_key"]
            self.hmac_secret = data["hmac_secret"]
        else:
            # Fallback to mock credentials
            self.api_key = "test-key"
            self.hmac_secret = "test-secret"
    
    @task(10)
    def submit_job(self):
        """Submit a moderation job"""
        payload = {
            "text": "Sản phẩm rất tốt, tôi rất hài lòng với chất lượng!"
        }
        body = json.dumps(payload)
        
        # Generate HMAC signature
        signature = hmac.new(
            self.hmac_secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()
        
        self.client.post(
            "/api/v1/submit",
            data=body,
            headers={
                "X-API-Key": self.api_key,
                "X-Hub-Signature-256": f"sha256={signature}",
                "Content-Type": "application/json"
            },
            name="/api/v1/submit"
        )
    
    @task(2)
    def health_check(self):
        """Check health endpoint"""
        self.client.get("/api/v1/health", name="/api/v1/health")

