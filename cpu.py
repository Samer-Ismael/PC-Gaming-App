import os
import sys
import ctypes
import clr
import psutil
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

def get_cpu_temperature_intel():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            cpu_temp = temps["coretemp"][0].current  
            return cpu_temp
        else:
            return "Temperature data not available"
    except Exception as e:
        return f"Error retrieving CPU temperature: {e}"
    

def get_cpu_temperature_wmi():
    try:
        w = wmi.WMI()

        probes = w.query("SELECT * FROM Win32_TemperatureProbe")

        for probe in probes:
            if probe.CurrentReading is not None:
                temp = (probe.CurrentReading / 10.0) - 273.15
                return temp
        
        return "CPU temperature data not available."
    except Exception as e:
        return f"Error retrieving CPU temperature: {e}"