import os
import shutil
import tempfile
import psutil

def get_disk_metrics():
    disk = psutil.disk_usage('/')
    return {
        "usage": disk.percent,
        "free_space": round(disk.free / (1024 ** 3), 2),
        "read_speed": disk_io_stats()["read"],
        "write_speed": disk_io_stats()["write"],
    }

def delete_files_in_directory(directory):
    if os.path.exists(directory):
        number = 0
        for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                except PermissionError as e:
                    number += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

        print(f"Skipped {number} files because they were in use.")
                  
def clear_temp_files():
    temp_dir = tempfile.gettempdir()
    app_data_temp_dir = os.path.join(os.getenv('APPDATA'), 'Local', 'Temp')

    try:
        delete_files_in_directory(temp_dir)
        delete_files_in_directory(app_data_temp_dir)

        print("Temporary files cleared successfully.")
    except Exception as e:
        print(f"Error clearing temp files: {e}")


def disk_io_stats():
    disk_io = psutil.disk_io_counters()
    read_speed = disk_io.read_bytes / 1024 / 1024  # MB
    write_speed = disk_io.write_bytes / 1024 / 1024  # MB
    return {
        "read": round(read_speed, 2),
        "write": round(write_speed, 2),
    }
