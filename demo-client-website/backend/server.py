"""
Backend Flask Server - API for Demo Client Website
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hmac
import hashlib
from datetime import datetime
import json
import requests
import os
import psycopg2
from psycopg2.extras import RealDictCursor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'dist'))

app = Flask(
    __name__,
    static_folder=DIST_DIR,
    static_url_path=''
)
CORS(app)

# Storage (use database in production)
comments = []
moderation_results = {}

# VietCMS Configuration
VIETCMS_API_URL = os.getenv('VIETCMS_API_URL', 'http://localhost:8000/api/v1')
VIETCMS_API_KEY = os.getenv('VIETCMS_API_KEY', 'YOUR_API_KEY_HERE')
HMAC_SECRET = os.getenv('HMAC_SECRET', 'YOUR_HMAC_SECRET_HERE')

# Runtime config (can be overridden via API)
runtime_config = {
    'api_url': VIETCMS_API_URL,
    'api_key': VIETCMS_API_KEY,
    'hmac_secret': HMAC_SECRET,
    'webhook_url': ''
}

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': os.getenv('POSTGRES_PORT', '5432'),
    'database': os.getenv('POSTGRES_DB', 'vietcms_moderation'),
    'user': os.getenv('POSTGRES_USER', 'vietcms'),
    'password': os.getenv('POSTGRES_PASSWORD', 'vietcms_password_123')
}


def mask_secret(value: str, visible: int = 4) -> str:
    """Create a masked preview of a secret for UI display."""
    if not value or value in {'YOUR_API_KEY_HERE', 'YOUR_HMAC_SECRET_HERE'}:
        return ''

    if len(value) <= visible * 2:
        return value

    return f"{value[:visible]}...{value[-visible:]}"

def get_config():
    """Get current config (runtime or env)"""
    return {
        'api_url': runtime_config.get('api_url', VIETCMS_API_URL),
        'api_key': runtime_config.get('api_key', VIETCMS_API_KEY),
        'hmac_secret': runtime_config.get('hmac_secret', HMAC_SECRET),
        'webhook_url': runtime_config.get('webhook_url', '')
    }


def verify_webhook_signature(body, signature):
    """Verify HMAC signature from VietCMS"""
    if not signature or not signature.startswith('sha256='):
        return False
    
    config = get_config()
    hmac_secret = config['hmac_secret']
    
    received_signature = signature[7:]
    expected_signature = hmac.new(
        hmac_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_signature, expected_signature)


@app.route('/api/comments', methods=['GET'])
def get_comments():
    """Get all comments from database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query ALL jobs directly from database
        query = """
            SELECT 
                job_id,
                comment_id,
                text,
                job_metadata,
                status,
                moderation_result,
                sentiment,
                confidence_score,
                reasoning,
                processing_duration_ms,
                created_at
            FROM jobs
            ORDER BY created_at DESC
        """
        cursor.execute(query)
        jobs = cursor.fetchall()
        
        # Convert database jobs to comment format
        all_comments = []
        for job in jobs:
            # Extract author from metadata if available
            author = 'Anonymous'
            if job['job_metadata'] and isinstance(job['job_metadata'], dict):
                author = job['job_metadata'].get('author', 'Anonymous')
            
            comment = {
                'id': job['comment_id'],
                'job_id': job['job_id'],
                'author': author,
                'text': job['text'],
                'created_at': job['created_at'].isoformat() if job['created_at'] else None,
                'status': 'pending',
                'moderation_result': None,
                'visible': True
            }
            
            # Update status based on job status
            if job['status'] == 'completed':
                comment['status'] = 'moderated'
                comment['moderation_result'] = job['moderation_result']
                comment['sentiment'] = job['sentiment']
                comment['confidence'] = job['confidence_score']
                comment['reasoning'] = job['reasoning']
                comment['processing_time'] = job['processing_duration_ms']
                
                # Extract type from metadata if available
                if job['job_metadata'] and isinstance(job['job_metadata'], dict):
                    comment['type'] = job['job_metadata'].get('type', 'text')
                
                # Set visibility based on moderation result
                if job['moderation_result'] == 'reject':
                    comment['visible'] = False
                elif job['moderation_result'] == 'review':
                    comment['visible'] = False
                    comment['needs_review'] = True
                else:
                    comment['visible'] = True
            elif job['status'] == 'processing' or job['status'] == 'queued':
                comment['status'] = 'processing'
            elif job['status'] == 'failed':
                comment['status'] = 'error'
            
            all_comments.append(comment)
        
        cursor.close()
        conn.close()
        
        print(f"✅ Loaded {len(all_comments)} comments from database")
        return jsonify({'comments': all_comments})
        
    except Exception as e:
        print(f"⚠️ Database query failed: {e}")
        import traceback
        traceback.print_exc()
        # Fall back to in-memory comments if database query fails
        return jsonify({'comments': comments})


@app.route('/api/comments/clear', methods=['DELETE'])
def clear_comments():
    """Clear all comments (useful after load testing)"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Delete all jobs
        cursor.execute("DELETE FROM jobs")
        deleted_count = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n🗑️ Cleared {deleted_count} comments from database")
        
        return jsonify({
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Successfully cleared {deleted_count} comments'
        })
        
    except Exception as e:
        print(f"❌ Failed to clear comments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/submit-comment', methods=['POST'])
def submit_comment():
    """Submit new comment"""
    data = request.json
    
    comment = {
        'id': f'comment_{len(comments) + 1}',
        'author': data.get('author', 'Anonymous'),
        'text': data.get('text', ''),
        'type': data.get('type', 'text'),
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'moderation_result': None
    }
    
    comments.append(comment)
    
    print(f"\n✅ New comment submitted: {comment['id']}")
    print(f"   Author: {comment['author']}")
    print(f"   Text: {comment['text'][:50]}...")
    
    # Submit to VietCMS API for moderation
    config = get_config()
    if config['api_key'] != "YOUR_API_KEY_HERE":
        try:
            print(f"📤 Sending to VietCMS API for moderation...")
            api_base_url = (config.get('api_url') or VIETCMS_API_URL).rstrip('/')
            
            # Prepare request body
            comment_type = data.get('type', 'text')
            payload = {
                'comment_id': comment['id'],
                'text': comment['text'],
                'type': comment_type,
                'metadata': {
                    'author': comment['author'],
                    'source': 'demo-website',
                    'type': comment_type
                }
            }
            body = json.dumps(payload).encode('utf-8')
            
            # Calculate HMAC signature
            signature = hmac.new(
                config['hmac_secret'].encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            response = requests.post(
                f"{api_base_url}/submit",
                data=body,
                headers={
                    'X-API-Key': config['api_key'],
                    'X-Hub-Signature-256': f'sha256={signature}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code in [200, 202]:
                job_data = response.json()
                comment['job_id'] = job_data.get('data', {}).get('job_id')
                print(f"✅ Sent to VietCMS - Job ID: {comment['job_id']}")
            else:
                print(f"❌ VietCMS API error: {response.status_code} - {response.text}")
                comment['status'] = 'error'
                
        except Exception as e:
            print(f"❌ Failed to send to VietCMS: {e}")
            comment['status'] = 'error'
    else:
        print("⚠️  VietCMS API key not configured - skipping moderation")
    
    return jsonify({
        'success': True,
        'comment': comment
    })


@app.route('/webhooks/moderation', methods=['POST'])
def receive_webhook():
    """Receive moderation result from VietCMS"""
    
    # Verify signature (skip if HMAC_SECRET is not set)
    config = get_config()
    if config['hmac_secret'] != "YOUR_HMAC_SECRET_HERE":
        signature = request.headers.get('X-Hub-Signature-256')
        body = request.get_data()
        
        print(f"\n🔍 Webhook Signature Verification:")
        print(f"   Received Signature: {signature}")
        print(f"   HMAC Secret: {config['hmac_secret'][:20]}...")
        print(f"   Body length: {len(body)} bytes")
        
        if not verify_webhook_signature(body, signature):
            print("❌ Invalid webhook signature!")
            return jsonify({'error': 'Invalid signature'}), 403
        
        print("✅ Signature verified!")
    
    data = request.json
    
    print("\n" + "="*60)
    print("🔔 WEBHOOK RECEIVED FROM VIETCMS")
    print("="*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("="*60 + "\n")
    
    job_id = data.get('job_id')
    comment_id = data.get('comment_id')
    moderation_result = data.get('moderation_result')
    sentiment = data.get('sentiment')
    confidence = data.get('confidence')
    reasoning = data.get('reasoning')
    extracted_text = data.get('extracted_text')  # OCR from image
    transcribed_text = data.get('transcribed_text')  # From audio
    
    # Save result
    moderation_results[job_id] = data
    
    # Update comment status
    for comment in comments:
        if comment['id'] == comment_id:
            comment['status'] = 'moderated'
            comment['moderation_result'] = moderation_result
            comment['sentiment'] = sentiment
            comment['confidence'] = confidence
            comment['reasoning'] = reasoning
            comment['extracted_text'] = extracted_text  # Save OCR text
            comment['transcribed_text'] = transcribed_text  # Save audio transcript
            
            if moderation_result == 'reject':
                comment['visible'] = False
                print(f"❌ Comment {comment_id} REJECTED: {reasoning}")
            elif moderation_result == 'review':
                comment['visible'] = False
                comment['needs_review'] = True
                print(f"⚠️  Comment {comment_id} NEEDS REVIEW: {reasoning}")
            else:
                comment['visible'] = True
                print(f"✅ Comment {comment_id} ALLOWED")
            
            break
    
    return jsonify({'received': True, 'job_id': job_id}), 200


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get all moderation results"""
    return jsonify({
        'total': len(moderation_results),
        'results': list(moderation_results.values())
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'comments_count': len(comments),
        'results_count': len(moderation_results)
    })


@app.route('/api/config', methods=['GET'])
def get_api_config():
    """Get current API configuration"""
    config = get_config()
    is_configured = config['api_key'] != 'YOUR_API_KEY_HERE'

    config_payload = None
    if is_configured:
        config_payload = {
            'api_url': config['api_url'],
            'api_key': config['api_key'],
            'hmac_secret': config['hmac_secret'],
            'webhook_url': config['webhook_url'],
            'api_key_preview': mask_secret(config['api_key']),
            'hmac_secret_preview': mask_secret(config['hmac_secret'])
        }

    return jsonify({
        'configured': is_configured,
        'config': config_payload,
        'default_api_url': config['api_url']
    })


@app.route('/api/config', methods=['POST'])
def save_api_config():
    """Save API configuration"""
    data = request.json
    current_config = get_config()

    api_url = data.get('api_url', '').strip() or current_config.get('api_url') or VIETCMS_API_URL
    api_key = data.get('api_key', '').strip() or current_config.get('api_key')
    hmac_secret = data.get('hmac_secret', '').strip() or current_config.get('hmac_secret')
    webhook_url = data.get('webhook_url', '').strip()

    api_url = api_url.rstrip('/')

    if not api_url.lower().startswith('http'):
        return jsonify({
            'success': False,
            'error': 'API URL must be a valid HTTP/HTTPS'
        }), 400

    if not api_key or api_key == 'YOUR_API_KEY_HERE' or not hmac_secret or hmac_secret == 'YOUR_HMAC_SECRET_HERE':
        return jsonify({
            'success': False,
            'error': 'API Key and HMAC Secret cannot be empty'
        }), 400

    # Update runtime config
    runtime_config['api_url'] = api_url
    runtime_config['api_key'] = api_key
    runtime_config['hmac_secret'] = hmac_secret
    runtime_config['webhook_url'] = webhook_url
    
    print(f"\n✅ API Config updated:")
    print(f"   API URL: {api_url}")
    print(f"   API Key: {api_key[:20]}...")
    print(f"   HMAC Secret: {hmac_secret[:10]}...")
    print(f"   Webhook URL: {webhook_url or '(not set)'}")
    
    # Update webhook URL in VietCMS database
    if webhook_url and api_key:
        try:
            print(f"\n📤 Updating webhook URL in VietCMS API...")
            api_base_url = runtime_config['api_url'].rstrip('/')
            
            # Call VietCMS API to update webhook URL
            update_response = requests.put(
                f"{api_base_url}/update-webhook",
                json={'webhook_url': webhook_url},
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': api_key
                },
                timeout=10
            )
            
            if update_response.status_code == 200:
                update_data = update_response.json()
                print(f"✅ Webhook URL updated in VietCMS database!")
                print(f"   New URL: {webhook_url}")
            else:
                print(f"⚠️  Failed to update webhook URL in VietCMS: {update_response.status_code}")
                print(f"   Response: {update_response.text}")
        
        except Exception as e:
            print(f"⚠️  Failed to update webhook URL in VietCMS: {e}")
    
    return jsonify({
        'success': True,
        'message': 'Configuration saved successfully'
    })


@app.route('/api/config', methods=['DELETE'])
def clear_api_config():
    """Clear API configuration"""
    runtime_config['api_key'] = 'YOUR_API_KEY_HERE'
    runtime_config['hmac_secret'] = 'YOUR_HMAC_SECRET_HERE'
    runtime_config['webhook_url'] = ''
    runtime_config['api_url'] = VIETCMS_API_URL
    
    print("\n❌ API Config cleared")
    
    return jsonify({
        'success': True,
        'message': 'Configuration deleted'
    })


@app.route('/api/test-config', methods=['POST'])
def test_api_config():
    """Test API configuration by calling VietCMS health endpoint"""
    data = request.json

    config = get_config()

    api_url = (data.get('api_url', '').strip() or config['api_url'] or VIETCMS_API_URL).rstrip('/')
    api_key = data.get('api_key', '').strip() or config['api_key']
    hmac_secret = data.get('hmac_secret', '').strip() or config['hmac_secret']

    if (not api_key or api_key == 'YOUR_API_KEY_HERE' or
            not hmac_secret or hmac_secret == 'YOUR_HMAC_SECRET_HERE'):
        return jsonify({
            'success': False,
            'error': 'API Key and HMAC Secret cannot be empty'
        }), 400

    if not api_url.lower().startswith('http'):
        return jsonify({
            'success': False,
            'error': 'Invalid API URL'
        }), 400
    
    try:
        # Test submit with empty text to check credentials
        test_payload = {
            'text': 'test connection',
            'comment_id': 'test_' + str(int(datetime.now().timestamp()))
        }
        body = json.dumps(test_payload).encode('utf-8')
        
        signature = hmac.new(
            hmac_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        response = requests.post(
            f"{api_url}/submit",
            data=body,
            headers={
                'X-API-Key': api_key,
                'X-Hub-Signature-256': f'sha256={signature}',
                'Content-Type': 'application/json'
            },
            timeout=5
        )
        
        if response.status_code in [200, 202]:
            return jsonify({
                'success': True,
                'message': 'Connection successful!'
            })
        elif response.status_code == 401:
            return jsonify({
                'success': False,
                'error': 'Incorrect API Key or HMAC Secret'
            }), 401
        else:
            return jsonify({
                'success': False,
                'error': f'API returned error: {response.status_code}'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Timeout - could not connect to VietCMS API'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Connection error: {str(e)}'
        }), 500


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve built React frontend from dist directory."""
    if not os.path.exists(DIST_DIR):
        return jsonify({
            'success': False,
            'error': 'Frontend build not found. Run `npm run build` in demo-client-website.'
        }), 503
    file_path = os.path.join(DIST_DIR, path)
    if path and os.path.isfile(file_path):
        return send_from_directory(DIST_DIR, path)
    return send_from_directory(DIST_DIR, 'index.html')


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 DEMO CLIENT BACKEND SERVER")
    print("="*60)
    print("📍 Full stack: http://localhost:5000")
    print("📍 Webhook: http://localhost:5000/webhooks/moderation")
    print("\n💡 To get HTTPS for webhook:")
    print("   ngrok http 5000")
    print("   or cloudflared tunnel --url http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)

