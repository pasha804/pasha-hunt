"""Pasha Hunt 2.0 — APINEX Edition Desktop Workstation
1:1 Pixel-Perfect Modern Desktop Architecture (Picture 2)
Powered by PySide6 & QWebEngineView with native background worker threads and local IPC server.
"""
import sys
import os
import json
import threading
import time
from PySide6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bot
import desktop_server

# Intercept CLI commands when packaged
if len(sys.argv) > 1 and sys.argv[1] == "--bot":
    del sys.argv[1]
    bot.main()
    sys.exit(0)
elif len(sys.argv) > 1 and sys.argv[1] == "--cv":
    del sys.argv[1]
    try:
        import cv
        cv.main()
    except Exception as e:
        sys.stderr.write(f"CV error: {e}\n")
    sys.exit(0)


class WorkstationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pasha Hunt 2.0 — APINEX Edition")
        self.resize(1360, 880)
        self.setMinimumSize(1100, 720)

        # Set Icon
        icon_path = os.path.join(HERE, "installer", "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Start Local IPC Server on 127.0.0.1:58241 if not already running
        self.port = 58241
        self.server_thread = threading.Thread(
            target=desktop_server.start_server,
            args=(self.port,),
            daemon=True
        )
        self.server_thread.start()
        time.sleep(0.3)

        # WebEngine View
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.setCentralWidget(self.browser)

        # Load from local server
        self.browser.setUrl(QtCore.QUrl(f"http://127.0.0.1:{self.port}/"))

        # Background Scraper Thread state
        self.is_scanning = False

    def scan_jobs_async(self):
        """Asynchronously runs the 18 scraper feeds without blocking the GUI."""
        if self.is_scanning:
            return
        self.is_scanning = True
        threading.Thread(target=self._run_scrapers, daemon=True).start()

    def _run_scrapers(self):
        try:
            bot.src_all()
        except Exception as e:
            print("Scraper error:", e)
        finally:
            self.is_scanning = False


def main():
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = WorkstationWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
