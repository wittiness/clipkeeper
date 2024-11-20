# clipkeeper/core/__init__.py
"""
Core functionality for clipboard management.
"""
from .manager import ClipboardManager
from .clipboard import WindowsClipboard, get_clipboard_handler

__all__ = [
    "ClipboardManager",
    "WindowsClipboard",
    "get_clipboard_handler"
]