"""
Screenshot Capture - Take screenshots of the PC screen
"""
import io
import base64
import logging

logger = logging.getLogger('PCGamingApp')

try:
    import pyautogui
    # Disable pyautogui failsafe for headless operation
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.warning("pyautogui not available. Screenshot feature will be disabled.")


def take_screenshot():
    """
    Take a screenshot of the current screen
    
    Returns:
        Base64 encoded image string
    """
    if not PYAUTOGUI_AVAILABLE:
        raise ImportError("pyautogui is not installed. Please install it to use screenshot feature.")
    
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return img_base64
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        raise

