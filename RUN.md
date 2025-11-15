# Chạy dự án

## 🚀 Khởi động hệ thống

```bash
docker-compose up -d
```

## 👤 Tạo test client

```bash
python scripts/create-test-client.py
```

## 🌐 Expose ra internet (tùy chọn)

**Ngrok (cho Admin UI):**
```bash
    ngrok http 80 --config ngrok.yml
```

**Cloudflared (cho Demo Website):**
```bash
cloudflared tunnel --url http://localhost:5000
```

## 🔗 Truy cập

### Ứng dụng chính
- **Admin UI**: http://localhost
- **Demo Client**: http://localhost:5000
- **API**: http://localhost/api

### Monitoring & Management
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin123)
- **RabbitMQ Management**: http://localhost:15672 (admin/password)
- **Traefik Dashboard**: http://localhost:8080

## 📊 Performance Specs

- **Throughput**: ≥1000 jobs/phút
- **Latency**: <2s per job
- **Scaling**: 3 API replicas + 5 Worker replicas
- **Concurrency**: 60 parallel jobs

## ⚙️ Cấu hình nâng cao

Chỉnh sửa file `.env` để tùy chỉnh:
- `WORKER_CONCURRENCY=12` - Số jobs xử lý đồng thời mỗi worker
- `CONFIDENCE_THRESHOLD=0.7` - Ngưỡng tin cậy AI (càng cao = ít false positive)

