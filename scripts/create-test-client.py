#!/usr/bin/env python3
"""
Script to create a test client for VietCMS Moderation API
This inserts a test client directly into the database
"""
import sys
import secrets
import string
import psycopg2
from datetime import datetime

def generate_api_key(length=32):
    """Generate a random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_hmac_secret(length=64):
    """Generate a random HMAC secret"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_app_id():
    """Generate a unique app ID"""
    return f"app_{secrets.token_hex(8)}"

def create_test_client():
    """Create a test client in the database"""
    
    # Database connection parameters
    conn_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'vietcms_moderation',
        'user': 'vietcms',
        'password': 'vietcms_password'
    }
    
    try:
        # Connect to database
        print("Connecting to database...")
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Generate credentials
        app_id = generate_app_id()
        api_key = generate_api_key()
        hmac_secret = generate_hmac_secret()
        
        # Insert test client
        print("\nCreating test client...")
        cursor.execute("""
            INSERT INTO clients (
                app_id, 
                organization_name, 
                email, 
                api_key, 
                hmac_secret, 
                webhook_url, 
                status, 
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, app_id, api_key, hmac_secret
        """, (
            app_id,
            'Test Organization',
            'test@example.com',
            api_key,
            hmac_secret,
            'http://localhost:3000/webhook',
            'active',
            datetime.utcnow()
        ))
        
        result = cursor.fetchone()
        conn.commit()
        
        print("\n" + "="*70)
        print("✅ TEST CLIENT CREATED SUCCESSFULLY!")
        print("="*70)
        print(f"\nApp ID:      {result[1]}")
        print(f"API Key:     {result[2]}")
        print(f"HMAC Secret: {result[3]}")
        print("\n" + "="*70)
        print("\n📝 INSTRUCTIONS:")
        print("1. Copy the API Key and HMAC Secret above")
        print("2. Open test-client/index.html in your browser")
        print("3. Paste the credentials in the Configuration section")
        print("4. Start testing!")
        print("\n⚠️  IMPORTANT: Save these credentials! They won't be shown again.")
        print("="*70 + "\n")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_test_client()

