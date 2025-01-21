import os
import clr

dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'OpenHardwareMonitorLib.dll')

if os.path.exists(dll_path):
    print("DLL found!")
    clr.AddReference(dll_path)
    from OpenHardwareMonitor import Hardware
    print("Module loaded successfully!")
else:
    print("DLL not found!")

def get_gpu_metrics():
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
                    #print(f"Sensor: {sensor.Name}, Type: {sensor.SensorType}")  # Debugging sensor type info

                    if sensor.SensorType == Hardware.SensorType.Temperature:
                        gpu_metrics["temperature"] = sensor.Value
                    if sensor.SensorType == Hardware.SensorType.Load:
                        gpu_metrics["utilization"] = round(sensor.Value, 2)
                       # Retrieve memory information using GPU Memory sensors
                    if sensor.Name == "GPU Memory Used":
                        gpu_metrics["memory_used"] = round(sensor.Value, 2)  # Used memory in MB
                    if sensor.Name == "GPU Memory Total":
                        gpu_metrics["memory_total"] = round(sensor.Value, 2)  # Total memory in MB

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
    except Exception as e:
        print(f"Error fetching GPU metrics: {e}")
        return {
            "name": "Unavailable",
            "temperature": "Unavailable",
            "utilization": "Unavailable",
            "memory_used": "Unavailable",
            "memory_total": "Unavailable"
        }