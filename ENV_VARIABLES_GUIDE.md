# 🔧 Panduan Mengubah Environment Variables

## 🎯 **Mengapa Environment Variables Tidak Bisa Diubah dari Dashboard?**

Environment variables di dashboard **sengaja dibuat read-only** untuk:
- ✅ **Keamanan**: Mencegah perubahan kredensial sensitif dari interface
- ✅ **Konsistensi**: Menghindari konflik antara .env dan dashboard
- ✅ **Best Practice**: Konfigurasi sistem seharusnya di file .env

## 🛠️ **Cara Mengubah Environment Variables:**

### **Metode 1: Edit File .env Langsung (RECOMMENDED)**

#### **1. Buka File .env**
```bash
# Di Windows (Notepad)
notepad .env

# Di Windows (VS Code)
code .env

# Di Windows (Notepad++)
notepad++ .env
```

#### **2. Edit Nilai yang Diinginkan**
```env
# Contoh mengubah nomor WhatsApp
WHATSAPP_TO=whatsapp:+6281329512255

# Contoh mengubah lokasi kamera
CAMERA_LOCATION=Pantai Kuta, Bali

# Contoh mengubah RTSP URL
RTSP_URL=rtsp://admin:password@192.168.1.100:8554/stream
```

#### **3. Simpan File**
- Tekan `Ctrl + S` untuk menyimpan
- Restart dashboard untuk memuat perubahan

### **Metode 2: Menggunakan Command Line**

#### **Windows (PowerShell)**
```powershell
# Set environment variable sementara
$env:WHATSAPP_TO = "whatsapp:+6281329512255"
$env:CAMERA_LOCATION = "Pantai Kuta, Bali"

# Set environment variable permanen
[Environment]::SetEnvironmentVariable("WHATSAPP_TO", "whatsapp:+6281329512255", "User")
```

#### **Windows (Command Prompt)**
```cmd
# Set environment variable sementara
set WHATSAPP_TO=whatsapp:+6281329512255
set CAMERA_LOCATION=Pantai Kuta, Bali

# Set environment variable permanen
setx WHATSAPP_TO "whatsapp:+6281329512255"
setx CAMERA_LOCATION "Pantai Kuta, Bali"
```

## 📋 **Daftar Environment Variables yang Bisa Diubah:**

### **🔐 Kredensial Twilio (Wajib)**
```env
TWILIO_ACCOUNT_SID=AC3235371d25a8aa5e607a4d3a8dcef81d
TWILIO_AUTH_TOKEN=your_auth_token_here
```

### **📱 WhatsApp Configuration**
```env
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+6281329512255
```

### **📱 SMS Configuration**
```env
TWILIO_MESSAGING_SERVICE_SID=MG1b2be1c74b602bfbf68793e6b8aa6730
TWILIO_SMS_FROM=+12025550123
SMS_TO=+6281329512255
```

### **⚙️ System Configuration**
```env
OMBAK_CSV_PATH=deteksi_ombak.csv
RTSP_URL=rtsp://user:pass@ip:8554/Streaming/Channels/101
CAMERA_LOCATION=Pantai Kuta, Bali
```

## 🔄 **Cara Memuat Perubahan:**

### **1. Restart Dashboard**
```bash
# Stop dashboard (Ctrl + C)
# Jalankan ulang
streamlit run ombak_dashboard_streamlit.py
```

### **2. Refresh Browser**
- Tekan `F5` atau `Ctrl + R`
- Dashboard akan memuat ulang dengan nilai baru

## ⚠️ **Catatan Penting:**

### **1. Format Nomor Telepon**
```env
# WhatsApp (harus dengan prefix whatsapp:)
WHATSAPP_TO=whatsapp:+6281329512255

# SMS (format internasional)
SMS_TO=+6281329512255
```

### **2. Kredensial Twilio**
- ✅ **Account SID**: Dapatkan dari Twilio Console
- ✅ **Auth Token**: Dapatkan dari Twilio Console
- ✅ **Phone Numbers**: Harus terdaftar di akun Twilio Anda

### **3. File .env**
- ✅ **Lokasi**: Harus di folder yang sama dengan dashboard
- ✅ **Encoding**: Gunakan UTF-8
- ✅ **Format**: `KEY=value` (tanpa spasi di sekitar =)

## 🚀 **Contoh Lengkap File .env:**

```env
# Konfigurasi Twilio untuk WhatsApp, SMS, dan Tsunami Alert
# Daftar di https://console.twilio.com untuk mendapatkan kredensial

# Kredensial Twilio (Wajib untuk WA, SMS, dan Tsunami Alert)
TWILIO_ACCOUNT_SID=AC3235371d25a8aa5e607a4d3a8dcef81d
TWILIO_AUTH_TOKEN=your_auth_token_here

# WhatsApp Configuration
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+6281329512255

# SMS Configuration  
TWILIO_MESSAGING_SERVICE_SID=MG1b2be1c74b602bfbf68793e6b8aa6730
TWILIO_SMS_FROM=+12025550123
SMS_TO=+6281329512255

# Path file CSV (opsional)
OMBAK_CSV_PATH=deteksi_ombak.csv

# RTSP URL (opsional)
RTSP_URL=rtsp://admin:password@192.168.1.100:8554/stream

# Camera Location Configuration
CAMERA_LOCATION=Pantai Kuta, Bali
```

## 🔍 **Troubleshooting:**

### **1. Perubahan Tidak Muncul**
- ✅ Restart dashboard
- ✅ Refresh browser
- ✅ Periksa format file .env

### **2. Error Kredensial**
- ✅ Periksa Account SID dan Auth Token
- ✅ Pastikan nomor telepon terdaftar di Twilio
- ✅ Verifikasi format nomor telepon

### **3. File .env Tidak Ditemukan**
- ✅ Pastikan file .env ada di folder dashboard
- ✅ Copy dari env_template.txt jika belum ada
- ✅ Periksa nama file (harus .env, bukan .env.txt)

---

**💡 Tips**: Gunakan editor teks seperti VS Code atau Notepad++ untuk mengedit file .env agar lebih mudah dan aman!
