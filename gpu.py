import subprocess
import time
from pynvml import *

def init_gpu():
    try:
        nvmlInit()
        return True
    except Exception as e:
        print(f"Error initializing NVML: {e}")
        return False

def get_gpu_metrics():
    try:
        device_count = nvmlDeviceGetCount()
        if device_count > 0:
            handle = nvmlDeviceGetHandleByIndex(0)

            name = nvmlDeviceGetName(handle)
            temperature = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            utilization = nvmlDeviceGetUtilizationRates(handle)
            memory_info = nvmlDeviceGetMemoryInfo(handle)

            return {
                "name": name.decode("utf-8") if isinstance(name, bytes) else name,
                "temperature": temperature,
                "utilization": utilization.gpu,
                "memory_used": round(memory_info.used / (1024 * 1024), 2),
                "memory_total": round(memory_info.total / (1024 * 1024), 2),
            }
        return {
            "name": "Unavailable",
            "temperature": "Unavailable",
            "utilization": "Unavailable",
            "memory_used": "Unavailable",
            "memory_total": "Unavailable",
        }
    except Exception as e:
        print(f"Error fetching GPU metrics: {e}")
        return {
            "name": "Unavailable",
            "temperature": "Unavailable",
            "utilization": "Unavailable",
            "memory_used": "Unavailable",
            "memory_total": "Unavailable",
        }
