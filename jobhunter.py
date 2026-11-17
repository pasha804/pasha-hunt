"""Entry point of the installed JobHunter.exe / PashaHunt.exe.

One exe does everything, so the installed app needs no Python:
  PashaHunt.exe              the workstation window (desktop_app.py)
  PashaHunt.exe --bot ...    a bot run, with bot.py's own options (used by the window and Auto-run)
  PashaHunt.exe --cv ...     build a CV or cover letter PDF (used by bot.py)

From source, keep using python -I desktop_app.py / bot.py / cv.py.
"""
import io
import os
import sys
import traceback


def log_crash(error_msg):
    """Write crash diagnostics to disk and display a user-friendly message."""
    try:
        local_app = os.environ.get("LOCALAPPDATA", "")
        log_dir = os.path.join(local_app, "Pasha Hunt") if local_app else os.path.expanduser("~")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "crash.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- CRASH AT {os.path.basename(sys.executable)} ---\n")
            f.write(error_msg + "\n")
    except Exception:
        pass

    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Pasha Hunt encountered an error starting the workstation:\n\n{error_msg[:400]}\n\nSee {log_file} for details.",
            "Pasha Hunt Startup Error",
            0x10  # MB_ICONERROR
        )
    except Exception:
        pass


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("--bot", "--cv") else None
    if mode:
        del sys.argv[1]  # bot.py and cv.py read their own options from sys.argv
    # A windowed exe has no console. The window reads the bot's output through a pipe, in UTF-8;
    # Auto-run has nowhere to write it, and runs.log keeps the summary anyway.
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name)
        if stream is None:
            setattr(sys, name, open(os.devnull, "w", encoding="utf-8"))
        elif isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    if mode == "--bot":
        import bot
        bot.main()
    elif mode == "--cv":
        import cv
        cv.main()
    else:
        try:
            # Check for live desktop_app.py on disk (in app dir or _internal)
            base_dir = os.path.dirname(os.path.abspath(sys.executable)) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            disk_candidates = [
                os.path.join(base_dir, "desktop_app.py"),
                os.path.join(base_dir, "_internal", "desktop_app.py"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "desktop_app.py")
            ]
            loaded_external = False
            for p in disk_candidates:
                if os.path.exists(p):
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location("desktop_app", p)
                        if spec and spec.loader:
                            mod = importlib.util.module_from_spec(spec)
                            sys.modules["desktop_app"] = mod
                            spec.loader.exec_module(mod)
                            mod.main()
                            loaded_external = True
                            break
                    except Exception as ex:
                        sys.stderr.write(f"Failed loading disk desktop_app from {p}: {ex}\n")
            if not loaded_external:
                import desktop_app
                desktop_app.main()
        except Exception as e:
            tb = traceback.format_exc()
            log_crash(f"{e}\n{tb}")
            try:
                import gui
                gui.App().mainloop()
            except Exception:
                pass


if __name__ == "__main__":
    main()
