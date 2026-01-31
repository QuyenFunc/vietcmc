
```bash
docker-compose up -d
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
