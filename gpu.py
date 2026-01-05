import os

# Try to import clr (pythonnet), handle gracefully if not available
try:
    import clr
    CLR_AVAILABLE = True
except ImportError:
    CLR_AVAILABLE = False

# Try to import pynvml for NVIDIA GPU monitoring
try:
    import pynvml
    PYNVML_AVAILABLE = True
    pynvml.nvmlInit()
except (ImportError, Exception):
    PYNVML_AVAILABLE = False

dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'OpenHardwareMonitorLib.dll')

Hardware = None
if CLR_AVAILABLE and os.path.exists(dll_path):
    try:
        clr.AddReference(dll_path)
        from OpenHardwareMonitor import Hardware
        print("OpenHardwareMonitor module loaded successfully!")
    except Exception as e:
        print(f"Warning: Could not load OpenHardwareMonitor DLL: {e}")
        Hardware = None
elif not CLR_AVAILABLE:
    print("Warning: pythonnet not installed. GPU monitoring will use pynvml if available.")
elif not os.path.exists(dll_path):
    print(f"Warning: OpenHardwareMonitorLib.dll not found at {dll_path}")

def get_gpu_metrics_openhardware():
    """Get GPU metrics using OpenHardwareMonitor."""
    if not CLR_AVAILABLE or Hardware is None:
        return None
    
    try:
        hw = Hardware.Computer()
        hw.GPUEnabled = True  
        hw.Open()  

        gpu_metrics = {}

        for i in hw.Hardware:
            if i.HardwareType == Hardware.HardwareType.GpuAti or i.HardwareType == Hardware.HardwareType.GpuNvidia:
                gpu_metrics["name"] = i.Name
                gpu_metrics["temperature"] = None
                gpu_metrics["utilization"] = None
                gpu_metrics["memory_used"] = None
                gpu_metrics["memory_total"] = None

                for sensor in i.Sensors:
                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        gpu_metrics["temperature"] = sensor.Value
                    if sensor.SensorType == Hardware.SensorType.Load:
                        gpu_metrics["utilization"] = round(sensor.Value, 2)
                    if sensor.Name == "GPU Memory Used":
                        gpu_metrics["memory_used"] = round(sensor.Value, 2)
                    if sensor.Name == "GPU Memory Total":
                        gpu_metrics["memory_total"] = round(sensor.Value, 2)

                if "name" not in gpu_metrics:
                    gpu_metrics["name"] = "Unavailable"
                if gpu_metrics["temperature"] is None:
                    gpu_metrics["temperature"] = "Unavailable"
                if gpu_metrics["utilization"] is None:
                    gpu_metrics["utilization"] = "Unavailable"
                if gpu_metrics["memory_used"] is None:
                    gpu_metrics["memory_used"] = "Unavailable"
                if gpu_metrics["memory_total"] is None:
                    gpu_metrics["memory_total"] = "Unavailable"

                return gpu_metrics
        return None
    except Exception as e:
        print(f"Error fetching GPU metrics from OpenHardwareMonitor: {e}")
        return None

def get_gpu_metrics_pynvml():
    """Get GPU metrics using pynvml (NVIDIA only)."""
    if not PYNVML_AVAILABLE:
        return None
    
    try:
        device_count = pynvml.nvmlDeviceGetCount()
        if device_count == 0:
            return None
        
        # Get first GPU
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        # Get GPU name
        name_bytes = pynvml.nvmlDeviceGetName(handle)
        # Handle both string and bytes (depending on pynvml version)
        name = name_bytes.decode('utf-8') if isinstance(name_bytes, bytes) else name_bytes
        
        # Get temperature
        try:
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        except:
            temp = None
        
        # Get utilization
        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            utilization = util.gpu
        except:
            utilization = None
        
        # Get memory info
        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            memory_used = round(mem_info.used / 1024 / 1024, 2)  # Convert to MB
            memory_total = round(mem_info.total / 1024 / 1024, 2)  # Convert to MB
        except:
            memory_used = None
            memory_total = None
        
        return {
            "name": name,
            "temperature": temp if temp is not None else "Unavailable",
            "utilization": round(utilization, 2) if utilization is not None else "Unavailable",
            "memory_used": memory_used if memory_used is not None else "Unavailable",
            "memory_total": memory_total if memory_total is not None else "Unavailable"
        }
    except Exception as e:
        print(f"Error fetching GPU metrics from pynvml: {e}")
        return None

def get_gpu_metrics():
    """Get GPU metrics using available methods (OpenHardwareMonitor first, then pynvml)."""
    # Try OpenHardwareMonitor first
    metrics = get_gpu_metrics_openhardware()
    if metrics:
        return metrics
    
    # Fallback to pynvml (NVIDIA GPUs)
    metrics = get_gpu_metrics_pynvml()
    if metrics:
        return metrics
    
    # If both fail, return unavailable
    return {
        "name": "Unavailable",
        "temperature": "Unavailable",
        "utilization": "Unavailable",
        "memory_used": "Unavailable",
        "memory_total": "Unavailable"
    }
