# Quick Start Guide - VietCMS Moderation

## 🚀 Bắt Đầu Nhanh (5 phút)

### Bước 1: Khởi động hệ thống
```bash
docker-compose up -d
```

Đợi tất cả services khởi động (khoảng 30 giây):
```bash
docker-compose ps
```

---

### Bước 2: Đăng ký tài khoản

1. Truy cập: **http://localhost/client-login**
2. Click **"Đăng ký"**
3. Điền thông tin:
   - Organization Name: `Demo Shop`
   - Email: `demo@example.com`
   - Password: `demo123456`
   - Webhook URL: `http://demo-website:5001/webhooks/moderation`
4. **Lưu lại credentials:**
   ```
   App ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   API Key: sk_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   HMAC Secret: whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

### Bước 3: Cấu hình Demo Website

Cập nhật file `.env` hoặc chạy:
```bash
# Windows PowerShell
docker-compose stop demo-website
$env:DEMO_API_KEY="sk_live_YOUR_API_KEY"
$env:DEMO_HMAC_SECRET="whsec_YOUR_HMAC_SECRET"
docker-compose up -d demo-website
```

```bash
# Linux/Mac
docker-compose stop demo-website
export DEMO_API_KEY="sk_live_YOUR_API_KEY"
export DEMO_HMAC_SECRET="whsec_YOUR_HMAC_SECRET"
docker-compose up -d demo-website
```

---

### Bước 4: Test thử

#### **Option 1: Qua Demo Website**
1. Truy cập: **http://localhost:5000**
2. Nhập API credentials (nếu chưa config env vars)
3. Submit comment test
4. Xem kết quả real-time

#### **Option 2: Qua Python Script**
```bash
# Sửa file test-submit.py với API Key và HMAC Secret của bạn
python test-submit.py
```

---

### Bước 5: Kiểm tra kết quả

#### **Xem logs:**
```bash
# API logs
docker logs vietcms-api --tail 50 -f

# Worker logs (xử lý AI)
docker logs vietcms-moderation-moderation-worker-1 --tail 50 -f

# Webhook logs
docker logs vietcms-dispatcher --tail 50 -f

# Demo backend logs
docker logs vietcms-demo-website --tail 50 -f
```

#### **Kiểm tra webhook delivery:**
```bash
docker exec vietcms-postgres psql -U vietcms -d vietcms_moderation -c \
  "SELECT job_id, response_status_code, status FROM webhook_logs ORDER BY id DESC LIMIT 5;"
```

**Kết quả mong đợi:**
```
response_status_code | status
----------------------+---------
                 200 | success
```

---

## 🎯 Luồng Hoạt Động Nhanh

```
1. Client submit content
   ↓
2. API validate → Queue vào RabbitMQ
   ↓
3. Worker xử lý AI (sentiment + toxic detection)
   ↓
4. Kết quả → Queue job_completed
   ↓
5. Webhook Dispatcher gửi kết quả về client
   ↓
6. Client nhận webhook → Xử lý (allow/review/reject)
```

---

## ✅ Checklist

- [ ] Services đang chạy (`docker-compose ps`)
- [ ] Đã đăng ký tài khoản client
- [ ] Đã lưu API Key và HMAC Secret
- [ ] Webhook URL đã cấu hình
- [ ] Demo website đã có credentials
- [ ] Test submit thành công
- [ ] Webhook nhận được kết quả (HTTP 200)

---

## 🔧 Troubleshooting Nhanh

### ❌ Webhook trả về 403
```bash
# Kiểm tra HMAC secret
docker exec vietcms-demo-website printenv | grep HMAC

# So sánh với database
docker exec vietcms-postgres psql -U vietcms -d vietcms_moderation -c \
  "SELECT id, organization_name, hmac_secret FROM clients;"
```
**Fix:** HMAC secret phải khớp nhau!

---

### ❌ Webhook trả về 404
```bash
# Kiểm tra webhook URL
docker exec vietcms-postgres psql -U vietcms -d vietcms_moderation -c \
  "SELECT id, organization_name, webhook_url FROM clients;"
```
**Fix:** URL phải là `http://demo-website:5001/webhooks/moderation`

---

### ❌ Job bị stuck ở "pending"
```bash
# Kiểm tra worker
docker logs vietcms-moderation-moderation-worker-1 --tail 20

# Kiểm tra RabbitMQ
docker logs vietcms-rabbitmq --tail 20
```
**Fix:** Restart worker: `docker-compose restart moderation-worker`

---

### ❌ API trả về 401 Unauthorized
**Fix:** Kiểm tra API Key có đúng không, có thêm prefix `sk_live_` không

---

## 📱 Demo Scenarios

### Test Case 1: Nội dung tích cực
```json
{
  "text": "Sản phẩm rất tuyệt vời, tôi rất hài lòng!"
}
```
**Kết quả mong đợi:**
- Sentiment: `positive`
- Moderation: `allow`

---

### Test Case 2: Nội dung tiêu cực nhẹ
```json
{
  "text": "Sản phẩm không được tốt lắm, hơi thất vọng"
}
```
**Kết quả mong đợi:**
- Sentiment: `negative`
- Moderation: `allow` hoặc `review`

---

### Test Case 3: Nội dung toxic
```json
{
  "text": "Sản phẩm như shit, nhân viên đần độn"
}
```
**Kết quả mong đợi:**
- Sentiment: `negative`
- Moderation: `reject`
- Reasoning: Chứa từ ngữ không phù hợp

---

## 🌐 URLs Quan Trọng

| Service | URL | Note |
|---------|-----|------|
| Admin UI | http://localhost | Giao diện quản trị |
| Client Login | http://localhost/client-login | Đăng ký/đăng nhập client |
| API | http://localhost/api/v1 | REST API endpoint |
| Demo Website | http://localhost:5000 | Website demo |
| Demo Backend | http://localhost:5001 | API backend của demo |
| RabbitMQ Admin | http://localhost:15672 | Queue management |
| Traefik Dashboard | http://localhost:8080 | Reverse proxy |

---

## 📞 Cần Trợ Giúp?

1. Xem logs chi tiết: `docker-compose logs -f [service-name]`
2. Kiểm tra database: `docker exec -it vietcms-postgres psql -U vietcms -d vietcms_moderation`
3. Đọc docs: `WORKFLOW.md` và `CONFIG-DEMO.md`

---

**Happy Moderating! 🎉**



