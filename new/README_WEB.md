# README_WEB.md - Panduan Sistem Monitoring Deteksi Ombak Web

## Sistem Monitoring Deteksi Ombak - Web Application

Aplikasi web untuk monitoring dan deteksi ombak menggunakan OpenCV dengan antarmuka web yang dapat diakses dari browser.

### Fitur Utama

1. **Web Interface**: Dashboard web yang responsif dengan real-time monitoring
2. **Headless OpenCV**: Deteksi berjalan di background tanpa window
3. **RTSP/HTTP Support**: Mendukung kamera IP dengan protokol RTSP atau HTTP
4. **Real-time Streaming**: Video feed langsung di web browser
5. **Konfigurasi Dynamic**: Pengaturan dapat diubah melalui web interface
6. **Live Charts**: Grafik real-time ketinggian ombak
7. **Data Logging**: Otomatis menyimpan ke CSV dan JSON
8. **WebSocket**: Update real-time menggunakan Socket.IO

### Instalasi

1. **Setup Environment**:
   ```bash
   # Jalankan setup.bat untuk instalasi otomatis
   setup.bat
   ```

2. **Manual Setup**:
   ```bash
   # Buat virtual environment
   python -m venv venv
   
   # Aktifkan virtual environment
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements_web.txt
   ```

### Menjalankan Aplikasi

1. **Menggunakan Batch File**:
   ```bash
   start.bat
   ```

2. **Manual**:
   ```bash
   # Aktifkan virtual environment
   venv\Scripts\activate
   
   # Jalankan aplikasi
   python app.py
   ```

3. **Akses Web Interface**:
   - Buka browser ke: `http://localhost:5000`
   - Untuk akses dari komputer lain: `http://[IP-ADDRESS]:5000`

### Konfigurasi

#### 1. Sumber Video
- **RTSP**: `rtsp://username:password@192.168.1.100:554/stream`
- **HTTP**: `http://192.168.1.100:8080/video`
- **File Video**: Path ke file video lokal
- **Webcam**: Gunakan `0`, `1`, `2` untuk webcam

#### 2. Garis Deteksi
Koordinat Y untuk berbagai level ombak:
- **Extreme**: Y < 180 (> 4 Meter)
- **Sangat Tinggi**: Y < 210 (4 Meter)
- **Tinggi**: Y < 230 (2.5 Meter)
- **Sedang**: Y < 250 (1.25 Meter)
- **Rendah**: Y < 280 (0.5 Meter)

#### 3. Parameter OpenCV
- **Canny Edge**: Ambang bawah dan atas untuk deteksi tepi
- **Hough Transform**: Parameter untuk deteksi garis
- **Save Interval**: Interval penyimpanan data (per frame)

### Struktur File

```
new/
├── app.py                 # Aplikasi web utama
├── templates/
│   └── index.html        # Template web interface
├── requirements_web.txt   # Dependencies Python
├── setup.bat             # Script setup
├── start.bat             # Script menjalankan aplikasi
├── deteksi_ombak.csv     # Output data CSV
├── deteksi_ombak.json    # Output data JSON
└── README_WEB.md         # Dokumentasi ini
```

### API Endpoints

1. **GET /api/config**: Mendapatkan konfigurasi saat ini
2. **POST /api/config**: Update konfigurasi
3. **POST /api/start**: Mulai monitoring
4. **POST /api/stop**: Hentikan monitoring
5. **GET /api/status**: Status real-time
6. **GET /api/data/latest**: Data terbaru

### WebSocket Events

1. **wave_data**: Data deteksi real-time
2. **video_frame**: Frame video dalam base64
3. **connection_status**: Status koneksi kamera

### Troubleshooting

#### 1. Kamera Tidak Terhubung
- Pastikan URL RTSP/HTTP benar
- Check koneksi jaringan ke kamera
- Verifikasi username/password jika diperlukan
- Test URL di VLC media player terlebih dahulu

#### 2. Performance Issues
- Kurangi resolusi video di kamera
- Tingkatkan interval save frame
- Gunakan komputer dengan spesifikasi lebih tinggi

#### 3. Web Interface Tidak Loading
- Pastikan Flask berjalan di port 5000
- Check firewall Windows
- Pastikan tidak ada aplikasi lain menggunakan port 5000

#### 4. Data Tidak Tersimpan
- Check permission folder untuk write access
- Pastikan disk space cukup
- Lihat console untuk error messages

### Contoh Konfigurasi RTSP

#### Hikvision:
```
rtsp://admin:password123@192.168.1.100:554/Streaming/Channels/101
```

#### Dahua:
```
rtsp://admin:password123@192.168.1.100:554/cam/realmonitor?channel=1&subtype=0
```

#### Generic IP Camera:
```
rtsp://username:password@192.168.1.100:554/stream
```

### Keamanan

1. **Jaringan Lokal**: Aplikasi hanya berjalan di jaringan lokal
2. **Authentication**: Tambahkan autentikasi jika perlu akses public
3. **HTTPS**: Gunakan reverse proxy untuk HTTPS
4. **Firewall**: Konfigurasi firewall sesuai kebutuhan

### Tips Optimasi

1. **Video Quality**: Gunakan resolusi optimal (720p-1080p)
2. **Frame Rate**: 15-30 FPS sudah cukup untuk deteksi
3. **Network**: Pastikan bandwidth cukup untuk streaming
4. **CPU Usage**: Monitor penggunaan CPU, kurangi kualitas jika perlu

### Pengembangan Lanjutan

1. **Database**: Integrasi dengan PostgreSQL/MySQL
2. **Alerts**: Sistem notifikasi via email/SMS
3. **Multiple Cameras**: Support multiple camera feeds
4. **AI Enhancement**: Integrasi dengan model AI untuk deteksi lebih akurat
5. **Mobile App**: Aplikasi mobile companion
6. **Cloud Integration**: Backup data ke cloud storage

### Support

Untuk bantuan lebih lanjut:
1. Check log error di console
2. Verify konfigurasi kamera
3. Test koneksi jaringan
4. Review parameter deteksi sesuai kondisi lapangan

---

**CATATAN**: Pastikan kamera IP sudah dikonfigurasi dengan benar dan dapat diakses dari komputer server sebelum menjalankan aplikasi.