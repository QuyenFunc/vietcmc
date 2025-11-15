# Cải Thiện Performance và AI Model

## 📝 Ngày: 3/11/2025

### 🎯 Mục tiêu đã hoàn thành:

## 1. Tăng Performance lên 1000 jobs/phút

**Trước:**
- 16.53 jobs/phút (quá thấp)
- 1 API instance, 1 worker instance
- WORKER_CONCURRENCY = 2

**Sau:**
- **Target: ≥1000 jobs/phút** (16.67 jobs/giây)
- **3 API instances** với 4 workers mỗi instance = 12 API processes
- **5 Worker instances** với concurrency 12 = 60 parallel jobs
- Database pool: 30 base + 50 overflow = 80 connections
- Redis cache để giảm tải database
- Rate limiting: 100 req/phút per IP

**Tính toán:**
```
60 workers song song × (60 giây / 3 giây/job) = 1200 jobs/phút ✅
```

## 2. Cải Thiện AI Model - Giảm False Positives

**Vấn đề:** 
- Lọc cả feedback tiêu cực bình thường của khách hàng
- "Giao hàng sai màu, không đổi trả" → ⚠️ Cần xem xét (SAI!)
- "Cấu hình mạnh mẽ, chơi game mượt" → ⚠️ Cần xem xét (SAI!)

**Nguyên nhân:**
- `CONFIDENCE_THRESHOLD = 0.5` quá thấp
- Không phân biệt giữa feedback tiêu cực hợp lệ vs toxic content

**Giải pháp:**
1. ✅ Tăng `CONFIDENCE_THRESHOLD` lên **0.7** (chỉ lọc khi chắc chắn)
2. ✅ Thêm logic lọc thông minh:
   - **Chỉ block:** toxic, hate, harassment, threat, PII, sexual
   - **Cho phép:** Feedback tiêu cực, complaint, đánh giá thấp (ý kiến khách hàng hợp lệ)
3. ✅ Profanity chỉ block nếu confidence ≥ 80%

**Code Logic:**
```python
# Chỉ lọc các label thực sự có hại
harmful_labels = {'toxicity', 'hate', 'harassment', 'threat', 'pii', 'sexual'}

# Cho phép feedback tiêu cực bình thường
if not triggered_harmful:
    return allowed với message "Đánh giá tiêu cực nhưng hợp lệ"
```

## 3. Infrastructure Improvements

### Redis Cache
- Cache kết quả jobs đã hoàn thành (TTL: 1 giờ)
- Giảm tải database khi client check status nhiều lần

### Monitoring
- **Prometheus**: Thu thập metrics
- **Grafana**: Visualize dashboard
- Ports:
  - Prometheus: 9090
  - Grafana: 3001 (default password: admin123)

### Docker Scaling
```yaml
moderation-api:
  replicas: 3
  resources:
    limits: 1 CPU, 1GB RAM
    
moderation-worker:
  replicas: 5
  resources:
    limits: 2 CPU, 4GB RAM
```

## 4. Cấu hình mới trong .env

```bash
# Performance
WORKER_CONCURRENCY=12
CONFIDENCE_THRESHOLD=0.7

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
GRAFANA_ADMIN_PASSWORD=admin123
```

## 🚀 Cách Apply Changes

### Bước 1: Cập nhật .env
```bash
cp env-example.txt .env
# Chỉnh sửa các giá trị cần thiết
```

### Bước 2: Restart Workers để áp dụng CONFIDENCE_THRESHOLD mới
```bash
docker-compose restart moderation-worker
```

### Bước 3: Test với Load Testing
- Truy cập: http://localhost:5000
- Click vào **Load Testing Panel**
- Chọn "1000 requests" và nhấn "Bắt đầu Load Test"

### Bước 4: Kiểm tra Metrics
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin123)
- RabbitMQ: http://localhost:15672 (admin/password từ .env)

## 📊 Kết quả mong đợi

| Metric | Trước | Sau |
|--------|-------|-----|
| Jobs/phút | 16.53 | ≥1000 |
| False Positives | Cao | Thấp |
| Latency | N/A | <2s/job |
| Success Rate | 99.5% | ≥99.5% |

## ⚠️ Lưu ý

1. **Model chưa train:** Hiện tại dùng base PhoBERT + rule-based. Để tốt hơn, cần train model với data thực tế.

2. **Resource Requirements:** 
   - Tối thiểu: 4 CPU cores, 8GB RAM
   - Khuyến nghị: 8 CPU cores, 16GB RAM

3. **Production Deployment:**
   - Cấu hình HTTPS với Traefik
   - Setup proper logging & alerting
   - Backup database định kỳ
   - Monitor resource usage

## 🎯 Tiếp theo

- [ ] Thu thập data thực tế để retrain model
- [ ] Setup alerting khi performance giảm
- [ ] A/B testing với các threshold khác nhau
- [ ] Tối ưu model size để inference nhanh hơn

