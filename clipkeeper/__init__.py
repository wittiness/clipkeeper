# clipkeeper/__init__.py
"""
Clipkeeper - A Windows-based clipboard history manager.
"""
from .core import ClipboardManager
from .web import WebInterface
from .utils import logger

__version__ = "0.1.4"
__author__ = "wittiness"
__license__ = "MIT"

__all__ = ["ClipboardManager", "WebInterface", "logger"]