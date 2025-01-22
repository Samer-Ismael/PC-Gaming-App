import clr
import wmi
import os

class CPUInfo:
    """Class to retrieve CPU information, including temperature."""
    def __init__(self):
        self._load_library()

    def _load_library(self):
        """Load the OpenHardwareMonitor library."""
        self.dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'..', 'lib', 'OpenHardwareMonitorLib.dll')

        if not os.path.exists(self.dll_path):
            raise FileNotFoundError(f"Library not found at {self.dll_path}")
        clr.AddReference(self.dll_path)
        from OpenHardwareMonitor import Hardware
        self.Hardware = Hardware

    def get_cpu_temperature(self):
        """Retrieve CPU temperature using OpenHardwareMonitor."""
        hw = self.Hardware.Computer()
        hw.CPUEnabled = True
        hw.Open()

        cpu_temp = None
        for hardware in hw.Hardware:
            hardware.Update()
            if hardware.HardwareType == self.Hardware.HardwareType.CPU:
                for sensor in hardware.Sensors:
                    if sensor.SensorType == self.Hardware.SensorType.Temperature:
                        cpu_temp = sensor.Value
                        break
            if cpu_temp is not None:
                break
        return cpu_temp

    @staticmethod
    def get_cpu_temperature_wmi():
        """Retrieve CPU temperature using WMI."""
        try:
            w = wmi.WMI(namespace="root\wmi")
            temperature_info = w.MSAcpi_ThermalZoneTemperature()
            if temperature_info:
                for temp in temperature_info:
                    temp_celsius = (temp.CurrentTemperature / 10) - 273.15
                    return temp_celsius
            return None
        except Exception as e:
            return f"Error retrieving CPU temperature: {e}"

    def get_cpu_temperature_metrics(self):
        """Retrieve CPU temperature, falling back to WMI if necessary."""
        cpu_temp = self.get_cpu_temperature()
        if cpu_temp is not None:
            return cpu_temp
        return self.get_cpu_temperature_wmi()