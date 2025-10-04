# Docker Compose - Quick Commands

## 🚀 Development (Simple)

```bash
# Start aplikasi (development mode)
docker-compose up -d

# Stop aplikasi
docker-compose down

# Rebuild dan start
docker-compose up --build -d

# Lihat logs
docker-compose logs -f tsunami-app
```

**Akses**: http://localhost:8501

---

## 🏭 Production (Full Stack)

```bash
# Start full production stack
docker-compose -f docker-compose.prod.yml up -d

# Stop production stack
docker-compose -f docker-compose.prod.yml down

# Update dan restart
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

**Access Points**:
- **App**: http://localhost (via Nginx)
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

---

## 🔧 Maintenance Commands

```bash
# Lihat status semua container
docker-compose ps

# Restart specific service
docker-compose restart tsunami-app

# Update single service
docker-compose up -d --no-deps tsunami-app

# Backup database
docker-compose exec postgres pg_dump -U tsunami_user tsunami_db > backup_$(date +%Y%m%d).sql

# Cleanup
docker system prune -f
```

---

## 🚨 Troubleshooting

```bash
# Check container logs
docker-compose logs tsunami-app

# Access container shell
docker-compose exec tsunami-app bash

# Test RTSP connection
docker-compose exec tsunami-app ffmpeg -i "$RTSP_URL" -f null -

# Reset everything
docker-compose down -v
docker-compose up -d
```

---

## ⚙️ Configuration Files

- **Development**: `docker-compose.yml`
- **Production**: `docker-compose.prod.yml`
- **Environment**: `.env`
- **Nginx**: `nginx/nginx.conf`
- **Database**: `db_init.sql`