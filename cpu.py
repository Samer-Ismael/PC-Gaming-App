import os
import sys
import ctypes
import clr

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

def get_temperatures():
    hw = Hardware.Computer()
    hw.CPUEnabled = True
    hw.GPUEnabled = True
    hw.Open()

    cpu_temp = None

    for i in hw.Hardware:
        i.Update()  
        for sensor in i.Sensors:
           
            if sensor.SensorType == Hardware.SensorType.Temperature and i.HardwareType == Hardware.HardwareType.CPU:
                if sensor.Name == "CPU Package":
                    cpu_temp = sensor.Value
           
            if sensor.SensorType == Hardware.SensorType.Temperature and i.HardwareType == Hardware.HardwareType.GpuNvidia:
                if sensor.Name == "GPU Core":
                    gpu_temp = sensor.Value

    return cpu_temp
