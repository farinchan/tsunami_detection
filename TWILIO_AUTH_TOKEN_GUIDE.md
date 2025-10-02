# 🔐 Panduan Mengisi Twilio Auth Token

## ✅ **SID dan Token Sudah Dikembalikan!**

File `.env` sudah dibuat dengan nilai yang sudah ada sebelumnya:

### 🔑 **Kredensial yang Sudah Dikembalikan:**

```env
# Account SID (Sudah ada)
TWILIO_ACCOUNT_SID=AC3235371d25a8aa5e607a4d3a8dcef81d

# Auth Token (Perlu diisi)
TWILIO_AUTH_TOKEN=your_auth_token_here

# WhatsApp Configuration (Sudah ada)
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
WHATSAPP_TO=whatsapp:+6281329512255

# SMS Configuration (Sudah ada)
TWILIO_MESSAGING_SERVICE_SID=MG1b2be1c74b602bfbf68793e6b8aa6730
TWILIO_SMS_FROM=+12025550123
SMS_TO=+6281329512255
```

## 🔧 **Cara Mengisi Auth Token:**

### **Metode 1: Edit File .env Langsung**

#### **1. Buka File .env**
```bash
# Di Windows (Notepad)
notepad .env

# Di Windows (VS Code)
code .env

# Di Windows (Notepad++)
notepad++ .env
```

#### **2. Ganti Auth Token**
```env
# Ganti baris ini:
TWILIO_AUTH_TOKEN=your_auth_token_here

# Menjadi:
TWILIO_AUTH_TOKEN=your_actual_auth_token_from_twilio_console
```

#### **3. Simpan File**
- Tekan `Ctrl + S` untuk menyimpan
- Restart dashboard untuk memuat perubahan

### **Metode 2: Menggunakan Command Line**

#### **Windows (PowerShell)**
```powershell
# Set environment variable sementara
$env:TWILIO_AUTH_TOKEN = "your_actual_auth_token_here"

# Set environment variable permanen
[Environment]::SetEnvironmentVariable("TWILIO_AUTH_TOKEN", "your_actual_auth_token_here", "User")
```

#### **Windows (Command Prompt)**
```cmd
# Set environment variable sementara
set TWILIO_AUTH_TOKEN=your_actual_auth_token_here

# Set environment variable permanen
setx TWILIO_AUTH_TOKEN "your_actual_auth_token_here"
```

## 🔍 **Cara Mendapatkan Auth Token dari Twilio Console:**

### **1. Login ke Twilio Console**
- Buka: https://console.twilio.com
- Login dengan akun Twilio Anda

### **2. Navigate ke Dashboard**
- Setelah login, Anda akan melihat dashboard
- Cari section "Account Info" atau "Project Info"

### **3. Copy Auth Token**
- **Account SID**: `AC3235371d25a8aa5e607a4d3a8dcef81d` (sudah ada)
- **Auth Token**: Klik "Show" untuk menampilkan token
- Copy token yang muncul

### **4. Paste ke File .env**
- Buka file `.env`
- Ganti `your_auth_token_here` dengan token yang dicopy
- Simpan file

## ⚠️ **Catatan Penting:**

### **1. Keamanan Auth Token**
- ✅ **Jangan share** Auth Token dengan siapa pun
- ✅ **Jangan commit** ke repository public
- ✅ **Simpan aman** di file .env

### **2. Format File .env**
```env
# Format yang benar:
TWILIO_AUTH_TOKEN=your_actual_token_here

# Format yang salah:
TWILIO_AUTH_TOKEN = your_actual_token_here  # Ada spasi
TWILIO_AUTH_TOKEN="your_actual_token_here"  # Ada quote
```

### **3. Restart Dashboard**
- Setelah mengubah `.env`, restart dashboard:
```bash
# Stop dashboard (Ctrl + C)
# Jalankan ulang
streamlit run ombak_dashboard_streamlit.py
```

## 🚀 **Verifikasi Konfigurasi:**

### **1. Cek di Dashboard**
- Buka dashboard
- Lihat di sidebar "WhatsApp Configuration"
- Auth Token akan menampilkan `***` jika sudah diisi

### **2. Test WhatsApp**
- Klik "Kirim Tes WhatsApp" di sidebar
- Jika berhasil, konfigurasi sudah benar

### **3. Test SMS**
- Klik "Kirim Tes SMS" di sidebar
- Jika berhasil, konfigurasi sudah benar

## 📋 **Contoh File .env Lengkap:**

```env
# Konfigurasi Twilio untuk WhatsApp, SMS, dan Tsunami Alert
# Daftar di https://console.twilio.com untuk mendapatkan kredensial

# Kredensial Twilio (Wajib untuk WA, SMS, dan Tsunami Alert)
TWILIO_ACCOUNT_SID=AC3235371d25a8aa5e607a4d3a8dcef81d
TWILIO_AUTH_TOKEN=your_actual_auth_token_from_twilio_console

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
RTSP_URL=rtsp://user:pass@ip:8554/Streaming/Channels/101

# Camera Location Configuration
CAMERA_LOCATION=Pantai Kuta, Bali
```

---

**💡 Tips**: Setelah mengisi Auth Token, dashboard akan bisa mengirim WhatsApp dan SMS dengan kredensial yang sudah ada!
