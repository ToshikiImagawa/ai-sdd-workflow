"""HTTP server for HTML visualization."""

import http.server
import socketserver
import webbrowser
import threading
import time
import os
import shutil
from pathlib import Path
from importlib import resources


def start_server(cache_dir: Path, data_file: str, port: int = 8000) -> None:
    """Start local HTTP server and open browser.

    Args:
        cache_dir: Cache directory containing data files
        data_file: Data file stem (e.g., "dependency-graph" or "presenter-view-graph")
        port: Port number (default: 8000, auto-increment if busy)
    """
    # Copy HTML template from package to cache directory
    template_html = cache_dir / "graph.html"
    if not template_html.exists():
        # Read template from package
        try:
            # Python 3.9+
            template_content = (
                resources.files("sdd_cli.visualizer.templates")
                .joinpath("graph.html")
                .read_text(encoding="utf-8")
            )
        except AttributeError:
            # Python 3.8 fallback
            import pkg_resources
            template_content = pkg_resources.resource_string(
                "sdd_cli.visualizer.templates", "graph.html"
            ).decode("utf-8")

        template_html.write_text(template_content, encoding="utf-8")

    # Save current directory
    original_dir = os.getcwd()

    # Find available port
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            # Change to the cache directory
            os.chdir(cache_dir)

            handler = http.server.SimpleHTTPRequestHandler

            with socketserver.TCPServer(("", port), handler) as httpd:
                url = f"http://localhost:{port}/graph.html?data={data_file}"

                print(f"✓ Server started at {url}")
                print(f"  Serving from: {cache_dir}")
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
                finally:
                    # Restore original directory
                    os.chdir(original_dir)
                break

        except OSError as e:
            if "Address already in use" in str(e):
                port += 1
                if attempt < max_attempts - 1:
                    os.chdir(original_dir)
                    continue
                else:
                    os.chdir(original_dir)
                    raise RuntimeError(
                        f"Could not find available port after {max_attempts} attempts"
                    )
            else:
                os.chdir(original_dir)
                raise
