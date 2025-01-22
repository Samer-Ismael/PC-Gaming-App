from flask import Blueprint, app, jsonify
import psutil

from Services.CPUInfo import CPUInfo
from Services.MemoryManager import MemoryManager
from Services.DiskManager import DiskManager
from Services.GPUManager import GPUManager

cpu = CPUInfo()
ram = MemoryManager()
disk = DiskManager()
gpu = GPUManager()

bp = Blueprint('metrics', __name__)

@app.route("/metrics/cpu")
def cpu_metrics():
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        
        cpu_freq = psutil.cpu_freq()
        current_freq = cpu_freq.current if cpu_freq else "Unavailable"
        max_freq = cpu_freq.max if cpu_freq else "Unavailable"

        cpu_temp = cpu.get_cpu_temperature_metrics()
        if isinstance(cpu_temp, str):
            cpu_temp = "Unavailable"

        return jsonify({
            "usage": cpu_usage,
            "frequency_current": current_freq,
            "frequency_max": max_freq,
            "temperature": cpu_temp,
        })
    except Exception as e:
        print(f"Error fetching CPU metrics: {e}")
        return jsonify({
            "usage": "Unavailable",
            "frequency_current": "Unavailable",
            "frequency_max": "Unavailable",
            "temperature": "Unavailable",
        }), 500


@app.route("/metrics/ram")
def ram_metrics():
    try:
        ram_metrics = ram.get_ram_metrics()
        return jsonify(ram_metrics)
    except Exception as e:
        print(f"Error fetching RAM metrics: {e}")
        return jsonify({"usage": "Unavailable", "total": "Unavailable", "free": "Unavailable"}), 500


@app.route("/metrics/disk")
def disk_metrics():
    try:
        disk_metrics = disk.get_disk_metrics()
        return jsonify(disk_metrics)
    except Exception as e:
        print(f"Error fetching Disk metrics: {e}")
        return jsonify({"usage": "Unavailable", "free_space": "Unavailable"}), 500


@app.route("/metrics/gpu")
def gpu_metrics():
    try:
        gpu_metrics = gpu.get_gpu_metrics()
        return jsonify(gpu_metrics)
    except Exception as e:
        print(f"Error fetching GPU metrics: {e}")
        return jsonify({"name": "Unavailable", "temperature": "Unavailable", "utilization": "Unavailable", "memory_used": "Unavailable", "memory_total": "Unavailable"}), 500
