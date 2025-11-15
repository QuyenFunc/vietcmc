-- Create a test client with fixed credentials for easy testing
-- Run this after database initialization

-- Insert test client
-- These credentials are for testing purposes only
INSERT INTO clients (
    app_id, 
    organization_name, 
    email, 
    api_key, 
    hmac_secret, 
    webhook_url, 
    status, 
    created_at
) VALUES (
    'test-app-123',
    'Test Organization',
    'test@example.com',
    'test_api_key_vietcms_2024_abcdef123456',
    'test_hmac_secret_vietcms_2024_xyz789',
    'http://localhost:3000/webhook',
    'active',
    now()
) ON CONFLICT (email) DO UPDATE SET
    api_key = EXCLUDED.api_key,
    hmac_secret = EXCLUDED.hmac_secret,
    status = EXCLUDED.status,
    updated_at = now();

-- Display the credentials
SELECT 
    '==================================================================' as separator
UNION ALL
SELECT '✅ TEST CLIENT CREATED SUCCESSFULLY!'
UNION ALL
SELECT '==================================================================' 
UNION ALL
SELECT ''
UNION ALL
SELECT '📋 CREDENTIALS FOR TEST CLIENT:'
UNION ALL
SELECT ''
UNION ALL
SELECT 'App ID:      test-app-123'
UNION ALL
SELECT 'API Key:     test_api_key_vietcms_2024_abcdef123456'
UNION ALL
SELECT 'HMAC Secret: test_hmac_secret_vietcms_2024_xyz789'
UNION ALL
SELECT 'Email:       test@example.com'
UNION ALL
SELECT ''
UNION ALL
SELECT '==================================================================' 
UNION ALL
SELECT '📝 These credentials are pre-filled in test-client/index.html'
UNION ALL
SELECT '⚠️  DO NOT use these credentials in production!'
UNION ALL
SELECT '==================================================================';

