import gc
import os
import subprocess
import psutil
from flask import jsonify

def get_ram_metrics():
    ram = psutil.virtual_memory()
    return {
        "usage": ram.percent,
        "total": round(ram.total / (1024 ** 3), 2),
        "free": round(ram.available / (1024 ** 3), 2),
    }

def trim_working_sets():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process = psutil.Process(proc.info['pid'])
            process.suspend()  # Temporarily suspend the process
            process.memory_full_info()  # Access memory info (triggers trimming in some cases)
            process.resume()  # Resume the process
            print(f"Trimmed working set for {proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def clear_standby_list():
    try:
        subprocess.run(["EmptyStandbyList.exe", "standbylist"], check=True)
        print("Standby list cleared successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error clearing standby list: {e}")



def log_memory_stats():
    memory = psutil.virtual_memory()
    print(f"Total: {memory.total / (1024 ** 3):.2f} GB")
    print(f"Available: {memory.available / (1024 ** 3):.2f} GB")
    print(f"Used: {memory.used / (1024 ** 3):.2f} GB")
    print(f"Percentage Used: {memory.percent}%")

def clear_cache_mem():
    tool_path = os.path.join(os.path.dirname(__file__), "lib", "EmptyStandbyList.exe")
    
    if not os.path.exists(tool_path):
        raise FileNotFoundError(f"{tool_path} not found. Download it from Sysinternals.")
    
    subprocess.run([tool_path], check=True)
    gc.collect()

        
