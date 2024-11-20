# clipkeeper/run.py
import logging
import webbrowser
import time
from clipkeeper import ClipboardManager, WebInterface

def setup_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    setup_logging()
    logging.info("Starting Clipkeeper...")
    
    try:
        manager = ClipboardManager()
        manager.start_monitoring()
        logging.info("✓ Clipboard monitoring started")
        
        web = WebInterface(manager, host='127.0.0.1', port=5000)
        
        url = f"http://{web.host}:{web.port}"
        logging.info(f"✓ Opening web interface at {url}")
        time.sleep(1)
        webbrowser.open(url)
        
        logging.info("\nClipkeeper is running!")
        logging.info("- Copy some text to see it appear in the web interface")
        logging.info("- Press Ctrl+C to stop")
        
        web.run()
        
    except KeyboardInterrupt:
        logging.info("\nShutting down...")
        manager.stop_monitoring()
    except Exception as e:
        logging.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()