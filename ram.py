import gc
import os
import subprocess
import time
import ctypes
import psutil

def is_admin():
    """Check if the script is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_ram_metrics():
    """Get RAM usage metrics."""
    ram = psutil.virtual_memory()
    return {
        "usage": ram.percent,
        "total": round(ram.total / (1024 ** 3), 2),
        "free": round(ram.available / (1024 ** 3), 2),
    }

def clear_cache_mem():
    """Clear system memory cache. Requires administrator privileges."""
    if not is_admin():
        raise PermissionError(
            "Administrator privileges required to clear memory cache. "
            "Please run the application as administrator."
        )
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, 'lib', 'EmptyStandbyList.exe')
    
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"EmptyStandbyList.exe not found at {path}. "
            "This tool is required to clear memory cache."
        )
    
    def clear_cache_once():
        """Clear cache once with error handling."""
        try:
            # Clear working sets
            result1 = subprocess.run(
                [path, "workingsets"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            time.sleep(1)
            
            # Clear standby list
            result2 = subprocess.run(
                [path, "standbylist"],
                check=False,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Check if either command failed
            if result1.returncode != 0 and result2.returncode != 0:
                error_msg = result1.stderr or result2.stderr or "Unknown error"
                raise subprocess.CalledProcessError(
                    result1.returncode or result2.returncode,
                    path,
                    error_msg
                )
            
            return True
        except subprocess.TimeoutExpired:
            raise TimeoutError("Memory clearing operation timed out.")
        except Exception as e:
            raise Exception(f"Error during memory clearing: {str(e)}")
    
    try:
        # Try clearing multiple times for better results
        clear_cache_once()
        time.sleep(2)
        clear_cache_once()
        time.sleep(2)
        clear_cache_once()
        
        # Force garbage collection
        gc.collect()
        
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if hasattr(e, 'stderr') and e.stderr else str(e)
        if "privilege" in error_msg.lower() or "admin" in error_msg.lower():
            raise PermissionError(
                "Administrator privileges required. Please run the application as administrator."
            )
        else:
            raise Exception(f"Failed to clear memory cache: {error_msg}")
    except Exception as e:
        raise
