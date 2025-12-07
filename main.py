# quest_master/main.py
import sys
import os
# Ensure the script directory is on sys.path so local modules import reliably
sys.path.insert(0, os.path.dirname(__file__) or os.getcwd())
from PyQt6.QtWidgets import QApplication

# Ensure project root is on sys.path so package imports like `gui.*` resolve
base_dir = os.path.dirname(__file__) or os.getcwd()
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Try to import the window from the `gui` package (preferred).
try:
    # Some modules inside `gui/` use bare imports (e.g., `from quest_wizard import ...`).
    # To support that style, ensure `gui/` directory itself is on sys.path too.
    gui_dir = os.path.join(base_dir, 'gui')
    if gui_dir not in sys.path:
        sys.path.insert(0, gui_dir)
    from gui.main_window import MainWindow
except Exception:
    # Fallback: try to load gui/main_window.py directly from disk.
    import importlib.util
    from pathlib import Path
    base = Path(__file__).resolve().parent
    mod_path = str(base.joinpath('gui', 'main_window.py'))
    spec = importlib.util.spec_from_file_location('gui.main_window', mod_path)
    if spec and spec.loader:
        mw = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mw)
            MainWindow = getattr(mw, 'MainWindow')
        except FileNotFoundError:
            # As last resort, read-and-exec the file content
            with open(mod_path, 'r', encoding='utf-8') as f:
                src = f.read()
            mw_globals = {}
            exec(compile(src, mod_path, 'exec'), mw_globals)
            MainWindow = mw_globals.get('MainWindow')
            if MainWindow is None:
                raise
    else:
        raise

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Try to load an application-wide stylesheet (blue theme)
    try:
        with open("assets/theme_blue.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        # fallback: no stylesheet
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())