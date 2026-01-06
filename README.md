# PC Gaming Monitor 🚀

A modern system monitoring application that allows you to monitor your PC's performance metrics in real-time and control it remotely from any device on your network.

## 🖥️ Screenshots

![PC Gaming Monitor Dashboard](static/Screenshot_20260105-225210.png)

---

## ✨ Features

### System Monitoring
- **CPU**: Usage, frequency, temperature
- **RAM**: Usage, total, free memory (with cache clearing)
- **Disk**: Usage, free space, read/write speeds (with temp file cleanup)
- **GPU**: Name, temperature, utilization, memory usage
- **Network**: Real-time upload/download speeds and active connections
- **Internet Speed Test**: Download, upload, and ping testing

### Remote Control
- **Remote Desktop**: Live screen viewing with mouse and keyboard control
- **File Explorer**: Browse and download files from your PC

### System Controls
- Shutdown, restart, logout, lock system
- Clear RAM cache and temporary files
- Close application

### Media Controls
- Play/Pause, Previous/Next track
- Per-application volume control
- Mute/Unmute individual apps

### Additional Features
- Real-time metric updates
- Automatic update checking
- System information display
- Standalone desktop window (PyQt5)
- Mobile-friendly interface
- Modern dark theme UI

---

## 🚀 Getting Started

### Download

Download the latest version from the [Releases](https://github.com/yourusername/PC-Gaming-App/releases) page.

### Requirements
- Windows 10/11 (64-bit)
- Administrator privileges (for system controls and hardware monitoring)

### Usage

1. Run `Monitor.exe` (administrator privileges recommended)
2. The standalone window will open automatically
3. Access from your phone/network: `http://<your-ip>:5000`

### Development Setup

If you want to run from source:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python Monitor.py
```

---

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **System Monitoring**: psutil, pynvml, OpenHardwareMonitor
- **Remote Desktop**: pyautogui
- **Standalone Window**: PyQt5, PyQtWebEngine
- **Media Control**: pycaw

---

## 📋 System Requirements

- Windows 10/11 (64-bit)
- Administrator privileges
- 4GB RAM minimum
- Network access for remote control

---

## 🔧 Configuration

Edit `config.py` to customize:
- Server host and port
- Update intervals
- Cache TTL
- Logging levels

---

## 📝 Notes

- The app runs as a standalone window by default
- Some features require administrator privileges
- GPU monitoring requires NVIDIA GPU with NVML support
- Remote desktop works best on the same network
- Only use on trusted networks

---

## 📄 License

See LICENSE file for details.

---

**Version**: 2.3.2
