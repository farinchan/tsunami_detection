
# notify_sms.py
# Helper kirim SMS via Twilio.
# - Prefer "TWILIO_MESSAGING_SERVICE_SID" jika tersedia.
# - Fallback ke "TWILIO_SMS_FROM" (nomor Twilio berformat E.164, contoh: +12025550123).
# - Trial: hanya bisa ke nomor yang terverifikasi di Twilio.
import os
from typing import Optional, Iterable

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from twilio.rest import Client

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")

MSID = os.getenv("TWILIO_MESSAGING_SERVICE_SID")  # disarankan untuk produksi
SMS_FROM = os.getenv("TWILIO_SMS_FROM")           # fallback: nomor Twilio (E.164, mis. +1415...)

if not ACCOUNT_SID or not AUTH_TOKEN:
    raise RuntimeError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN belum di-set.")

_client = Client(ACCOUNT_SID, AUTH_TOKEN)

def _normalize_targets(to: Optional[str | Iterable[str]]) -> list[str]:
    if to is None:
        # coba dari env
        env_to = os.getenv("SMS_TO", "").strip()
        to = env_to
    if isinstance(to, str):
        to_list = [t.strip() for t in to.split(",") if t.strip()]
    else:
        to_list = list(to or [])
    if not to_list:
        raise ValueError("Nomor tujuan kosong. Set SMS_TO di .env atau beri argumen to=... (komaseparated/list).")
    # harus E.164: +62...
    return to_list

def send_sms(message: str, to: Optional[str | Iterable[str]] = None) -> list[str]:
    """
    Kirim SMS ke satu/lebih nomor (E.164, contoh +62812xxxxxx).
    Return: list message_sid
    """
    if not (MSID or SMS_FROM):
        raise RuntimeError("Setidaknya TWILIO_MESSAGING_SERVICE_SID atau TWILIO_SMS_FROM harus di-set di .env")
    sids = []
    for dest in _normalize_targets(to):
        if MSID:
            msg = _client.messages.create(
                messaging_service_sid=MSID,
                to=dest,
                body=message
            )
        else:
            msg = _client.messages.create(
                from_=SMS_FROM,
                to=dest,
                body=message
            )
        sids.append(msg.sid)
    return sids
