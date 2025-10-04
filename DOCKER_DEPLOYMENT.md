# Tsunami Detection - Docker Deployment Guide

## 🐳 Docker Compose Deployment

Repository ini menyediakan beberapa konfigurasi Docker Compose untuk deployment yang fleksibel:

### 📁 File yang Tersedia

1. **`docker-compose.yml`** - Konfigurasi dasar untuk development
2. **`docker-compose.prod.yml`** - Konfigurasi lengkap untuk production
3. **`Dockerfile`** - Image definition untuk aplikasi Streamlit
4. **`nginx/nginx.conf`** - Konfigurasi Nginx reverse proxy
5. **`db_init.sql`** - Database initialization script

### 🚀 Quick Start (Development)

```bash
# Clone repository
git clone <repository-url>
cd tsunami_detection

# Copy dan edit environment variables
cp .env.example .env
# Edit .env sesuai konfigurasi Anda

# Build dan jalankan
docker-compose up -d

# Akses aplikasi
open http://localhost:8501
```

### 🏭 Production Deployment

```bash
# Gunakan konfigurasi production
docker-compose -f docker-compose.prod.yml up -d

# Atau dengan build ulang
docker-compose -f docker-compose.prod.yml up --build -d
```

### 📊 Services yang Tersedia

#### Development (`docker-compose.yml`)
- **tsunami-app**: Aplikasi Streamlit utama (port 8501)
- **Network mode**: `host` untuk akses RTSP langsung

#### Production (`docker-compose.prod.yml`)
- **tsunami-app**: Aplikasi Streamlit utama (port 8501)
- **postgres**: Database PostgreSQL (port 5432)
- **redis**: Cache Redis (port 6379)
- **nginx**: Reverse proxy (port 80/443)
- **prometheus**: Monitoring (port 9090)
- **grafana**: Dashboard monitoring (port 3000)

### 🔧 Konfigurasi Environment

Edit file `.env` dengan konfigurasi yang sesuai:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+62xxx

# RTSP Configuration
RTSP_URL=rtsp://user:pass@ip:port/stream

# Database (untuk production)
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_redis_password

# Grafana (untuk production)
GRAFANA_USER=admin
GRAFANA_PASSWORD=your_grafana_password
```

### 🎥 RTSP Network Configuration

Untuk akses kamera RTSP:

#### Option 1: Host Network (Recommended untuk development)
```yaml
network_mode: "host"
```

#### Option 2: Bridge Network dengan Port Mapping
```yaml
networks:
  - tsunami-network
ports:
  - "8554:8554"  # RTSP port
```

### 💾 Data Persistence

Volume mounts untuk data persistence:

```yaml
volumes:
  - ./data:/app/data              # Data aplikasi
  - ./logs:/app/logs              # Log files
  - ./deteksi_ombak.csv:/app/deteksi_ombak.csv  # CSV log
  - postgres_data:/var/lib/postgresql/data      # Database
```

### 🔍 Monitoring dan Logging

#### Access Logs
```bash
# Application logs
docker-compose logs -f tsunami-app

# Database logs
docker-compose logs -f postgres

# Nginx logs
docker-compose logs -f nginx
```

#### Monitoring URLs (Production)
- **Aplikasi**: http://localhost
- **Grafana**: http://localhost:3000 (admin/admin_secure_2024)
- **Prometheus**: http://localhost:9090

### 🛠 Development Commands

```bash
# Build ulang image
docker-compose build --no-cache

# Restart service tertentu
docker-compose restart tsunami-app

# Update single service
docker-compose up -d --no-deps tsunami-app

# Lihat resource usage
docker stats

# Access container shell
docker-compose exec tsunami-app bash
```

### 🔒 Security Considerations

#### Production Security
1. **Change default passwords** di `.env`
2. **Enable HTTPS** dengan SSL certificates
3. **Configure firewall** untuk membatasi akses
4. **Regular updates** untuk base images
5. **Monitor logs** untuk security events

#### SSL Configuration
```bash
# Generate self-signed certificate (untuk testing)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem

# Uncomment HTTPS section di nginx.conf
```

### 🚨 Troubleshooting

#### Common Issues

1. **RTSP Connection Failed**
   ```bash
   # Check network connectivity
   docker-compose exec tsunami-app ping camera_ip
   
   # Test RTSP URL
   ffmpeg -i "rtsp://user:pass@ip:port/stream" -f null -
   ```

2. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   docker-compose exec postgres pg_isready -U tsunami_user
   
   # Reset database
   docker-compose down -v
   docker-compose up -d postgres
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port
   netstat -tulpn | grep :8501
   
   # Change port in docker-compose.yml
   ports:
     - "8502:8501"  # Use different external port
   ```

#### Performance Tuning

1. **Memory Limits**
   ```yaml
   deploy:
     resources:
       limits:
         memory: 2G
       reservations:
         memory: 1G
   ```

2. **CPU Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
   ```

### 🔄 Updates dan Maintenance

```bash
# Update images
docker-compose pull
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U tsunami_user tsunami_db > backup.sql

# Cleanup unused resources
docker system prune -a
```

### 📋 Health Checks

Built-in health checks tersedia untuk:
- Streamlit app: `/_stcore/health`
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`
- Nginx: `/health`

### 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database passwords changed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Log rotation configured
- [ ] Resource limits set