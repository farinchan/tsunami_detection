# main.py — Deteksi Ombak + Logging CSV aman (DictWriter, append)
# Perbaikan utama:
# - Tulisan CSV via DictWriter (status mengandung koma tetap 1 kolom)
# - Header dipastikan sekali (ensure_csv_header)
# - Mode append, tidak overwrite tiap tulis
# - Tetap simpan JSON seperti versi Anda (opsional), interval per N frame
# - Loop ulang video saat habis

import datetime
import cv2
import numpy as np
import json
import csv
import os

# ====================================================================
# PENGATURAN - WAJIB DISESUAIKAN DENGAN TAMPILAN KAMERA ANDA
# ====================================================================

# Sumber video: 0 untuk kamera, atau ganti dengan path file video
SUMBER_VIDEO = 'wave2.mp4'   # Ganti dengan 0, 1, atau path file video Anda

# --- Atur Posisi Vertikal (Y) Garis Batas ---
# Koordinat dihitung dari atas (Y=0) ke bawah.
# Sesuaikan angka ini agar garisnya pas di video Anda.
GARIS_EXTREME_Y        = 180   # Garis extreme (merah tua)
GARIS_SANGAT_TINGGI_Y  = 210   # Garis merah
GARIS_TINGGI_Y         = 230   # Garis oranye
GARIS_SEDANG_Y         = 250   # Garis kuning
GARIS_RENDAH_Y         = 280   # Garis hijau

# --- Pengaturan Deteksi ---
AMBANG_BAWAH_CANNY = 50
AMBANG_ATAS_CANNY  = 150
HOUGH_THRESHOLD = 80
HOUGH_MIN_PANJANG_GARIS = 90
HOUGH_MAKS_JARAK_GARIS  = 30

# --- Output Data ---
FILE_JSON_OUTPUT_NAME = "deteksi_ombak.json"
FILE_CSV_OUTPUT_NAME  = "deteksi_ombak.csv"

# Simpan tiap n frame (untuk kurangi ukuran file)
SIMPAN_SETIAP_N_FRAME = 30

# ====================================================================
# Utilitas CSV aman (DictWriter + append)
# ====================================================================

CSV_FIELDS = [
    "timestamp", "tanggal", "jam", "frame",
    "puncak_ombak_y", "status_ombak", "jumlah_garis_terdeteksi"
]

def ensure_csv_header(path: str):
    """Pastikan file CSV ada dan memiliki header sekali saja."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

def append_csv(path: str, frame_idx: int, peak_y: int, status: str, num_lines: int):
    """Tambahkan satu baris ke CSV (status mengandung koma tetap aman)."""
    ensure_csv_header(path)
    now = datetime.datetime.now()
    row = {
        "timestamp": now.isoformat(),
        "tanggal":  now.strftime("%Y-%m-%d"),
        "jam":      now.strftime("%H:%M:%S"),
        "frame":    int(frame_idx),
        "puncak_ombak_y": int(peak_y),
        "status_ombak":   status,
        "jumlah_garis_terdeteksi": int(num_lines),
    }
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)

# ====================================================================

def jalankan_analisis_visual():
    """Fungsi utama untuk deteksi ombak berbasis garis visual."""
    kamera = cv2.VideoCapture(SUMBER_VIDEO)
    if not kamera.isOpened():
        print(f"Error: Gagal membuka sumber video '{SUMBER_VIDEO}'.")
        return

    print("Analisis Visual Dimulai... Tekan 'q' untuk keluar.")

    # Inisialisasi data untuk JSON (opsional)
    data_deteksi_json = []
    frame_count = 0

    # Pastikan header CSV ada sejak awal
    ensure_csv_header(FILE_CSV_OUTPUT_NAME)

    while True:
        ret, frame = kamera.read()

        # --- LOGIKA UNTUK MENGULANG VIDEO ---
        if not ret:
            print("Video selesai. Mengulang dari awal...")
            kamera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame_count += 1
        frame_height, frame_width = frame.shape[:2]

        # ==========================
        # 1) Deteksi garis/puncak
        # ==========================
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        tepi = cv2.Canny(blur, AMBANG_BAWAH_CANNY, AMBANG_ATAS_CANNY)
        garis = cv2.HoughLinesP(
            tepi, 1, np.pi / 180, HOUGH_THRESHOLD,
            minLineLength=HOUGH_MIN_PANJANG_GARIS,
            maxLineGap=HOUGH_MAKS_JARAK_GARIS
        )

        # Puncak ombak = Y terkecil dari semua garis
        puncak_ombak_y = frame_height
        if garis is not None:
            for line in garis:
                x1, y1, x2, y2 = line[0]
                puncak_ombak_y = min(puncak_ombak_y, y1, y2)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # ==========================
        # 2) Klasifikasi status
        # ==========================
        status = "Tenang"
        warna_status = (255, 255, 255)  # Putih

        if puncak_ombak_y < GARIS_RENDAH_Y:
            status, warna_status = "0,5 Meter (Rendah)", (0, 255, 0)
        if puncak_ombak_y < GARIS_SEDANG_Y:
            status, warna_status = "1,25 Meter (Sedang)", (0, 255, 255)
        if puncak_ombak_y < GARIS_TINGGI_Y:
            status, warna_status = "2,5 Meter (Tinggi)", (0, 165, 255)
        if puncak_ombak_y < GARIS_SANGAT_TINGGI_Y:
            status, warna_status = "4 Meter (SANGAT TINGGI)", (0, 0, 255)
        if puncak_ombak_y < GARIS_EXTREME_Y:
            status, warna_status = "> 4 Meter (EXTREME)", (0, 0, 139)

        # ==========================
        # 3) Overlay info ke frame
        # ==========================
        # Panel status
        cv2.rectangle(frame, (frame_width - 300, 10), (frame_width - 10, 80), (0, 0, 0), -1)
        cv2.putText(frame, "STATUS OMBAK:", (frame_width - 290, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, status, (frame_width - 290, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, warna_status, 2)

        # Timestamp on-frame
        waktu_sekarang = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, waktu_sekarang, (10, frame_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Garis acuan
        cv2.line(frame, (0, GARIS_EXTREME_Y),       (frame_width, GARIS_EXTREME_Y),       (0, 0, 139), 1)
        cv2.line(frame, (0, GARIS_SANGAT_TINGGI_Y), (frame_width, GARIS_SANGAT_TINGGI_Y), (0, 0, 255), 1)
        cv2.line(frame, (0, GARIS_TINGGI_Y),        (frame_width, GARIS_TINGGI_Y),        (0, 165, 255), 1)
        cv2.line(frame, (0, GARIS_SEDANG_Y),        (frame_width, GARIS_SEDANG_Y),        (0, 255, 255), 1)
        cv2.line(frame, (0, GARIS_RENDAH_Y),        (frame_width, GARIS_RENDAH_Y),        (0, 255, 0), 1)

        # ==========================
        # 4) Simpan data (JSON & CSV)
        # ==========================
        if frame_count % SIMPAN_SETIAP_N_FRAME == 0:
            # JSON (opsional, menulis keseluruhan list)
            data_point = {
                "timestamp": datetime.datetime.now().isoformat(),
                "tanggal":   datetime.datetime.now().strftime("%Y-%m-%d"),
                "jam":       datetime.datetime.now().strftime("%H:%M:%S"),
                "frame":     frame_count,
                "puncak_ombak_y": int(puncak_ombak_y),
                "status_ombak":   status,
                "jumlah_garis_terdeteksi": len(garis) if garis is not None else 0,
            }
            data_deteksi_json.append(data_point)
            try:
                with open(FILE_JSON_OUTPUT_NAME, 'w', encoding='utf-8') as json_file:
                    json.dump(data_deteksi_json, json_file, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"[WARN] Gagal menulis JSON: {e}")

            # CSV (append aman)
            try:
                append_csv(
                    FILE_CSV_OUTPUT_NAME,
                    frame_idx=frame_count,
                    peak_y=int(puncak_ombak_y),
                    status=status,
                    num_lines=(len(garis) if garis is not None else 0),
                )
            except Exception as e:
                print(f"[WARN] Gagal menulis CSV: {e}")

        # ==========================
        # 5) Tampilkan jendela
        # ==========================
        cv2.imshow('Deteksi Ombak Visual', frame)
        cv2.imshow('Canny Edge Detection', tepi)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()
    print("Program dihentikan.")

if __name__ == '__main__':
    jalankan_analisis_visual()
