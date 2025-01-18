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


def print_memory_info():
    mem = psutil.virtual_memory()
    print(f"Total: {mem.total // (1024 ** 2)} MB")
    print(f"Available: {mem.available // (1024 ** 2)} MB")
    print(f"Used: {mem.used // (1024 ** 2)} MB")
    return mem

def clear_cache_mem():
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'lib', 'EmptyStandbyList.exe')
    
    
    if os.path.exists(path):
            try:
                print("Before: ")
                print_memory_info
                subprocess.run([path, "standbylist"], check=True)
                print ("After: ")
                print_memory_info
                
                print("Standby list cleared successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error clearing standby list: {e}")
