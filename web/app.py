from flask import Flask, render_template, request, jsonify, send_file, Response
import cv2
import numpy as np
import pandas as pd
import csv
import os
import time
import json
from datetime import datetime, date
from typing import Tuple
import io
import threading
import queue

# Import modules
try:
    from notify_whatsapp import send_whatsapp, send_tsunami_alert_whatsapp
    SEND_WA_AVAILABLE = True
except ImportError:
    SEND_WA_AVAILABLE = False

try:
    from notify_sms import send_sms
    SEND_SMS_AVAILABLE = True
except ImportError:
    SEND_SMS_AVAILABLE = False

try:
    from earthquake_bmkg import BMKGEarthquakeAPI
    from notify_earthquake import send_earthquake_alert
    BMKG_AVAILABLE = True
except ImportError:
    BMKG_AVAILABLE = False

try:
    import sys
    sys.path.append('..')
    from dashboard_config import load_config, save_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global variables
streaming_active = False
video_capture = None
config_data = {}
extreme_count = 0
last_alert_time = 0
frame_queue = queue.Queue(maxsize=5)

# CSV Fields
CSV_FIELDS = [
    "timestamp","tanggal","jam","frame",
    "puncak_ombak_y","status_ombak","jumlah_garis_terdeteksi","extreme_count","alert_sent"
]

def load_app_config():
    """Load configuration data"""
    global config_data
    if CONFIG_AVAILABLE:
        config_data = load_config()
    else:
        config_data = {
            "csv_path": "deteksi_ombak.csv",
            "sample_every_sec": 2,
            "rtsp_url": "",
            "resize_width": 960,
            "camera_location": "",
            "garis_extreme_y": 180,
            "garis_sangat_tinggi_y": 210,
            "garis_tinggi_y": 230,
            "garis_sedang_y": 250,
            "garis_rendah_y": 280,
            "line_thickness": 1,
            "peak_thickness": 2,
            "font_scale": 0.7,
            "font_thickness": 2,
            "enable_wa": False,
            "wa_cooldown_sec": 300,
            "enable_sms": False,
            "sms_cooldown_sec": 300,
            "extreme_threshold": 12,
            "alert_cooldown_min": 30,
            "enable_tsunami_alert": False,
            "enable_earthquake_monitoring": False,
            "magnitude_threshold": 5.0,
            "tsunami_threshold": 6.0,
            "earthquake_check_interval": 300
        }

def classify_wave_status(peak_y: int, thresholds: dict) -> Tuple[str, str]:
    """Classify wave status based on peak Y position"""
    status, color_class = "Tenang", "success"
    
    if peak_y < thresholds['RENDAH']:
        status, color_class = "0,5 Meter (Rendah)", "success"
    if peak_y < thresholds['SEDANG']:
        status, color_class = "1,25 Meter (Sedang)", "info"
    if peak_y < thresholds['TINGGI']:
        status, color_class = "2,5 Meter (Tinggi)", "warning"
    if peak_y < thresholds['SANGAT_TINGGI']:
        status, color_class = "4 Meter (SANGAT TINGGI)", "danger"
    if peak_y < thresholds['EXTREME']:
        status, color_class = "> 4 Meter (EXTREME)", "dark"
    
    return status, color_class

def detect_peak_y_hough(frame_bgr):
    """Detect wave peak using Hough line detection"""
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 0)
    edges = cv2.Canny(blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, minLineLength=90, maxLineGap=30)
    
    h = frame_bgr.shape[0]
    peak_y = h
    
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            peak_y = min(peak_y, y1, y2)
            cv2.line(frame_bgr, (x1,y1), (x2,y2), (0,0,255), 2)
    
    return int(peak_y), lines

def draw_overlay(frame, thresholds, peak_y, status, extreme_count=0, alert_sent=False):
    """Draw overlay on frame with detection results"""
    h, w = frame.shape[:2]
    
    # Draw threshold lines
    cv2.line(frame, (0, thresholds['EXTREME']), (w, thresholds['EXTREME']), (0,0,139), config_data.get('line_thickness', 1))
    cv2.line(frame, (0, thresholds['SANGAT_TINGGI']), (w, thresholds['SANGAT_TINGGI']), (0,0,255), config_data.get('line_thickness', 1))
    cv2.line(frame, (0, thresholds['TINGGI']), (w, thresholds['TINGGI']), (0,165,255), config_data.get('line_thickness', 1))
    cv2.line(frame, (0, thresholds['SEDANG']), (w, thresholds['SEDANG']), (0,255,255), config_data.get('line_thickness', 1))
    cv2.line(frame, (0, thresholds['RENDAH']), (w, thresholds['RENDAH']), (0,255,0), config_data.get('line_thickness', 1))
    
    # Draw peak line
    cv2.line(frame, (0, peak_y), (w, peak_y), (255,255,255), config_data.get('peak_thickness', 2))
    
    # Add text overlay
    font_scale = config_data.get('font_scale', 0.7)
    font_thickness = config_data.get('font_thickness', 2)
    
    cv2.putText(frame, f"Peak Y: {peak_y}", (w-180, max(15, peak_y-6)), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255,255,255), font_thickness)
    
    # Status panel
    x1, y1, x2, y2 = w-300, 10, w-10, 120
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,0), -1)
    cv2.putText(frame, "STATUS OMBAK:", (x1+10, y1+25), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255,255,255), font_thickness)
    cv2.putText(frame, status, (x1+10, y1+55), 
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255,255,255), font_thickness)
    cv2.putText(frame, f"EXTREME: {extreme_count}/{config_data.get('extreme_threshold', 12)}", 
                (x1+10, y1+80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    
    if alert_sent:
        cv2.putText(frame, "ALERT SENT!", (x1+10, y1+100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
    
    # Timestamp
    cv2.putText(frame, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

def ensure_csv_header(path: str):
    """Ensure CSV file has proper header"""
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()

def append_csv_data(path: str, frame_idx: int, peak_y: int, status: str, num_lines: int, extreme_count: int = 0, alert_sent: bool = False):
    """Append data to CSV file"""
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
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)

def generate_video_feed():
    """Generate video feed for streaming"""
    global streaming_active, video_capture, extreme_count, last_alert_time
    
    while streaming_active and video_capture and video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break
            
        # Resize frame if needed
        resize_width = config_data.get('resize_width', 960)
        if resize_width > 0:
            h, w = frame.shape[:2]
            if w != resize_width:
                ratio = resize_width / float(w)
                frame = cv2.resize(frame, (resize_width, int(h * ratio)), interpolation=cv2.INTER_AREA)
        
        # Create thresholds dictionary
        thresholds = {
            'EXTREME': config_data.get('garis_extreme_y', 180),
            'SANGAT_TINGGI': config_data.get('garis_sangat_tinggi_y', 210),
            'TINGGI': config_data.get('garis_tinggi_y', 230),
            'SEDANG': config_data.get('garis_sedang_y', 250),
            'RENDAH': config_data.get('garis_rendah_y', 280)
        }
        
        # Detect wave peak
        peak_y, lines = detect_peak_y_hough(frame)
        status, color_class = classify_wave_status(peak_y, thresholds)
        
        # Handle extreme count and tsunami alert
        alert_sent = False
        if "EXTREME" in status:
            extreme_count += 1
            
            # Check tsunami alert condition
            if (config_data.get('enable_tsunami_alert', False) and 
                extreme_count >= config_data.get('extreme_threshold', 12) and
                time.time() - last_alert_time > config_data.get('alert_cooldown_min', 30) * 60):
                
                if SEND_WA_AVAILABLE:
                    try:
                        # Send tsunami alert
                        alert_msg = f"🚨 PERINGATAN TSUNAMI! 🚨\n\nTerdeteksi {extreme_count} kali EXTREME berturut-turut!\n\nLokasi: {config_data.get('camera_location', 'Tidak diketahui')}\nWaktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n⚠️ SEGERA EVAKUASI KE TEMPAT TINGGI! ⚠️"
                        send_whatsapp(alert_msg)
                        alert_sent = True
                        last_alert_time = time.time()
                        extreme_count = 0  # Reset after alert
                    except Exception as e:
                        print(f"Error sending tsunami alert: {e}")
        else:
            extreme_count = 0
        
        # Draw overlay
        draw_overlay(frame, thresholds, peak_y, status, extreme_count, alert_sent)
        
        # Save to CSV periodically
        append_csv_data(config_data.get('csv_path', 'deteksi_ombak.csv'), 
                       0, peak_y, status, len(lines) if lines is not None else 0, 
                       extreme_count, alert_sent)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        
        # Add to queue for web streaming
        if not frame_queue.full():
            try:
                frame_queue.put_nowait(frame_bytes)
            except queue.Full:
                pass
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.1)  # Control frame rate

@app.route('/')
def index():
    """Main dashboard page"""
    load_app_config()
    return render_template('index.html', 
                         config=config_data,
                         wa_available=SEND_WA_AVAILABLE,
                         sms_available=SEND_SMS_AVAILABLE,
                         bmkg_available=BMKG_AVAILABLE)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    """Start video streaming"""
    global streaming_active, video_capture
    
    rtsp_url = request.json.get('rtsp_url', '')
    if not rtsp_url:
        return jsonify({'success': False, 'message': 'RTSP URL diperlukan'})
    
    try:
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;10000000|max_delay;500000|buffer_size;102400"
        os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "quiet"
        
        video_capture = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        
        if not video_capture.isOpened():
            return jsonify({'success': False, 'message': 'Gagal membuka stream RTSP'})
        
        streaming_active = True
        return jsonify({'success': True, 'message': 'Stream dimulai'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    """Stop video streaming"""
    global streaming_active, video_capture
    
    streaming_active = False
    if video_capture:
        video_capture.release()
        video_capture = None
    
    return jsonify({'success': True, 'message': 'Stream dihentikan'})

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_video_feed(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update_config', methods=['POST'])
def update_config():
    """Update configuration"""
    global config_data
    
    try:
        new_config = request.json
        config_data.update(new_config)
        
        if CONFIG_AVAILABLE:
            save_config(config_data)
        
        return jsonify({'success': True, 'message': 'Konfigurasi diperbarui'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/send_test_wa', methods=['POST'])
def send_test_wa():
    """Send test WhatsApp message"""
    if not SEND_WA_AVAILABLE:
        return jsonify({'success': False, 'message': 'WhatsApp tidak tersedia'})
    
    try:
        message = request.json.get('message', 'Test WhatsApp dari dashboard')
        to_number = request.json.get('to', None)
        
        sid = send_whatsapp(message, to=to_number)
        return jsonify({'success': True, 'message': f'WhatsApp terkirim. SID: {sid}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/send_test_sms', methods=['POST'])
def send_test_sms():
    """Send test SMS message"""
    if not SEND_SMS_AVAILABLE:
        return jsonify({'success': False, 'message': 'SMS tidak tersedia'})
    
    try:
        message = request.json.get('message', 'Test SMS dari dashboard')
        to_number = request.json.get('to', None)
        
        sids = send_sms(message, to=to_number)
        return jsonify({'success': True, 'message': f'SMS terkirim. SID(s): {", ".join(sids)}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_wave_data')
def get_wave_data():
    """Get wave detection data"""
    try:
        csv_path = config_data.get('csv_path', 'deteksi_ombak.csv')
        if not os.path.exists(csv_path):
            return jsonify({'data': [], 'total': 0})
        
        df = pd.read_csv(csv_path)
        
        # Get latest 100 records
        df_latest = df.tail(100)
        
        data = []
        for _, row in df_latest.iterrows():
            data.append({
                'timestamp': row.get('timestamp', ''),
                'peak_y': row.get('puncak_ombak_y', 0),
                'status': row.get('status_ombak', ''),
                'extreme_count': row.get('extreme_count', 0),
                'alert_sent': row.get('alert_sent', False)
            })
        
        return jsonify({'data': data, 'total': len(df)})
    
    except Exception as e:
        return jsonify({'data': [], 'total': 0, 'error': str(e)})

@app.route('/get_earthquake_data')
def get_earthquake_data():
    """Get earthquake data from BMKG"""
    if not BMKG_AVAILABLE:
        return jsonify({'success': False, 'message': 'BMKG API tidak tersedia'})
    
    try:
        api = BMKGEarthquakeAPI()
        earthquake_data = api.get_earthquake_data()
        
        if earthquake_data:
            return jsonify({'success': True, 'data': earthquake_data})
        else:
            return jsonify({'success': False, 'message': 'Tidak ada data gempa'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/send_test_tsunami_alert', methods=['POST'])
def send_test_tsunami_alert():
    """Send test tsunami alert"""
    if not SEND_WA_AVAILABLE:
        return jsonify({'success': False, 'message': 'WhatsApp tidak tersedia'})
    
    try:
        message = request.json.get('message', '🚨 TES ALERT TSUNAMI! 🚨')
        to_number = request.json.get('to', None)
        
        sid = send_whatsapp(message, to=to_number)
        return jsonify({'success': True, 'message': f'Tsunami alert test terkirim. SID: {sid}'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/get_status')
def get_status():
    """Get current system status"""
    return jsonify({
        'streaming_active': streaming_active,
        'extreme_count': extreme_count,
        'wa_available': SEND_WA_AVAILABLE,
        'sms_available': SEND_SMS_AVAILABLE,
        'bmkg_available': BMKG_AVAILABLE,
        'config_available': CONFIG_AVAILABLE
    })

if __name__ == '__main__':
    load_app_config()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
