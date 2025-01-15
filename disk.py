import psutil

def get_disk_metrics():
    disk = psutil.disk_usage('/')
    return {
        "usage": disk.percent,
        "free_space": round(disk.free / (1024 ** 3), 2),
    }
