import os
import sys
import ctypes
import clr
import wmi

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges."""
    script = sys.argv[0] 
    params = " ".join(sys.argv[1:])  
    
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"{script} {params}", None, 1)
    sys.exit()  

if not is_admin():
    print("Restarting script with administrator privileges...")
    run_as_admin()  

print("Running with administrator privileges.")

dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'OpenHardwareMonitorLib.dll')


clr.AddReference(dll_path)

from OpenHardwareMonitor import Hardware

def get_cpu_temperature():
    hw = Hardware.Computer()
    hw.CPUEnabled = True
    hw.Open()

    cpu_temp = None

    for i in hw.Hardware:
        i.Update() 
        if i.HardwareType == Hardware.HardwareType.CPU:
            for sensor in i.Sensors:
                if sensor.SensorType == Hardware.SensorType.Temperature:
                    cpu_temp = sensor.Value
                    break  
        if cpu_temp is not None:
            break  

    return cpu_temp

def get_cpu_temperature_wmi():
    try:
        w = wmi.WMI(namespace="root\wmi")
        temperature_info = w.MSAcpi_ThermalZoneTemperature()

        if temperature_info:
            for temp in temperature_info:
                temp_celsius = (temp.CurrentTemperature / 10) - 273.15
                return temp_celsius
        else:
            return "Temperature information not available for the CPU."

    except Exception as e:
        return f"Error retrieving CPU temperature: {e}"

def get_cpu_temperature_metrics():
    cpu_temp = get_cpu_temperature()

    if cpu_temp is not None:
        return cpu_temp
    else:
        cpu_temp_wmi = get_cpu_temperature_wmi()
        if cpu_temp_wmi is not None:
            return cpu_temp_wmi
        else:
            return "Unable to retrieve CPU temperature."
                