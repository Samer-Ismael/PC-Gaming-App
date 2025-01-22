import sys
import ctypes


class AdminPrivileges:
    
    @staticmethod
    def is_admin():
        """Check if the script is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    @staticmethod
    def run_as_admin():
        """Restart the script with administrator privileges."""
        script = sys.argv[0]
        params = " ".join(sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"{script} {params}", None, 1)
        sys.exit()