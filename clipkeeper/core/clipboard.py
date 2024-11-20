import io
import base64
import logging
import threading
import time
from typing import Optional, Union
from dataclasses import dataclass
from PIL import Image
from enum import Enum, auto

class ClipboardFormat(Enum):
    TEXT = auto()
    IMAGE = auto()
    UNKNOWN = auto()

class ClipboardError(Exception):
    pass

@dataclass
class ClipboardContent:
    content: Union[str, bytes, None]
    format: ClipboardFormat
    timestamp: float
    error: Optional[str] = None

class WindowsClipboard:
    def __init__(self):
        try:
            import win32clipboard
            import win32con
            import win32ui
            from PIL import ImageGrab
            self.win32clipboard = win32clipboard
            self.win32con = win32con
            self.win32ui = win32ui
            self.ImageGrab = ImageGrab
        except ImportError as e:
            raise ClipboardError(f"Required packages not installed: {e}")
        
        self._lock = threading.Lock()

    def get_clipboard(self) -> ClipboardContent:
        with self._lock:
            try:
                self.win32clipboard.OpenClipboard()
                try:
                    if self.win32clipboard.IsClipboardFormatAvailable(self.win32con.CF_UNICODETEXT):
                        content = self.win32clipboard.GetClipboardData(self.win32con.CF_UNICODETEXT)
                        return ClipboardContent(
                            content=content,
                            format=ClipboardFormat.TEXT,
                            timestamp=time.time()
                        )
                finally:
                    self.win32clipboard.CloseClipboard()
                    
            except Exception as e:
                logging.error(f"Error getting clipboard text: {e}")
                return ClipboardContent(
                    content=None,
                    format=ClipboardFormat.UNKNOWN,
                    timestamp=time.time(),
                    error=str(e)
                )

    def get_clipboard_image(self) -> ClipboardContent:
        with self._lock:
            try:
                image = self.ImageGrab.grabclipboard()
                if image:
                    buffer = io.BytesIO()
                    if image.mode == 'RGBA':
                        image = image.convert('RGB')
                    image.save(buffer, format='PNG')
                    image_str = base64.b64encode(buffer.getvalue()).decode()
                    return ClipboardContent(
                        content=image_str,
                        format=ClipboardFormat.IMAGE,
                        timestamp=time.time()
                    )
                return ClipboardContent(
                    content=None,
                    format=ClipboardFormat.UNKNOWN,
                    timestamp=time.time()
                )
            except Exception as e:
                logging.error(f"Error getting clipboard image: {e}")
                return ClipboardContent(
                    content=None,
                    format=ClipboardFormat.UNKNOWN,
                    timestamp=time.time(),
                    error=str(e)
                )

    def set_clipboard(self, content: Union[str, bytes], content_type: str = "text") -> bool:
        with self._lock:
            try:
                self.win32clipboard.OpenClipboard()
                try:
                    self.win32clipboard.EmptyClipboard()
                    
                    if content_type == "text":
                        self.win32clipboard.SetClipboardText(content, self.win32con.CF_UNICODETEXT)
                    elif content_type == "image":
                        if isinstance(content, str):
                            image_data = base64.b64decode(content)
                        else:
                            image_data = content
                            
                        image = Image.open(io.BytesIO(image_data))
                        output = io.BytesIO()
                        image.convert('RGB').save(output, 'BMP')
                        data = output.getvalue()[14:]
                        
                        self.win32clipboard.SetClipboardData(self.win32con.CF_DIB, data)
                    return True
                finally:
                    self.win32clipboard.CloseClipboard()
            except Exception as e:
                logging.error(f"Failed to set clipboard: {e}")
                return False

def get_clipboard_handler() -> WindowsClipboard:
    """Get the clipboard handler for Windows platform"""
    try:
        return WindowsClipboard()
    except Exception as e:
        raise ClipboardError(f"Failed to initialize clipboard handler: {e}")