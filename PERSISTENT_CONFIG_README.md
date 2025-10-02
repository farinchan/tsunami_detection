# 📋 Persistent Configuration Dashboard

## 🎯 Fitur Auto-Save Configuration

Dashboard sekarang memiliki sistem **persistent configuration** yang otomatis menyimpan semua pengaturan dan tidak perlu diulang lagi setiap kali refresh atau restart.

### ✅ **Yang Tersimpan Otomatis:**

#### 📄 **Data & Logging**
- CSV log path
- Interval tulis log (detik)

#### 🎥 **RTSP & Streaming**
- RTSP/HTTP URL
- Resize lebar (px)

#### 🧭 **Ambang Garis (Threshold)**
- EXTREME (px)
- 4m SANGAT TINGGI (px)
- 2.5m TINGGI (px)
- 1.25m SEDANG (px)
- 0.5m RENDAH (px)

#### ✏️ **Overlay Settings**
- Ketebalan garis
- Ketebalan garis puncak
- Ukuran font
- Ketebalan font

#### 📣 **WhatsApp Settings**
- Enable/disable WA otomatis
- Cooldown WA (detik)
- Nomor WA override

#### 📱 **SMS Settings**
- Enable/disable SMS otomatis
- Cooldown SMS (detik)
- Nomor SMS override

#### 🚨 **Tsunami Alert Settings**
- Threshold EXTREME untuk alert
- Cooldown alert (menit)
- Enable/disable tsunami alert
- Nomor WA tsunami override

### 🔧 **Cara Kerja:**

1. **Auto-Save**: Konfigurasi otomatis tersimpan setiap kali ada perubahan
2. **File JSON**: Data disimpan di `dashboard_config.json`
3. **Load on Start**: Dashboard memuat konfigurasi terakhir saat startup
4. **Fallback**: Jika file tidak ada, menggunakan default values

### ⚙️ **Kelola Konfigurasi:**

#### 💾 **Simpan Manual**
- Klik tombol "💾 Simpan Konfigurasi" di sidebar

#### 🔄 **Reset ke Default**
- Klik tombol "🔄 Reset ke Default" untuk mengembalikan ke pengaturan awal

#### 📤 **Export Konfigurasi**
- Klik "📤 Export Konfigurasi" untuk download file JSON
- Berguna untuk backup atau sharing konfigurasi

#### 📥 **Import Konfigurasi**
- Upload file JSON konfigurasi
- Berguna untuk restore backup atau menggunakan konfigurasi orang lain

### 📁 **File yang Dibuat:**

- `dashboard_config.json` - File konfigurasi utama
- `dashboard_config.py` - Module untuk mengelola konfigurasi

### 🎯 **Keuntungan:**

1. **Tidak Perlu Setup Ulang**: Semua pengaturan tersimpan otomatis
2. **Backup & Restore**: Bisa export/import konfigurasi
3. **Sharing**: Bisa share konfigurasi dengan tim
4. **Version Control**: File JSON bisa di-commit ke git
5. **Multi-Environment**: Bisa punya konfigurasi berbeda per environment

### 🚀 **Cara Menggunakan:**

1. **Jalankan Dashboard** seperti biasa:
   ```bash
   streamlit run ombak_dashboard_streamlit.py
   ```

2. **Atur Konfigurasi** di sidebar sesuai kebutuhan

3. **Konfigurasi Otomatis Tersimpan** - tidak perlu melakukan apa-apa

4. **Restart Dashboard** - semua pengaturan akan tetap sama

5. **Kelola Konfigurasi** melalui section "⚙️ Konfigurasi" di sidebar

### 📋 **Contoh File Konfigurasi:**

```json
{
    "csv_path": "deteksi_ombak.csv",
    "sample_every_sec": 2,
    "rtsp_url": "rtsp://user:pass@192.168.1.100:8554/stream",
    "resize_width": 960,
    "garis_extreme_y": 180,
    "garis_sangat_tinggi_y": 210,
    "garis_tinggi_y": 230,
    "garis_sedang_y": 250,
    "garis_rendah_y": 280,
    "line_thickness": 1,
    "peak_thickness": 2,
    "font_scale": 0.7,
    "font_thickness": 2,
    "enable_wa": true,
    "wa_cooldown_sec": 300,
    "enable_sms": false,
    "sms_cooldown_sec": 300,
    "extreme_threshold": 12,
    "alert_cooldown_min": 30,
    "enable_tsunami_alert": true,
    "wa_to_override": "whatsapp:+6281234567890",
    "sms_to_override": "+6281234567890",
    "tsunami_wa_to_override": "whatsapp:+6281234567890"
}
```

### ⚠️ **Catatan Penting:**

- File `dashboard_config.json` akan dibuat otomatis saat pertama kali menjalankan dashboard
- Jika file rusak atau tidak bisa dibaca, dashboard akan menggunakan default values
- Konfigurasi tersimpan di direktori yang sama dengan dashboard
- Pastikan dashboard memiliki permission untuk menulis file di direktori tersebut

---

**🎉 Sekarang dashboard Anda memiliki persistent configuration yang akan menghemat waktu setup!**
