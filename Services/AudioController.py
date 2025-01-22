from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
from comtypes import CLSCTX_ALL

class AudioController:
    def __init__(self):
        self.audio_endpoint = self.get_audio_endpoint()

    @staticmethod
    def get_audio_endpoint():
        """
        Retrieves the audio endpoint interface for controlling volume.

        Returns:
            IAudioEndpointVolume: The audio endpoint volume interface.
        """
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None
        )
        return interface.QueryInterface(IAudioEndpointVolume)

    @staticmethod
    def press_volume_key(key_code, times=1):
        """
        Simulates pressing a volume key.

        Args:
            key_code (int): The virtual-key code of the key to press.
            times (int): Number of times to press the key.
        """
        for _ in range(times):
            ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
            ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)  # Key release

