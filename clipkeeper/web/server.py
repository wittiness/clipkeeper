# clipkeeper/web/server.py
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import threading
from datetime import datetime
import logging
import time

class WebInterface:
    def __init__(self, clipboard_manager, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        self.clipboard_manager = clipboard_manager
        self.host = host
        self.port = port
        
        # Register routes and socket events
        self.register_routes()
        self.register_socket_events()
        
        # Add handler for new clipboard content
        self.clipboard_manager.add_content_handler(self._on_new_clipboard_content)

    def _on_new_clipboard_content(self, content):
        """Broadcast new clipboard content to all connected clients"""
        try:
            time.sleep(0.1)
            items = self.clipboard_manager.get_history(limit=50)
            self.socketio.emit('history_update', items)
        except Exception as e:
            logging.error(f"Error broadcasting update: {e}")

    def register_socket_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            try:
                items = self.clipboard_manager.get_history(limit=50)
                self.socketio.emit('history_update', items)
            except Exception as e:
                logging.error(f"Error sending initial history: {e}")

    def register_routes(self):
        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/api/history')
        def get_history():
            search_query = request.args.get('search', '')
            try:
                if search_query:
                    items = self.clipboard_manager.search_history(search_query, limit=50)
                else:
                    items = self.clipboard_manager.get_history(limit=50)
                return jsonify(items)
            except Exception as e:
                logging.error(f"Error retrieving history: {e}")
                return jsonify({'error': 'Failed to retrieve history'}), 500

        @self.app.route('/api/copy/<int:item_id>', methods=['POST'])
        def copy_item(item_id):
            try:
                with self.clipboard_manager._get_db_connection() as conn:
                    cursor = conn.execute(
                        """
                        SELECT content, content_type 
                        FROM clipboard_history 
                        WHERE id = ?
                        """,
                        (item_id,)
                    )
                    result = cursor.fetchone()
                    
                    if result:
                        content, content_type = result
                        success = self.clipboard_manager.clipboard.set_clipboard(content, content_type)
                        if success:
                            return jsonify({'success': True})
                        return jsonify({'error': 'Failed to set clipboard'}), 500
                    return jsonify({'error': 'Item not found'}), 404
            except Exception as e:
                logging.error(f"Error copying item: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/delete/<int:item_id>', methods=['DELETE'])
        def delete_item(item_id):
            try:
                success = self.clipboard_manager.delete_item(item_id)
                if success:
                    # Broadcast update after deletion
                    items = self.clipboard_manager.get_history(limit=50)
                    self.socketio.emit('history_update', items)
                    return jsonify({'success': True})
                return jsonify({'error': 'Item not found'}), 404
            except Exception as e:
                logging.error(f"Error deleting item: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.errorhandler(Exception)
        def handle_error(e):
            logging.error(f"Unhandled error: {e}")
            return jsonify({'error': str(e)}), 500

    def run(self):
        """Run the web interface with WebSocket support"""
        try:
            self.socketio.run(self.app, host=self.host, port=self.port, debug=False)
        except Exception as e:
            logging.error(f"Failed to start server: {e}")
            raise