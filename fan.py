import subprocess
import clr
import os
from OpenHardwareMonitor.Hardware import Computer

def set_fan_speed(speed_percentage):
    command = f"SpeedFan /SPEED={speed_percentage}"

    try:
        subprocess.run(command, check=True, shell=True)
        print(f"Fan speed set to {speed_percentage}% using SpeedFan.")
    except subprocess.CalledProcessError as e:
        print(f"Error setting fan speed: {e}")



dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'OpenHardwareMonitorLib.dll')

def initialize_computer():
    computer = Computer()
    computer.MainboardEnabled = True
    computer.CPUEnabled = True
    computer.FanControllerEnabled = True
    computer.Open()
    return computer

def get_fan_speeds(computer):
    fan_speeds = []
    for hardware in computer.Hardware:
        hardware.Update()
        for sensor in hardware.Sensors:
            if sensor.SensorType == "Fan":
                fan_speeds.append((sensor.Name, sensor.Value)) 
    return fan_speeds

computer = initialize_computer()

fan_speeds = get_fan_speeds(computer)

for fan_name, speed in fan_speeds:
    print(f"{fan_name}: {speed} RPM")