
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
from comtypes import CLSCTX_ALL



def get_audio_endpoint():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    return interface.QueryInterface(IAudioEndpointVolume)


def press_volume_key(key_code, times=1):
    """Simulates pressing a volume key."""
    for _ in range(times):
        ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key release