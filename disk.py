import os
import shutil
import tempfile
import psutil

def get_disk_metrics():
    """Get disk usage metrics."""
    disk = psutil.disk_usage('/')
    return {
        "usage": disk.percent,
        "free_space": round(disk.free / (1024 ** 3), 2),
        "read_speed": disk_io_stats()["read"],
        "write_speed": disk_io_stats()["write"],
    }

def delete_files_in_directory(directory):
    """Delete files in a directory, skipping files in use."""
    if not os.path.exists(directory):
        return {"deleted": 0, "skipped": 0, "errors": 0}
    
    deleted = 0
    skipped = 0
    errors = 0
    
    try:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    deleted += 1
                else:
                    os.remove(file_path)
                    deleted += 1
            except PermissionError:
                skipped += 1
            except FileNotFoundError:
                # File was already deleted
                pass
            except Exception as e:
                errors += 1
                # Don't print every error to avoid spam
        
        return {
            "deleted": deleted,
            "skipped": skipped,
            "errors": errors
        }
    except Exception as e:
        raise Exception(f"Error accessing directory {directory}: {str(e)}")
                  
def clear_temp_files():
    """Clear temporary files from system temp directories."""
    temp_dir = tempfile.gettempdir()
    app_data_temp_dir = os.path.join(os.getenv('APPDATA', ''), 'Local', 'Temp')
    
    results = {
        "temp_dir": None,
        "app_data_temp_dir": None,
        "total_deleted": 0,
        "total_skipped": 0,
        "total_errors": 0
    }
    
    try:
        # Clear system temp directory
        if os.path.exists(temp_dir):
            result = delete_files_in_directory(temp_dir)
            results["temp_dir"] = result
            results["total_deleted"] += result["deleted"]
            results["total_skipped"] += result["skipped"]
            results["total_errors"] += result["errors"]
        
        # Clear AppData temp directory
        if os.path.exists(app_data_temp_dir):
            result = delete_files_in_directory(app_data_temp_dir)
            results["app_data_temp_dir"] = result
            results["total_deleted"] += result["deleted"]
            results["total_skipped"] += result["skipped"]
            results["total_errors"] += result["errors"]
        
        return results
    except Exception as e:
        raise Exception(f"Error clearing temp files: {str(e)}")

def disk_io_stats():
    """Get disk I/O statistics."""
    try:
        disk_io = psutil.disk_io_counters()
        if disk_io is None:
            return {"read": 0, "write": 0}
        
        read_speed = disk_io.read_bytes / 1024 / 1024  # MB
        write_speed = disk_io.write_bytes / 1024 / 1024  # MB
        return {
            "read": round(read_speed, 2),
            "write": round(write_speed, 2),
        }
    except Exception:
        return {"read": 0, "write": 0}
