# clipkeeper/cli/commands.py
import click
from pathlib import Path
import sys
import webbrowser
import logging
from ..core import ClipboardManager
from ..web import WebInterface
from ..utils import logger, setup_logger

if sys.platform != "win32":
    raise EnvironmentError(
        "Clipkeeper is only supported on Windows. Future updates will include cross-platform support."
    )

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--log-file', type=click.Path(), help='Path to log file')
def cli(debug, log_file):
    """Clipkeeper - Cross-platform clipboard history manager"""
    log_level = logging.DEBUG if debug else logging.INFO
    if log_file:
        setup_logger(level=log_level, log_file=Path(log_file))
    else:
        setup_logger(level=log_level)

@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=5000, help='Port to listen on')
@click.option('--browser/--no-browser', default=True, help='Open web browser automatically')
def start(host, port, browser):
    """Start the clipboard manager and web interface"""
    try:
        manager = ClipboardManager()
        manager.start_monitoring()
        logger.info("Clipboard monitoring started")

        web = WebInterface(manager, host=host, port=port)
        url = f"http://{host}:{port}"
        
        if browser:
            webbrowser.open(url)
            
        logger.info(f"Web interface available at {url}")
        web.app.run(host=host, port=port)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        manager.stop_monitoring()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

@cli.command()
@click.option('--limit', default=10, help='Number of items to show')
def history(limit):
    """Show clipboard history in the terminal"""
    try:
        manager = ClipboardManager()
        items = manager.get_history(limit=limit)
        
        if not items:
            click.echo("No clipboard history found.")
            return

        for item in items:
            click.echo("-" * 40)
            click.echo(f"Time: {item['timestamp']}")
            click.echo(f"Content: {item['content'][:100]}...")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

@cli.command()
def clear():
    """Clear clipboard history"""
    try:
        if click.confirm("Are you sure you want to clear all clipboard history?"):
            manager = ClipboardManager()
            manager.clear_history()
            click.echo("Clipboard history cleared.")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

@cli.command()
@click.argument('pattern')
def search(pattern):
    """Search clipboard history"""
    try:
        manager = ClipboardManager()
        items = manager.search_history(pattern)
        
        if not items:
            click.echo("No matching items found.")
            return

        for item in items:
            click.echo("-" * 40)
            click.echo(f"Time: {item['timestamp']}")
            click.echo(f"Content: {item['content'][:100]}...")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    cli()