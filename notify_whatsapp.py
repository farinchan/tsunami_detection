# notify_whatsapp.py
# Helper kirim WhatsApp via Twilio Sandbox/Business
# Baca kredensial dari .env / environment variables.

import os
from typing import Optional, Iterable

try:
    from dotenv import load_dotenv
    load_dotenv()  # muat .env kalau ada
except Exception:
    pass

from twilio.rest import Client

# Wajib diisi (lihat .env di bawah)
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")

# Nomor pengirim (Twilio WhatsApp). Sandbox default: whatsapp:+14155238886
FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Nomor penerima default (bisa beberapa, pisahkan koma)
# Format WA: 'whatsapp:+62xxxxxxxxxx'
TO_DEFAULT = os.getenv("WHATSAPP_TO", "").strip()

if not ACCOUNT_SID or not AUTH_TOKEN:
    raise RuntimeError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN belum di-set.")

_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def _normalize_targets(to: Optional[str | Iterable[str]]) -> list[str]:
    if to is None or (isinstance(to, str) and not to.strip()):
        to = TO_DEFAULT
    if isinstance(to, str):
        to_list = [t.strip() for t in to.split(",") if t.strip()]
    else:
        to_list = list(to)
    if not to_list:
        raise ValueError("Nomor tujuan kosong. Set WHATSAPP_TO di .env atau kirim argumen to=...")
    # Pastikan sudah berformat 'whatsapp:+62...'
    norm = []
    for t in to_list:
        if not t.startswith("whatsapp:"):
            t = "whatsapp:" + t
        norm.append(t)
    return norm

def send_whatsapp(message: str, to: Optional[str | Iterable[str]] = None, media_url: Optional[str] = None) -> list[str]:
    """
    Kirim pesan WhatsApp ke satu/lebih nomor.
    - message: isi pesan (teks)
    - to: string satu nomor atau comma-separated atau list[str]
    - media_url: opsional; URL gambar/file bila ingin kirim media
    return: list message_sid
    """
    sids = []
    for dest in _normalize_targets(to):
        kwargs = {"from_": FROM, "to": dest, "body": message}
        if media_url:
            kwargs["media_url"] = [media_url]
        msg = _client.messages.create(**kwargs)
        sids.append(msg.sid)
    return sids

def send_tsunami_alert_whatsapp(extreme_count: int, peak_y: int, frame_idx: int, to: Optional[str | Iterable[str]] = None, location: Optional[str] = None) -> list[str]:
    """
    Kirim alert tsunami khusus via WhatsApp.
    
    Args:
        extreme_count (int): Jumlah deteksi EXTREME berturut-turut
        peak_y (int): Posisi Y puncak ombak
        frame_idx (int): Nomor frame
        to (str, optional): Nomor tujuan (format: +62... atau whatsapp:+62...)
        location (str, optional): Lokasi kamera (default: dari .env atau placeholder)
    
    Returns:
        list[str]: List SID dari pesan yang berhasil dikirim
    """
    
    from datetime import datetime
    
    # Tentukan lokasi
    if location:
        location_text = location
    else:
        # Coba ambil dari environment variable
        camera_location = os.getenv("CAMERA_LOCATION", "")
        if camera_location:
            location_text = camera_location
        else:
            location_text = "[LOKASI KAMERA ANDA]"
    
    alert_message = f"""🚨 *PERINGATAN TSUNAMI POTENSIAL!* 🚨

Sistem deteksi ombak telah mendeteksi *{extreme_count} kali berturut-turut* ombak EXTREME (>4 meter).

*Waktu:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Lokasi:* {location_text}
*Status:* > 4 Meter (EXTREME)
*Puncak Ombak Y:* {peak_y}
*Frame:* {frame_idx}

⚠️ *SEGERA EVAKUASI KE TEMPAT TINGGI!* ⚠️
Hubungi pihak berwenang segera!

_Sistem Deteksi Ombak Otomatis - Tsunami Alert_"""
    
    return send_whatsapp(alert_message, to)