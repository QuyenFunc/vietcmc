import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../services/moderation-api'))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data


def test_register_client_success():
    """Test client registration with valid data"""
    payload = {
        "organization_name": "Test Organization",
        "email": f"test_{os.urandom(4).hex()}@example.com",
        "webhook_url": "https://example.com/webhook"
    }
    
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["success"] is True
    assert "app_id" in data["data"]
    assert "api_key" in data["data"]
    assert "hmac_secret" in data["data"]


def test_register_client_invalid_email():
    """Test client registration with invalid email"""
    payload = {
        "organization_name": "Test",
        "email": "invalid-email",
        "webhook_url": "https://example.com/webhook"
    }
    
    response = client.post("/api/v1/register", json=payload)
    assert response.status_code == 422


def test_submit_job_missing_api_key():
    """Test job submission without API key"""
    payload = {"text": "Test comment"}
    response = client.post("/api/v1/submit", json=payload)
    assert response.status_code == 401


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "version" in data

