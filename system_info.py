"""
System Information - Get detailed system and hardware information
"""
import platform
import psutil
import logging
import subprocess
import re

logger = logging.getLogger('PCGamingApp')


def get_system_info():
    """
    Get comprehensive system information
    
    Returns:
        Dictionary with system information
    """
    try:
        info = {
            'os': {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0]
            },
            'cpu': {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "Unknown",
                'min_frequency': f"{psutil.cpu_freq().min:.0f} MHz" if psutil.cpu_freq() else "Unknown"
            },
            'memory': {
                'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'available_gb': round(psutil.virtual_memory().available / (1024**3), 2)
            },
            'disk': [],
            'network': {
                'hostname': platform.node(),
                'interfaces': []
            }
        }
        
        # Get disk information
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disk'].append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent': usage.percent
                })
            except PermissionError:
                pass
        
        # Get network interfaces
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            interface_info = {
                'name': interface_name,
                'addresses': [],
                'is_up': net_if_stats[interface_name].isup if interface_name in net_if_stats else False,
                'speed': f"{net_if_stats[interface_name].speed} Mbps" if interface_name in net_if_stats and net_if_stats[interface_name].speed > 0 else "Unknown"
            }
            
            for addr in addresses:
                interface_info['addresses'].append({
                    'family': str(addr.family),
                    'address': addr.address,
                    'netmask': addr.netmask if addr.netmask else None
                })
            
            info['network']['interfaces'].append(interface_info)
        
        # Try to get CPU model name (Windows)
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'name'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        cpu_name = lines[1].strip()
                        if cpu_name:
                            info['cpu']['model'] = cpu_name
        except Exception as e:
            logger.debug(f"Could not get CPU model: {e}")
        
        # Try to get motherboard info (Windows)
        try:
            if platform.system() == 'Windows':
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'manufacturer,product'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].strip().split()
                        if len(parts) >= 2:
                            info['motherboard'] = {
                                'manufacturer': parts[0],
                                'product': ' '.join(parts[1:])
                            }
        except Exception as e:
            logger.debug(f"Could not get motherboard info: {e}")
        
        return info
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'error': str(e),
            'os': {'system': platform.system()},
            'cpu': {},
            'memory': {},
            'disk': [],
            'network': {}
        }

