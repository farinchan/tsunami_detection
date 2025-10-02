# ombak_dashboard_streamlit.py
# Streamlit dashboard lengkap:
# - Live RTSP + deteksi (logika main.py)
# - WhatsApp Alert + Tombol "Kirim Tes WA"
# - SMS Alert + Tombol "Kirim Tes SMS"
# - WhatsApp Tsunami Alert: 12 kali EXTREME berturut-turut → Alert Tsunami
# - Tab "📈 Log & Grafik / Laporan (PDF)"
# - Persistent Configuration dengan auto-save

import os, io, time, csv, cv2, numpy as np, pandas as pd, streamlit as st
from datetime import datetime, date
from typing import Tuple
from dashboard_config import load_config, save_config

st.set_page_config(page_title="🌊 Dashboard + Tsunami Alert", layout="wide")
st.title("🌊 Dashboard + Tsunami Alert")

# ===== Optional WhatsApp & SMS =====
SEND_WA_AVAILABLE = False
try:
    from notify_whatsapp import send_whatsapp, send_tsunami_alert_whatsapp
    SEND_WA_AVAILABLE = True
except Exception:
    SEND_WA_AVAILABLE = False

SEND_SMS_AVAILABLE = False
try:
    from notify_sms import send_sms
    SEND_SMS_AVAILABLE = True
except Exception:
    SEND_SMS_AVAILABLE = False


# ===== Load Configuration =====
config = load_config()

# ===== Sidebar (shared) =====
st.sidebar.header("📄 Data")
csv_path = st.sidebar.text_input("CSV log path", value=config.get("csv_path", os.getenv("OMBAK_CSV_PATH","deteksi_ombak.csv")))
sample_every_sec = st.sidebar.number_input("Interval tulis log (detik)", 1, 60, config.get("sample_every_sec", 2))

st.sidebar.header("🎥 RTSP / Streaming")
rtsp_url = st.sidebar.text_input("RTSP / HTTP URL", value=config.get("rtsp_url", os.getenv("RTSP_URL","")),
    help="Contoh: rtsp://user:pass@ip:8554/Streaming/Channels/101")
resize_width = st.sidebar.number_input("Resize lebar (px, 0 = asli)", 0, 3840, config.get("resize_width", 960), step=10)

st.sidebar.header("📍 Lokasi Kamera")
camera_location = st.sidebar.text_input("Lokasi Kamera", value=config.get("camera_location", os.getenv("CAMERA_LOCATION", "")),
    help="Contoh: Pantai Kuta, Bali atau Jl. Pantai Selatan No. 123, Jakarta")

st.sidebar.header("🧭 Ambang Garis (Absolute px)")
GARIS_EXTREME_Y        = st.sidebar.number_input("EXTREME (px)",        0, 4000, config.get("garis_extreme_y", 180))
GARIS_SANGAT_TINGGI_Y  = st.sidebar.number_input("4 m (SANGAT) (px)",   0, 4000, config.get("garis_sangat_tinggi_y", 210))
GARIS_TINGGI_Y         = st.sidebar.number_input("2,5 m (TINGGI) (px)", 0, 4000, config.get("garis_tinggi_y", 230))
GARIS_SEDANG_Y         = st.sidebar.number_input("1,25 m (SEDANG) (px)",0, 4000, config.get("garis_sedang_y", 250))
GARIS_RENDAH_Y         = st.sidebar.number_input("0,5 m (RENDAH) (px)", 0, 4000, config.get("garis_rendah_y", 280))

st.sidebar.header("✏️ Overlay")
line_thickness  = st.sidebar.slider("Ketebalan garis", 1, 6, config.get("line_thickness", 1))
peak_thickness  = st.sidebar.slider("Ketebalan garis puncak", 1, 6, config.get("peak_thickness", 2))
font_scale      = st.sidebar.slider("Ukuran font", 0.4, 2.0, config.get("font_scale", 0.7), 0.1)
font_thickness  = st.sidebar.slider("Ketebalan font", 1, 4, config.get("font_thickness", 2))

# ===== WhatsApp Section =====
st.sidebar.header("📣 WhatsApp")
st.sidebar.caption(f"Modul WA: {'✅' if SEND_WA_AVAILABLE else '❌'} (butuh notify_whatsapp.py + .env)")
enable_wa = st.sidebar.checkbox("Kirim WA otomatis bila status ≥ 2,5 m", value=config.get("enable_wa", False))
wa_cooldown_sec = st.sidebar.number_input("Cooldown WA (detik)", 30, 3600, config.get("wa_cooldown_sec", 300), step=30)

with st.sidebar.expander("🔔 Kirim Tes WhatsApp", expanded=False):
    wa_to_override = st.text_input("Nomor WA (opsional, whatsapp:+62...)", value=config.get("wa_to_override", os.getenv("WHATSAPP_TO","")))
    wa_test_msg = st.text_area("Pesan uji WA", value="Tes WA dari dashboard ombak ✅", height=80)
    if st.button("Kirim Tes WA"):
        if not SEND_WA_AVAILABLE:
            st.error("notify_whatsapp.py tidak ditemukan / kredensial belum diisi.")
        else:
            try:
                to_arg = wa_to_override.strip() or None
                sid = send_whatsapp(wa_test_msg, to=to_arg)
                st.success(f"Tes WA terkirim. SID: {sid}")
            except Exception as e:
                st.error(f"Gagal kirim WA: {e}")

# ===== SMS Section =====
st.sidebar.header("📱 SMS")
st.sidebar.caption(f"Modul SMS: {'✅' if SEND_SMS_AVAILABLE else '❌'} (butuh notify_sms.py + .env)")
enable_sms = st.sidebar.checkbox("Kirim SMS otomatis bila status ≥ 2,5 m", value=config.get("enable_sms", False))
sms_cooldown_sec = st.sidebar.number_input("Cooldown SMS (detik)", 30, 3600, config.get("sms_cooldown_sec", 300), step=30)

with st.sidebar.expander("✉️ Kirim Tes SMS", expanded=False):
    sms_to_override = st.text_input("Nomor SMS (opsional, E.164: +62...)", value=config.get("sms_to_override", os.getenv("SMS_TO","")))
    sms_test_msg = st.text_area("Pesan uji SMS", value="Tes SMS dari dashboard ombak ✅", height=80)
    if st.button("Kirim Tes SMS"):
        if not SEND_SMS_AVAILABLE:
            st.error("notify_sms.py tidak ditemukan / kredensial belum diisi.")
        else:
            try:
                to_arg = sms_to_override.strip() or None
                sids = send_sms(sms_test_msg, to=to_arg)
                st.success(f"Tes SMS terkirim. SID(s): {', '.join(sids)}")
            except Exception as e:
                st.error(f"Gagal kirim SMS: {e}")

# ===== WHATSAPP TSUNAMI ALERT Section =====
st.sidebar.header("🚨 WhatsApp Tsunami Alert")
st.sidebar.caption(f"Modul WA: {'✅' if SEND_WA_AVAILABLE else '❌'} (butuh notify_whatsapp.py + .env)")

# Tsunami Alert Settings
extreme_threshold = st.sidebar.number_input("Threshold EXTREME untuk Alert", 5, 50, config.get("extreme_threshold", 12), 
    help="Jumlah deteksi EXTREME berturut-turut untuk mengirim alert tsunami")
alert_cooldown_min = st.sidebar.number_input("Cooldown Alert (menit)", 5, 120, config.get("alert_cooldown_min", 30),
    help="Jeda waktu antar alert tsunami (menit)")

enable_tsunami_alert = st.sidebar.checkbox("Kirim Tsunami Alert otomatis bila 12 kali EXTREME", value=config.get("enable_tsunami_alert", False))

with st.sidebar.expander("🚨 Tes WhatsApp Tsunami Alert", expanded=False):
    tsunami_wa_to_override = st.text_input("Nomor WA Tsunami Alert (opsional, whatsapp:+62...)", value=config.get("tsunami_wa_to_override", os.getenv("WHATSAPP_TO","")))
    tsunami_test_msg = st.text_area("Pesan uji Tsunami Alert", 
        value="🚨 *TES ALERT TSUNAMI!* 🚨\n\nSistem deteksi ombak mengirim pesan uji.\n\n*Waktu:* " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n⚠️ *Ini hanya tes, bukan peringatan nyata!* ⚠️", 
        height=120)
    if st.button("Kirim Tes Tsunami Alert"):
        if not SEND_WA_AVAILABLE:
            st.error("notify_whatsapp.py tidak ditemukan / kredensial belum diisi.")
        else:
            try:
                to_arg = tsunami_wa_to_override.strip() or None
                sids = send_whatsapp(tsunami_test_msg, to=to_arg)
                st.success(f"Tes Tsunami Alert terkirim. SID(s): {', '.join(sids)}")
            except Exception as e:
                st.error(f"Gagal kirim Tsunami Alert: {e}")

# ===== Auto-Save Configuration =====
def auto_save_config():
    """Simpan konfigurasi secara otomatis."""
    try:
        current_config = {
            "csv_path": csv_path,
            "sample_every_sec": sample_every_sec,
            "rtsp_url": rtsp_url,
            "resize_width": resize_width,
            "camera_location": camera_location,
            "garis_extreme_y": GARIS_EXTREME_Y,
            "garis_sangat_tinggi_y": GARIS_SANGAT_TINGGI_Y,
            "garis_tinggi_y": GARIS_TINGGI_Y,
            "garis_sedang_y": GARIS_SEDANG_Y,
            "garis_rendah_y": GARIS_RENDAH_Y,
            "line_thickness": line_thickness,
            "peak_thickness": peak_thickness,
            "font_scale": font_scale,
            "font_thickness": font_thickness,
            "enable_wa": enable_wa,
            "wa_cooldown_sec": wa_cooldown_sec,
            "enable_sms": enable_sms,
            "sms_cooldown_sec": sms_cooldown_sec,
            "extreme_threshold": extreme_threshold,
            "alert_cooldown_min": alert_cooldown_min,
            "enable_tsunami_alert": enable_tsunami_alert,
            "wa_to_override": wa_to_override,
            "sms_to_override": sms_to_override,
            "tsunami_wa_to_override": tsunami_wa_to_override
        }
        save_config(current_config)
        return True
    except Exception as e:
        print(f"Error auto-saving config: {e}")
        return False

# ===== Configuration Management =====
st.sidebar.header("⚙️ Konfigurasi")
with st.sidebar.expander("💾 Kelola Konfigurasi", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Simpan Konfigurasi"):
            if auto_save_config():
                st.success("✅ Konfigurasi tersimpan!")
            else:
                st.error("❌ Gagal menyimpan konfigurasi")
    
    with col2:
        if st.button("🔄 Reset ke Default"):
            from dashboard_config import reset_config
            if reset_config():
                st.success("✅ Konfigurasi direset!")
                st.rerun()
            else:
                st.error("❌ Gagal reset konfigurasi")
    
    # Export/Import
    st.subheader("📤 Export/Import")
    if st.button("📤 Export Konfigurasi"):
        from dashboard_config import export_config
        config_json = export_config()
        st.download_button(
            "Download Konfigurasi",
            data=config_json,
            file_name="dashboard_config.json",
            mime="application/json"
        )
    
    uploaded_file = st.file_uploader("📥 Import Konfigurasi", type=['json'])
    if uploaded_file is not None:
        try:
            config_data = uploaded_file.read().decode('utf-8')
            from dashboard_config import import_config
            if import_config(config_data):
                st.success("✅ Konfigurasi diimpor!")
                st.rerun()
            else:
                st.error("❌ Gagal mengimpor konfigurasi")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ===== Tabs =====
TAB_LIVE, TAB_LOG, TAB_EARTHQUAKE = st.tabs(["🎥 Live RTSP + Deteksi + WhatsApp Tsunami Alert", "📈 Log & Grafik / Laporan", "🌍 Monitoring Gempa BMKG"])

# ===== Halaman Monitoring Gempa BMKG =====
with TAB_EARTHQUAKE:
    st.subheader("🌍 Monitoring Gempa BMKG")
    st.caption("Monitoring gempa real-time dari Badan Meteorologi, Klimatologi, dan Geofisika")
    
    # Import modul gempa
    try:
        from earthquake_bmkg import BMKGEarthquakeAPI
        from notify_earthquake import send_earthquake_alert
        BMKG_AVAILABLE = True
    except ImportError as e:
        st.error(f"❌ Modul gempa tidak tersedia: {e}")
        BMKG_AVAILABLE = False
    
    if BMKG_AVAILABLE:
        # ===== Konfigurasi Monitoring Gempa =====
        st.header("⚙️ Konfigurasi Monitoring Gempa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_earthquake_monitoring = st.checkbox(
                "🔍 Enable Monitoring Gempa", 
                value=config.get("enable_earthquake_monitoring", False),
                help="Aktifkan monitoring gempa otomatis"
            )
            
            magnitude_threshold = st.number_input(
                "📊 Threshold Magnitude Alert", 
                min_value=1.0, 
                max_value=10.0, 
                value=config.get("magnitude_threshold", 5.0),
                step=0.1,
                help="Magnitude minimum untuk mengirim alert"
            )
            
            tsunami_threshold = st.number_input(
                "🌊 Threshold Tsunami Alert", 
                min_value=1.0, 
                max_value=10.0, 
                value=config.get("tsunami_threshold", 6.0),
                step=0.1,
                help="Magnitude minimum untuk alert tsunami"
            )
        
        with col2:
            earthquake_check_interval = st.number_input(
                "⏰ Interval Cek Gempa (detik)", 
                min_value=30, 
                max_value=3600, 
                value=config.get("earthquake_check_interval", 300),
                step=30,
                help="Interval untuk mengecek gempa terbaru"
            )
            
            enable_earthquake_wa = st.checkbox(
                "📱 Kirim Alert via WhatsApp", 
                value=config.get("enable_earthquake_wa", True),
                help="Kirim notifikasi gempa via WhatsApp"
            )
            
            enable_earthquake_sms = st.checkbox(
                "📱 Kirim Alert via SMS", 
                value=config.get("enable_earthquake_sms", True),
                help="Kirim notifikasi gempa via SMS"
            )
        
        # ===== Status Monitoring =====
        st.header("📊 Status Monitoring")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if enable_earthquake_monitoring:
                st.success("🟢 Monitoring Aktif")
            else:
                st.warning("🟡 Monitoring Nonaktif")
        
        with col2:
            st.metric("Threshold Alert", f"M{magnitude_threshold}")
        
        with col3:
            st.metric("Threshold Tsunami", f"M{tsunami_threshold}")
        
        # ===== Data Gempa Terbaru =====
        st.header("🌍 Data Gempa Terbaru")
        
        if st.button("🔄 Refresh Data Gempa", type="primary"):
            with st.spinner("Mengambil data gempa terbaru..."):
                try:
                    api = BMKGEarthquakeAPI()
                    earthquake_data = api.get_earthquake_data()
                    
                    if earthquake_data:
                        parsed_data = api.parse_earthquake_data(earthquake_data)
                        
                        # Tampilkan data gempa
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Magnitude", f"M{parsed_data.get('magnitude', 'N/A')}")
                            st.metric("Kedalaman", parsed_data.get('kedalaman', 'N/A'))
                            st.metric("Waktu", parsed_data.get('datetime_str', 'N/A'))
                        
                        with col2:
                            st.metric("Lokasi", parsed_data.get('wilayah', 'N/A'))
                            st.metric("Koordinat", parsed_data.get('coordinates', 'N/A'))
                            st.metric("Potensi Tsunami", parsed_data.get('potensi_tsunami', 'N/A'))
                        
                        # Tampilkan detail lengkap
                        with st.expander("📋 Detail Lengkap Gempa Terbaru", expanded=True):
                            st.json(parsed_data)
                        
                        # Cek alert
                        alert_result = api.check_earthquake_alert(
                            magnitude_threshold=magnitude_threshold,
                            tsunami_threshold=tsunami_threshold
                        )
                        
                        if alert_result['alert']:
                            st.warning(f"⚠️ {alert_result['message']}")
                            
                            # Tombol kirim alert manual
                            if st.button("📤 Kirim Alert Manual"):
                                with st.spinner("Mengirim alert..."):
                                    result = send_earthquake_alert(
                                        parsed_data,
                                        alert_level=alert_result['alert_level'],
                                        enable_whatsapp=enable_earthquake_wa,
                                        enable_sms=enable_earthquake_sms
                                    )
                                    
                                    if result['success']:
                                        st.success("✅ Alert berhasil dikirim!")
                                        if result['whatsapp_sent']:
                                            st.info(f"📱 WhatsApp: {len(result['whatsapp_sids'])} pesan")
                                        if result['sms_sent']:
                                            st.info(f"📱 SMS: {len(result['sms_sids'])} pesan")
                                    else:
                                        st.error("❌ Gagal mengirim alert")
                                        for error in result['errors']:
                                            st.error(f"   - {error}")
                        else:
                            st.info(f"ℹ️ {alert_result['message']}")
                    
                    else:
                        st.error("❌ Gagal mengambil data gempa")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        # ===== Riwayat Gempa =====
        st.header("📈 Riwayat Gempa")
        
        col1, col2 = st.columns(2)
        
        with col1:
            history_hours = st.selectbox(
                "⏰ Periode Riwayat", 
                [6, 12, 24, 48, 72], 
                index=2,
                help="Periode riwayat gempa dalam jam"
            )
        
        with col2:
            if st.button("📊 Tampilkan Riwayat"):
                with st.spinner(f"Mengambil riwayat gempa {history_hours} jam..."):
                    try:
                        api = BMKGEarthquakeAPI()
                        history = api.get_earthquake_history(hours=history_hours)
                        
                        if history:
                            st.success(f"✅ Ditemukan {len(history)} gempa dalam {history_hours} jam terakhir")
                            
                            # Tampilkan tabel riwayat
                            import pandas as pd
                            
                            df_data = []
                            for eq in history:
                                df_data.append({
                                    'Waktu': eq.get('datetime_str', 'N/A'),
                                    'Magnitude': eq.get('magnitude', 'N/A'),
                                    'Kedalaman': eq.get('kedalaman', 'N/A'),
                                    'Lokasi': eq.get('wilayah', 'N/A'),
                                    'Potensi Tsunami': eq.get('potensi_tsunami', 'N/A')
                                })
                            
                            df = pd.DataFrame(df_data)
                            st.dataframe(df, use_container_width=True)
                            
                            # Grafik magnitude
                            if len(history) > 1:
                                st.subheader("📊 Grafik Magnitude vs Waktu")
                                import plotly.express as px
                                
                                fig = px.line(
                                    df, 
                                    x='Waktu', 
                                    y='Magnitude',
                                    title=f'Magnitude Gempa {history_hours} Jam Terakhir',
                                    markers=True
                                )
                                fig.add_hline(y=magnitude_threshold, line_dash="dash", line_color="red", 
                                            annotation_text=f"Threshold Alert (M{magnitude_threshold})")
                                fig.add_hline(y=tsunami_threshold, line_dash="dash", line_color="orange", 
                                            annotation_text=f"Threshold Tsunami (M{tsunami_threshold})")
                                
                                st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info(f"ℹ️ Tidak ada gempa dalam {history_hours} jam terakhir")
                            
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # ===== Test Notifikasi =====
        st.header("🧪 Test Notifikasi Gempa")
        
        with st.expander("📤 Test Kirim Alert Gempa", expanded=False):
            st.caption("Test mengirim notifikasi gempa dengan data dummy")
            
            col1, col2 = st.columns(2)
            
            with col1:
                test_magnitude = st.number_input(
                    "Magnitude Test", 
                    min_value=1.0, 
                    max_value=10.0, 
                    value=6.5,
                    step=0.1
                )
                
                test_location = st.text_input(
                    "Lokasi Test", 
                    value="Laut Banda, Maluku"
                )
            
            with col2:
                test_alert_level = st.selectbox(
                    "Level Alert Test", 
                    ["EARTHQUAKE", "TSUNAMI"]
                )
                
                test_potensi = st.selectbox(
                    "Potensi Tsunami Test", 
                    ["Tidak berpotensi tsunami", "Berpotensi tsunami"]
                )
            
            if st.button("📤 Kirim Test Alert"):
                # Data gempa dummy untuk testing
                dummy_earthquake = {
                    'datetime_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'magnitude': test_magnitude,
                    'kedalaman': '15 km',
                    'wilayah': test_location,
                    'coordinates': '4.5 LS, 129.2 BT',
                    'potensi_tsunami': test_potensi,
                    'dirasakan': 'Dirasakan di wilayah sekitar'
                }
                
                with st.spinner("Mengirim test alert..."):
                    result = send_earthquake_alert(
                        dummy_earthquake,
                        alert_level=test_alert_level,
                        enable_whatsapp=enable_earthquake_wa,
                        enable_sms=enable_earthquake_sms
                    )
                    
                    if result['success']:
                        st.success("✅ Test alert berhasil dikirim!")
                        if result['whatsapp_sent']:
                            st.info(f"📱 WhatsApp: {len(result['whatsapp_sids'])} pesan")
                        if result['sms_sent']:
                            st.info(f"📱 SMS: {len(result['sms_sids'])} pesan")
                    else:
                        st.error("❌ Gagal mengirim test alert")
                        for error in result['errors']:
                            st.error(f"   - {error}")

# ===== Helpers Deteksi =====
def classify_main_style(peak_y: int, L: dict) -> Tuple[str, tuple]:
    status, warna = "Tenang", (144,238,144)
    if peak_y < L['RENDAH']:        status, warna = "0,5 Meter (Rendah)", (0,255,0)
    if peak_y < L['SEDANG']:        status, warna = "1,25 Meter (Sedang)", (0,255,255)
    if peak_y < L['TINGGI']:        status, warna = "2,5 Meter (Tinggi)", (0,165,255)
    if peak_y < L['SANGAT_TINGGI']: status, warna = "4 Meter (SANGAT TINGGI)", (0,0,255)
    if peak_y < L['EXTREME']:       status, warna = "> 4 Meter (EXTREME)", (0,0,139)
    return status, warna

def detect_peak_y_hough(frame_bgr):
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, minLineLength=90, maxLineGap=30)
    h = frame_bgr.shape[0]; peak_y = h
    if lines is not None:
        for l in lines:
            x1,y1,x2,y2 = l[0]
            peak_y = min(peak_y, y1, y2)
            cv2.line(frame_bgr, (x1,y1),(x2,y2),(0,0,255),2)
    return int(peak_y), lines

def draw_overlay(frame, L, peak_y, status, color, extreme_count=0, alert_sent=False):
    h,w = frame.shape[:2]
    cv2.line(frame,(0,L['EXTREME']),(w,L['EXTREME']),(0,0,139),line_thickness)
    cv2.line(frame,(0,L['SANGAT_TINGGI']),(w,L['SANGAT_TINGGI']),(0,0,255),line_thickness)
    cv2.line(frame,(0,L['TINGGI']),(w,L['TINGGI']),(0,165,255),line_thickness)
    cv2.line(frame,(0,L['SEDANG']),(w,L['SEDANG']),(0,255,255),line_thickness)
    cv2.line(frame,(0,L['RENDAH']),(w,L['RENDAH']),(0,255,0),line_thickness)
    cv2.line(frame,(0,peak_y),(w,peak_y),(255,255,255),peak_thickness)
    cv2.putText(frame,f"Peak Y: {peak_y}",(w-180,max(15,peak_y-6)),cv2.FONT_HERSHEY_SIMPLEX,font_scale,(255,255,255),font_thickness)
    
    # Status panel (diperbesar untuk menampung info tambahan)
    x1,y1,x2,y2 = w-300,10,w-10,120
    cv2.rectangle(frame,(x1,y1),(x2,y2),(0,0,0),-1)
    cv2.putText(frame,"STATUS OMBAK:",(x1+10,y1+25),cv2.FONT_HERSHEY_SIMPLEX,font_scale,(255,255,255),font_thickness)
    cv2.putText(frame,status,(x1+10,y1+55),cv2.FONT_HERSHEY_SIMPLEX,font_scale,color,font_thickness)
    
    # Extreme counter
    cv2.putText(frame,f"EXTREME: {extreme_count}/{extreme_threshold}",(x1+10,y1+80),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    
    # Alert status
    if alert_sent:
        cv2.putText(frame,"ALERT SENT!",(x1+10,y1+100),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,0),2)
    
    cv2.putText(frame,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),(10,h-10),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)

# ===== CSV Helpers (diperbarui untuk extreme count) =====
CSV_FIELDS = [
    "timestamp","tanggal","jam","frame",
    "puncak_ombak_y","status_ombak","jumlah_garis_terdeteksi","extreme_count","alert_sent"
]

def ensure_csv_header(path: str):
    if not os.path.exists(path):
        with open(path,"w",newline="",encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

def append_csv(path: str, frame_idx: int, peak_y: int, status: str, num_lines: int, extreme_count: int = 0, alert_sent: bool = False):
    """Tulis baris CSV aman (status bisa mengandung koma)."""
    ensure_csv_header(path)
    ts = datetime.now()
    row = {
        "timestamp": ts.isoformat(),
        "tanggal": ts.strftime("%Y-%m-%d %H:%M:%S"),
        "jam": ts.strftime("%H:%M:%S"),
        "frame": frame_idx,
        "puncak_ombak_y": peak_y,
        "status_ombak": status,
        "jumlah_garis_terdeteksi": num_lines,
        "extreme_count": extreme_count,
        "alert_sent": alert_sent,
    }
    with open(path,"a",newline="",encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)

# ===== Twilio Helper Functions =====
def check_tsunami_alert_condition(extreme_count: int, last_alert_time: float, cooldown_minutes: int) -> bool:
    """Cek apakah perlu mengirim alert tsunami."""
    # Cek apakah sudah mencapai threshold
    if extreme_count < extreme_threshold:
        return False
    
    # Cek cooldown
    if last_alert_time > 0:
        time_diff = time.time() - last_alert_time
        if time_diff < (cooldown_minutes * 60):
            return False
    
    return True

with TAB_LIVE:
    # Auto-save konfigurasi saat ada perubahan
    auto_save_config()
    
    c1,c2,_ = st.columns([1,1,6])
    with c1: start_btn = st.button("▶️ Start")
    with c2: stop_btn  = st.button("⏹ Stop")
    if "running" not in st.session_state: st.session_state.running = False
    if start_btn and rtsp_url: st.session_state.running = True
    if stop_btn: st.session_state.running = False

    frame_holder = st.empty(); info_holder = st.empty()

    # Initialize session state for tracking
    if "last_log" not in st.session_state: st.session_state.last_log = 0.0
    if "last_wa_alert" not in st.session_state: st.session_state.last_wa_alert = 0.0
    if "last_sms_alert" not in st.session_state: st.session_state.last_sms_alert = 0.0
    if "last_twilio_alert" not in st.session_state: st.session_state.last_twilio_alert = 0.0
    if "frame_idx" not in st.session_state: st.session_state.frame_idx = 0
    if "extreme_count" not in st.session_state: st.session_state.extreme_count = 0
    if st.session_state.running and rtsp_url:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;10000000|max_delay;500000|buffer_size;102400"
        os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "quiet"
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            st.error("Gagal membuka stream. Cek URL/kredensial/jaringan."); st.session_state.running = False
        else:
            if resize_width>0: cap.set(cv2.CAP_PROP_FRAME_WIDTH, resize_width)
            info_holder.info("Streaming... Klik Stop untuk berhenti.")
            fail = 0
            while st.session_state.running:
                ok, frame = cap.read()
                if not ok or frame is None:
                    fail += 1
                    if fail >= 30:
                        cap.release(); time.sleep(1)
                        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG); fail = 0
                    continue
                fail = 0; st.session_state.frame_idx += 1
                h,w = frame.shape[:2]
                if resize_width>0 and w != resize_width:
                    ratio = resize_width / float(w)
                    frame = cv2.resize(frame,(resize_width,int(h*ratio)),interpolation=cv2.INTER_AREA)

                L = {'EXTREME':int(GARIS_EXTREME_Y),'SANGAT_TINGGI':int(GARIS_SANGAT_TINGGI_Y),
                     'TINGGI':int(GARIS_TINGGI_Y),'SEDANG':int(GARIS_SEDANG_Y),'RENDAH':int(GARIS_RENDAH_Y)}
                peak_y,_ = detect_peak_y_hough(frame)
                status,color = classify_main_style(peak_y, L)

                # ===== TWILIO TSUNAMI ALERT LOGIC =====
                alert_sent = False
                
                if "EXTREME" in status:
                    st.session_state.extreme_count += 1
                    print(f"🚨 EXTREME #{st.session_state.extreme_count} - Puncak Y: {peak_y}")
                    
                    # Cek apakah perlu kirim tsunami alert
                    if (enable_tsunami_alert and SEND_WA_AVAILABLE and 
                        check_tsunami_alert_condition(st.session_state.extreme_count, st.session_state.last_twilio_alert, alert_cooldown_min)):
                        
                        try:
                            sids = send_tsunami_alert_whatsapp(st.session_state.extreme_count, peak_y, st.session_state.frame_idx, location=camera_location)
                            st.session_state.last_twilio_alert = time.time()
                            alert_sent = True
                            st.sidebar.success(f"🚨 TSUNAMI ALERT DIKIRIM! SID(s): {', '.join(sids)}")
                        except Exception as e:
                            st.sidebar.error(f"Tsunami Alert error: {e}")
                else:
                    # Reset counter jika bukan extreme
                    if st.session_state.extreme_count > 0:
                        print(f"✅ Status kembali normal. Extreme count direset dari {st.session_state.extreme_count}")
                    st.session_state.extreme_count = 0

                draw_overlay(frame,L,peak_y,status,color,st.session_state.extreme_count,alert_sent)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_holder.image(rgb, channels="RGB", width="stretch")

                now = time.time()
                if now - st.session_state.last_log >= sample_every_sec:
                    append_csv(csv_path, st.session_state.frame_idx, peak_y, status, 0, 
                             st.session_state.extreme_count, alert_sent)

                    # ===== WA alert =====
                    if enable_wa and SEND_WA_AVAILABLE and status in ["2,5 Meter (Tinggi)","4 Meter (SANGAT TINGGI)","> 4 Meter (EXTREME)"]:
                        if now - st.session_state.last_wa_alert >= wa_cooldown_sec:
                            try:
                                send_whatsapp(
                                    "⚠️ *PERINGATAN OMBAK TINGGI*\\n\\n"
                                    f"Status: *{status}*\\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\\n"
                                    f"Frame: {st.session_state.frame_idx}\\nPuncak Ombak (Y): {peak_y}\\n"
                                    f"Extreme Count: {st.session_state.extreme_count}"
                                )
                                st.session_state.last_wa_alert = now
                            except Exception as e:
                                st.sidebar.error(f"WA error: {e}")

                    # ===== SMS alert =====
                    if enable_sms and SEND_SMS_AVAILABLE and status in ["2,5 Meter (Tinggi)","4 Meter (SANGAT TINGGI)","> 4 Meter (EXTREME)"]:
                        if now - st.session_state.last_sms_alert >= sms_cooldown_sec:
                            try:
                                msg = (
                                    "PERINGATAN OMBAK TINGGI!\n"
                                    f"Status: {status}\n"
                                    f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                                    f"Frame: {st.session_state.frame_idx}\n"
                                    f"PeakY: {peak_y}\n"
                                    f"Extreme Count: {st.session_state.extreme_count}"
                                )
                                send_sms(msg)
                                st.session_state.last_sms_alert = now
                            except Exception as e:
                                st.sidebar.error(f"SMS error: {e}")

                    st.session_state.last_log = now
                time.sleep(0.005)
            cap.release(); info_holder.success("Stream dihentikan.")
    else:
        st.info("Masukkan RTSP URL di sidebar, lalu klik Start.")


with TAB_LOG:
    import plotly.express as px
    st.subheader("📈 Log & Grafik")

    def load_df(path: str) -> pd.DataFrame:
        if not os.path.exists(path):
            st.warning("File CSV belum ada. Mulai Live deteksi untuk menghasilkan log.")
            return pd.DataFrame()
        try:
            df = pd.read_csv(path)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                df['waktu'] = df['timestamp']
            elif {'tanggal','jam'}.issubset(df.columns):
                df['waktu'] = pd.to_datetime(df['tanggal'].astype(str)+" "+df['jam'].astype(str), errors='coerce')
            else:
                df['waktu'] = pd.NaT
            return df
        except Exception as e:
            st.error(f"Gagal baca CSV: {e}")
            return pd.DataFrame()

    df = load_df(csv_path)
    if not df.empty and 'waktu' in df.columns:
        min_d = df['waktu'].min().date() if pd.notna(df['waktu'].min()) else date.today()
        max_d = df['waktu'].max().date() if pd.notna(df['waktu'].max()) else date.today()

        # ⛑️ Perbaikan: date_input aman baik satu tanggal atau rentang
        _sel = st.date_input("Rentang tanggal", value=(min_d, max_d))
        if isinstance(_sel, (list, tuple)) and len(_sel) == 2:
            d1, d2 = _sel
        else:
            d1 = d2 = _sel

        mask = (df['waktu'] >= pd.to_datetime(d1)) & (df['waktu'] <= pd.to_datetime(d2) + pd.Timedelta(days=1))
        dff = df.loc[mask].copy()
    else:
        dff = df.copy()

    colA, colB, colC, colD, colE = st.columns(5)
    if not dff.empty:
        latest = dff.sort_values('waktu').tail(1).iloc[0]
        colA.metric("Status Terbaru", str(latest.get('status_ombak','—')))
        colB.metric("Frame Terbaru", int(latest.get('frame',0)) if pd.notna(latest.get('frame',None)) else 0)
        colC.metric("Peak Y Terbaru", int(latest.get('puncak_ombak_y',0)) if pd.notna(latest.get('puncak_ombak_y',None)) else 0)
        colD.metric("Extreme Count", int(latest.get('extreme_count',0)) if pd.notna(latest.get('extreme_count',None)) else 0)
        colE.metric("Jumlah Data", len(dff))
    else:
        st.info("Belum ada data untuk ditampilkan.")

    st.divider()
    if not dff.empty:
        if 'waktu' in dff.columns and 'puncak_ombak_y' in dff.columns:
            fig_ts = px.line(dff.sort_values('waktu'), x='waktu', y='puncak_ombak_y', markers=True,
                             title="Pergerakan Puncak Ombak (Y) vs Waktu",
                             labels={'waktu':'Waktu','puncak_ombak_y':'Puncak Ombak (Y)'})
            st.plotly_chart(fig_ts, width="stretch")
        
        # Grafik Extreme Count
        if 'extreme_count' in dff.columns:
            fig_extreme = px.line(dff.sort_values('waktu'), x='waktu', y='extreme_count', markers=True,
                                 title="Extreme Count vs Waktu (Tsunami Alert Tracking)",
                                 labels={'waktu':'Waktu','extreme_count':'Extreme Count'})
            # Tambahkan garis threshold
            fig_extreme.add_hline(y=extreme_threshold, line_dash="dash", line_color="red", 
                                 annotation_text=f"Alert Threshold: {extreme_threshold}")
            st.plotly_chart(fig_extreme, width="stretch")
        
        if 'status_ombak' in dff.columns:
            status_counts = dff['status_ombak'].value_counts().reset_index()
            status_counts.columns = ['status_ombak','jumlah']
            fig_bar = px.bar(status_counts, x='status_ombak', y='jumlah', title="Distribusi Status Ombak",
                             labels={'status_ombak':'Status','jumlah':'Jumlah'})
            st.plotly_chart(fig_bar, width="stretch")

        # Alert History
        if 'alert_sent' in dff.columns:
            alerts = dff[dff['alert_sent'] == True]
            if not alerts.empty:
                st.subheader("🚨 Riwayat Alert Tsunami")
                st.dataframe(alerts[['waktu', 'status_ombak', 'puncak_ombak_y', 'extreme_count']], 
                           width="stretch", height=200)

        st.subheader("Data (terbatas 500 baris)")
        st.dataframe(dff.tail(500), width="stretch", height=420)

        # ========== Laporan (PDF) ==========
        st.subheader("📄 Laporan (PDF)")
        st.caption("Butuh paket `reportlab` (install: `pip install reportlab`).")
        def make_report_bytes(d: pd.DataFrame) -> bytes:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import cm

            buff = io.BytesIO()
            c = canvas.Canvas(buff, pagesize=A4)
            W, H = A4

            def line(y): c.line(1.5*cm, y, W-1.5*cm, y)

            # Header
            c.setFont("Helvetica-Bold", 16)
            c.drawString(2*cm, H-2*cm, "Laporan Deteksi Ombak + Tsunami Alert")
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, H-2.6*cm, f"Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            line(H-2.8*cm)

            # Ringkasan
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, H-3.6*cm, "Ringkasan")
            c.setFont("Helvetica", 10)

            waktu_min = str(d['waktu'].min()) if 'waktu' in d.columns else "-"
            waktu_max = str(d['waktu'].max()) if 'waktu' in d.columns else "-"
            total = len(d)

            y = H-4.2*cm
            c.drawString(2*cm, y, f"Rentang data : {waktu_min}  s/d  {waktu_max}"); y -= 0.6*cm
            c.drawString(2*cm, y, f"Jumlah entri : {total}"); y -= 0.6*cm

            if 'puncak_ombak_y' in d.columns and len(d)>0:
                c.drawString(2*cm, y, f"Peak Y  (min/mean/max) : {int(d['puncak_ombak_y'].min())} / {round(d['puncak_ombak_y'].mean(),1)} / {int(d['puncak_ombak_y'].max())}")
                y -= 0.6*cm

            if 'extreme_count' in d.columns and len(d)>0:
                max_extreme = int(d['extreme_count'].max())
                c.drawString(2*cm, y, f"Maximum Extreme Count : {max_extreme}")
                y -= 0.6*cm

            if 'alert_sent' in d.columns and len(d)>0:
                alert_count = len(d[d['alert_sent'] == True])
                c.drawString(2*cm, y, f"Jumlah Alert Tsunami : {alert_count}")
                y -= 0.6*cm

            if 'status_ombak' in d.columns and len(d)>0:
                c.drawString(2*cm, y, "Distribusi status:"); y -= 0.5*cm
                counts = d['status_ombak'].value_counts()
                for s, n in counts.items():
                    c.drawString(2.5*cm, y, f"- {s}: {n}")
                    y -= 0.5*cm

            # Footer
            line(2*cm)
            c.setFont("Helvetica-Oblique", 9)
            c.drawString(2*cm, 1.5*cm, "Generated by Ombak Dashboard + Tsunami Alert")

            c.showPage(); c.save()
            return buff.getvalue()

        if st.button("📄 Unduh Laporan (PDF)"):
            try:
                pdf_bytes = make_report_bytes(dff)
                st.download_button("Download sekarang", data=pdf_bytes, file_name="laporan_ombak_tsunami_alert.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"Gagal membuat PDF. Pastikan reportlab terpasang. Error: {e}")
    else:
        st.info("Tidak ada data untuk grafik/laporan.")
