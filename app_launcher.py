"""
Application Launcher - Launch applications on the PC
"""
import subprocess
import os
import logging
import winreg

logger = logging.getLogger('PCGamingApp')


def get_installed_apps():
    """
    Get list of installed applications from Windows registry
    
    Returns:
        List of application dictionaries
    """
    apps = []
    try:
        # Common registry paths for installed applications
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hkey, path in registry_paths:
            try:
                key = winreg.OpenKey(hkey, path)
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            app_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0] if winreg.QueryValueEx(subkey, "InstallLocation")[0] else None
                            
                            # Only add if it has a display name
                            if app_name:
                                apps.append({
                                    'name': app_name,
                                    'location': install_location or ''
                                })
                        except (FileNotFoundError, OSError):
                            pass
                        finally:
                            subkey.Close()
                    except (OSError, WindowsError):
                        pass
                key.Close()
            except (OSError, WindowsError):
                pass
        
        # Remove duplicates and sort
        seen = set()
        unique_apps = []
        for app in apps:
            if app['name'] not in seen:
                seen.add(app['name'])
                unique_apps.append(app)
        
        return sorted(unique_apps, key=lambda x: x['name'])
    except Exception as e:
        logger.error(f"Error getting installed apps: {e}")
        return []


def launch_app(app_name_or_path):
    """
    Launch an application
    
    Args:
        app_name_or_path: Application name or full path
    
    Returns:
        Tuple (success: bool, message: str)
    """
    try:
        # Try to launch as a path first
        if os.path.exists(app_name_or_path):
            subprocess.Popen([app_name_or_path], shell=True)
            return True, f"Launched: {app_name_or_path}"
        
        # Try common application locations
        common_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), app_name_or_path),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), app_name_or_path),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), app_name_or_path),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                subprocess.Popen([path], shell=True)
                return True, f"Launched: {path}"
        
        # Try to launch by name (Windows will search PATH)
        try:
            subprocess.Popen([app_name_or_path], shell=True)
            return True, f"Launched: {app_name_or_path}"
        except Exception:
            pass
        
        return False, f"Could not find application: {app_name_or_path}"
    except Exception as e:
        logger.error(f"Error launching app {app_name_or_path}: {e}")
        return False, f"Error launching application: {str(e)}"


def get_common_apps():
    """
    Get list of commonly used applications with their paths
    
    Returns:
        List of common app dictionaries
    """
    common_apps = [
        {'name': 'Notepad', 'path': 'notepad.exe'},
        {'name': 'Calculator', 'path': 'calc.exe'},
        {'name': 'File Explorer', 'path': 'explorer.exe'},
        {'name': 'Command Prompt', 'path': 'cmd.exe'},
        {'name': 'PowerShell', 'path': 'powershell.exe'},
        {'name': 'Task Manager', 'path': 'taskmgr.exe'},
        {'name': 'Control Panel', 'path': 'control.exe'},
        {'name': 'Settings', 'path': 'ms-settings:'},
        {'name': 'Paint', 'path': 'mspaint.exe'},
        {'name': 'Snipping Tool', 'path': 'snippingtool.exe'},
    ]
    
    return common_apps

