import os
import clr

class GPUManager:
    def __init__(self):
        self.dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'OpenHardwareMonitorLib.dll')
        self._load_module()

    def _load_module(self):
        """
        Loads the OpenHardwareMonitorLib DLL if available.
        """
        if os.path.exists(self.dll_path):
            clr.AddReference(self.dll_path)
            from OpenHardwareMonitor import Hardware
            self.Hardware = Hardware
            print("Module loaded successfully!")
        else:
            self.Hardware = None
            print("DLL not found!")

    def get_gpu_metrics(self):
        """
        Fetches GPU metrics including name, temperature, utilization, and memory information.

        Returns:
            dict: A dictionary containing GPU metrics or 'Unavailable' for missing data.
        """
        if not self.Hardware:
            return {
                "name": "Unavailable",
                "temperature": "Unavailable",
                "utilization": "Unavailable",
                "memory_used": "Unavailable",
                "memory_total": "Unavailable"
            }

        try:
            hw = self.Hardware.Computer()
            hw.GPUEnabled = True
            hw.Open()

            gpu_metrics = {}

            for i in hw.Hardware:
                if i.HardwareType == self.Hardware.HardwareType.GpuAti or i.HardwareType == self.Hardware.HardwareType.GpuNvidia:
                    gpu_metrics["name"] = i.Name
                    gpu_metrics["temperature"] = None
                    gpu_metrics["utilization"] = None
                    gpu_metrics["memory_used"] = None
                    gpu_metrics["memory_total"] = None

                    for sensor in i.Sensors:
                        if sensor.SensorType == self.Hardware.SensorType.Temperature:
                            gpu_metrics["temperature"] = sensor.Value
                        if sensor.SensorType == self.Hardware.SensorType.Load:
                            gpu_metrics["utilization"] = round(sensor.Value, 2)
                        if sensor.Name == "GPU Memory Used":
                            gpu_metrics["memory_used"] = round(sensor.Value, 2)
                        if sensor.Name == "GPU Memory Total":
                            gpu_metrics["memory_total"] = round(sensor.Value, 2)

                    gpu_metrics.setdefault("name", "Unavailable")
                    gpu_metrics["temperature"] = gpu_metrics["temperature"] or "Unavailable"
                    gpu_metrics["utilization"] = gpu_metrics["utilization"] or "Unavailable"
                    gpu_metrics["memory_used"] = gpu_metrics["memory_used"] or "Unavailable"
                    gpu_metrics["memory_total"] = gpu_metrics["memory_total"] or "Unavailable"

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
