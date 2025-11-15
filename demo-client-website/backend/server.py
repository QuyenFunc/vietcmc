"""
Backend Flask Server - API cho Demo Client Website
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import hmac
import hashlib
from datetime import datetime
import json
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'dist'))

app = Flask(
    __name__,
    static_folder=DIST_DIR,
    static_url_path=''
)
CORS(app)

# Storage (trong production dùng database)
comments = []
moderation_results = {}

# VietCMS Configuration
VIETCMS_API_URL = os.getenv('VIETCMS_API_URL', 'http://localhost:8000/api/v1')
VIETCMS_API_KEY = os.getenv('VIETCMS_API_KEY', 'YOUR_API_KEY_HERE')
HMAC_SECRET = os.getenv('HMAC_SECRET', 'YOUR_HMAC_SECRET_HERE')

# Runtime config (có thể override bằng API)
runtime_config = {
    'api_url': VIETCMS_API_URL,
    'api_key': VIETCMS_API_KEY,
    'hmac_secret': HMAC_SECRET,
    'webhook_url': ''
}

def get_config():
    """Get current config (runtime hoặc env)"""
    return {
        'api_url': runtime_config.get('api_url', VIETCMS_API_URL),
        'api_key': runtime_config.get('api_key', VIETCMS_API_KEY),
        'hmac_secret': runtime_config.get('hmac_secret', HMAC_SECRET),
        'webhook_url': runtime_config.get('webhook_url', '')
    }


def verify_webhook_signature(body, signature):
    """Verify HMAC signature từ VietCMS"""
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
    """Get all comments"""
    return jsonify({'comments': comments})


@app.route('/api/comments/clear', methods=['DELETE'])
def clear_comments():
    """Clear all comments (useful after load testing)"""
    global comments, moderation_results
    
    count = len(comments)
    comments = []
    moderation_results = {}
    
    print(f"\n🗑️ Cleared {count} comments from demo website")
    
    return jsonify({
        'success': True,
        'deleted_count': count,
        'message': f'Successfully cleared {count} comments'
    })


@app.route('/api/submit-comment', methods=['POST'])
def submit_comment():
    """Submit new comment"""
    data = request.json
    
    comment = {
        'id': f'comment_{len(comments) + 1}',
        'author': data.get('author', 'Anonymous'),
        'text': data.get('text', ''),
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
            payload = {
                'comment_id': comment['id'],
                'text': comment['text'],
                'metadata': {
                    'author': comment['author'],
                    'source': 'demo-website'
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
    
    # Verify signature (skip nếu chưa set HMAC_SECRET)
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
            'hmac_secret': config['hmac_secret'][:10] + '...',
            'webhook_url': config['webhook_url']
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
    
    api_url = data.get('api_url', '').strip() or VIETCMS_API_URL
    api_key = data.get('api_key', '').strip()
    hmac_secret = data.get('hmac_secret', '').strip()
    webhook_url = data.get('webhook_url', '').strip()
    
    api_url = api_url.rstrip('/')
    
    if not api_url.lower().startswith('http'):
        return jsonify({
            'success': False,
            'error': 'API URL phải là HTTP/HTTPS hợp lệ'
        }), 400
    
    if not api_key or not hmac_secret:
        return jsonify({
            'success': False,
            'error': 'API Key và HMAC Secret không được để trống'
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
        'message': 'Cấu hình đã được lưu thành công'
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
        'message': 'Đã xóa cấu hình'
    })


@app.route('/api/test-config', methods=['POST'])
def test_api_config():
    """Test API configuration by calling VietCMS health endpoint"""
    data = request.json
    
    api_url = data.get('api_url', '').strip()
    api_key = data.get('api_key', '').strip()
    hmac_secret = data.get('hmac_secret', '').strip()
    
    if not api_key or not hmac_secret:
        return jsonify({
            'success': False,
            'error': 'API Key và HMAC Secret không được để trống'
        }), 400
    
    config = get_config()
    api_url = (api_url or config['api_url'] or VIETCMS_API_URL).rstrip('/')
    
    if not api_url.lower().startswith('http'):
        return jsonify({
            'success': False,
            'error': 'API URL không hợp lệ'
        }), 400
    
    try:
        # Test submit với text rỗng để kiểm tra credentials
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
                'message': 'Kết nối thành công!'
            })
        elif response.status_code == 401:
            return jsonify({
                'success': False,
                'error': 'API Key hoặc HMAC Secret không đúng'
            }), 401
        else:
            return jsonify({
                'success': False,
                'error': f'API trả về lỗi: {response.status_code}'
            }), 400
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Timeout - không thể kết nối đến VietCMS API'
        }), 408
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Lỗi kết nối: {str(e)}'
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
    print("\n💡 Để có HTTPS cho webhook:")
    print("   ngrok http 5000")
    print("   hoặc cloudflared tunnel --url http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

