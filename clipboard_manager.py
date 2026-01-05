"""
Clipboard Manager - Get and set clipboard content
"""
import logging

logger = logging.getLogger('PCGamingApp')

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False
    logger.warning("pyperclip not available. Clipboard feature will be disabled.")


def get_clipboard():
    """
    Get current clipboard content
    
    Returns:
        Clipboard text or None
    """
    if not PYPERCLIP_AVAILABLE:
        logger.error("pyperclip is not installed. Please install it to use clipboard feature.")
        return None
    
    try:
        return pyperclip.paste()
    except Exception as e:
        logger.error(f"Error getting clipboard: {e}")
        return None


def set_clipboard(text):
    """
    Set clipboard content
    
    Args:
        text: Text to set in clipboard
    
    Returns:
        Success status
    """
    if not PYPERCLIP_AVAILABLE:
        logger.error("pyperclip is not installed. Please install it to use clipboard feature.")
        return False
    
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        logger.error(f"Error setting clipboard: {e}")
        return False

