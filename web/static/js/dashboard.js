// Tsunami Alert Dashboard JavaScript
class TsunamiDashboard {
    constructor() {
        this.streamingActive = false;
        this.waveChart = null;
        this.dataRefreshInterval = null;
        this.alertSound = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeChart();
        this.updateSystemStatus();
        this.loadWaveData();
        this.startDataRefresh();
        this.initializeAudio();
    }

    // Initialize audio for alerts
    initializeAudio() {
        // Create audio context for alert sounds
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported');
        }
    }

    // Play alert sound
    playAlertSound(type = 'default') {
        if (!this.audioContext) return;

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        // Different tones for different alert types
        const frequencies = {
            'default': 800,
            'warning': 600,
            'danger': 400,
            'tsunami': 300
        };

        oscillator.frequency.setValueAtTime(frequencies[type] || 800, this.audioContext.currentTime);
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + 0.1);
        gainNode.gain.linearRampToValueAtTime(0, this.audioContext.currentTime + 0.5);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.5);
    }

    // Setup event listeners
    setupEventListeners() {
        // Stream controls
        document.getElementById('startStreamBtn').addEventListener('click', () => this.startStream());
        document.getElementById('stopStreamBtn').addEventListener('click', () => this.stopStream());

        // Configuration
        document.getElementById('saveConfigBtn').addEventListener('click', () => this.saveConfiguration());

        // Test alerts
        document.getElementById('testWABtn').addEventListener('click', () => this.sendTestWhatsApp());
        document.getElementById('testSMSBtn').addEventListener('click', () => this.sendTestSMS());
        document.getElementById('testTsunamiBtn').addEventListener('click', () => this.sendTestTsunamiAlert());

        // Data refresh
        document.getElementById('refreshDataBtn').addEventListener('click', () => this.refreshData());
        document.getElementById('refreshEarthquakeBtn').addEventListener('click', () => this.refreshEarthquakeData());

        // Tab switching
        document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => this.onTabChange(e.target.id));
        });

        // Real-time form updates
        this.setupFormWatchers();

        // Keyboard shortcuts
        this.setupKeyboardShortcuts();
    }

    // Setup form watchers for real-time updates
    setupFormWatchers() {
        const inputs = ['rtspUrl', 'cameraLocation', 'resizeWidth'];
        inputs.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.autoSaveConfig());
            }
        });
    }

    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl+S to save config
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveConfiguration();
            }
            // Ctrl+R to refresh data
            if (e.ctrlKey && e.key === 'r') {
                e.preventDefault();
                this.refreshData();
            }
            // Space to start/stop stream
            if (e.code === 'Space' && e.target.tagName !== 'INPUT') {
                e.preventDefault();
                if (this.streamingActive) {
                    this.stopStream();
                } else {
                    this.startStream();
                }
            }
        });
    }

    // Auto-save configuration
    autoSaveConfig() {
        // Debounce auto-save
        clearTimeout(this.autoSaveTimeout);
        this.autoSaveTimeout = setTimeout(() => {
            this.saveConfiguration(false); // Silent save
        }, 2000);
    }

    // Start video stream
    async startStream() {
        const rtspUrl = document.getElementById('rtspUrl').value.trim();
        if (!rtspUrl) {
            this.showAlert('RTSP URL harus diisi!', 'warning');
            return;
        }

        this.setLoading('streamLoading', true);

        try {
            const response = await fetch('/start_stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ rtsp_url: rtspUrl })
            });

            const data = await response.json();
            
            if (data.success) {
                this.streamingActive = true;
                this.updateStreamUI(true);
                this.showAlert('Stream berhasil dimulai!', 'success');
                this.playAlertSound('default');
            } else {
                this.showAlert(data.message, 'danger');
                this.playAlertSound('danger');
            }
        } catch (error) {
            this.showAlert('Error: ' + error.message, 'danger');
            this.playAlertSound('danger');
        } finally {
            this.setLoading('streamLoading', false);
        }
    }

    // Stop video stream
    async stopStream() {
        try {
            const response = await fetch('/stop_stream', { method: 'POST' });
            const data = await response.json();

            this.streamingActive = false;
            this.updateStreamUI(false);
            this.showAlert('Stream dihentikan!', 'info');
            this.playAlertSound('default');
        } catch (error) {
            this.showAlert('Error: ' + error.message, 'danger');
        }
    }

    // Update stream UI
    updateStreamUI(active) {
        const placeholder = document.getElementById('videoPlaceholder');
        const stream = document.getElementById('videoStream');
        const indicator = document.querySelector('.streaming-indicator');

        if (active) {
            placeholder.style.display = 'none';
            stream.style.display = 'block';
            stream.src = '/video_feed?t=' + new Date().getTime();
            
            if (!indicator) {
                const newIndicator = document.createElement('div');
                newIndicator.className = 'streaming-indicator active';
                newIndicator.innerHTML = '<i class="bi bi-broadcast"></i> LIVE';
                document.getElementById('videoContainer').appendChild(newIndicator);
            }
        } else {
            placeholder.style.display = 'block';
            stream.style.display = 'none';
            stream.src = '';
            
            if (indicator) {
                indicator.remove();
            }
        }
    }

    // Save configuration
    async saveConfiguration(showMessage = true) {
        const config = this.collectConfiguration();

        try {
            const response = await fetch('/update_config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            const data = await response.json();
            
            if (data.success && showMessage) {
                this.showAlert('Konfigurasi berhasil disimpan!', 'success');
                this.playAlertSound('default');
            } else if (!data.success) {
                this.showAlert(data.message, 'danger');
                this.playAlertSound('danger');
            }
        } catch (error) {
            this.showAlert('Error: ' + error.message, 'danger');
        }
    }

    // Collect configuration from form
    collectConfiguration() {
        return {
            rtsp_url: this.getInputValue('rtspUrl'),
            camera_location: this.getInputValue('cameraLocation'),
            resize_width: parseInt(this.getInputValue('resizeWidth')) || 960,
            garis_extreme_y: parseInt(this.getInputValue('garisExtreme')) || 180,
            garis_sangat_tinggi_y: parseInt(this.getInputValue('garisSangatTinggi')) || 210,
            garis_tinggi_y: parseInt(this.getInputValue('garisTinggi')) || 230,
            garis_sedang_y: parseInt(this.getInputValue('garisSedang')) || 250,
            garis_rendah_y: parseInt(this.getInputValue('garisRendah')) || 280,
            line_thickness: parseInt(this.getInputValue('lineThickness')) || 1,
            peak_thickness: parseInt(this.getInputValue('peakThickness')) || 2,
            font_scale: parseFloat(this.getInputValue('fontSize')) || 0.7,
            font_thickness: parseInt(this.getInputValue('fontThickness')) || 2,
            enable_wa: this.getCheckboxValue('enableWA'),
            wa_cooldown_sec: parseInt(this.getInputValue('waCooldown')) || 300,
            enable_sms: this.getCheckboxValue('enableSMS'),
            sms_cooldown_sec: parseInt(this.getInputValue('smsCooldown')) || 300,
            enable_tsunami_alert: this.getCheckboxValue('enableTsunamiAlert'),
            extreme_threshold: parseInt(this.getInputValue('extremeThreshold')) || 12,
            alert_cooldown_min: parseInt(this.getInputValue('alertCooldown')) || 30,
            enable_earthquake_monitoring: this.getCheckboxValue('enableEarthquakeMonitoring'),
            magnitude_threshold: parseFloat(this.getInputValue('magnitudeThreshold')) || 5.0,
            tsunami_threshold: parseFloat(this.getInputValue('tsunamiThreshold')) || 6.0,
            earthquake_check_interval: parseInt(this.getInputValue('earthquakeInterval')) || 300
        };
    }

    // Helper methods for form values
    getInputValue(id) {
        const element = document.getElementById(id);
        return element ? element.value : '';
    }

    getCheckboxValue(id) {
        const element = document.getElementById(id);
        return element ? element.checked : false;
    }

    // Send test WhatsApp
    async sendTestWhatsApp() {
        const message = 'Test WhatsApp dari Dashboard Tsunami Alert - ' + new Date().toLocaleString();
        const toNumber = this.getInputValue('waTestNumber');

        await this.sendTestMessage('/send_test_wa', { message, to: toNumber || null });
    }

    // Send test SMS
    async sendTestSMS() {
        const message = 'Test SMS dari Dashboard Tsunami Alert - ' + new Date().toLocaleString();
        const toNumber = this.getInputValue('smsTestNumber');

        await this.sendTestMessage('/send_test_sms', { message, to: toNumber || null });
    }

    // Send test tsunami alert
    async sendTestTsunamiAlert() {
        const message = '🚨 TES ALERT TSUNAMI! 🚨\n\nSistem deteksi ombak mengirim pesan uji.\n\nWaktu: ' + 
                       new Date().toLocaleString() + '\n\n⚠️ Ini hanya tes, bukan peringatan nyata! ⚠️';

        await this.sendTestMessage('/send_test_tsunami_alert', { message });
    }

    // Generic test message sender
    async sendTestMessage(endpoint, payload) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            
            if (data.success) {
                this.showAlert(data.message, 'success');
                this.playAlertSound('default');
            } else {
                this.showAlert(data.message, 'danger');
                this.playAlertSound('danger');
            }
        } catch (error) {
            this.showAlert('Error: ' + error.message, 'danger');
            this.playAlertSound('danger');
        }
    }

    // Update system status
    async updateSystemStatus() {
        try {
            const response = await fetch('/get_status');
            const data = await response.json();

            this.updateStatusIndicators(data);
            document.getElementById('extremeCount').textContent = data.extreme_count || 0;
            
            // Check for extreme conditions
            if (data.extreme_count >= 10) {
                this.showEmergencyAlert(data.extreme_count);
            }
        } catch (error) {
            console.error('Error updating status:', error);
        }
    }

    // Update status indicators
    updateStatusIndicators(data) {
        const statusIndicator = document.getElementById('systemStatus');
        const statusText = document.getElementById('systemStatusText');

        if (data.streaming_active) {
            statusIndicator.className = 'status-indicator status-active';
            statusText.textContent = 'System Aktif';
        } else {
            statusIndicator.className = 'status-indicator status-inactive';
            statusText.textContent = 'System Standby';
        }
    }

    // Show emergency alert
    showEmergencyAlert(extremeCount) {
        const threshold = parseInt(this.getInputValue('extremeThreshold')) || 12;
        
        if (extremeCount >= threshold - 2) { // Alert 2 counts before tsunami alert
            const alertDiv = document.createElement('div');
            alertDiv.className = 'emergency-alert';
            alertDiv.innerHTML = `
                <h4>⚠️ PERINGATAN TSUNAMI ALERT ⚠️</h4>
                <p>Extreme Count: ${extremeCount}/${threshold}</p>
                <p>Tsunami alert akan dikirim pada ${threshold} deteksi EXTREME!</p>
            `;
            
            // Insert at top of main container
            const mainContainer = document.querySelector('.main-container');
            mainContainer.insertBefore(alertDiv, mainContainer.firstChild);
            
            // Auto-remove after 10 seconds
            setTimeout(() => alertDiv.remove(), 10000);
            
            this.playAlertSound('tsunami');
        }
    }

    // Load wave data
    async loadWaveData() {
        try {
            const response = await fetch('/get_wave_data');
            const data = await response.json();

            this.updateDataTable(data.data);
            this.updateChart(data.data);
            document.getElementById('totalData').textContent = data.total;

            if (data.data.length > 0) {
                const latest = data.data[data.data.length - 1];
                this.updateCurrentStatus(latest);
            }
        } catch (error) {
            console.error('Error loading wave data:', error);
        }
    }

    // Update current status display
    updateCurrentStatus(latest) {
        document.getElementById('currentStatus').textContent = latest.status || 'Menunggu...';
        document.getElementById('peakY').textContent = latest.peak_y || 0;
        
        // Update status styling
        const statusElement = document.getElementById('currentStatus');
        statusElement.className = 'metric-value ' + this.getStatusClass(latest.status);
    }

    // Get CSS class for status
    getStatusClass(status) {
        if (status.includes('EXTREME')) return 'status-extreme';
        if (status.includes('SANGAT TINGGI')) return 'status-very-high';
        if (status.includes('TINGGI')) return 'status-high';
        if (status.includes('SEDANG')) return 'status-medium';
        if (status.includes('RENDAH')) return 'status-low';
        return '';
    }

    // Update data table
    updateDataTable(data) {
        const tbody = document.getElementById('dataTableBody');
        
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">Belum ada data</td></tr>';
            return;
        }

        const rows = data.slice(-20).reverse().map(row => {
            const alertBadge = row.alert_sent ? 
                '<span class="badge bg-danger">Ya</span>' : 
                '<span class="badge bg-secondary">Tidak</span>';
            
            const statusBadge = `<span class="badge ${this.getStatusBadgeClass(row.status)}">${row.status}</span>`;
            
            return `
                <tr class="table-row-animated">
                    <td>${new Date(row.timestamp).toLocaleString()}</td>
                    <td>${row.peak_y}</td>
                    <td>${statusBadge}</td>
                    <td>${row.extreme_count}</td>
                    <td>${alertBadge}</td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = rows;

        // Add row animations
        setTimeout(() => {
            document.querySelectorAll('.table-row-animated').forEach((row, index) => {
                row.style.animationDelay = `${index * 0.1}s`;
                row.classList.add('fadeInUp');
            });
        }, 100);
    }

    // Get badge class for status
    getStatusBadgeClass(status) {
        if (status.includes('EXTREME')) return 'bg-dark';
        if (status.includes('SANGAT TINGGI')) return 'bg-danger';
        if (status.includes('TINGGI')) return 'bg-warning';
        if (status.includes('SEDANG')) return 'bg-info';
        if (status.includes('RENDAH')) return 'bg-success';
        return 'bg-secondary';
    }

    // Initialize chart
    initializeChart() {
        const ctx = document.getElementById('waveChart').getContext('2d');
        
        this.waveChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Peak Y (px)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true,
                    pointBackgroundColor: 'rgb(75, 192, 192)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        reverse: true,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Pergerakan Puncak Ombak (Real-time)',
                        font: {
                            size: 16,
                            weight: 'bold'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
    }

    // Update chart
    updateChart(data) {
        if (!this.waveChart || data.length === 0) return;

        const last30 = data.slice(-30);
        const labels = last30.map(item => new Date(item.timestamp).toLocaleTimeString());
        const values = last30.map(item => item.peak_y);

        this.waveChart.data.labels = labels;
        this.waveChart.data.datasets[0].data = values;
        this.waveChart.update('none');
    }

    // Refresh data manually
    refreshData() {
        this.loadWaveData();
        this.showAlert('Data berhasil direfresh!', 'info');
        this.playAlertSound('default');
    }

    // Refresh earthquake data
    async refreshEarthquakeData() {
        try {
            const response = await fetch('/get_earthquake_data');
            const data = await response.json();
            
            this.updateEarthquakeDisplay(data);
        } catch (error) {
            this.showAlert('Error loading earthquake data: ' + error.message, 'danger');
        }
    }

    // Update earthquake display
    updateEarthquakeDisplay(data) {
        const earthquakeDiv = document.getElementById('earthquakeData');
        
        if (data.success) {
            const eq = data.data;
            earthquakeDiv.innerHTML = `
                <div class="alert alert-info earthquake-info">
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="bi bi-geo-alt"></i> ${eq.wilayah}</h6>
                            <p><strong>Magnitude:</strong> <span class="badge bg-primary">${eq.magnitude} SR</span></p>
                            <p><strong>Kedalaman:</strong> ${eq.kedalaman}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Waktu:</strong> ${eq.datetime_str}</p>
                            <p><strong>Koordinat:</strong> ${eq.coordinates}</p>
                            <p><strong>Potensi Tsunami:</strong> 
                                <span class="badge ${eq.potensi_tsunami.includes('Tidak') ? 'bg-success' : 'bg-danger'}">
                                    ${eq.potensi_tsunami}
                                </span>
                            </p>
                        </div>
                    </div>
                </div>
            `;
            
            // Play alert sound for high magnitude
            if (parseFloat(eq.magnitude) >= 6.0) {
                this.playAlertSound('warning');
            }
        } else {
            earthquakeDiv.innerHTML = `
                <div class="alert alert-warning">
                    <i class="bi bi-exclamation-triangle"></i> ${data.message}
                </div>
            `;
        }
    }

    // Start data refresh interval
    startDataRefresh() {
        this.dataRefreshInterval = setInterval(() => {
            this.updateSystemStatus();
            if (this.streamingActive) {
                this.loadWaveData();
            }
        }, 5000);
    }

    // Handle tab changes
    onTabChange(tabId) {
        switch(tabId) {
            case 'data-tab':
                this.loadWaveData();
                break;
            case 'earthquake-tab':
                // Auto-refresh earthquake data when tab is opened
                break;
        }
    }

    // Set loading state
    setLoading(elementId, loading) {
        const element = document.getElementById(elementId);
        if (element) {
            if (loading) {
                element.classList.add('show');
            } else {
                element.classList.remove('show');
            }
        }
    }

    // Show alert modal
    showAlert(message, type) {
        const alertModal = new bootstrap.Modal(document.getElementById('alertModal'));
        const alertBody = document.getElementById('alertModalBody');
        
        const alertClass = {
            'success': 'alert-success',
            'danger': 'alert-danger',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const icon = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        }[type] || 'info-circle';
        
        alertBody.innerHTML = `
            <div class="alert ${alertClass}">
                <i class="bi bi-${icon}"></i> ${message}
            </div>
        `;
        
        alertModal.show();
        
        // Auto-close success messages
        if (type === 'success') {
            setTimeout(() => alertModal.hide(), 3000);
        }
    }

    // Cleanup
    destroy() {
        if (this.dataRefreshInterval) {
            clearInterval(this.dataRefreshInterval);
        }
        
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.tsunamiDashboard = new TsunamiDashboard();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.tsunamiDashboard) {
        window.tsunamiDashboard.destroy();
    }
});