"""
Remote Desktop - Live screen viewing and mouse/keyboard control
"""
import pyautogui
import io
import base64
import logging
import time

logger = logging.getLogger('PCGamingApp')

# Disable pyautogui failsafe for remote control
pyautogui.FAILSAFE = False
# Set pause between actions (reduce for faster response)
pyautogui.PAUSE = 0.01


def get_screen_frame():
    """
    Get current screen as base64 encoded image
    
    Returns:
        Base64 encoded image string and timestamp
    """
    try:
        screenshot = pyautogui.screenshot()
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        screenshot.save(img_buffer, format='PNG', optimize=True, quality=85)
        img_buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return img_base64, time.time()
    except Exception as e:
        logger.error(f"Error getting screen frame: {e}")
        raise


def move_mouse(x, y, relative=False):
    """
    Move mouse to coordinates
    
    Args:
        x: X coordinate
        y: Y coordinate
        relative: If True, move relative to current position
    """
    try:
        if relative:
            pyautogui.moveRel(x, y, duration=0.1)
        else:
            pyautogui.moveTo(x, y, duration=0.1)
        return True
    except Exception as e:
        logger.error(f"Error moving mouse: {e}")
        return False


def click_mouse(button='left', x=None, y=None):
    """
    Click mouse button at current position (does NOT move the mouse)
    
    Args:
        button: 'left', 'right', or 'middle'
        x: X coordinate (ignored - always clicks at current position)
        y: Y coordinate (ignored - always clicks at current position)
    """
    try:
        # Always click at current position without moving
        # This prevents the mouse from jumping around
        pyautogui.click(button=button)
        return True
    except Exception as e:
        logger.error(f"Error clicking mouse: {e}")
        return False


def scroll_mouse(x, y, clicks):
    """
    Scroll mouse wheel
    
    Args:
        x: X coordinate
        y: Y coordinate
        clicks: Number of scroll clicks (positive for up, negative for down)
    """
    try:
        pyautogui.scroll(clicks, x=x, y=y)
        return True
    except Exception as e:
        logger.error(f"Error scrolling mouse: {e}")
        return False


def press_key(key):
    """
    Press a key
    
    Args:
        key: Key to press (e.g., 'enter', 'space', 'ctrl', etc.)
    """
    try:
        pyautogui.press(key)
        return True
    except Exception as e:
        logger.error(f"Error pressing key: {e}")
        return False


def type_text(text):
    """
    Type text
    
    Args:
        text: Text to type
    """
    try:
        pyautogui.write(text, interval=0.01)
        return True
    except Exception as e:
        logger.error(f"Error typing text: {e}")
        return False


def get_screen_size():
    """
    Get screen size
    
    Returns:
        Tuple (width, height)
    """
    try:
        return pyautogui.size()
    except Exception as e:
        logger.error(f"Error getting screen size: {e}")
        return (1920, 1080)  # Default fallback

