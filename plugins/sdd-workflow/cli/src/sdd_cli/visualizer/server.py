"""HTTP server for HTML visualization."""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path
from importlib import resources


class StaticFileHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves from both static and cache directories."""

    def __init__(self, *args, static_dir=None, cache_dir=None, **kwargs):
        self.static_dir = static_dir
        self.cache_dir = cache_dir
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Translate URL path to file system path.

        Serves HTML/CSS/JS files from static directory, other files from cache directory.
        """
        # Get the path without query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]

        # Default to index.html
        if path == '':
            path = 'index.html'

        # Serve static files (HTML, CSS, JS) from static directory
        if (path.endswith('.html') or
            path.endswith('.css') or path.startswith('css/') or
            path.endswith('.js') or path.startswith('js/')):
            file_path = self.static_dir / path
        else:
            # JSON data files from cache directory
            file_path = self.cache_dir / path

        return str(file_path)


def start_server(cache_dir: Path, data_file: str, port: int = 8000) -> None:
    """Start local HTTP server and open browser.

    Args:
        cache_dir: Cache directory containing data files
        data_file: Data file stem (kept for backward compatibility, no longer used in URL)
        port: Port number (default: 8000, auto-increment if busy)
    """
    # Get static directory from package
    try:
        # First try to use __path__ attribute (works with editable installs)
        import sdd_cli.visualizer.static as static_module
        if hasattr(static_module, '__path__'):
            static_dir = Path(list(static_module.__path__)[0])
        else:
            # Python 3.9+
            static_files = resources.files("sdd_cli.visualizer.static")
            # Convert to Path - handle MultiplexedPath by getting the actual file path
            if hasattr(static_files, '__fspath__'):
                static_dir = Path(static_files.__fspath__())
            else:
                # Fallback: get path from a known file
                static_dir = Path(str(static_files._paths[0]) if hasattr(static_files, '_paths') else str(static_files))
    except (AttributeError, Exception):
        # Python 3.8 fallback or any error
        import pkg_resources
        static_dir = Path(pkg_resources.resource_filename("sdd_cli.visualizer.static", ""))

    # Find available port
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Create handler with both directories
            def handler_factory(*args, **kwargs):
                return StaticFileHTTPRequestHandler(
                    *args,
                    static_dir=static_dir,
                    cache_dir=cache_dir,
                    **kwargs
                )

            with socketserver.TCPServer(("", port), handler_factory) as httpd:
                url = f"http://localhost:{port}/"

                print(f"✓ Server started at {url}")
                print(f"  Static files from: {static_dir}")
                print(f"  Data from: {cache_dir}")
                print(f"  Press Ctrl+C to stop the server\n")

                # Open browser after a short delay
                def open_browser():
                    time.sleep(1.0)
                    webbrowser.open(url)

                browser_thread = threading.Thread(target=open_browser)
                browser_thread.daemon = True
                browser_thread.start()

                try:
                    # Start server (this blocks until Ctrl+C)
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\n\n✓ Server stopped")
                break

        except OSError as e:
            if "Address already in use" in str(e):
                port += 1
                if attempt < max_attempts - 1:
                    continue
                else:
                    raise RuntimeError(
                        f"Could not find available port after {max_attempts} attempts"
                    )
            else:
                raise
