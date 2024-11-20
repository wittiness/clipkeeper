# clipkeeper/core/manager.py
import sqlite3
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Union, Callable
import logging
from .clipboard import get_clipboard_handler, ClipboardContent, ClipboardFormat
from contextlib import contextmanager
import time

class ClipboardManager:
    def __init__(self, db_path: Optional[str] = None, check_interval: float = 0.3):
        """
        Initialize clipboard manager.
        
        Args:
            db_path: Optional custom database path
            check_interval: Clipboard check interval in seconds (default: 0.3)
        """
        self._stop_flag = threading.Event()
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._check_interval = check_interval
        self._setup_database(db_path)
        self.clipboard = get_clipboard_handler()
        self._content_handlers = []
        self._last_content = None
    
    def _setup_database(self, db_path: Optional[str] = None):
        """Set up the database file and connection."""
        if db_path is None:
            home = Path.home()
            db_dir = home / '.clipkeeper'
            db_dir.mkdir(parents=True, exist_ok=True)
            self._db_path = str(db_dir / 'clipboard.db')
        else:
            self._db_path = db_path
            
        with self._get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    hash TEXT UNIQUE NOT NULL
                )
            """)
    
    @contextmanager
    def _get_db_connection(self):
        """Thread-safe database connection context manager."""
        with self._lock:
            conn = sqlite3.connect(
                self._db_path,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate stable hash for content."""
        return hashlib.sha256(str(content).encode('utf-8')).hexdigest()
    
    def _save_clipboard(self, content: Union[str, bytes], content_type: str = "text"):
        """
        Save clipboard content with deduplication.
        
        Args:
            content: The content to save (text or base64 encoded image)
            content_type: Type of content ("text" or "image")
        """
        if not content:
            return
            
        content_hash = self._calculate_hash(content)
        try:
            with self._get_db_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO clipboard_history (content, content_type, hash)
                    VALUES (?, ?, ?)
                    ON CONFLICT(hash) DO UPDATE SET timestamp=CURRENT_TIMESTAMP
                    """,
                    (content, content_type, content_hash)
                )
        except Exception as e:
            logging.error(f"Error saving to database: {e}")

    def add_content_handler(self, handler: Callable[[ClipboardContent], None]):
        """Add a callback function to handle new content"""
        if handler not in self._content_handlers:
            self._content_handlers.append(handler)

    def remove_content_handler(self, handler: Callable[[ClipboardContent], None]):
        """Remove a content handler callback"""
        if handler in self._content_handlers:
            self._content_handlers.remove(handler)

    def _handle_new_content(self, content: ClipboardContent):
        """Handle new clipboard content"""
        try:
            if content.content is not None and content.content != self._last_content:
                self._last_content = content.content
                
                self._save_clipboard(
                    content.content,
                    "text" if content.format == ClipboardFormat.TEXT else "image"
                )
                
                for handler in self._content_handlers:
                    try:
                        handler(content)
                    except Exception as e:
                        logging.error(f"Error in content handler: {e}")
                        
        except Exception as e:
            logging.error(f"Error handling new content: {e}")

    def monitor_clipboard(self):
        """Monitor clipboard with enhanced error handling"""
        while not self._stop_flag.is_set():
            try:
                content_result = self.clipboard.get_clipboard()
                if content_result and content_result.content is not None:
                    self._handle_new_content(content_result)
                
                time.sleep(0.1)
                
                image_result = self.clipboard.get_clipboard_image()
                if image_result and image_result.content is not None:
                    self._handle_new_content(image_result)
                    
            except Exception as e:
                logging.error(f"Clipboard monitoring error: {e}")
                time.sleep(0.1)
            
            self._stop_flag.wait(self._check_interval)
    
    def get_history(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Retrieve clipboard history with pagination."""
        with self._get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, content, content_type, timestamp 
                FROM clipboard_history 
                ORDER BY timestamp DESC, id DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            )
            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ]
        
    def clear_history(self):
        """Clear all clipboard history."""
        with self._get_db_connection() as conn:
            conn.execute("DELETE FROM clipboard_history")
    
    def search_history(self, pattern: str, limit: int = 100) -> List[Dict]:
        """Search clipboard history for pattern."""
        with self._get_db_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, content, content_type, timestamp 
                FROM clipboard_history 
                WHERE content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT ?
                """,
                (f"%{pattern}%", limit)
            )
            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'content_type': row[2],
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ]
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a specific clipboard history item."""
        try:
            with self._get_db_connection() as conn:
                conn.execute(
                    "DELETE FROM clipboard_history WHERE id = ?",
                    (item_id,)
                )
                return True
        except Exception as e:
            logging.error(f"Error deleting item: {e}")
            return False

    def start_monitoring(self):
        """Start clipboard monitoring"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_flag.clear()
            self._monitor_thread = threading.Thread(target=self.monitor_clipboard)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            logging.info("Clipboard monitoring started")

    def stop_monitoring(self):
        """Stop clipboard monitoring"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._stop_flag.set()
            self._monitor_thread.join(timeout=5.0)
            if self._monitor_thread.is_alive():
                logging.warning("Monitor thread did not stop cleanly")
            else:
                logging.info("Clipboard monitoring stopped")

    def __enter__(self):
        """Context manager support"""
        self.start_monitoring()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure cleanup on context manager exit"""
        self.stop_monitoring()