"""HTTP server for HTML visualization."""

import http.server
import socketserver
import webbrowser
import threading
import time
from pathlib import Path
from importlib import resources


class DualDirectoryHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that serves from both template and cache directories."""

    def __init__(self, *args, template_dir=None, cache_dir=None, **kwargs):
        self.template_dir = template_dir
        self.cache_dir = cache_dir
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        """Translate URL path to file system path.

        Serves .html files from template directory, other files from cache directory.
        """
        # Get the path without query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]

        # Remove leading slash
        if path.startswith('/'):
            path = path[1:]

        # If requesting .html file, serve from template directory
        if path.endswith('.html') or path == '':
            if path == '':
                path = 'graph.html'
            file_path = self.template_dir / path
        else:
            # Otherwise serve from cache directory (JSON files, etc.)
            file_path = self.cache_dir / path

        return str(file_path)


def start_server(cache_dir: Path, data_file: str, port: int = 8000) -> None:
    """Start local HTTP server and open browser.

    Args:
        cache_dir: Cache directory containing data files
        data_file: Data file stem (e.g., "dependency-graph" or "presenter-view-graph")
        port: Port number (default: 8000, auto-increment if busy)
    """
    # Get template directory from package
    try:
        # Python 3.9+
        template_files = resources.files("sdd_cli.visualizer.templates")
        # Convert to Path - handle MultiplexedPath by getting the actual file path
        if hasattr(template_files, '__fspath__'):
            template_dir = Path(template_files.__fspath__())
        else:
            # Fallback: get path from a known file
            template_dir = Path(str(template_files._paths[0]) if hasattr(template_files, '_paths') else str(template_files))
    except (AttributeError, Exception):
        # Python 3.8 fallback or any error
        import pkg_resources
        template_dir = Path(pkg_resources.resource_filename("sdd_cli.visualizer.templates", ""))

    # Find available port
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Create handler with both directories
            def handler_factory(*args, **kwargs):
                return DualDirectoryHTTPRequestHandler(
                    *args,
                    template_dir=template_dir,
                    cache_dir=cache_dir,
                    **kwargs
                )

            with socketserver.TCPServer(("", port), handler_factory) as httpd:
                url = f"http://localhost:{port}/graph.html?data={data_file}"

                print(f"✓ Server started at {url}")
                print(f"  Template from: {template_dir}")
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
