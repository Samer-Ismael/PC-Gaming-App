"""
Network Monitor - Real-time network usage and connection monitoring
"""
import psutil
import logging
import socket

logger = logging.getLogger('PCGamingApp')

# Store previous network stats for calculating speeds
_prev_stats = None


def get_network_stats():
    """
    Get current network statistics (bytes sent/received, speed)
    
    Returns:
        Dictionary with network statistics
    """
    global _prev_stats
    
    try:
        net_io = psutil.net_io_counters()
        current_stats = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
        
        # Calculate speeds if we have previous stats
        if _prev_stats:
            time_diff = 1.0  # Assuming 1 second between calls
            upload_speed = (current_stats['bytes_sent'] - _prev_stats['bytes_sent']) / time_diff
            download_speed = (current_stats['bytes_recv'] - _prev_stats['bytes_recv']) / time_diff
            
            current_stats['upload_speed_mbps'] = round((upload_speed * 8) / (1024 * 1024), 2)
            current_stats['download_speed_mbps'] = round((download_speed * 8) / (1024 * 1024), 2)
        else:
            current_stats['upload_speed_mbps'] = 0
            current_stats['download_speed_mbps'] = 0
        
        # Format bytes for display
        current_stats['bytes_sent_mb'] = round(current_stats['bytes_sent'] / (1024 * 1024), 2)
        current_stats['bytes_recv_mb'] = round(current_stats['bytes_recv'] / (1024 * 1024), 2)
        
        _prev_stats = current_stats.copy()
        
        return current_stats
    except Exception as e:
        logger.error(f"Error getting network stats: {e}")
        return {
            'bytes_sent_mb': 0,
            'bytes_recv_mb': 0,
            'upload_speed_mbps': 0,
            'download_speed_mbps': 0,
            'packets_sent': 0,
            'packets_recv': 0
        }


def get_active_connections(limit=20):
    """
    Get active network connections
    
    Args:
        limit: Maximum number of connections to return
    
    Returns:
        List of connection dictionaries
    """
    try:
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            try:
                conn_info = {
                    'status': conn.status,
                    'local_address': f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A",
                    'remote_address': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                    'pid': conn.pid,
                    'process_name': None
                }
                
                # Get process name if PID is available
                if conn.pid:
                    try:
                        proc = psutil.Process(conn.pid)
                        conn_info['process_name'] = proc.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                connections.append(conn_info)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
        
        return connections[:limit]
    except Exception as e:
        logger.error(f"Error getting active connections: {e}")
        return []

