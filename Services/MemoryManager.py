import gc
import os
import subprocess
import time
import psutil
from flask import jsonify

class MemoryManager:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.cache_clear_tool_path = os.path.join(self.current_dir, 'lib', 'EmptyStandbyList.exe')

    def get_ram_metrics(self):
        """
        Retrieves RAM usage metrics.

        Returns:
            dict: A dictionary containing RAM usage percentage, total RAM, and free RAM in GB.
        """
        ram = psutil.virtual_memory()
        return {
            "usage": ram.percent,
            "total": round(ram.total / (1024 ** 3), 2),
            "free": round(ram.available / (1024 ** 3), 2),
        }

    def _clear_cache_step(self):
        """
        Executes the cache clearing tool for both workingsets and standbylist.
        """
        subprocess.run([self.cache_clear_tool_path, "workingsets"], check=True)
        time.sleep(1)
        subprocess.run([self.cache_clear_tool_path, "standbylist"], check=True)

    def clear_cache_mem(self):
        """
        Clears cache memory by invoking the external tool multiple times with delays.
        """
        if not os.path.exists(self.cache_clear_tool_path):
            raise FileNotFoundError(f"Cache clearing tool not found at {self.cache_clear_tool_path}")

        try:
            for _ in range(3):
                self._clear_cache_step()
                time.sleep(3)
            gc.collect()

            print("Working sets cleared successfully!")
            print("Standby list cleared successfully!")
            print("Memory cleared successfully!")
        except subprocess.CalledProcessError as e:
            print(f"Error clearing standby list: {e}")



