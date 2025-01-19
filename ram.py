from asyncio import sleep
import gc
import os
import subprocess
import time
import psutil
from flask import jsonify

def get_ram_metrics():
    ram = psutil.virtual_memory()
    return {
        "usage": ram.percent,
        "total": round(ram.total / (1024 ** 3), 2),
        "free": round(ram.available / (1024 ** 3), 2),
    }

def clear_cache_mem():
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'lib', 'EmptyStandbyList.exe')
    
    def clear_cache_more_that_one_time():
        subprocess.run([path, "workingsets"], check=True)
        time.sleep(1)
        subprocess.run([path, "standbylist"], check=True)
    
    clear_cache_more_that_one_time()
    time.sleep(3)
    clear_cache_more_that_one_time()
    time.sleep(3)
    clear_cache_more_that_one_time()
    gc.collect()
    
    print("Working sets cleared successfully!")

    print("Standby list cleared successfully!")

    
    if os.path.exists(path):
            try:
                
                print("Memory cleared successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error clearing standby list: {e}")
