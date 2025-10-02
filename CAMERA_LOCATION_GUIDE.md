# 📍 Panduan Menentukan Lokasi Kamera

## 🎯 **Cara Menentukan Lokasi untuk Tsunami Alert**

Sistem tsunami alert sekarang mendukung lokasi kamera yang dapat dikonfigurasi. Berikut adalah cara-cara untuk menentukan lokasi:

### 🔧 **1. Melalui Dashboard (Recommended)**

#### **Langkah-langkah:**
1. **Buka Dashboard:**
   ```bash
   streamlit run ombak_dashboard_streamlit.py
   ```

2. **Buka Sidebar:**
   - Scroll ke section "📍 Lokasi Kamera"
   - Isi field "Lokasi Kamera"

3. **Contoh Lokasi:**
   - `Pantai Kuta, Bali`
   - `Jl. Pantai Selatan No. 123, Jakarta`
   - `Pantai Sanur, Denpasar, Bali`
   - `Pelabuhan Tanjung Priok, Jakarta Utara`

4. **Auto-Save:**
   - Lokasi akan otomatis tersimpan
   - Tidak perlu setup ulang saat restart

### 🔧 **2. Melalui File .env**

#### **Langkah-langkah:**
1. **Buka file `.env`** di direktori proyek
2. **Tambahkan variabel:**
   ```bash
   CAMERA_LOCATION=Pantai Kuta, Bali
   ```
3. **Restart dashboard** untuk memuat konfigurasi baru

### 🔧 **3. Melalui Environment Variable**

#### **Windows (PowerShell):**
```powershell
$env:CAMERA_LOCATION="Pantai Kuta, Bali"
streamlit run ombak_dashboard_streamlit.py
```

#### **Linux/Mac (Terminal):**
```bash
export CAMERA_LOCATION="Pantai Kuta, Bali"
streamlit run ombak_dashboard_streamlit.py
```

## 📋 **Format Lokasi yang Disarankan**

### ✅ **Format yang Baik:**
- `Pantai Kuta, Bali`
- `Jl. Pantai Selatan No. 123, Jakarta`
- `Pelabuhan Tanjung Priok, Jakarta Utara`
- `Pantai Sanur, Denpasar, Bali`
- `Pantai Parangtritis, Yogyakarta`

### ❌ **Format yang Kurang Baik:**
- `Kamera 1` (terlalu umum)
- `Lokasi` (tidak informatif)
- `Camera` (tidak spesifik)

## 🎯 **Prioritas Lokasi**

Sistem akan menggunakan lokasi dengan prioritas berikut:

1. **Parameter `location`** (jika diberikan saat pemanggilan fungsi)
2. **Environment Variable `CAMERA_LOCATION`** (dari file .env)
3. **Konfigurasi Dashboard** (dari persistent config)
4. **Placeholder** `[LOKASI KAMERA ANDA]` (jika tidak ada konfigurasi)

## 📱 **Contoh Pesan Tsunami Alert dengan Lokasi**

### **Sebelum (Placeholder):**
```
🚨 *PERINGATAN TSUNAMI POTENSIAL!* 🚨

Sistem deteksi ombak telah mendeteksi *12 kali berturut-turut* ombak EXTREME (>4 meter).

*Waktu:* 2025-01-18 14:30:25
*Lokasi:* [LOKASI KAMERA ANDA]
*Status:* > 4 Meter (EXTREME)
*Puncak Ombak Y:* 150
*Frame:* 1250

⚠️ *SEGERA EVAKUASI KE TEMPAT TINGGI!* ⚠️
Hubungi pihak berwenang segera!

_Sistem Deteksi Ombak Otomatis - Tsunami Alert_
```

### **Sesudah (Dengan Lokasi):**
```
🚨 *PERINGATAN TSUNAMI POTENSIAL!* 🚨

Sistem deteksi ombak telah mendeteksi *12 kali berturut-turut* ombak EXTREME (>4 meter).

*Waktu:* 2025-01-18 14:30:25
*Lokasi:* Pantai Kuta, Bali
*Status:* > 4 Meter (EXTREME)
*Puncak Ombak Y:* 150
*Frame:* 1250

⚠️ *SEGERA EVAKUASI KE TEMPAT TINGGI!* ⚠️
Hubungi pihak berwenang segera!

_Sistem Deteksi Ombak Otomatis - Tsunami Alert_
```

## 🔧 **Implementasi Teknis**

### **Fungsi `send_tsunami_alert_whatsapp`:**
```python
def send_tsunami_alert_whatsapp(extreme_count: int, peak_y: int, frame_idx: int, 
                               to: Optional[str] = None, location: Optional[str] = None):
    # Tentukan lokasi
    if location:
        location_text = location
    else:
        camera_location = os.getenv("CAMERA_LOCATION", "")
        if camera_location:
            location_text = camera_location
        else:
            location_text = "[LOKASI KAMERA ANDA]"
    
    # Gunakan location_text dalam pesan
```

### **Konfigurasi Dashboard:**
```python
st.sidebar.header("📍 Lokasi Kamera")
camera_location = st.sidebar.text_input("Lokasi Kamera", 
    value=config.get("camera_location", os.getenv("CAMERA_LOCATION", "")),
    help="Contoh: Pantai Kuta, Bali atau Jl. Pantai Selatan No. 123, Jakarta")
```

## 🎯 **Tips dan Rekomendasi**

### **1. Gunakan Nama Lokasi yang Jelas:**
- ✅ `Pantai Kuta, Bali`
- ✅ `Pelabuhan Tanjung Priok, Jakarta Utara`
- ❌ `Kamera 1`
- ❌ `Lokasi`

### **2. Sertakan Informasi Geografis:**
- ✅ `Pantai Sanur, Denpasar, Bali`
- ✅ `Jl. Pantai Selatan No. 123, Jakarta`
- ❌ `Sanur`
- ❌ `Jakarta`

### **3. Konsisten dengan Nama Resmi:**
- ✅ `Pantai Parangtritis, Yogyakarta`
- ✅ `Pantai Kuta, Badung, Bali`
- ❌ `Pantai Kuta Bali`
- ❌ `Parangtritis`

### **4. Update Lokasi jika Pindah:**
- Ganti konfigurasi di dashboard
- Atau update file `.env`
- Restart dashboard jika perlu

## 🚀 **Cara Cepat Setup Lokasi**

### **Metode 1: Dashboard (Paling Mudah)**
1. Buka dashboard
2. Isi "Lokasi Kamera" di sidebar
3. Selesai! (Auto-save)

### **Metode 2: File .env**
1. Buka file `.env`
2. Tambahkan `CAMERA_LOCATION=Pantai Kuta, Bali`
3. Restart dashboard

### **Metode 3: Environment Variable**
1. Set environment variable
2. Jalankan dashboard
3. Lokasi akan otomatis terdeteksi

---

**🎉 Sekarang sistem tsunami alert akan menampilkan lokasi kamera yang jelas dan informatif!**
