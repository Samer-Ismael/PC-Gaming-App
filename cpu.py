import os
import sys
import ctypes

# Try to import clr (pythonnet), handle gracefully if not available
try:
    import clr
    CLR_AVAILABLE = True
except ImportError:
    CLR_AVAILABLE = False
    print("Warning: pythonnet (clr) not available. CPU temperature monitoring will be limited.")

# Try to import wmi
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    print("Warning: WMI not available. Install with: pip install WMI")

# Cache for WMI failure to avoid repeated errors
_wmi_failed = False
_wmi_error_logged = False

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

# Admin check is now handled in Monitor.py
# This module no longer requests admin privileges on import

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
    print("Warning: pythonnet not installed. Install with: pip install pythonnet")
elif not os.path.exists(dll_path):
    print(f"Warning: OpenHardwareMonitorLib.dll not found at {dll_path}")

def get_cpu_temperature():
    """Get CPU temperature using OpenHardwareMonitor."""
    if not CLR_AVAILABLE or Hardware is None:
        return None
    
    try:
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
    except Exception as e:
        # Only log error once to avoid spam
        if not hasattr(get_cpu_temperature, '_error_logged'):
            print(f"Error getting CPU temperature from OpenHardwareMonitor: {e}")
            get_cpu_temperature._error_logged = True
        return None

def get_cpu_temperature_wmi():
    """Get CPU temperature using WMI as fallback."""
    global _wmi_failed, _wmi_error_logged
    
    # If WMI already failed, don't try again
    if _wmi_failed:
        return None
    
    if not WMI_AVAILABLE:
        return None
    
    try:
        w = wmi.WMI(namespace="root\\wmi")
        temperature_info = w.MSAcpi_ThermalZoneTemperature()

        if temperature_info:
            for temp in temperature_info:
                temp_celsius = (temp.CurrentTemperature / 10) - 273.15
                return temp_celsius
        return None
    except Exception as e:
        # Mark WMI as failed and log error only once
        _wmi_failed = True
        if not _wmi_error_logged:
            error_msg = str(e)
            # Check if it's the common COM error
            if "0x80041003" in error_msg or "COM Error" in error_msg:
                print("Note: WMI temperature monitoring unavailable (requires specific hardware support).")
            else:
                print(f"Error retrieving CPU temperature from WMI: {e}")
            _wmi_error_logged = True
        return None

def get_cpu_temperature_metrics():
    """Get CPU temperature using available methods."""
    # Try OpenHardwareMonitor first
    cpu_temp = get_cpu_temperature()

    if cpu_temp is not None:
        return cpu_temp
    
    # Fallback to WMI (only if not already failed)
    if not _wmi_failed:
        cpu_temp_wmi = get_cpu_temperature_wmi()
        if cpu_temp_wmi is not None:
            return cpu_temp_wmi
    
    # If both fail, return unavailable message
    return "Unavailable"
