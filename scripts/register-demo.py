#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick script to register demo client"""
import requests
import json
import sys

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_URL = "http://localhost/register"
data = {
    "organization_name": "Demo Organization",
    "email": "demo@example.com",
    "password": "demo123456",
    "webhook_url": "http://demo-website:5000/webhooks/moderation"
}

print("Registering demo client...")
try:
    response = requests.post(API_URL, json=data, timeout=10)
    response.raise_for_status()
    result = response.json()
    
    print(f"Success! Registered client")
    print(f"\nCredentials:")
    print(f"   API Key: {result['api_key']}")
    print(f"   HMAC Secret: {result['hmac_secret']}")
    print(f"\nUpdating .env file...")
    
    with open('.env', 'a') as f:
        f.write(f"\nDEMO_API_KEY={result['api_key']}\n")
        f.write(f"DEMO_HMAC_SECRET={result['hmac_secret']}\n")
    
    print("Done! Restart demo-website: docker-compose restart demo-website")
    
except Exception as e:
    print(f"Error: {e}")

