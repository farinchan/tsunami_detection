# 🌍 Panduan Monitoring Gempa BMKG

## 📋 **Overview**

Fitur monitoring gempa menggunakan API BMKG (Badan Meteorologi, Klimatologi, dan Geofisika) untuk mengambil data gempa real-time dan mengirim notifikasi otomatis via WhatsApp dan SMS.

## 🚀 **Fitur Utama**

### **1. Monitoring Real-time**
- ✅ Mengambil data gempa terbaru dari API BMKG
- ✅ Monitoring otomatis dengan interval yang dapat dikonfigurasi
- ✅ Alert otomatis berdasarkan threshold magnitude

### **2. Notifikasi Multi-Channel**
- ✅ **WhatsApp**: Notifikasi lengkap dengan emoji dan format yang menarik
- ✅ **SMS**: Notifikasi singkat untuk jangkauan yang lebih luas
- ✅ **Dual Alert**: Bisa mengirim ke WhatsApp dan SMS bersamaan

### **3. Konfigurasi Fleksibel**
- ✅ **Threshold Magnitude**: Set minimum magnitude untuk alert
- ✅ **Threshold Tsunami**: Set minimum magnitude untuk alert tsunami
- ✅ **Interval Monitoring**: Set interval pengecekan gempa
- ✅ **Enable/Disable**: Aktifkan/nonaktifkan monitoring per channel

### **4. Data & Analisis**
- ✅ **Data Gempa Terbaru**: Informasi lengkap gempa terkini
- ✅ **Riwayat Gempa**: Data gempa dalam periode tertentu
- ✅ **Grafik Magnitude**: Visualisasi trend magnitude vs waktu
- ✅ **Detail Lengkap**: JSON data gempa untuk analisis mendalam

## 📁 **File yang Dibuat**

### **1. `earthquake_bmkg.py`**
Modul utama untuk mengambil data gempa dari API BMKG.

**Fitur:**
- `get_earthquake_data()`: Ambil data gempa terbaru
- `get_earthquake_list()`: Ambil daftar gempa
- `parse_earthquake_data()`: Parse data gempa ke format yang mudah digunakan
- `check_earthquake_alert()`: Cek apakah gempa perlu di-alert
- `get_earthquake_history()`: Ambil riwayat gempa

### **2. `notify_earthquake.py`**
Modul untuk mengirim notifikasi gempa via WhatsApp dan SMS.

**Fitur:**
- `send_earthquake_alert_whatsapp()`: Kirim alert gempa via WhatsApp
- `send_earthquake_alert_sms()`: Kirim alert gempa via SMS
- `send_earthquake_alert()`: Kirim alert ke multiple channel

### **3. Dashboard Integration**
Halaman baru "🌍 Monitoring Gempa BMKG" di dashboard dengan:
- Konfigurasi monitoring gempa
- Status monitoring real-time
- Data gempa terbaru
- Riwayat gempa dengan grafik
- Test notifikasi

## ⚙️ **Konfigurasi**

### **1. Threshold Magnitude**
```python
# Default: 5.0
magnitude_threshold = 5.0  # Minimum magnitude untuk alert gempa
tsunami_threshold = 6.0    # Minimum magnitude untuk alert tsunami
```

### **2. Interval Monitoring**
```python
# Default: 300 detik (5 menit)
earthquake_check_interval = 300  # Interval pengecekan gempa
```

### **3. Channel Notifikasi**
```python
enable_earthquake_wa = True   # Enable WhatsApp
enable_earthquake_sms = True  # Enable SMS
```

## 📱 **Format Notifikasi**

### **WhatsApp Alert Gempa**
```
⚠️ *ALERT GEMPA!* ⚠️

🌍 *INFORMASI GEMPA TERBARU*

*Waktu:* 2024-01-15 14:30:25
*Magnitude:* M6.2
*Kedalaman:* 10 km
*Lokasi:* Laut Banda, Maluku
*Koordinat:* 4.5 LS, 129.2 BT

*Potensi Tsunami:* Tidak berpotensi tsunami
*Dirasakan:* Dirasakan di Ambon, Tual

📢 *WASPADA DAN SIAP SIAGA!* 📢

📡 *Sumber:* BMKG
🕐 *Update:* 2024-01-15 14:35:00

_Sistem Monitoring Gempa Otomatis_
```

### **WhatsApp Alert Tsunami**
```
🚨 *ALERT TSUNAMI POTENSIAL!* 🚨

🌊 *INFORMASI GEMPA TERBARU*

*Waktu:* 2024-01-15 14:30:25
*Magnitude:* M7.5
*Kedalaman:* 15 km
*Lokasi:* Laut Banda, Maluku
*Koordinat:* 4.5 LS, 129.2 BT

*Potensi Tsunami:* Berpotensi tsunami
*Dirasakan:* Dirasakan di Ambon, Tual

⚠️ *SEGERA EVAKUASI KE TEMPAT TINGGI!* ⚠️

📡 *Sumber:* BMKG
🕐 *Update:* 2024-01-15 14:35:00

_Sistem Monitoring Gempa Otomatis_
```

## 🔧 **Cara Menggunakan**

### **1. Aktifkan Monitoring**
1. Buka dashboard
2. Pilih tab "🌍 Monitoring Gempa BMKG"
3. Centang "🔍 Enable Monitoring Gempa"
4. Set threshold magnitude sesuai kebutuhan
5. Pilih channel notifikasi (WhatsApp/SMS)

### **2. Monitor Data Real-time**
1. Klik "🔄 Refresh Data Gempa" untuk mengambil data terbaru
2. Lihat informasi gempa di metrics cards
3. Buka "📋 Detail Lengkap Gempa Terbaru" untuk data JSON

### **3. Lihat Riwayat Gempa**
1. Pilih periode riwayat (6, 12, 24, 48, 72 jam)
2. Klik "📊 Tampilkan Riwayat"
3. Lihat tabel data dan grafik magnitude

### **4. Test Notifikasi**
1. Buka "📤 Test Kirim Alert Gempa"
2. Set magnitude, lokasi, dan level alert
3. Klik "📤 Kirim Test Alert"
4. Verifikasi notifikasi diterima

## 📊 **Data yang Tersedia**

### **Informasi Gempa**
- **Waktu**: Tanggal dan jam kejadian
- **Magnitude**: Kekuatan gempa (skala Richter)
- **Kedalaman**: Kedalaman pusat gempa
- **Lokasi**: Wilayah kejadian gempa
- **Koordinat**: Latitude dan longitude
- **Potensi Tsunami**: Status potensi tsunami
- **Dirasakan**: Area yang merasakan gempa

### **Riwayat Gempa**
- Data gempa dalam periode tertentu
- Tabel dengan informasi lengkap
- Grafik magnitude vs waktu
- Threshold lines untuk alert

## 🚨 **Level Alert**

### **1. EARTHQUAKE Alert**
- **Kondisi**: Magnitude ≥ threshold magnitude
- **Notifikasi**: ⚠️ ALERT GEMPA!
- **Action**: Waspada dan siap siaga

### **2. TSUNAMI Alert**
- **Kondisi**: Magnitude ≥ threshold tsunami
- **Notifikasi**: 🚨 ALERT TSUNAMI POTENSIAL!
- **Action**: Segera evakuasi ke tempat tinggi

### **3. NONE**
- **Kondisi**: Magnitude < threshold magnitude
- **Notifikasi**: ℹ️ Informasi gempa (tidak perlu alert)
- **Action**: Monitoring saja

## 🔗 **API BMKG**

### **Endpoint yang Digunakan**
- **Data Gempa Terbaru**: `https://data.bmkg.go.id/DataMKG/TEWS/autogempa.json`
- **Daftar Gempa**: `https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json`

### **Format Data BMKG**
```json
{
  "Infogempa": {
    "gempa": {
      "Tanggal": "18 Sep 2025",
      "Jam": "21:59:34 WIB",
      "Magnitude": "4.7",
      "Kedalaman": "10 km",
      "Coordinates": "4.5 LS, 129.2 BT",
      "Wilayah": "Pusat gempa berada di laut 218 Km barat daya Kuta Selatan",
      "Potensi": "Tidak berpotensi tsunami",
      "Dirasakan": "Dirasakan di wilayah sekitar"
    }
  }
}
```

## ⚠️ **Catatan Penting**

### **1. Rate Limiting**
- API BMKG memiliki rate limiting
- Gunakan interval monitoring yang wajar (minimal 30 detik)
- Jangan spam request ke API

### **2. Akurasi Data**
- Data dari BMKG adalah data resmi
- Update data tergantung pada BMKG
- Selalu verifikasi dengan sumber resmi

### **3. Notifikasi**
- Pastikan kredensial WhatsApp dan SMS sudah benar
- Test notifikasi sebelum mengaktifkan monitoring
- Monitor log untuk memastikan notifikasi terkirim

### **4. Monitoring 24/7**
- Untuk monitoring 24/7, pastikan server selalu online
- Gunakan service seperti systemd atau PM2
- Monitor log dan error handling

## 🛠️ **Troubleshooting**

### **1. API BMKG Tidak Responsif**
```python
# Cek koneksi internet
# Cek status API BMKG
# Gunakan timeout yang wajar
```

### **2. Notifikasi Tidak Terkirim**
```python
# Cek kredensial Twilio
# Cek nomor tujuan
# Cek log error
```

### **3. Data Gempa Tidak Update**
```python
# Cek interval monitoring
# Cek API response
# Cek parsing data
```

## 📈 **Pengembangan Selanjutnya**

### **1. Fitur yang Bisa Ditambahkan**
- ✅ **Database Logging**: Simpan riwayat gempa ke database
- ✅ **Email Notifications**: Tambah notifikasi via email
- ✅ **Webhook Integration**: Integrasi dengan sistem lain
- ✅ **Mobile App**: Aplikasi mobile untuk monitoring
- ✅ **Map Integration**: Tampilkan lokasi gempa di peta

### **2. Optimasi**
- ✅ **Caching**: Cache data gempa untuk mengurangi API calls
- ✅ **Batch Processing**: Proses multiple gempa sekaligus
- ✅ **Error Recovery**: Auto retry untuk failed requests
- ✅ **Performance Monitoring**: Monitor performa sistem

---

**💡 Tips**: Fitur monitoring gempa ini sangat berguna untuk early warning system. Pastikan untuk selalu mengupdate threshold sesuai dengan kebutuhan dan kondisi geografis area monitoring Anda!
