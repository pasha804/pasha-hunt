"""Pasha Hunt 2.0 — APINEX Edition Desktop Workstation
1:1 Pixel-Perfect Modern Desktop Architecture (Picture 2)
Integrated with Native Cinematic Splash Screen (OpenCV + PySide6),
Dynamic Candidate Intelligence, Real-Time MX Verification,
and Local REST IPC Server on 127.0.0.1:58241.
"""
import sys
import os
import json
import threading
import time
import urllib.request
import cv2
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


class NativeVideoSplash(QtWidgets.QWidget):
    finished = QtCore.Signal()

    def __init__(self, video_path):
        super().__init__()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, False)
        self.setStyleSheet("background-color: #070A0E;")
        
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        
        # 16:9 cinematic aspect ratio centered
        self.video_w = 960
        self.video_h = 540
        self.resize(self.video_w, self.video_h)
        
        # Center on primary monitor
        screen = QtGui.QGuiApplication.primaryScreen().geometry()
        x = (screen.width() - self.video_w) // 2
        y = (screen.height() - self.video_h) // 2
        self.move(x, y)
        
        # Video render canvas
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(0, 0, self.video_w, self.video_h)
        self.label.setScaledContents(True)

        # Skip Intro Button
        self.skip_btn = QtWidgets.QPushButton("Skip Intro [Esc] ⏭", self)
        self.skip_btn.setGeometry(self.video_w - 180, self.video_h - 55, 160, 36)
        self.skip_btn.setCursor(QtGui.Qt.PointingHandCursor)
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(14, 19, 24, 0.88);
                border: 1px solid #FF6B00;
                color: #FFFFFF;
                font-family: -apple-system, Segoe UI, sans-serif;
                font-size: 12px;
                font-weight: 700;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #FF6B00;
                color: #000000;
            }
        """)
        self.skip_btn.clicked.connect(self.close_and_finish)

        # 24 FPS timer (~41ms)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(41)

    def next_frame(self):
        if not self.cap or not self.cap.isOpened():
            self.close_and_finish()
            return
        ret, frame = self.cap.read()
        if not ret:
            self.close_and_finish()
            return
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        q_img = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        self.label.setPixmap(QtGui.QPixmap.fromImage(q_img))

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Escape, QtCore.Qt.Key_Space, QtCore.Qt.Key_Return):
            self.close_and_finish()

    def mousePressEvent(self, event):
        self.close_and_finish()

    def close_and_finish(self):
        if hasattr(self, "timer") and self.timer.isActive():
            self.timer.stop()
        if hasattr(self, "cap") and self.cap:
            self.cap.release()
            self.cap = None
        self.finished.emit()


class WorkstationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pasha Hunt 2.0 — APINEX Edition")
        self.resize(1360, 880)
        self.setMinimumSize(1100, 720)

        # Set native dark background to eliminate any flicker or white flash
        self.setAttribute(QtCore.Qt.WA_NativeWindow, True)
        self.setStyleSheet("background-color: #070A0E; color: #FFFFFF;")

        # Set Application Icon
        icon_path = os.path.join(HERE, "installer", "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(HERE, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Port for IPC Server
        self.port = 58241

        # Connect replay callback
        desktop_server.set_replay_intro_callback(self.replay_intro)

        # WebEngine View with dark background
        self.browser = QtWebEngineWidgets.QWebEngineView(self)
        self.browser.setStyleSheet("background-color: #070A0E;")
        self.browser.page().setBackgroundColor(QtGui.QColor("#070A0E"))
        self.setCentralWidget(self.browser)

        # Resilient auto-reload on load failure / ERR_EMPTY_RESPONSE
        self._page_ready = False
        self.browser.loadFinished.connect(self._on_load_finished)

        # Keyboard shortcuts
        self.refresh_shortcut = QtGui.QShortcut(QtGui.QKeySequence("F5"), self)
        self.refresh_shortcut.activated.connect(self.browser.reload)
        self.ctrl_r_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        self.ctrl_r_shortcut.activated.connect(self.browser.reload)

        # Initial URL load
        self.browser.setUrl(QtCore.QUrl(f"http://127.0.0.1:{self.port}/"))

        # Background Scraper Thread state
        self.is_scanning = False

    def _on_load_finished(self, success):
        if success:
            self._page_ready = True
        else:
            if not self._page_ready:
                print(f"[Workstation] WebEngine load returned empty/failed. Retrying connection to http://127.0.0.1:{self.port}/...")
                QtCore.QTimer.singleShot(400, lambda: self.browser.setUrl(QtCore.QUrl(f"http://127.0.0.1:{self.port}/")))

    def replay_intro(self):
        """Replays cinematic intro splash natively upon user request."""
        video_path = os.path.join(HERE, "intro.mp4")
        if not os.path.exists(video_path):
            video_path = os.path.join(os.path.dirname(HERE), "intro.mp4")
        if os.path.exists(video_path):
            self.splash = NativeVideoSplash(video_path)
            self.splash.finished.connect(self.splash.close)
            self.splash.show()

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
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Pasha Hunt 2.0")

    # Set dark Fusion palette application-wide to prevent white flash
    app.setStyle("Fusion")
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#070A0E"))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#E2E8F0"))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#070A0E"))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#0E1318"))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor("#070A0E"))
    palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColor("#FFFFFF"))
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#E2E8F0"))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#0E1318"))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#FFFFFF"))
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#FF6B00"))
    palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor("#000000"))
    app.setPalette(palette)

    # Start Local IPC Server on 127.0.0.1:58241
    port = 58241
    server_thread = threading.Thread(
        target=desktop_server.start_server,
        args=(port,),
        daemon=True
    )
    server_thread.start()

    # Locate intro.mp4
    video_path = os.path.join(HERE, "intro.mp4")
    if not os.path.exists(video_path):
        video_path = os.path.join(os.path.dirname(HERE), "intro.mp4")

    # Initialize main window
    window = WorkstationWindow()

    # If video exists, play Native Video Splash first
    if os.path.exists(video_path):
        splash = NativeVideoSplash(video_path)
        
        def on_splash_done():
            # Show and bring window to front FIRST before closing splash to ensure zero flicker
            window.show()
            window.raise_()
            window.activateWindow()
            QtCore.QTimer.singleShot(150, splash.close)

        splash.finished.connect(on_splash_done)
        splash.show()
    else:
        window.show()
        window.raise_()
        window.activateWindow()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
