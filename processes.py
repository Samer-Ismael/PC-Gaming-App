"""
Process Manager - Get process information and manage processes
"""
import psutil
import logging

logger = logging.getLogger('PCGamingApp')


def get_top_processes(limit=10, sort_by='cpu'):
    """
    Get top processes by CPU or memory usage
    
    Args:
        limit: Number of processes to return
        sort_by: 'cpu' or 'memory'
    
    Returns:
        List of process dictionaries
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                pinfo = proc.info
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': round(pinfo['cpu_percent'] or 0, 1),
                    'memory_percent': round(pinfo['memory_percent'] or 0, 1),
                    'memory_mb': round((pinfo['memory_info'].rss / 1024 / 1024), 1) if pinfo['memory_info'] else 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by specified metric
        if sort_by == 'cpu':
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        else:  # memory
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        
        return processes[:limit]
    except Exception as e:
        logger.error(f"Error getting top processes: {e}")
        return []


def kill_process(pid):
    """
    Kill a process by PID
    
    Args:
        pid: Process ID
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        process = psutil.Process(pid)
        process.terminate()
        # Wait for process to terminate
        try:
            process.wait(timeout=3)
        except psutil.TimeoutExpired:
            # Force kill if it doesn't terminate
            process.kill()
        return True, f"Process {pid} ({process.name()}) terminated successfully"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Access denied. Cannot kill process {pid}. Try running as administrator."
    except Exception as e:
        logger.error(f"Error killing process {pid}: {e}")
        return False, f"Error killing process: {str(e)}"

