"""
Configuration management for PC Gaming App
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Server configuration
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', 5000))
DEBUG = os.getenv('FLASK_ENV') == 'development'

# Paths
LIB_FOLDER = BASE_DIR / 'lib'
STATIC_FOLDER = BASE_DIR / 'static'
TEMPLATES_FOLDER = BASE_DIR / 'templates'

# Hardware monitoring
CPU_UPDATE_INTERVAL = 1.0  # seconds
METRICS_CACHE_TTL = 0.5  # seconds - cache metrics for performance

# Hardware DLL paths
OPENHARDWARE_DLL = LIB_FOLDER / 'OpenHardwareMonitorLib.dll'
EMPTY_STANDBY_LIST = LIB_FOLDER / 'EmptyStandbyList.exe'
RAMMAP_EXE = LIB_FOLDER / 'RAMMap.exe'

# App version
APP_VERSION = "2.0.0"

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

