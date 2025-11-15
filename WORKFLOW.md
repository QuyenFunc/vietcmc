# Luồng Hoạt Động - VietCMS Moderation System

## 📋 Tổng Quan

VietCMS là hệ thống kiểm duyệt nội dung tự động sử dụng AI để phân tích sentiment và phát hiện nội dung độc hại trong tiếng Việt.

## 🔄 Luồng Hoạt Động Chi Tiết

### **Bước 1: Đăng Ký Tài Khoản Client**

```
Client → Admin UI (http://localhost/client-login)
         ↓
    Đăng ký tài khoản mới
         ↓
    Nhận được credentials:
    - App ID
    - API Key (YOUR_API_KEY_HERE)
    - HMAC Secret (YOUR_HMAC_SECRET_HERE)
    - Webhook URL (cần cập nhật sau)
```

**Lưu ý:** Credentials này cần được lưu trữ an toàn!

---

### **Bước 2: Cấu Hình Webhook URL**

#### **Option 1: Internal Docker Network (Dùng cho Demo)**
```
Webhook URL: http://demo-website:5001/webhooks/moderation
```
- ✅ Dùng cho môi trường development/demo
- ✅ Không cần expose ra internet
- ✅ Đơn giản, nhanh chóng

#### **Option 2: External HTTPS (Dùng cho Production)**
```bash
# Sử dụng Cloudflare Tunnel
cloudflared tunnel --url http://localhost:5001

# Hoặc ngrok
ngrok http 5001
```

Sau đó cập nhật webhook URL:
```
Webhook URL: https://your-tunnel-url.com/webhooks/moderation
```

**Cập nhật trong Admin Dashboard:**
```
http://localhost/client-login → Dashboard → Update Webhook URL
```

---

### **Bước 3: Submit Content để Kiểm Duyệt**

```python
import requests
import json
import hmac
import hashlib

API_KEY = "YOUR_API_KEY_HERE"
HMAC_SECRET = "YOUR_HMAC_SECRET_HERE"
API_URL = "http://localhost/api/v1/submit"

# Payload
data = {
    "comment_id": "comment_123",  # ID từ hệ thống của bạn
    "text": "Nội dung cần kiểm duyệt",
    "metadata": {
        "author": "User Name",
        "source": "facebook"
    }
}

# Tính HMAC signature
body = json.dumps(data).encode('utf-8')
signature = hmac.new(
    HMAC_SECRET.encode('utf-8'),
    body,
    hashlib.sha256
).hexdigest()

# Gửi request
response = requests.post(
    API_URL,
    data=body,
    headers={
        "X-API-Key": API_KEY,
        "X-Hub-Signature-256": f"sha256={signature}",
        "Content-Type": "application/json"
    }
)

result = response.json()
job_id = result['data']['job_id']
print(f"Job submitted: {job_id}")
```

**Response:**
```json
{
  "success": true,
  "data": {
    "job_id": "uuid-here",
    "status": "pending",
    "comment_id": "comment_123"
  }
}
```

---

### **Bước 4: Xử Lý Nội Bộ**

```
API nhận request → Validate HMAC + API Key
                 ↓
          Lưu vào Database (jobs table)
                 ↓
          Gửi message vào RabbitMQ (job_queue)
                 ↓
          Trả response ngay cho client (202 Accepted)
```

#### **Worker xử lý:**
```
Worker lắng nghe RabbitMQ queue
    ↓
Nhận job mới
    ↓
Tiền xử lý text (normalize, tokenize)
    ↓
Chạy AI model (PhoBERT):
    - Phân tích sentiment (positive/negative/neutral)
    - Kiểm tra toxic words
    - Tính confidence score
    ↓
Quyết định moderation:
    - "allow" (cho phép)
    - "review" (cần xem xét)
    - "reject" (từ chối)
    ↓
Lưu kết quả vào database
    ↓
Gửi message vào RabbitMQ (job_completed queue)
```

---

### **Bước 5: Gửi Webhook về Client**

```
Webhook Dispatcher lắng nghe job_completed queue
    ↓
Nhận job hoàn thành
    ↓
Lấy webhook_url + hmac_secret từ database
    ↓
Tạo webhook payload:
{
  "job_id": "uuid",
  "comment_id": "comment_123",
  "text": "Nội dung đã kiểm duyệt",
  "sentiment": "positive/negative/neutral",
  "moderation_result": "allow/review/reject",
  "confidence": 0.95,
  "reasoning": "Lý do kiểm duyệt",
  "timestamp": "2025-10-30T09:20:04Z"
}
    ↓
Tính HMAC signature cho payload
    ↓
POST đến webhook_url với header:
    - Content-Type: application/json
    - X-Hub-Signature-256: sha256=signature
    ↓
Retry logic (nếu thất bại):
    - Attempt 1: Ngay lập tức
    - Attempt 2: Sau 5 giây
    - Attempt 3: Sau 10 giây
    ↓
Log kết quả vào webhook_logs table
```

---

### **Bước 6: Client Nhận Webhook**

```python
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
HMAC_SECRET = "whsec_..."

def verify_signature(body, signature):
    if not signature or not signature.startswith('sha256='):
        return False
    
    received_sig = signature[7:]
    expected_sig = hmac.new(
        HMAC_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_sig, expected_sig)

@app.route('/webhooks/moderation', methods=['POST'])
def webhook():
    # 1. Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    body = request.get_data()
    
    if not verify_signature(body, signature):
        return jsonify({'error': 'Invalid signature'}), 403
    
    # 2. Parse payload
    data = request.json
    
    # 3. Xử lý kết quả
    job_id = data['job_id']
    comment_id = data['comment_id']
    result = data['moderation_result']
    
    if result == 'allow':
        # Cho phép hiển thị comment
        approve_comment(comment_id)
    elif result == 'review':
        # Đưa vào hàng đợi review thủ công
        queue_for_review(comment_id, data['reasoning'])
    elif result == 'reject':
        # Từ chối/ẩn comment
        reject_comment(comment_id, data['reasoning'])
    
    # 4. Trả về 200 OK
    return jsonify({'received': True}), 200
```

---

## 📊 Sơ Đồ Tổng Quan

```
┌─────────────┐
│   Client    │
│  (Website)  │
└──────┬──────┘
       │ 1. POST /api/v1/submit
       │    + X-API-Key
       │    + X-Hub-Signature-256
       ▼
┌─────────────────┐
│ Moderation API  │
│   (FastAPI)     │
└────────┬────────┘
         │ 2. Validate & Queue
         ▼
┌─────────────────┐
│   RabbitMQ      │
│  (job_queue)    │
└────────┬────────┘
         │ 3. Consume
         ▼
┌─────────────────┐
│ Worker (AI/NLP) │
│   (PhoBERT)     │
└────────┬────────┘
         │ 4. Process & Result
         ▼
┌─────────────────┐
│   RabbitMQ      │
│(job_completed)  │
└────────┬────────┘
         │ 5. Consume
         ▼
┌─────────────────┐
│   Webhook       │
│  Dispatcher     │
└────────┬────────┘
         │ 6. POST webhook
         │    + X-Hub-Signature-256
         ▼
┌─────────────────┐
│  Client Webhook │
│   Endpoint      │
└─────────────────┘
```

---

## ✅ Checklist Triển Khai Chuẩn

### **1. Development/Testing**

- [x] Đăng ký tài khoản client
- [x] Lưu API Key và HMAC Secret
- [x] Cấu hình webhook URL (internal hoặc tunnel)
- [x] Implement webhook endpoint
- [x] Verify HMAC signature trong webhook
- [x] Test submit content
- [x] Test nhận webhook
- [x] Kiểm tra logs (API, Worker, Dispatcher)

### **2. Production**

- [ ] Sử dụng HTTPS cho webhook URL
- [ ] Store credentials trong environment variables/secrets manager
- [ ] Implement retry logic khi gọi API
- [ ] Implement idempotency cho webhook (check duplicate job_id)
- [ ] Monitor webhook logs
- [ ] Setup alerting cho failed webhooks
- [ ] Rate limiting awareness (1000 requests/hour default)
- [ ] Backup/fallback mechanism nếu API down

---

## 🔒 Security Best Practices

1. **HMAC Signature Verification**
   - LUÔN verify signature trong webhook
   - Dùng `hmac.compare_digest()` để tránh timing attacks

2. **Credentials Storage**
   ```bash
   # ĐÚNG: Environment variables
   export VIETCMS_API_KEY="sk_live_..."
   export VIETCMS_HMAC_SECRET="whsec_..."
   
   # SAI: Hard-code trong code
   api_key = "sk_live_..."  # ❌ KHÔNG BAO GIỜ LÀM
   ```

3. **HTTPS Only**
   - Production PHẢI dùng HTTPS cho webhook
   - Validate SSL certificates

4. **Idempotency**
   ```python
   # Lưu job_id đã xử lý để tránh duplicate
   processed_jobs = set()
   
   @app.route('/webhooks/moderation', methods=['POST'])
   def webhook():
       data = request.json
       job_id = data['job_id']
       
       if job_id in processed_jobs:
           return jsonify({'received': True}), 200
       
       # Process...
       processed_jobs.add(job_id)
   ```

---

## 🛠️ Monitoring & Debugging

### **Check API Logs**
```bash
docker logs vietcms-api --tail 100 -f
```

### **Check Worker Logs**
```bash
docker logs vietcms-moderation-moderation-worker-1 --tail 100 -f
```

### **Check Webhook Dispatcher Logs**
```bash
docker logs vietcms-dispatcher --tail 100 -f
```

### **Check Webhook Delivery Status**
```sql
SELECT 
    job_id,
    webhook_url,
    response_status_code,
    status,
    attempt_number,
    error_message
FROM webhook_logs
ORDER BY id DESC
LIMIT 20;
```

### **Check Failed Jobs**
```sql
SELECT j.id, j.status, j.error_message, c.organization_name
FROM jobs j
JOIN clients c ON j.client_id = c.id
WHERE j.status = 'failed'
ORDER BY j.created_at DESC;
```

---

## 🚀 Quick Start

```bash
# 1. Start services
docker-compose up -d

# 2. Register client account
# Visit: http://localhost/client-login

# 3. Update webhook URL in dashboard
# URL: http://demo-website:5001/webhooks/moderation

# 4. Test submit
python test-submit.py

# 5. Check logs
docker logs vietcms-dispatcher --tail 20
```

---

## 📞 Troubleshooting

### **Webhook trả về 403 (Invalid signature)**
- Kiểm tra HMAC_SECRET có đúng không
- Verify signature trước khi parse JSON
- Check encoding (UTF-8)

### **Webhook trả về 404**
- Kiểm tra webhook URL có đúng không
- Endpoint có tồn tại không
- Tunnel có đang chạy không (nếu dùng ngrok/cloudflare)

### **Webhook timeout**
- Endpoint xử lý quá chậm (> 10s)
- Network issue
- Server không phản hồi

### **Job stuck ở "pending"**
- Worker không chạy: `docker logs vietcms-moderation-moderation-worker-1`
- RabbitMQ issue: `docker logs vietcms-rabbitmq`
- Check queue: http://localhost:15672 (admin/rabbitmq_password_456)

---

## 📚 Tài Liệu Liên Quan

- `CONFIG-DEMO.md` - Hướng dẫn cấu hình demo
- `RUN.md` - Hướng dẫn chạy hệ thống
- `API Documentation` - Chi tiết API endpoints
- `Client SDKs` - SDK cho Node.js và Python

---

**Cập nhật:** 2025-10-30










