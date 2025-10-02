# app.py - Web Application untuk Deteksi Ombak
import datetime
import cv2
import numpy as np
import json
import csv
import os
import threading
import time
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# ====================================================================
# GLOBAL VARIABLES
# ====================================================================
class DeteksiOmbakConfig:
    def __init__(self):
        self.SUMBER_VIDEO = 'https://ijsot.org/example/wave.mp4'  # Default RTSP URL
        self.GARIS_EXTREME_Y = 180
        self.GARIS_SANGAT_TINGGI_Y = 210
        self.GARIS_TINGGI_Y = 230
        self.GARIS_SEDANG_Y = 250
        self.GARIS_RENDAH_Y = 280
        self.AMBANG_BAWAH_CANNY = 50
        self.AMBANG_ATAS_CANNY = 150
        self.HOUGH_THRESHOLD = 80
        self.HOUGH_MIN_PANJANG_GARIS = 90
        self.HOUGH_MAKS_JARAK_GARIS = 30
        self.SIMPAN_SETIAP_N_FRAME = 30
        self.FILE_JSON_OUTPUT_NAME = "deteksi_ombak.json"
        self.FILE_CSV_OUTPUT_NAME = "deteksi_ombak.csv"
        self.is_running = False
        self.is_connected = False

# Instance konfigurasi global
config = DeteksiOmbakConfig()

# Status dan data global
current_status = {
    'status_ombak': 'Tenang',
    'puncak_ombak_y': 0,
    'jumlah_garis': 0,
    'timestamp': '',
    'frame_count': 0,
    'is_recording': False
}

# Threading untuk OpenCV
detection_thread = None
camera = None

# ====================================================================
# CSV UTILITIES
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
    """Tambahkan satu baris ke CSV."""
    ensure_csv_header(path)
    now = datetime.datetime.now()
    row = {
        "timestamp": now.isoformat(),
        "tanggal": now.strftime("%Y-%m-%d"),
        "jam": now.strftime("%H:%M:%S"),
        "frame": int(frame_idx),
        "puncak_ombak_y": int(peak_y),
        "status_ombak": status,
        "jumlah_garis_terdeteksi": int(num_lines),
    }
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)

# ====================================================================
# OPENCV DETECTION FUNCTIONS
# ====================================================================
def detect_waves():
    """Fungsi deteksi ombak yang berjalan di background thread."""
    global camera, current_status, config
    
    camera = cv2.VideoCapture(config.SUMBER_VIDEO)
    if not camera.isOpened():
        print(f"Error: Gagal membuka sumber video '{config.SUMBER_VIDEO}'.")
        config.is_connected = False
        socketio.emit('connection_status', {'connected': False})
        return

    config.is_connected = True
    socketio.emit('connection_status', {'connected': True})
    
    print("Analisis Visual Dimulai...")
    data_deteksi_json = []
    frame_count = 0
    ensure_csv_header(config.FILE_CSV_OUTPUT_NAME)

    while config.is_running:
        ret, frame = camera.read()

        if not ret:
            print("Video selesai atau koneksi terputus. Mencoba reconnect...")
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            time.sleep(1)
            continue

        frame_count += 1
        frame_height, frame_width = frame.shape[:2]

        # Deteksi garis/puncak
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        tepi = cv2.Canny(blur, config.AMBANG_BAWAH_CANNY, config.AMBANG_ATAS_CANNY)
        garis = cv2.HoughLinesP(
            tepi, 1, np.pi / 180, config.HOUGH_THRESHOLD,
            minLineLength=config.HOUGH_MIN_PANJANG_GARIS,
            maxLineGap=config.HOUGH_MAKS_JARAK_GARIS
        )

        # Puncak ombak
        puncak_ombak_y = frame_height
        if garis is not None:
            for line in garis:
                x1, y1, x2, y2 = line[0]
                puncak_ombak_y = min(puncak_ombak_y, y1, y2)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Klasifikasi status
        status = "Tenang"
        if puncak_ombak_y < config.GARIS_RENDAH_Y:
            status = "0,5 Meter (Rendah)"
        if puncak_ombak_y < config.GARIS_SEDANG_Y:
            status = "1,25 Meter (Sedang)"
        if puncak_ombak_y < config.GARIS_TINGGI_Y:
            status = "2,5 Meter (Tinggi)"
        if puncak_ombak_y < config.GARIS_SANGAT_TINGGI_Y:
            status = "4 Meter (SANGAT TINGGI)"
        if puncak_ombak_y < config.GARIS_EXTREME_Y:
            status = "> 4 Meter (EXTREME)"

        # Update status global
        current_status.update({
            'status_ombak': status,
            'puncak_ombak_y': int(puncak_ombak_y),
            'jumlah_garis': len(garis) if garis is not None else 0,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'frame_count': frame_count,
            'is_recording': True
        })

        # Emit data ke web client
        socketio.emit('wave_data', current_status)

        # Simpan data
        if frame_count % config.SIMPAN_SETIAP_N_FRAME == 0:
            # JSON
            data_point = {
                "timestamp": datetime.datetime.now().isoformat(),
                "tanggal": datetime.datetime.now().strftime("%Y-%m-%d"),
                "jam": datetime.datetime.now().strftime("%H:%M:%S"),
                "frame": frame_count,
                "puncak_ombak_y": int(puncak_ombak_y),
                "status_ombak": status,
                "jumlah_garis_terdeteksi": len(garis) if garis is not None else 0,
            }
            data_deteksi_json.append(data_point)
            
            try:
                with open(config.FILE_JSON_OUTPUT_NAME, 'w', encoding='utf-8') as json_file:
                    json.dump(data_deteksi_json, json_file, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"[WARN] Gagal menulis JSON: {e}")

            # CSV
            try:
                append_csv(
                    config.FILE_CSV_OUTPUT_NAME,
                    frame_idx=frame_count,
                    peak_y=int(puncak_ombak_y),
                    status=status,
                    num_lines=(len(garis) if garis is not None else 0),
                )
            except Exception as e:
                print(f"[WARN] Gagal menulis CSV: {e}")

        # Encode frame untuk streaming (opsional)
        if frame_count % 5 == 0:  # Stream setiap 5 frame untuk performa
            # Tambahkan overlay untuk streaming
            frame_with_overlay = frame.copy()
            
            # Garis acuan
            cv2.line(frame_with_overlay, (0, config.GARIS_EXTREME_Y), (frame_width, config.GARIS_EXTREME_Y), (0, 0, 139), 2)
            cv2.line(frame_with_overlay, (0, config.GARIS_SANGAT_TINGGI_Y), (frame_width, config.GARIS_SANGAT_TINGGI_Y), (0, 0, 255), 2)
            cv2.line(frame_with_overlay, (0, config.GARIS_TINGGI_Y), (frame_width, config.GARIS_TINGGI_Y), (0, 165, 255), 2)
            cv2.line(frame_with_overlay, (0, config.GARIS_SEDANG_Y), (frame_width, config.GARIS_SEDANG_Y), (0, 255, 255), 2)
            cv2.line(frame_with_overlay, (0, config.GARIS_RENDAH_Y), (frame_width, config.GARIS_RENDAH_Y), (0, 255, 0), 2)
            
            # Status overlay
            cv2.rectangle(frame_with_overlay, (10, 10), (300, 80), (0, 0, 0), -1)
            cv2.putText(frame_with_overlay, f"Status: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame_with_overlay, f"Y: {puncak_ombak_y} | Lines: {len(garis) if garis is not None else 0}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            ret, buffer = cv2.imencode('.jpg', frame_with_overlay)
            if ret:
                frame_encoded = base64.b64encode(buffer).decode('utf-8')
                socketio.emit('video_frame', {'frame': frame_encoded})

        time.sleep(0.033)  # ~30 FPS

    camera.release()
    print("Deteksi dihentikan.")

def start_detection():
    """Mulai thread deteksi."""
    global detection_thread, config
    if not config.is_running:
        config.is_running = True
        detection_thread = threading.Thread(target=detect_waves)
        detection_thread.daemon = True
        detection_thread.start()

def stop_detection():
    """Hentikan thread deteksi."""
    global config, camera
    config.is_running = False
    if camera:
        camera.release()

# ====================================================================
# FLASK ROUTES
# ====================================================================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Dapatkan konfigurasi saat ini."""
    return jsonify({
        'SUMBER_VIDEO': config.SUMBER_VIDEO,
        'GARIS_EXTREME_Y': config.GARIS_EXTREME_Y,
        'GARIS_SANGAT_TINGGI_Y': config.GARIS_SANGAT_TINGGI_Y,
        'GARIS_TINGGI_Y': config.GARIS_TINGGI_Y,
        'GARIS_SEDANG_Y': config.GARIS_SEDANG_Y,
        'GARIS_RENDAH_Y': config.GARIS_RENDAH_Y,
        'AMBANG_BAWAH_CANNY': config.AMBANG_BAWAH_CANNY,
        'AMBANG_ATAS_CANNY': config.AMBANG_ATAS_CANNY,
        'HOUGH_THRESHOLD': config.HOUGH_THRESHOLD,
        'HOUGH_MIN_PANJANG_GARIS': config.HOUGH_MIN_PANJANG_GARIS,
        'HOUGH_MAKS_JARAK_GARIS': config.HOUGH_MAKS_JARAK_GARIS,
        'SIMPAN_SETIAP_N_FRAME': config.SIMPAN_SETIAP_N_FRAME,
        'is_running': config.is_running,
        'is_connected': config.is_connected
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update konfigurasi."""
    data = request.json
    
    # Update konfigurasi
    config.SUMBER_VIDEO = data.get('SUMBER_VIDEO', config.SUMBER_VIDEO)
    config.GARIS_EXTREME_Y = int(data.get('GARIS_EXTREME_Y', config.GARIS_EXTREME_Y))
    config.GARIS_SANGAT_TINGGI_Y = int(data.get('GARIS_SANGAT_TINGGI_Y', config.GARIS_SANGAT_TINGGI_Y))
    config.GARIS_TINGGI_Y = int(data.get('GARIS_TINGGI_Y', config.GARIS_TINGGI_Y))
    config.GARIS_SEDANG_Y = int(data.get('GARIS_SEDANG_Y', config.GARIS_SEDANG_Y))
    config.GARIS_RENDAH_Y = int(data.get('GARIS_RENDAH_Y', config.GARIS_RENDAH_Y))
    config.AMBANG_BAWAH_CANNY = int(data.get('AMBANG_BAWAH_CANNY', config.AMBANG_BAWAH_CANNY))
    config.AMBANG_ATAS_CANNY = int(data.get('AMBANG_ATAS_CANNY', config.AMBANG_ATAS_CANNY))
    config.HOUGH_THRESHOLD = int(data.get('HOUGH_THRESHOLD', config.HOUGH_THRESHOLD))
    config.HOUGH_MIN_PANJANG_GARIS = int(data.get('HOUGH_MIN_PANJANG_GARIS', config.HOUGH_MIN_PANJANG_GARIS))
    config.HOUGH_MAKS_JARAK_GARIS = int(data.get('HOUGH_MAKS_JARAK_GARIS', config.HOUGH_MAKS_JARAK_GARIS))
    config.SIMPAN_SETIAP_N_FRAME = int(data.get('SIMPAN_SETIAP_N_FRAME', config.SIMPAN_SETIAP_N_FRAME))
    
    return jsonify({'status': 'success', 'message': 'Konfigurasi berhasil diupdate'})

@app.route('/api/start', methods=['POST'])
def start_monitoring():
    """Mulai monitoring."""
    start_detection()
    return jsonify({'status': 'success', 'message': 'Monitoring dimulai'})

@app.route('/api/stop', methods=['POST'])
def stop_monitoring():
    """Hentikan monitoring."""
    stop_detection()
    return jsonify({'status': 'success', 'message': 'Monitoring dihentikan'})

@app.route('/api/status')
def get_status():
    """Dapatkan status saat ini."""
    return jsonify(current_status)

@app.route('/api/data/latest')
def get_latest_data():
    """Dapatkan data terbaru dari JSON."""
    try:
        if os.path.exists(config.FILE_JSON_OUTPUT_NAME):
            with open(config.FILE_JSON_OUTPUT_NAME, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data[-10:] if len(data) > 10 else data)  # 10 data terakhir
    except Exception as e:
        print(f"Error reading JSON: {e}")
    return jsonify([])

# ====================================================================
# SOCKETIO EVENTS
# ====================================================================
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_status', {'connected': config.is_connected})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# ====================================================================
# MAIN
# ====================================================================
if __name__ == '__main__':
    print("Starting Wave Detection Web Application...")
    print("Akses web di: http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)