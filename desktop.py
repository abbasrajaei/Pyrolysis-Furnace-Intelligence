"""Desktop launcher for Pyrolysis Furnace Intelligence."""
from __future__ import annotations

import argparse
import sys
import threading
import time
from urllib.error import URLError
from urllib.request import urlopen

from werkzeug.serving import make_server

from app.app import server

APP_TITLE = "Pyrolysis Furnace Intelligence"
HOST = "127.0.0.1"


class LocalApplicationServer:
    def __init__(self) -> None:
        self._httpd = make_server(HOST, 0, server, threaded=True)
        self.port = int(self._httpd.server_port)
        self.url = f"http://{HOST}:{self.port}"
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            name="furnace-workbench-server",
            daemon=True,
        )

    def start(self) -> None:
        self._thread.start()
        self.wait_until_ready()

    def wait_until_ready(self, timeout: float = 12.0) -> None:
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                with urlopen(self.url, timeout=0.75) as response:
                    if response.status == 200:
                        return
            except (OSError, URLError) as exc:
                last_error = exc
                time.sleep(0.08)
        raise RuntimeError("Local application server did not become ready") from last_error

    def shutdown(self) -> None:
        if self._thread.is_alive():
            self._httpd.shutdown()
            self._thread.join(timeout=3.0)
        self._httpd.server_close()


def smoke_test() -> int:
    local = LocalApplicationServer()
    try:
        local.start()
        with urlopen(local.url, timeout=3.0) as response:
            if response.status != 200:
                raise RuntimeError(f"Application root returned HTTP {response.status}")
            if b"Pyrolysis Furnace Intelligence" not in response.read():
                raise RuntimeError("Application title was not found in the rendered page")
        with urlopen(f"{local.url}/assets/workbench.css", timeout=3.0) as response:
            if response.status != 200 or len(response.read()) < 100:
                raise RuntimeError("Bundled stylesheet check failed")
        return 0
    finally:
        local.shutdown()


def _show_startup_error(message: str) -> None:
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0, message, f"{APP_TITLE} - Startup error", 0x10
            )
            return
        except Exception:
            pass
    print(message, file=sys.stderr)


def run_desktop() -> int:
    local = LocalApplicationServer()
    try:
        local.start()
        import webview

        webview.create_window(
            APP_TITLE,
            local.url,
            width=1540,
            height=920,
            min_size=(1100, 700),
            background_color="#07121D",
        )
        webview.start(debug=False)
        return 0
    except Exception as exc:
        _show_startup_error(
            "Pyrolysis Furnace Intelligence could not start.\n\n"
            f"{type(exc).__name__}: {exc}\n\n"
            "The Windows desktop shell requires Microsoft Edge WebView2 Runtime."
        )
        return 1
    finally:
        local.shutdown()


def main() -> int:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    return smoke_test() if args.smoke_test else run_desktop()


if __name__ == "__main__":
    raise SystemExit(main())
