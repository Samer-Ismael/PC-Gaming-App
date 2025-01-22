import os
import shutil
import tempfile
import psutil

class DiskManager:
    @staticmethod
    def get_disk_metrics():
        """
        Retrieves disk usage metrics including usage percentage, free space, read speed, and write speed.

        Returns:
            dict: A dictionary with disk metrics.
        """
        disk = psutil.disk_usage('/')
        return {
            "usage": disk.percent,
            "free_space": round(disk.free / (1024 ** 3), 2),
            "read_speed": DiskManager.disk_io_stats()["read"],
            "write_speed": DiskManager.disk_io_stats()["write"],
        }

    @staticmethod
    def delete_files_in_directory(directory):
        """
        Deletes all files and subdirectories in the specified directory.

        Args:
            directory (str): Path to the directory to be cleared.
        """
        if os.path.exists(directory):
            skipped_files = 0
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                try:
                    if os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                except PermissionError:
                    skipped_files += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

            print(f"Skipped {skipped_files} files because they were in use.")

    @staticmethod
    def clear_temp_files():
        """
        Clears temporary files from the system's temp directory and AppData temp directory.
        """
        temp_dir = tempfile.gettempdir()
        app_data_temp_dir = os.path.join(os.getenv('APPDATA'), 'Local', 'Temp')

        try:
            DiskManager.delete_files_in_directory(temp_dir)
            DiskManager.delete_files_in_directory(app_data_temp_dir)

            print("Temporary files cleared successfully.")
        except Exception as e:
            print(f"Error clearing temp files: {e}")

    @staticmethod
    def disk_io_stats():
        """
        Retrieves disk I/O statistics including read and write speeds.

        Returns:
            dict: A dictionary with read and write speeds in MB.
        """
        disk_io = psutil.disk_io_counters()
        read_speed = disk_io.read_bytes / 1024 / 1024  # MB
        write_speed = disk_io.write_bytes / 1024 / 1024  # MB
        return {
            "read": round(read_speed, 2),
            "write": round(write_speed, 2),
        }

