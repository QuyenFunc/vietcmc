"""Example usage of VietCMS Moderation SDK"""
import sys
sys.path.insert(0, '../client-sdk/python')

from vietcms_moderation import ModerationClient, WebhookHandler
from flask import Flask, request
import time

# Initialize client
client = ModerationClient(
    api_key="your-api-key-here",
    hmac_secret="your-hmac-secret-here",
    base_url="http://localhost/api/v1"
)

# Example 1: Submit a single comment
print("Example 1: Submit single comment")
print("=" * 50)

result = client.submit_job(
    text="Sản phẩm rất tốt, tôi rất hài lòng!",
    comment_id="comment_001",
    metadata={
        "user_id": "user_123",
        "post_id": "post_456"
    }
)

print(f"Job ID: {result['job_id']}")
print(f"Status: {result['status']}")

# Wait and check status
print("\nWaiting for processing...")
time.sleep(5)

status = client.get_job_status(result['job_id'])
print(f"Current status: {status['status']}")

if status['status'] == 'completed':
    print(f"Sentiment: {status['result']['sentiment']}")
    print(f"Moderation: {status['result']['moderation_result']}")
    print(f"Confidence: {status['result']['confidence']}")


# Example 2: Webhook handler with Flask
print("\n\nExample 2: Webhook Handler")
print("=" * 50)

app = Flask(__name__)
webhook_handler = WebhookHandler(hmac_secret="your-hmac-secret-here")

@app.route('/webhooks/moderation', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    
    if not webhook_handler.verify_signature(request.data, signature):
        return {'error': 'Invalid signature'}, 403
    
    # Process webhook
    payload = request.json
    
    print(f"Received webhook for job: {payload['job_id']}")
    print(f"Result: {payload['moderation_result']}")
    print(f"Sentiment: {payload['sentiment']}")
    
    # Handle in your application
    # update_comment_status(payload['comment_id'], payload['moderation_result'])
    
    return {'received': True}, 200

if __name__ == "__main__":
    print("Webhook server ready on http://localhost:5000/webhooks/moderation")
    # app.run(host='0.0.0.0', port=5000)

