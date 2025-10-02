# 🌊 Tsunami Alert Web Dashboard

Dashboard web profesional untuk sistem monitoring tsunami dengan teknologi AI dan deteksi real-time.

## ✨ Fitur Utama

### 🎥 Live Monitoring
- **Real-time RTSP Streaming**: Monitoring langsung dari kamera CCTV
- **AI Wave Detection**: Deteksi otomatis tinggi gelombang menggunakan computer vision
- **Visual Overlay**: Tampilan garis threshold dan status real-time
- **Auto-scaling**: Penyesuaian ukuran video otomatis

### 🚨 Alert System
- **WhatsApp Alert**: Notifikasi otomatis via WhatsApp untuk gelombang tinggi
- **SMS Alert**: Backup notifikasi via SMS
- **Tsunami Alert**: Alert khusus untuk kondisi extreme berulang
- **Cooldown System**: Pencegahan spam notifikasi

### 📊 Data Analytics
- **Real-time Charts**: Grafik pergerakan gelombang live
- **Historical Data**: Penyimpanan dan analisis data historis
- **Status Tracking**: Monitor status gelombang dan extreme count
- **Export Reports**: Download laporan dalam format PDF

### 🌍 Earthquake Monitoring
- **BMKG Integration**: Data gempa real-time dari BMKG
- **Magnitude Threshold**: Alert berdasarkan magnitude gempa
- **Tsunami Risk Assessment**: Evaluasi risiko tsunami dari gempa

### ⚙️ Configuration Management
- **Persistent Settings**: Penyimpanan konfigurasi otomatis
- **Threshold Adjustment**: Penyesuaian ambang batas deteksi
- **Visual Customization**: Kustomisasi tampilan overlay
- **Alert Configuration**: Pengaturan alert dan cooldown

## 🚀 Instalasi

### Prerequisites
- Python 3.8 atau lebih baru
- OpenCV dengan dukungan FFMPEG
- Akses ke RTSP stream atau webcam

### Step 1: Clone Repository
```bash
cd "PENELITIAN 6/web"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables
Buat file `.env` di root directory:

```env
# RTSP Configuration
RTSP_URL=rtsp://username:password@ip:port/stream
CAMERA_LOCATION=Pantai Kuta, Bali

# CSV Data Path
OMBAK_CSV_PATH=deteksi_ombak.csv

# WhatsApp Configuration (Optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+62812345678

# SMS Configuration (Optional)
SMS_FROM=+14155238886
SMS_TO=+62812345678

# Threshold Configuration
GARIS_EXTREME_Y=180
GARIS_SANGAT_TINGGI_Y=210
GARIS_TINGGI_Y=230
GARIS_SEDANG_Y=250
GARIS_RENDAH_Y=280
```

### Step 4: Run Application
```bash
python app.py
```

Dashboard akan tersedia di: `http://localhost:5000`

## 📱 Penggunaan

### 1. Live Monitoring
1. Buka tab **"Live Monitoring"**
2. Masukkan RTSP URL di sidebar
3. Klik **"Start Stream"** untuk memulai monitoring
4. Monitor status gelombang real-time

### 2. Konfigurasi System
1. Buka tab **"Konfigurasi"**
2. Sesuaikan ambang batas deteksi (pixel threshold)
3. Konfigurasi WhatsApp dan SMS alert
4. Atur tsunami alert threshold
5. Klik **"Simpan Konfigurasi"**

### 3. Analisis Data
1. Buka tab **"Data & Grafik"**
2. Lihat grafik pergerakan gelombang real-time
3. Analisis data historis dalam tabel
4. Download laporan PDF

### 4. Monitoring Gempa
1. Buka tab **"Monitoring Gempa"**
2. Klik **"Refresh Data Gempa"** untuk data terbaru
3. Monitor magnitude dan risiko tsunami
4. Konfigurasi alert threshold gempa

## 🔧 Konfigurasi Lanjutan

### Threshold Detection
- **EXTREME**: Gelombang > 4 meter (Alert tsunami)
- **SANGAT TINGGI**: Gelombang 2.5-4 meter
- **TINGGI**: Gelombang 1.25-2.5 meter
- **SEDANG**: Gelombang 0.5-1.25 meter
- **RENDAH**: Gelombang < 0.5 meter

### Alert Logic
- **WhatsApp/SMS**: Trigger untuk gelombang ≥ 2.5 meter
- **Tsunami Alert**: 12 deteksi EXTREME berturut-turut
- **Cooldown**: Mencegah spam notifikasi (default 5 menit)

### Data Storage
- Format: CSV dengan timestamp, peak_y, status, extreme_count
- Auto-header: Membuat header CSV otomatis
- Backup: Data tersimpan persistent

## 🛠️ API Endpoints

### Stream Control
- `POST /start_stream` - Mulai streaming
- `POST /stop_stream` - Hentikan streaming
- `GET /video_feed` - Video stream endpoint

### Configuration
- `POST /update_config` - Update konfigurasi
- `GET /get_status` - Status sistem

### Alerts
- `POST /send_test_wa` - Test WhatsApp
- `POST /send_test_sms` - Test SMS
- `POST /send_test_tsunami_alert` - Test tsunami alert

### Data
- `GET /get_wave_data` - Data gelombang
- `GET /get_earthquake_data` - Data gempa BMKG

## 🔒 Security Features

### Input Validation
- Sanitasi input RTSP URL
- Validasi parameter konfigurasi
- Error handling comprehensive

### Rate Limiting
- Cooldown untuk alerts
- Throttling untuk API calls
- Buffer overflow protection

### Data Protection
- Secure config storage
- Environment variable protection
- Session management

## 📊 Monitoring & Analytics

### Real-time Metrics
- Status gelombang saat ini
- Peak Y position (pixel)
- Extreme count tracking
- Total data points

### Historical Analysis
- Grafik time series
- Status distribution
- Alert frequency analysis
- Trend detection

### Performance Monitoring
- Stream frame rate
- Detection accuracy
- Response time alerts
- System resource usage

## 🚨 Alert Configuration

### WhatsApp Setup
```python
# Diperlukan: Twilio account dengan WhatsApp sandbox
TWILIO_ACCOUNT_SID = "your_sid"
TWILIO_AUTH_TOKEN = "your_token"
WHATSAPP_FROM = "whatsapp:+14155238886"
WHATSAPP_TO = "whatsapp:+62xxxxxxxxxxxx"
```

### SMS Setup
```python
# Diperlukan: Twilio account dengan SMS service
SMS_FROM = "+14155238886"
SMS_TO = "+62xxxxxxxxxxxx"
```

### Custom Alert Messages
Alert messages dapat dikustomisasi melalui konfigurasi:
- Template pesan dinamis
- Lokasi kamera otomatis
- Timestamp real-time
- Status gelombang detail

## 🔄 Auto-restart & Recovery

### Stream Recovery
- Auto-reconnect untuk RTSP yang terputus
- Fallback ke backup stream
- Error logging comprehensive

### Data Recovery
- CSV corruption handling
- Auto-backup data penting
- Recovery dari file backup

### Alert Recovery
- Retry mechanism untuk gagal kirim
- Queue system untuk alert pending
- Fallback notification methods

## 📈 Scalability

### Multi-Camera Support
- Ekstensi untuk multiple streams
- Centralized monitoring dashboard
- Load balancing untuk processing

### Cloud Integration
- AWS/Azure deployment ready
- Docker containerization
- Kubernetes orchestration

### Database Integration
- PostgreSQL/MySQL support
- Redis untuk caching
- InfluxDB untuk time series

## 🐛 Troubleshooting

### Common Issues

**1. Stream tidak muncul**
- Periksa RTSP URL dan kredensial
- Test koneksi jaringan
- Verify codec support

**2. Alert tidak terkirim**
- Periksa Twilio credentials
- Verify phone number format
- Check balance Twilio account

**3. Data tidak tersimpan**
- Periksa permission direktori
- Verify CSV path configuration
- Check disk space available

**4. Performance lambat**
- Reduce video resolution
- Optimize detection parameters
- Check system resources

### Debug Mode
Jalankan dengan debug untuk troubleshooting:
```bash
FLASK_DEBUG=1 python app.py
```

### Log Files
Monitor log files untuk error analysis:
- Stream errors: Check OpenCV warnings
- Alert errors: Check Twilio logs
- Detection errors: Check algorithm output

## 👥 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Support

- **Email**: support@tsunamialert.com
- **Documentation**: [Wiki](link-to-wiki)
- **Issues**: [GitHub Issues](link-to-issues)
- **Discord**: [Community Server](link-to-discord)

## 🙏 Acknowledgments

- **BMKG**: Data gempa real-time
- **OpenCV**: Computer vision library
- **Twilio**: Communication platform
- **Bootstrap**: UI framework
- **Chart.js**: Data visualization

---

**⚠️ Disclaimer**: Sistem ini untuk tujuan monitoring dan early warning. Selalu ikuti protokol evakuasi resmi dari pihak berwenang dalam situasi darurat.