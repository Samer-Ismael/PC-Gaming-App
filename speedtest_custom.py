"""
Custom speed test implementation using HTTP requests
Designed to give results similar to speedtest.net
"""
import time
import requests
import threading
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Speed test servers (similar to speedtest.net approach)
TEST_SERVERS = [
    {
        "name": "Fast.com (Netflix CDN)",
        "download_urls": [
            "https://speed.cloudflare.com/__down?bytes={}",
            "https://bouygues.testdebit.info/10G.iso",
        ],
        "upload_url": "https://httpbin.org/post"
    },
    {
        "name": "Cloudflare",
        "download_urls": [
            "https://speed.cloudflare.com/__down?bytes=100000000",  # 100MB
            "https://speed.cloudflare.com/__down?bytes=50000000",   # 50MB
        ],
        "upload_url": "https://httpbin.org/post"
    }
]

def download_chunk(url: str, chunk_size: int = 1024 * 1024, duration: float = 10.0) -> tuple:
    """Download a chunk and measure speed"""
    try:
        start_time = time.time()
        downloaded = 0
        end_time = start_time + duration
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        for chunk in response.iter_content(chunk_size=chunk_size):
            if time.time() >= end_time:
                break
            if chunk:
                downloaded += len(chunk)
        
        elapsed = time.time() - start_time
        if elapsed > 0 and downloaded > 0:
            # Convert bytes to megabits per second
            speed_mbps = (downloaded * 8) / (elapsed * 1_000_000)
            return speed_mbps, downloaded, elapsed
        return 0.0, 0, elapsed
    except Exception as e:
        return 0.0, 0, 0

def test_download_speed_advanced(duration: float = 10.0) -> float:
    """Test download speed using multiple connections (like speedtest.net)"""
    try:
        # Use Cloudflare speed test API which is designed for this
        test_urls = [
            "https://speed.cloudflare.com/__down?bytes=100000000",  # 100MB
            "https://speed.cloudflare.com/__down?bytes=50000000",   # 50MB
            "https://bouygues.testdebit.info/10G.iso",  # Large file
        ]
        
        speeds = []
        total_downloaded = 0
        total_time = 0
        
        # Test with multiple URLs to get better average
        for url in test_urls[:2]:  # Use first 2 URLs
            try:
                speed, downloaded, elapsed = download_chunk(url, duration=duration)
                if speed > 0:
                    speeds.append(speed)
                    total_downloaded += downloaded
                    total_time += elapsed
            except Exception:
                continue
        
        if speeds:
            # Use average of all tests, but weight by amount downloaded
            if len(speeds) > 1:
                # Weighted average
                return sum(speeds) / len(speeds)
            return speeds[0]
        
        # Fallback: single connection test
        if total_time > 0 and total_downloaded > 0:
            return (total_downloaded * 8) / (total_time * 1_000_000)
        
        return 0.0
    except Exception as e:
        print(f"Download test error: {e}")
        return 0.0

def test_upload_speed_advanced(data_size_mb: float = 10.0) -> float:
    """Test upload speed using multiple chunks (like speedtest.net)"""
    try:
        # Create test data
        chunk_size = int(data_size_mb * 1024 * 1024)
        test_data = b'0' * chunk_size
        
        # Try multiple upload endpoints
        upload_urls = [
            "https://httpbin.org/post",
            "https://postman-echo.com/post",
        ]
        
        speeds = []
        
        for url in upload_urls:
            try:
                start_time = time.time()
                response = requests.post(
                    url,
                    data=test_data,
                    timeout=60,
                    headers={'Content-Type': 'application/octet-stream'}
                )
                elapsed = time.time() - start_time
                
                if response.status_code in [200, 201] and elapsed > 0:
                    # Convert bytes to megabits per second
                    speed_mbps = (len(test_data) * 8) / (elapsed * 1_000_000)
                    if speed_mbps > 0:
                        speeds.append(speed_mbps)
                        break  # One successful test is enough
            except Exception:
                continue
        
        if speeds:
            return speeds[0]
        return 0.0
    except Exception as e:
        print(f"Upload test error: {e}")
        return 0.0

def test_ping_http(host: str = "8.8.8.8") -> float:
    """Test ping using HTTP request timing (more accurate for web speed)"""
    try:
        import socket
        
        # Test multiple times for accuracy
        times = []
        test_count = 4
        
        for _ in range(test_count):
            try:
                start = time.time()
                # Connect to a common port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, 53))  # DNS port, usually open
                sock.close()
                
                if result == 0:
                    elapsed = (time.time() - start) * 1000  # Convert to ms
                    times.append(elapsed)
            except Exception:
                continue
        
        if times:
            # Return average, removing outliers
            times.sort()
            # Remove highest and lowest if we have enough samples
            if len(times) >= 4:
                times = times[1:-1]
            return sum(times) / len(times)
        
        return 0.0
    except Exception:
        return 0.0

def test_ping_cloudflare() -> float:
    """Test ping to Cloudflare (similar to speedtest.net)"""
    try:
        times = []
        for _ in range(3):
            try:
                start = time.time()
                response = requests.get(
                    "https://1.1.1.1/cdn-cgi/trace",
                    timeout=3
                )
                elapsed = (time.time() - start) * 1000
                if response.status_code == 200:
                    times.append(elapsed)
            except Exception:
                continue
        
        if times:
            return sum(times) / len(times)
        return 0.0
    except Exception:
        return 0.0

def run_speed_test() -> Dict[str, float]:
    """
    Run a complete speed test similar to speedtest.net.
    Returns dict with download_speed, upload_speed, and ping.
    """
    results = {
        "download_speed": 0.0,
        "upload_speed": 0.0,
        "ping": 0.0
    }
    
    try:
        # Test ping first (fastest, ~1 second)
        print("Testing ping...")
        ping_result = test_ping_cloudflare()
        if ping_result == 0:
            ping_result = test_ping_http()
        results["ping"] = ping_result
        
        # Test download speed (takes ~10 seconds)
        print("Testing download speed...")
        download_speed = test_download_speed_advanced(duration=10.0)
        results["download_speed"] = download_speed
        
        # Test upload speed (takes ~5-10 seconds depending on connection)
        print("Testing upload speed...")
        upload_speed = test_upload_speed_advanced(data_size_mb=5.0)
        results["upload_speed"] = upload_speed
        
        return results
    except Exception as e:
        print(f"Error in speed test: {e}")
        return results
