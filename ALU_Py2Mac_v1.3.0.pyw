#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ALU Py2Mac v1.3.0
Μετατρέπει μια Python εφαρμογή (.py / .pyw) σε macOS .app (+ προαιρετικά .dmg / .zip).

Developer: Nikolaos K. Paridis (aka nikkpap) — ALU DEV TEAM

Τρέχει σε macOS. Στην πρώτη εκκίνηση φτιάχνει μόνο του ένα ιδιωτικό περιβάλλον Python
(~/Library/Application Support/ALU_Py2Mac/venv) και εγκαθιστά ό,τι χρειάζεται
(PyQt6, PyInstaller). Δεν χρειάζεται να εγκαταστήσεις τίποτα με το χέρι.

Εκκίνηση:  python3 ALU_Py2Mac_v1.3.0.pyw
"""

APP_NAME = "ALU Py2Mac"
APP_VERSION = "1.3.0"
DEVELOPER = "Nikolaos K. Paridis (aka nikkpap)"

import os
import sys
import subprocess

# ----------------------------------------------------------------------------
# 1) BOOTSTRAP: ιδιωτικό venv + αυτόματη εγκατάσταση εξαρτήσεων
# ----------------------------------------------------------------------------
if sys.platform == "darwin":
    HOME_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "ALU_Py2Mac")
else:
    HOME_DIR = os.path.join(os.path.expanduser("~"), ".alu_py2mac")
VENV_DIR = os.path.join(HOME_DIR, "venv")
if os.name == "nt":
    VENV_PY = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    VENV_PY = os.path.join(VENV_DIR, "bin", "python3")
BASE_PACKAGES = ["PyQt6", "pyinstaller", "Pillow"]
OPTIONAL_PACKAGES = ["pillow-heif"]  # φωτογραφίες HEIC από iPhone


def _notify(msg):
    print(f"[{APP_NAME}] {msg}", flush=True)
    if sys.platform == "darwin":
        try:
            safe = msg.replace('"', "'")
            subprocess.run(["osascript", "-e", f'display notification "{safe}" with title "{APP_NAME}"'],
                           timeout=5, capture_output=True)
        except Exception:
            pass


def _fatal(msg):
    print(f"[{APP_NAME}] ΣΦΑΛΜΑ: {msg}", flush=True)
    if sys.platform == "darwin":
        try:
            safe = msg.replace('"', "'").replace("\\", "/")
            subprocess.run(["osascript", "-e",
                            f'display dialog "{safe}" with title "{APP_NAME}" buttons {{"OK"}} with icon stop'],
                           timeout=300, capture_output=True)
        except Exception:
            pass
    sys.exit(1)


def _in_our_venv():
    try:
        return os.path.realpath(sys.prefix) == os.path.realpath(VENV_DIR)
    except Exception:
        return False


def _bootstrap():
    if sys.version_info < (3, 9):
        _fatal("Χρειάζεται Python 3.9 ή νεότερη. Κατέβασέ την από https://www.python.org/downloads/macos/")

    if not _in_our_venv():
        if not os.path.exists(VENV_PY):
            _notify("Πρώτη εκκίνηση: δημιουργία περιβάλλοντος Python…")
            os.makedirs(HOME_DIR, exist_ok=True)
            r = subprocess.run([sys.executable, "-m", "venv", "--clear", VENV_DIR])
            if r.returncode != 0 or not os.path.exists(VENV_PY):
                _fatal("Δεν μπόρεσα να δημιουργήσω περιβάλλον Python (venv).\n"
                       "Εγκατάστησε την Python από python.org και ξαναδοκίμασε.")
        os.execv(VENV_PY, [VENV_PY, os.path.abspath(__file__)] + sys.argv[1:])

    missing = []
    for mod, pkg in (("PyQt6.QtWidgets", "PyQt6"), ("PyInstaller", "pyinstaller"), ("PIL.Image", "Pillow")):
        try:
            __import__(mod)
        except Exception:
            missing.append(pkg)
    if missing:
        _notify("Εγκατάσταση εργαλείων (PyQt6, PyInstaller, Pillow)… 1-3 λεπτά, περίμενε.")
        env = dict(os.environ, PIP_DISABLE_PIP_VERSION_CHECK="1")
        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], env=env)
        r = subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade"] + BASE_PACKAGES, env=env)
        if r != 0:
            _fatal("Αποτυχία εγκατάστασης PyQt6 / PyInstaller / Pillow. Έλεγξε τη σύνδεση στο internet.")
        subprocess.call([sys.executable, "-m", "pip", "install"] + OPTIONAL_PACKAGES, env=env)  # προαιρετικό
        _notify("Τα εργαλεία εγκαταστάθηκαν. Ξεκινάω…")


LOG_FILE = os.path.join(HOME_DIR, "py2mac.log")


def _detach_from_terminal():
    """Αν ανοίξαμε από Terminal: ξαναξεκινάμε στο παρασκήνιο και κλείνουμε το παράθυρο του Terminal."""
    if sys.platform != "darwin" or os.environ.get("ALU_PY2MAC_CHILD") or "--console" in sys.argv:
        return
    try:
        if not sys.stdin or not sys.stdin.isatty():
            return
        tty = os.ttyname(sys.stdin.fileno())
    except Exception:
        return
    env = dict(os.environ, ALU_PY2MAC_CHILD="1")
    try:
        log = open(LOG_FILE, "a", encoding="utf-8")
        subprocess.Popen([sys.executable, os.path.abspath(__file__)] + sys.argv[1:],
                         stdin=subprocess.DEVNULL, stdout=log, stderr=log, env=env,
                         cwd=os.path.expanduser("~"), start_new_session=True)
    except Exception:
        return  # αν κάτι πάει στραβά, συνεχίζουμε κανονικά μέσα στο Terminal
    if os.environ.get("TERM_PROGRAM") == "Apple_Terminal":
        script = (
            'delay 0.8\n'
            'tell application "Terminal"\n'
            '  repeat with w in windows\n'
            '    try\n'
            f'      if (count of tabs of w) is 1 and tty of (tab 1 of w) is "{tty}" then\n'
            '        close w\n'
            '        exit repeat\n'
            '      end if\n'
            '    end try\n'
            '  end repeat\n'
            'end tell')
        try:
            subprocess.Popen(["osascript", "-e", script], stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception:
            pass
    print(f"[{APP_NAME}] Άνοιξε το παράθυρο. Το Terminal μπορεί να κλείσει.", flush=True)
    os._exit(0)


_bootstrap()
_detach_from_terminal()

# ----------------------------------------------------------------------------
# 2) ΚΥΡΙΑ ΕΦΑΡΜΟΓΗ
# ----------------------------------------------------------------------------
import ast
import json
import re
import shlex
import shutil
import plistlib
import tempfile
import datetime

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QEvent, QTimer
from PyQt6.QtGui import QFont, QDesktopServices, QTextCursor, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QGroupBox, QPlainTextEdit, QCheckBox, QComboBox,
    QListWidget, QListWidgetItem, QProgressBar, QMessageBox, QScrollArea, QSplitter, QFrame,
    QStackedWidget,
)

SETTINGS_FILE = os.path.join(HOME_DIR, "settings.json")
BUILD_CACHE = os.path.join(HOME_DIR, "build")
IS_MAC = sys.platform == "darwin"

# import-name -> pip-name
IMPORT_TO_PIP = {
    "cv2": "opencv-python", "PIL": "Pillow", "yaml": "PyYAML", "sklearn": "scikit-learn",
    "bs4": "beautifulsoup4", "skimage": "scikit-image", "dateutil": "python-dateutil",
    "docx": "python-docx", "pptx": "python-pptx", "fitz": "PyMuPDF", "pymupdf": "PyMuPDF",
    "serial": "pyserial", "usb": "pyusb", "Crypto": "pycryptodome", "Cryptodome": "pycryptodomex",
    "OpenSSL": "pyOpenSSL", "jwt": "PyJWT", "dotenv": "python-dotenv", "magic": "python-magic",
    "attr": "attrs", "google": "protobuf", "telegram": "python-telegram-bot", "gi": "PyGObject",
    "wx": "wxPython", "Levenshtein": "python-Levenshtein", "osgeo": "GDAL", "qrcode": "qrcode",
    "pyzbar": "pyzbar", "zmq": "pyzmq", "kivy": "Kivy", "ezdxf": "ezdxf", "pyproj": "pyproj",
    "shapely": "shapely", "can": "python-can", "ttkbootstrap": "ttkbootstrap",
    "customtkinter": "customtkinter", "pdfplumber": "pdfplumber", "PyPDF2": "PyPDF2",
    "pypdf": "pypdf", "reportlab": "reportlab", "openpyxl": "openpyxl", "xlrd": "xlrd",
    "xlsxwriter": "XlsxWriter", "matplotlib": "matplotlib", "numpy": "numpy", "pandas": "pandas",
    "requests": "requests", "PyQt5": "PyQt5", "PyQt6": "PyQt6", "PySide6": "PySide6",
    "PySide2": "PySide2", "lxml": "lxml", "psutil": "psutil", "pynput": "pynput",
    "websocket": "websocket-client", "socketio": "python-socketio", "speech_recognition": "SpeechRecognition",
    "Image": "Pillow", "sip": None,
}
WINDOWS_ONLY = {"win32api", "win32con", "win32gui", "win32com", "win32print", "win32clipboard",
                "win32process", "win32event", "win32file", "pywintypes", "pythoncom", "wmi",
                "comtypes", "pywinauto", "winshell", "win10toast", "winsound", "msvcrt", "winreg",
                "_winapi", "ctypes.wintypes"}
STDLIB_FALLBACK = set("""
__future__ abc aifc argparse array ast asyncio atexit base64 bdb binascii bisect builtins bz2
calendar cgi cgitb chunk cmath cmd code codecs codeop collections colorsys compileall concurrent
configparser contextlib contextvars copy copyreg cProfile crypt csv ctypes curses dataclasses datetime
dbm decimal difflib dis doctest email encodings ensurepip enum errno faulthandler fcntl filecmp
fileinput fnmatch fractions ftplib functools gc getopt getpass gettext glob graphlib grp gzip hashlib
heapq hmac html http idlelib imaplib imghdr imp importlib inspect io ipaddress itertools json keyword
lib2to3 linecache locale logging lzma mailbox mailcap marshal math mimetypes mmap modulefinder
msilib msvcrt multiprocessing netrc nntplib numbers operator optparse os pathlib pdb pickle
pickletools pipes pkgutil platform plistlib poplib posix pprint profile pstats pty pwd py_compile
pyclbr pydoc queue quopri random re readline reprlib resource rlcompleter runpy sched secrets select
selectors shelve shlex shutil signal site smtplib sndhdr socket socketserver sqlite3 ssl stat
statistics string stringprep struct subprocess sunau symtable sys sysconfig syslog tabnanny tarfile
telnetlib tempfile termios textwrap threading time timeit tkinter token tokenize tomllib trace
traceback tracemalloc tty turtle types typing unicodedata unittest urllib uu uuid venv warnings wave
weakref webbrowser winreg winsound wsgiref xdrlib xml xmlrpc zipapp zipfile zipimport zlib zoneinfo
_thread
""".split())

# ----------------------------------------------------------------------------
# Κείμενα (Ελληνικά / English)
# ----------------------------------------------------------------------------
T = {
    "el": {
        "subtitle": "Κάνε την Python εφαρμογή σου κανονική εφαρμογή Mac (.app)",
        "lang": "🌐 English",
        "about": "ℹ️",
        "import": "📥 Εισαγωγή",
        "export": "📤 Εξαγωγή",
        "import_tip": "Άνοιγμα αποθηκευμένων ρυθμίσεων (.py2mac)",
        "export_tip": "Αποθήκευση των ρυθμίσεων σε αρχείο (.py2mac) για να τις ξαναχρησιμοποιήσεις",
        "step1": "1 · Αρχείο", "step2": "2 · Στοιχεία", "step3": "3 · Βιβλιοθήκες", "step4": "4 · Δημιουργία",
        "back": "◀  Πίσω", "next": "Επόμενο  ▶",
        "p1_title": "Ποια εφαρμογή θέλεις να μετατρέψεις;",
        "drop": "⬇\n\nΣύρε εδώ το αρχείο .py / .pyw\n\nή κάνε κλικ για να το διαλέξεις",
        "drop_set": "✅  {f}\n\nΚάνε κλικ για να διαλέξεις άλλο",
        "recent": "Πρόσφατα (διπλό κλικ για άνοιγμα):",
        "recent_empty": "— κανένα ακόμα —",
        "p2_title": "Πώς θα λέγεται η εφαρμογή σου;",
        "p2_hint": "Τα συμπλήρωσα αυτόματα. Άλλαξέ τα μόνο αν θέλεις.",
        "name": "Όνομα:", "version": "Έκδοση:", "bump": "+1",
        "bump_tip": "Αύξηση έκδοσης (π.χ. 1.0.0 → 1.0.1)",
        "copyright": "Δημιουργός:", "icon": "Εικονίδιο:", "no_icon": "χωρίς εικονίδιο\n\nκλικ ή σύρε\nμια εικόνα εδώ",
        "icon_crop": "✂ Κόψιμο σε τετράγωνο", "icon_fit": "🖼 Ολόκληρη εικόνα",
        "icon_round": "Στυλ macOS (στρογγυλές γωνίες)",
        "icon_hint": "Οποιαδήποτε εικόνα (JPG, PNG, HEIC, WEBP…).\nΤην κόβω και τη φτιάχνω μόνη της.",
        "icon_bad": "⚠ Δεν μπορώ να ανοίξω\nαυτή την εικόνα",
        "choose": "Επιλογή…", "clear": "Καθαρισμός",
        "output": "Αποθήκευση σε:",
        "p3_title": "Τι χρειάζεται η εφαρμογή σου;",
        "p3_hint": "Τα βρήκα αυτόματα και θα εγκατασταθούν μόνα τους. Συνήθως δεν πειράζεις τίποτα.",
        "libs": "📦 Βιβλιοθήκες (ξετσέκαρε όσες δεν θέλεις):",
        "rescan": "🔍 Ξανά-εντοπισμός",
        "add_lib_ph": "πρόσθεσε βιβλιοθήκη (π.χ. requests) και πάτα Enter",
        "add": "Προσθήκη",
        "datas": "📁 Αρχεία/φάκελοι που χρειάζεται η εφαρμογή (εικόνες, βάσεις, templates…):",
        "add_file": "+ Αρχείο", "add_folder": "+ Φάκελος", "remove": "− Αφαίρεση",
        "show_adv": "⚙️ Ρυθμίσεις για προχωρημένους ▸", "hide_adv": "⚙️ Ρυθμίσεις για προχωρημένους ▾",
        "bundle": "Bundle ID:",
        "hidden": "Hidden imports (με κόμμα):",
        "collect": "Collect-all πακέτα (με κόμμα):",
        "arch": "Αρχιτεκτονική:",
        "arch_native": "Αυτόματα (αυτού του Mac)",
        "p4_title": "Έτοιμοι! Πάτα το μεγάλο κουμπί.",
        "summary": ("<b>{name}</b> &nbsp; v{ver}<br>📦 {libs} βιβλιοθήκες &nbsp;·&nbsp; 📁 {files} αρχεία"
                    "<br>💾 {out}"),
        "dmg": "Φτιάξε και .dmg (για να το δώσεις σε άλλους)",
        "zip": "Φτιάξε και .zip",
        "sign": "Ad-hoc υπογραφή + αφαίρεση καραντίνας (συνιστάται)",
        "clean": "Καθαρό build (πιο αργό – αν κάτι δεν δουλεύει)",
        "test": "▶  Δοκίμασέ την πρώτα",
        "build": "🚀  ΦΤΙΑΞΕ ΤΟ .app",
        "cancel": "■  Ακύρωση",
        "open_out": "📂 Άνοιγμα φακέλου",
        "show_log": "▸ Λεπτομέρειες", "hide_log": "▾ Λεπτομέρειες",
        "copy_log": "Αντιγραφή",
        "ready": "Πάτα «ΦΤΙΑΞΕ ΤΟ .app». Μπορεί να πάρει 1-5 λεπτά.",
        "no_script": "Διάλεξε πρώτα ένα αρχείο .py / .pyw.",
        "no_name": "Δώσε όνομα στην εφαρμογή.",
        "not_mac": "Το .app μπορεί να φτιαχτεί μόνο σε macOS. Τρέξε το πρόγραμμα σε Mac.",
        "overwrite": "Υπάρχει ήδη:\n{p}\n\nΝα αντικατασταθεί;",
        "detected": "Βρέθηκαν {n} βιβλιοθήκες.",
        "win_only": "Παραλείφθηκαν βιβλιοθήκες μόνο για Windows (δεν δουλεύουν σε Mac): {l}",
        "done_ok": "🎉 Έτοιμο! Η εφαρμογή σου δημιουργήθηκε:\n\n{p}",
        "done_fail": "Κάτι πήγε στραβά:\n\n{e}\n\nΆνοιξε τις «Λεπτομέρειες» για να δεις τι έγινε.",
        "open_now": "Δείξε τη στο Finder", "run_now": "Άνοιξέ τη", "close": "Κλείσιμο",
        "busy_quit": "Τρέχει εργασία. Να ακυρωθεί και να κλείσει;",
        "tip": "💡 Αν σε άλλο Mac βγει «δεν μπορεί να ανοίξει»: δεξί κλικ στο .app → Άνοιγμα → Άνοιγμα.",
        "exported": "Οι ρυθμίσεις αποθηκεύτηκαν:\n{p}",
        "imported": "Οι ρυθμίσεις φορτώθηκαν από:\n{p}",
        "import_bad": "Αυτό το αρχείο δεν είναι έγκυρο αρχείο ρυθμίσεων Py2Mac.",
        "import_missing": "Δεν βρέθηκε η εφαρμογή:\n{p}\n\nΘέλεις να τη διαλέξεις εσύ;",
        "s_pip": "Εγκατάσταση βιβλιοθηκών της εφαρμογής",
        "s_icon": "Προετοιμασία εικονιδίου",
        "s_pyi": "Δημιουργία .app (μπορεί να πάρει λίγα λεπτά)",
        "s_move": "Μεταφορά στο φάκελο εξόδου",
        "s_plist": "Ρύθμιση έκδοσης / ονόματος",
        "s_sign": "Υπογραφή / αφαίρεση καραντίνας",
        "s_dmg": "Δημιουργία .dmg",
        "s_zip": "Δημιουργία .zip",
        "s_run": "Εκκίνηση εφαρμογής για δοκιμή",
        "s_done": "Ολοκληρώθηκε ✔",
        "cancelled": "Ακυρώθηκε από τον χρήστη.",
        "pick_py": "Διάλεξε εφαρμογή Python", "pick_icon": "Διάλεξε εικονίδιο",
        "pick_out": "Διάλεξε φάκελο", "pick_data": "Διάλεξε αρχεία", "pick_dir": "Διάλεξε φάκελο",
        "launcher_made": ("✅ Έφτιαξα την εφαρμογή «ALU Py2Mac» στις Εφαρμογές σου και στην Επιφάνεια εργασίας.\n\n"
                          "Από τώρα άνοιγέ τη από εκεί με διπλό κλικ – χωρίς Terminal.\n\n"
                          "Μπορείς επίσης να σύρεις ένα .py πάνω στο εικονίδιό της."),
        "about_title": "Σχετικά",
        "about_text": ("<h3>{app} v{ver}</h3><p>Μετατρέπει Python εφαρμογές σε macOS .app "
                       "με PyInstaller.</p><p><b>Developer:</b> {dev}<br>ALU DEV TEAM</p>"
                       "<p>Περιβάλλον εργαλείων:<br><small>{venv}</small></p>"),
    },
    "en": {
        "subtitle": "Turn your Python app into a real Mac app (.app)",
        "lang": "🌐 Ελληνικά",
        "about": "ℹ️",
        "import": "📥 Import",
        "export": "📤 Export",
        "import_tip": "Open saved settings (.py2mac)",
        "export_tip": "Save these settings to a file (.py2mac) to reuse them",
        "step1": "1 · File", "step2": "2 · Details", "step3": "3 · Libraries", "step4": "4 · Build",
        "back": "◀  Back", "next": "Next  ▶",
        "p1_title": "Which app do you want to convert?",
        "drop": "⬇\n\nDrag your .py / .pyw file here\n\nor click to choose it",
        "drop_set": "✅  {f}\n\nClick to choose another",
        "recent": "Recent (double-click to open):",
        "recent_empty": "— none yet —",
        "p2_title": "What should your app be called?",
        "p2_hint": "Filled in automatically. Change only if you want.",
        "name": "Name:", "version": "Version:", "bump": "+1",
        "bump_tip": "Bump version (e.g. 1.0.0 → 1.0.1)",
        "copyright": "Author:", "icon": "Icon:", "no_icon": "no icon\n\nclick or drop\nan image here",
        "icon_crop": "✂ Crop to square", "icon_fit": "🖼 Whole image",
        "icon_round": "macOS style (rounded corners)",
        "icon_hint": "Any image (JPG, PNG, HEIC, WEBP…).\nIt gets cropped and converted automatically.",
        "icon_bad": "⚠ Can't open\nthis image",
        "choose": "Choose…", "clear": "Clear",
        "output": "Save to:",
        "p3_title": "What does your app need?",
        "p3_hint": "Found automatically and installed by itself. Usually you don't touch anything.",
        "libs": "📦 Libraries (uncheck any you don't want):",
        "rescan": "🔍 Re-scan",
        "add_lib_ph": "add a library (e.g. requests) and press Enter",
        "add": "Add",
        "datas": "📁 Files/folders your app needs (images, databases, templates…):",
        "add_file": "+ File", "add_folder": "+ Folder", "remove": "− Remove",
        "show_adv": "⚙️ Advanced settings ▸", "hide_adv": "⚙️ Advanced settings ▾",
        "bundle": "Bundle ID:",
        "hidden": "Hidden imports (comma separated):",
        "collect": "Collect-all packages (comma separated):",
        "arch": "Architecture:",
        "arch_native": "Automatic (this Mac)",
        "p4_title": "All set! Press the big button.",
        "summary": ("<b>{name}</b> &nbsp; v{ver}<br>📦 {libs} libraries &nbsp;·&nbsp; 📁 {files} files"
                    "<br>💾 {out}"),
        "dmg": "Also create a .dmg (to give to others)",
        "zip": "Also create a .zip",
        "sign": "Ad-hoc sign + remove quarantine (recommended)",
        "clean": "Clean build (slower – if something doesn't work)",
        "test": "▶  Test it first",
        "build": "🚀  BUILD THE .app",
        "cancel": "■  Cancel",
        "open_out": "📂 Open folder",
        "show_log": "▸ Details", "hide_log": "▾ Details",
        "copy_log": "Copy",
        "ready": "Press \"BUILD THE .app\". It may take 1-5 minutes.",
        "no_script": "Pick a .py / .pyw file first.",
        "no_name": "Give your app a name.",
        "not_mac": "A .app can only be built on macOS. Run this program on a Mac.",
        "overwrite": "Already exists:\n{p}\n\nReplace it?",
        "detected": "Found {n} libraries.",
        "win_only": "Skipped Windows-only libraries (won't work on Mac): {l}",
        "done_ok": "🎉 Done! Your app was created:\n\n{p}",
        "done_fail": "Something went wrong:\n\n{e}\n\nOpen \"Details\" to see what happened.",
        "open_now": "Show in Finder", "run_now": "Open it", "close": "Close",
        "busy_quit": "A task is running. Cancel it and quit?",
        "tip": "💡 If another Mac says it \"can't be opened\": right-click the .app → Open → Open.",
        "exported": "Settings saved:\n{p}",
        "imported": "Settings loaded from:\n{p}",
        "import_bad": "This is not a valid Py2Mac settings file.",
        "import_missing": "App not found:\n{p}\n\nDo you want to pick it yourself?",
        "s_pip": "Installing the app's libraries",
        "s_icon": "Preparing icon",
        "s_pyi": "Building .app (may take a few minutes)",
        "s_move": "Moving to output folder",
        "s_plist": "Setting version / name",
        "s_sign": "Signing / removing quarantine",
        "s_dmg": "Creating .dmg",
        "s_zip": "Creating .zip",
        "s_run": "Launching the app for testing",
        "s_done": "Finished ✔",
        "cancelled": "Cancelled by user.",
        "pick_py": "Pick a Python app", "pick_icon": "Pick an icon",
        "pick_out": "Pick a folder", "pick_data": "Pick files", "pick_dir": "Pick a folder",
        "launcher_made": ("✅ I created the \"ALU Py2Mac\" app in your Applications and on your Desktop.\n\n"
                          "From now on open it from there with a double-click – no Terminal.\n\n"
                          "You can also drop a .py file onto its icon."),
        "about_title": "About",
        "about_text": ("<h3>{app} v{ver}</h3><p>Turns Python apps into macOS .app bundles "
                       "using PyInstaller.</p><p><b>Developer:</b> {dev}<br>ALU DEV TEAM</p>"
                       "<p>Tools environment:<br><small>{venv}</small></p>"),
    },
}

# ----------------------------------------------------------------------------
# Βοηθητικά
# ----------------------------------------------------------------------------

def load_settings():
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"lang": "el", "projects": {}}


def save_settings(s):
    try:
        os.makedirs(HOME_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def split_name_version(stem):
    """'ALU_HygroLink_v1.1.1' -> ('ALU_HygroLink', '1.1.1')"""
    m = re.match(r"^(.*?)[_\-\s]?v(\d+(?:\.\d+){0,3})$", stem, re.IGNORECASE)
    if m and m.group(1):
        return m.group(1), m.group(2)
    return stem, "1.0.0"


def make_bundle_id(name):
    clean = re.sub(r"[^a-z0-9]+", "", name.lower()) or "app"
    return f"com.nikkpap.{clean}"


IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".heic", ".heif", ".webp", ".bmp", ".gif", ".tif", ".tiff",
              ".ico", ".icns", ".jfif")
ICON_DIR = os.path.join(HOME_DIR, "icons")


def _open_image(src):
    from PIL import Image, ImageOps
    try:
        import pillow_heif
        pillow_heif.register_heif_opener()
    except Exception:
        pass
    im = Image.open(src)
    try:
        im.seek(0)
    except Exception:
        pass
    try:
        im = ImageOps.exif_transpose(im)  # σωστός προσανατολισμός φωτογραφιών κινητού
    except Exception:
        pass
    return im.convert("RGBA")


def make_icon_png(src, mode="crop", rounded=True, size=1024):
    """Οποιαδήποτε εικόνα -> τετράγωνο PNG 1024x1024 έτοιμο για εικονίδιο macOS.
    mode: 'crop' = κόψιμο στο κέντρο, 'fit' = ολόκληρη με διαφανές περιθώριο.
    rounded: στυλ macOS (στρογγυλεμένο τετράγωνο με περιθώριο, όπως τα εικονίδια του Big Sur+)."""
    import hashlib
    from PIL import Image, ImageOps, ImageDraw
    st = os.stat(src)
    key = hashlib.md5(f"{os.path.abspath(src)}|{st.st_mtime}|{st.st_size}|{mode}|{rounded}|{size}"
                      .encode("utf-8")).hexdigest()[:16]
    os.makedirs(ICON_DIR, exist_ok=True)
    out = os.path.join(ICON_DIR, f"icon_{key}.png")
    if os.path.isfile(out):
        return out
    im = _open_image(src)
    body_size = int(size * 824 / 1024) if rounded else size
    if mode == "fit":
        im.thumbnail((body_size, body_size), Image.LANCZOS)
        body = Image.new("RGBA", (body_size, body_size), (0, 0, 0, 0))
        if rounded:  # στο στυλ macOS το φόντο του εικονιδίου είναι γεμάτο (λευκό)
            body = Image.new("RGBA", (body_size, body_size), (255, 255, 255, 255))
        body.alpha_composite(im, ((body_size - im.width) // 2, (body_size - im.height) // 2))
    else:
        body = ImageOps.fit(im, (body_size, body_size), Image.LANCZOS, centering=(0.5, 0.5))
    if rounded:
        ss = 4  # supersampling για λείες γωνίες
        mask = Image.new("L", (body_size * ss, body_size * ss), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, body_size * ss - 1, body_size * ss - 1),
                                               radius=int(body_size * 0.225 * ss), fill=255)
        mask = mask.resize((body_size, body_size), Image.LANCZOS)
        alpha = body.getchannel("A")
        from PIL import ImageChops
        body.putalpha(ImageChops.multiply(alpha, mask))
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        off = (size - body_size) // 2
        canvas.alpha_composite(body, (off, off))
        body = canvas
    body.save(out, "PNG")
    return out


def make_icns(png, out_icns):
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    if im.size != (1024, 1024):
        im = im.resize((1024, 1024), Image.LANCZOS)
    im.save(out_icns, format="ICNS")
    if not os.path.isfile(out_icns) or os.path.getsize(out_icns) < 1000:
        raise RuntimeError("ICNS write failed")


def find_icon(folder, stem):
    cands = [f"{stem}.icns", "icon.icns", "app.icns", f"{stem}.png", "icon.png", "app.png", "logo.png",
             f"{stem}.jpg", "icon.jpg", "logo.jpg"]
    for c in cands:
        p = os.path.join(folder, c)
        if os.path.isfile(p):
            return p
    return ""


def detect_requirements(script):
    """Επιστρέφει (packages, windows_only_skipped)."""
    folder = os.path.dirname(os.path.abspath(script))
    local = set()
    py_files = [os.path.abspath(script)]
    try:
        for entry in os.listdir(folder):
            full = os.path.join(folder, entry)
            if entry.endswith((".py", ".pyw")):
                local.add(os.path.splitext(entry)[0])
                if full not in py_files and len(py_files) < 200:
                    py_files.append(full)
            elif os.path.isdir(full) and not entry.startswith("."):
                local.add(entry)
    except Exception:
        pass

    names = set()
    for f in py_files:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as fh:
                tree = ast.parse(fh.read(), filename=f)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    names.add(a.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names.add(node.module.split(".")[0])

    stdlib = set(getattr(sys, "stdlib_module_names", ())) | STDLIB_FALLBACK | set(sys.builtin_module_names)
    pkgs, win_only = [], []
    for n in sorted(names):
        if n in WINDOWS_ONLY:
            win_only.append(n)
            continue
        if n in stdlib or n in local or n.startswith("_"):
            continue
        pip_name = IMPORT_TO_PIP.get(n, n)
        if pip_name and pip_name not in pkgs:
            pkgs.append(pip_name)

    req = os.path.join(folder, "requirements.txt")
    if os.path.isfile(req):
        try:
            with open(req, "r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.split("#")[0].strip()
                    if line and not line.startswith("-"):
                        base = re.split(r"[<>=!~;\[ ]", line)[0].lower()
                        if not any(p.lower() == base for p in pkgs):
                            pkgs.append(line)
        except Exception:
            pass
    return pkgs, win_only


LAUNCHER_NAME = "ALU Py2Mac.app"


def _launcher_icon_png():
    """Εικονίδιο για το ίδιο το Py2Mac (σχεδιάζεται με Pillow)."""
    from PIL import Image, ImageDraw, ImageFont
    out = os.path.join(ICON_DIR, "py2mac_launcher.png")
    if os.path.isfile(out):
        return out
    os.makedirs(ICON_DIR, exist_ok=True)
    S = 1024
    grad = Image.new("RGBA", (S, S))
    top, bot = (47, 111, 236), (47, 191, 113)
    for y in range(S):
        k = y / (S - 1)
        ImageDraw.Draw(grad).line([(0, y), (S, y)], fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)) + (255,))
    d = ImageDraw.Draw(grad)

    def font(sz):
        for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
                  "/Library/Fonts/Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
            try:
                return ImageFont.truetype(f, sz)
            except Exception:
                pass
        try:
            return ImageFont.load_default(size=sz)
        except Exception:
            return ImageFont.load_default()
    for text, sz, y in (("Py", 420, 330), ("→ .app", 170, 700)):
        f = font(sz)
        bb = d.textbbox((0, 0), text, font=f)
        d.text(((S - (bb[2] - bb[0])) // 2 - bb[0], y - (bb[3] - bb[1]) // 2 - bb[1]), text,
               font=f, fill=(255, 255, 255, 255))
    tmp = os.path.join(ICON_DIR, "py2mac_launcher_src.png")
    grad.save(tmp)
    png = make_icon_png(tmp, "crop", True)
    shutil.copyfile(png, out)
    return out


def ensure_launcher():
    """Φτιάχνει/ενημερώνει το ~/Applications/ALU Py2Mac.app ώστε να ανοίγει χωρίς Terminal.
    Επιστρέφει True αν δημιουργήθηκε τώρα για πρώτη φορά."""
    if not IS_MAC:
        return False
    try:
        apps = os.path.join(os.path.expanduser("~"), "Applications")
        app = os.path.join(apps, LAUNCHER_NAME)
        created = not os.path.isdir(app)
        macos = os.path.join(app, "Contents", "MacOS")
        res = os.path.join(app, "Contents", "Resources")
        os.makedirs(macos, exist_ok=True)
        os.makedirs(res, exist_ok=True)
        exe = os.path.join(macos, "ALU_Py2Mac")
        me = os.path.abspath(__file__)
        script = ("#!/bin/bash\n"
                  "export ALU_PY2MAC_CHILD=1\n"
                  f"exec {shlex.quote(VENV_PY)} {shlex.quote(me)} \"$@\" >> {shlex.quote(LOG_FILE)} 2>&1\n")
        old = ""
        if os.path.isfile(exe):
            with open(exe, "r", encoding="utf-8") as f:
                old = f.read()
        if old != script:
            with open(exe, "w", encoding="utf-8") as f:
                f.write(script)
            os.chmod(exe, 0o755)
        plist = {
            "CFBundleName": "ALU Py2Mac", "CFBundleDisplayName": "ALU Py2Mac",
            "CFBundleExecutable": "ALU_Py2Mac", "CFBundleIdentifier": "com.nikkpap.alupy2mac",
            "CFBundlePackageType": "APPL", "CFBundleIconFile": "AppIcon",
            "CFBundleShortVersionString": APP_VERSION, "CFBundleVersion": APP_VERSION,
            "NSHighResolutionCapable": True, "LSMinimumSystemVersion": "10.13",
            "NSHumanReadableCopyright": f"© {datetime.date.today().year} {DEVELOPER}",
            "CFBundleDocumentTypes": [{
                "CFBundleTypeName": "Python / Py2Mac files", "CFBundleTypeRole": "Viewer",
                "LSHandlerRank": "Alternate",
                "CFBundleTypeExtensions": ["py", "pyw", "py2mac"],
            }],
        }
        with open(os.path.join(app, "Contents", "Info.plist"), "wb") as f:
            plistlib.dump(plist, f)
        icns = os.path.join(res, "AppIcon.icns")
        if not os.path.isfile(icns):
            try:
                make_icns(_launcher_icon_png(), icns)
            except Exception:
                pass
        if created:
            desk = os.path.join(os.path.expanduser("~"), "Desktop", LAUNCHER_NAME)
            if not os.path.lexists(desk):
                try:
                    os.symlink(app, desk)
                except Exception:
                    pass
            for cmd in (["touch", app],
                        ["/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/"
                         "Support/lsregister", "-f", app]):
                try:
                    subprocess.run(cmd, capture_output=True, timeout=20)
                except Exception:
                    pass
        return created
    except Exception as e:
        print(f"[{APP_NAME}] launcher: {e}", flush=True)
        return False


class Cancelled(Exception):
    pass


# ----------------------------------------------------------------------------
# Worker (build / test σε ξεχωριστό thread)
# ----------------------------------------------------------------------------
class Worker(QThread):
    log = pyqtSignal(str)
    step = pyqtSignal(int, int, str)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, cfg, tr):
        super().__init__()
        self.cfg = cfg
        self.tr_ = tr
        self._cancel = False
        self._proc = None

    def cancel(self):
        self._cancel = True
        try:
            if self._proc and self._proc.poll() is None:
                self._proc.terminate()
        except Exception:
            pass

    def run_cmd(self, cmd, cwd=None, check=True):
        if self._cancel:
            raise Cancelled()
        self.log.emit("$ " + " ".join(shlex.quote(str(c)) for c in cmd))
        env = dict(os.environ, PYTHONUNBUFFERED="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
        self._proc = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                      errors="replace", bufsize=1)
        for line in self._proc.stdout:
            self.log.emit(line.rstrip("\n"))
            if self._cancel:
                break
        rc = self._proc.wait()
        self._proc = None
        if self._cancel:
            raise Cancelled()
        if rc != 0 and check:
            raise RuntimeError(f"Η εντολή απέτυχε (κωδικός {rc}): {os.path.basename(str(cmd[0]))} "
                               f"{' '.join(str(c) for c in cmd[1:3])}…")
        return rc

    def run(self):
        try:
            if self.cfg["mode"] == "test":
                self.do_test()
            else:
                self.do_build()
        except Cancelled:
            self.failed.emit(self.tr_("cancelled"))
        except Exception as e:
            self.failed.emit(str(e))

    def _install_pkgs(self):
        pkgs = self.cfg["pkgs"]
        if pkgs:
            self.run_cmd([sys.executable, "-m", "pip", "install"] + pkgs)
        else:
            self.log.emit("(καμία επιπλέον βιβλιοθήκη)")

    def do_test(self):
        c = self.cfg
        self.step.emit(1, 2, self.tr_("s_pip"))
        self._install_pkgs()
        self.step.emit(2, 2, self.tr_("s_run"))
        self.log.emit(f"$ {sys.executable} {c['script']}")
        subprocess.Popen([sys.executable, c["script"]], cwd=os.path.dirname(c["script"]))
        self.finished_ok.emit("")

    def do_build(self):
        c = self.cfg
        name = c["name"]
        steps = ["s_pip", "s_icon", "s_pyi", "s_move", "s_plist"]
        if c["sign"]:
            steps.append("s_sign")
        if c["dmg"]:
            steps.append("s_dmg")
        if c["zip"]:
            steps.append("s_zip")
        total = len(steps)
        n = 0

        def nxt(key):
            nonlocal n
            n += 1
            self.step.emit(n, total, self.tr_(key))
            self.log.emit(f"\n===== [{n}/{total}] {self.tr_(key)} =====")

        tmp = tempfile.mkdtemp(prefix="alu_py2mac_")
        try:
            # 1. pip
            nxt("s_pip")
            self._install_pkgs()

            # 2. icon
            nxt("s_icon")
            icon = c["icon"]
            icns = ""
            if icon and os.path.isfile(icon):
                png = make_icon_png(icon, c.get("icon_mode", "crop"), c.get("icon_round", True))
                self.log.emit(f"{icon}\n  → {png} (1024×1024)")
                icns = os.path.join(tmp, "icon.icns")
                try:
                    make_icns(png, icns)
                    self.log.emit("✔ icon.icns")
                except Exception as e:
                    self.log.emit(f"Pillow ICNS: {e} → iconutil")
                    iconset = os.path.join(tmp, "icon.iconset")
                    os.makedirs(iconset, exist_ok=True)
                    for s in (16, 32, 128, 256, 512):
                        for mult, suffix in ((1, ""), (2, "@2x")):
                            px = s * mult
                            self.run_cmd(["sips", "-z", str(px), str(px), png,
                                          "--out", os.path.join(iconset, f"icon_{s}x{s}{suffix}.png")])
                    self.run_cmd(["iconutil", "-c", "icns", iconset, "-o", icns])
            else:
                self.log.emit("(χωρίς εικονίδιο – θα μπει το προεπιλεγμένο)")

            # 3. PyInstaller
            nxt("s_pyi")
            dist = os.path.join(tmp, "dist")
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
            work = os.path.join(BUILD_CACHE, safe, "work")
            spec = os.path.join(BUILD_CACHE, safe, "spec")
            os.makedirs(work, exist_ok=True)
            os.makedirs(spec, exist_ok=True)
            cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--windowed", "--onedir",
                   "--name", name, "--distpath", dist, "--workpath", work, "--specpath", spec,
                   "--paths", os.path.dirname(c["script"])]
            if c["clean"]:
                cmd.append("--clean")
            if icns:
                cmd += ["--icon", icns]
            if c["bundle"]:
                cmd += ["--osx-bundle-identifier", c["bundle"]]
            if c["arch"] in ("arm64", "x86_64", "universal2"):
                cmd += ["--target-arch", c["arch"]]
            for d in c["datas"]:
                d = os.path.abspath(d)
                dest = os.path.basename(d.rstrip("/")) if os.path.isdir(d) else "."
                cmd += ["--add-data", f"{d}{os.pathsep}{dest}"]
            for h in c["hidden"]:
                cmd += ["--hidden-import", h]
            for col in c["collect"]:
                cmd += ["--collect-all", col]
            cmd.append(c["script"])
            self.run_cmd(cmd, cwd=os.path.dirname(c["script"]))

            built = os.path.join(dist, f"{name}.app")
            if not os.path.isdir(built):
                raise RuntimeError("Το PyInstaller δεν δημιούργησε .app (δες το log).")

            # 4. move
            nxt("s_move")
            os.makedirs(c["out"], exist_ok=True)
            final = os.path.join(c["out"], f"{name}.app")
            if os.path.exists(final):
                shutil.rmtree(final)
            shutil.move(built, final)
            self.log.emit(f"→ {final}")

            # 5. Info.plist
            nxt("s_plist")
            plist_path = os.path.join(final, "Contents", "Info.plist")
            with open(plist_path, "rb") as f:
                pl = plistlib.load(f)
            ver = c["version"] or "1.0.0"
            pl["CFBundleShortVersionString"] = ver
            pl["CFBundleVersion"] = ver
            pl["CFBundleDisplayName"] = name
            pl["CFBundleName"] = name
            pl["NSHighResolutionCapable"] = True
            pl["NSRequiresAquaSystemAppearance"] = False
            if c["copyright"]:
                pl["NSHumanReadableCopyright"] = f"© {datetime.date.today().year} {c['copyright']}"
            with open(plist_path, "wb") as f:
                plistlib.dump(pl, f)
            self.log.emit(f"Έκδοση {ver}, Bundle ID {pl.get('CFBundleIdentifier', '')}")

            # 6. sign
            if c["sign"]:
                nxt("s_sign")
                self.run_cmd(["xattr", "-cr", final], check=False)
                if self.run_cmd(["codesign", "--force", "--deep", "--sign", "-", final], check=False) != 0:
                    self.log.emit("⚠ Η υπογραφή απέτυχε – η εφαρμογή μάλλον θα τρέχει κανονικά στο δικό σου Mac.")

            # 7. dmg
            if c["dmg"]:
                nxt("s_dmg")
                stage = os.path.join(tmp, "dmg")
                os.makedirs(stage, exist_ok=True)
                self.run_cmd(["ditto", final, os.path.join(stage, f"{name}.app")])
                try:
                    os.symlink("/Applications", os.path.join(stage, "Applications"))
                except Exception:
                    pass
                dmg = os.path.join(c["out"], f"{name}_v{ver}.dmg")
                if os.path.exists(dmg):
                    os.remove(dmg)
                self.run_cmd(["hdiutil", "create", "-volname", name, "-srcfolder", stage,
                              "-ov", "-format", "UDZO", dmg])

            # 8. zip
            if c["zip"]:
                nxt("s_zip")
                z = os.path.join(c["out"], f"{name}_v{ver}.zip")
                if os.path.exists(z):
                    os.remove(z)
                self.run_cmd(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent", final, z])

            self.step.emit(total, total, self.tr_("s_done"))
            self.finished_ok.emit(final)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------
# Κύριο παράθυρο (οδηγός 4 βημάτων)
# ----------------------------------------------------------------------------
PROJECT_EXT = ".py2mac"

STYLE = """
QWidget { background: #1c1f27; color: #e6e9ef; font-size: 14px; }
QLabel { background: transparent; }
QLabel#title { font-size: 24px; font-weight: 800; color: #ffffff; }
QLabel#sub { color: #9aa4b5; }
QLabel#ptitle { font-size: 22px; font-weight: 700; color: #ffffff; padding: 4px 0; }
QLabel#hint { color: #8b95a7; }
QLabel#status { color: #cfd6e3; font-weight: 600; }
QLabel#summary { background: #252a36; border: 1px solid #343b4b; border-radius: 12px; padding: 14px; font-size: 15px; }
QLabel#iconprev { background: #151821; border: 2px dashed #3a4253; border-radius: 14px; color: #6b7280; }
QFrame#drop { background: #20253a; border: 3px dashed #4a6fd6; border-radius: 18px; }
QFrame#drop:hover { background: #26305a; border-color: #7fa1ff; }
QFrame#drop[ok="true"] { border: 3px solid #2fbf71; background: #1d3328; }
QLabel#droptext { font-size: 18px; color: #c9d6ff; }
QLineEdit, QPlainTextEdit, QListWidget, QComboBox { background: #151821; border: 1px solid #3a4150;
            border-radius: 8px; padding: 7px; selection-background-color: #3d6fd8; }
QLineEdit:focus { border: 1px solid #5b8cff; }
QListWidget::item { padding: 4px; }
QPushButton { background: #2d3443; border: 1px solid #414a5c; border-radius: 8px; padding: 8px 14px; }
QPushButton:hover { background: #394257; }
QPushButton:disabled { color: #636b7a; background: #242833; border-color: #2f3542; }
QPushButton#step { border-radius: 16px; padding: 7px 16px; background: #252a36; color: #8b95a7; border: 1px solid #333a49; }
QPushButton#step:checked { background: #2f6fec; color: white; border: none; font-weight: 700; }
QPushButton#step[done="true"] { color: #7fe0a8; }
QPushButton#primary { background: #2f6fec; border: none; font-weight: 700; padding: 10px 22px; }
QPushButton#primary:hover { background: #3f7ffc; }
QPushButton#build { background: #2fbf71; border: none; color: #0d1a12; font-size: 20px; font-weight: 800; padding: 18px 30px; border-radius: 14px; }
QPushButton#build:hover { background: #3fd683; }
QPushButton#build:disabled { background: #2a4a38; color: #7a9585; }
QPushButton#cancel { background: #b03a3a; border: none; }
QPushButton#link { background: transparent; border: none; color: #7fb3ff; text-align: left; padding: 4px 0; }
QPushButton#link:hover { color: #a9cbff; }
QProgressBar { border: 1px solid #3a4150; border-radius: 8px; text-align: center; background: #151821; height: 24px; }
QProgressBar::chunk { background: #2fbf71; border-radius: 7px; }
QCheckBox { spacing: 8px; padding: 3px 0; }
QCheckBox::indicator, QListWidget::indicator { width: 16px; height: 16px; border: 2px solid #6b7690;
            border-radius: 5px; background: #151821; }
QCheckBox::indicator:checked, QListWidget::indicator:checked { background: #2fbf71; border-color: #2fbf71; }
QCheckBox::indicator:hover, QListWidget::indicator:hover { border-color: #9fb4ff; }
QScrollArea { border: none; }
"""


def bump_version(v):
    parts = (v or "1.0.0").strip().split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
        return ".".join(parts)
    except Exception:
        return v


class ClickLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, e):
        self.clicked.emit()


class DropZone(QFrame):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("drop")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(230)
        lay = QVBoxLayout(self)
        self.label = QLabel()
        self.label.setObjectName("droptext")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        lay.addWidget(self.label)

    def set_ok(self, ok):
        self.setProperty("ok", "true" if ok else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, e):
        self.clicked.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.settings.setdefault("projects", {})
        self.settings.setdefault("recent", [])
        self.lang = self.settings.get("lang", "el") if self.settings.get("lang") in T else "el"
        self.worker = None
        self._trw = []
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(900, 720)
        self.setMinimumSize(760, 620)
        self.setAcceptDrops(True)
        self._build_ui()
        self.apply_lang()
        self.go(0)

    # ---------- i18n ----------
    def t(self, key):
        return T[self.lang].get(key, key)

    def reg(self, widget, key, kind="text"):
        self._trw.append((widget, key, kind))
        return widget

    def apply_lang(self):
        for w, key, kind in self._trw:
            if kind == "text":
                w.setText(self.t(key))
            elif kind == "ph":
                w.setPlaceholderText(self.t(key))
            elif kind == "tip":
                w.setToolTip(self.t(key))
        self.icon_mode.setItemText(0, self.t("icon_crop"))
        self.icon_mode.setItemText(1, self.t("icon_fit"))
        cur = self.arch.currentIndex()
        self.arch.setItemText(0, self.t("arch_native"))
        self.arch.setCurrentIndex(cur)
        self.b_adv.setText(self.t("hide_adv" if self.adv_box.isVisible() else "show_adv"))
        self.b_log.setText(self.t("hide_log" if self.logview.isVisible() else "show_log"))
        self.refresh_drop()
        self.refresh_recent()
        self.refresh_icon()
        self.refresh_summary()

    def toggle_lang(self):
        self.lang = "en" if self.lang == "el" else "el"
        self.settings["lang"] = self.lang
        save_settings(self.settings)
        self.apply_lang()

    # ---------- UI ----------
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 14, 18, 10)
        outer.setSpacing(10)

        # header
        hdr = QHBoxLayout()
        tb = QVBoxLayout()
        title = QLabel(f"🍏 {APP_NAME} <span style='font-size:13px;color:#7fb3ff'>v{APP_VERSION}</span>")
        title.setObjectName("title")
        tb.addWidget(title)
        tb.addWidget(self._obj(self.reg(QLabel(), "subtitle"), "sub"))
        hdr.addLayout(tb)
        hdr.addStretch()
        b_imp = self.reg(self.reg(QPushButton(), "import"), "import_tip", "tip")
        b_imp.clicked.connect(self.import_project)
        b_exp = self.reg(self.reg(QPushButton(), "export"), "export_tip", "tip")
        b_exp.clicked.connect(self.export_project)
        b_lang = self.reg(QPushButton(), "lang")
        b_lang.clicked.connect(self.toggle_lang)
        b_about = self.reg(QPushButton(), "about")
        b_about.clicked.connect(self.show_about)
        for b in (b_imp, b_exp, b_lang, b_about):
            hdr.addWidget(b)
        outer.addLayout(hdr)

        # step indicator
        sr = QHBoxLayout()
        self.step_btns = []
        for i, k in enumerate(("step1", "step2", "step3", "step4")):
            b = self.reg(QPushButton(), k)
            b.setObjectName("step")
            b.setCheckable(True)
            b.clicked.connect(lambda _=False, i=i: self.go(i))
            self.step_btns.append(b)
            sr.addWidget(b)
            if i < 3:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("color:#343b4b;")
                sr.addWidget(line, 1)
        outer.addLayout(sr)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        for page in (self._page1(), self._page2(), self._page3(), self._page4()):
            sc = QScrollArea()
            sc.setWidgetResizable(True)
            sc.setWidget(page)
            self.stack.addWidget(sc)

        # nav
        nav = QHBoxLayout()
        self.b_back = self.reg(QPushButton(), "back")
        self.b_back.clicked.connect(lambda: self.go(self.stack.currentIndex() - 1))
        self.b_next = self.reg(QPushButton(), "next")
        self.b_next.setObjectName("primary")
        self.b_next.clicked.connect(lambda: self.go(self.stack.currentIndex() + 1))
        foot = QLabel(f"© {datetime.date.today().year} {DEVELOPER} — ALU DEV TEAM")
        foot.setObjectName("hint")
        nav.addWidget(self.b_back)
        nav.addStretch()
        nav.addWidget(foot)
        nav.addStretch()
        nav.addWidget(self.b_next)
        outer.addLayout(nav)

    @staticmethod
    def _obj(w, name):
        w.setObjectName(name)
        return w

    def _page_base(self, title_key, hint_key=None):
        p = QWidget()
        lay = QVBoxLayout(p)
        lay.setContentsMargins(4, 8, 4, 4)
        lay.addWidget(self._obj(self.reg(QLabel(), title_key), "ptitle"))
        if hint_key:
            h = self._obj(self.reg(QLabel(), hint_key), "hint")
            h.setWordWrap(True)
            lay.addWidget(h)
        return p, lay

    def _page1(self):
        p, lay = self._page_base("p1_title")
        self.script = QLineEdit()  # αποθήκευση διαδρομής (κρυφό)
        self.script.setVisible(False)
        self.drop = DropZone()
        self.drop.clicked.connect(self.pick_script)
        lay.addWidget(self.drop, 2)
        lay.addSpacing(8)
        lay.addWidget(self.reg(QLabel(), "recent"))
        self.recent = QListWidget()
        self.recent.setMaximumHeight(150)
        self.recent.itemDoubleClicked.connect(self._open_recent)
        lay.addWidget(self.recent, 1)
        return p

    def _page2(self):
        p, lay = self._page_base("p2_title", "p2_hint")
        lay.addSpacing(6)
        body = QHBoxLayout()
        g = QGridLayout()
        g.setVerticalSpacing(12)
        self.name = QLineEdit()
        self.name.textEdited.connect(lambda s: self.bundle.setText(make_bundle_id(s)))
        self.version = QLineEdit("1.0.0")
        self.version.setMaximumWidth(140)
        b_bump = self.reg(self.reg(QPushButton(), "bump"), "bump_tip", "tip")
        b_bump.clicked.connect(lambda: self.version.setText(bump_version(self.version.text())))
        vr = QHBoxLayout()
        vr.addWidget(self.version)
        vr.addWidget(b_bump)
        vr.addStretch()
        self.copyright = QLineEdit(DEVELOPER)
        self.out = QLineEdit()
        bo = self.reg(QPushButton(), "choose")
        bo.clicked.connect(self.pick_out)
        orow = QHBoxLayout()
        orow.addWidget(self.out, 1)
        orow.addWidget(bo)
        g.addWidget(self.reg(QLabel(), "name"), 0, 0)
        g.addWidget(self.name, 0, 1)
        g.addWidget(self.reg(QLabel(), "version"), 1, 0)
        g.addLayout(vr, 1, 1)
        g.addWidget(self.reg(QLabel(), "copyright"), 2, 0)
        g.addWidget(self.copyright, 2, 1)
        g.addWidget(self.reg(QLabel(), "output"), 3, 0)
        g.addLayout(orow, 3, 1)
        g.setColumnStretch(1, 1)
        body.addLayout(g, 1)
        body.addSpacing(20)

        ic = QVBoxLayout()
        ic.addWidget(self.reg(QLabel(), "icon"), 0, Qt.AlignmentFlag.AlignHCenter)
        self.icon = QLineEdit()
        self.icon.setVisible(False)
        self.icon_prev = self._obj(ClickLabel(), "iconprev")
        self.icon_prev.setFixedSize(170, 170)
        self.icon_prev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_prev.clicked.connect(self.pick_icon)
        ic.addWidget(self.icon_prev, 0, Qt.AlignmentFlag.AlignHCenter)
        self.icon_mode = QComboBox()
        self.icon_mode.addItem("crop", "crop")
        self.icon_mode.addItem("fit", "fit")
        self.icon_mode.currentIndexChanged.connect(lambda _: self.refresh_icon())
        ic.addWidget(self.icon_mode)
        self.icon_round = self.reg(QCheckBox(), "icon_round")
        self.icon_round.setChecked(True)
        self.icon_round.toggled.connect(lambda _: self.refresh_icon())
        ic.addWidget(self.icon_round)
        brow = QHBoxLayout()
        bi = self.reg(QPushButton(), "choose")
        bi.clicked.connect(self.pick_icon)
        bc = self.reg(QPushButton(), "clear")
        bc.clicked.connect(lambda: (self.icon.clear(), self.refresh_icon()))
        brow.addWidget(bi)
        brow.addWidget(bc)
        ic.addLayout(brow)
        ih = self._obj(self.reg(QLabel(), "icon_hint"), "hint")
        ih.setWordWrap(True)
        ih.setMaximumWidth(240)
        ic.addWidget(ih)
        ic.addStretch()
        body.addLayout(ic)
        lay.addLayout(body)
        lay.addStretch()
        return p

    def _page3(self):
        p, lay = self._page_base("p3_title", "p3_hint")
        top = QHBoxLayout()
        top.addWidget(self.reg(QLabel(), "libs"))
        top.addStretch()
        b_rs = self.reg(QPushButton(), "rescan")
        b_rs.clicked.connect(lambda: self.detect(show=True))
        top.addWidget(b_rs)
        lay.addLayout(top)
        self.libs = QListWidget()
        self.libs.setMinimumHeight(110)
        lay.addWidget(self.libs, 2)
        ar = QHBoxLayout()
        self.lib_in = self.reg(QLineEdit(), "add_lib_ph", "ph")
        self.lib_in.returnPressed.connect(self.add_lib)
        b_add = self.reg(QPushButton(), "add")
        b_add.clicked.connect(self.add_lib)
        ar.addWidget(self.lib_in, 1)
        ar.addWidget(b_add)
        lay.addLayout(ar)

        lay.addSpacing(6)
        dl = self.reg(QLabel(), "datas")
        dl.setWordWrap(True)
        lay.addWidget(dl)
        dr = QHBoxLayout()
        self.datas = QListWidget()
        self.datas.setMinimumHeight(70)
        self.datas.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        dr.addWidget(self.datas, 1)
        db = QVBoxLayout()
        for key, fn in (("add_file", self.add_data_file), ("add_folder", self.add_data_dir),
                        ("remove", self.remove_data)):
            b = self.reg(QPushButton(), key)
            b.clicked.connect(fn)
            db.addWidget(b)
        db.addStretch()
        dr.addLayout(db)
        lay.addLayout(dr, 1)

        self.b_adv = QPushButton()
        self.b_adv.setObjectName("link")
        self.b_adv.clicked.connect(self.toggle_adv)
        lay.addWidget(self.b_adv, 0, Qt.AlignmentFlag.AlignLeft)
        self.adv_box = QWidget()
        self.adv_box.setMinimumHeight(170)
        al = QGridLayout(self.adv_box)
        al.setContentsMargins(0, 0, 0, 0)
        self.bundle = QLineEdit()
        self.hidden = QLineEdit()
        self.collect = QLineEdit()
        self.arch = QComboBox()
        self.arch.addItems(["native", "arm64", "x86_64", "universal2"])
        for r, (k, w) in enumerate((("bundle", self.bundle), ("hidden", self.hidden),
                                     ("collect", self.collect), ("arch", self.arch))):
            al.addWidget(self.reg(QLabel(), k), r, 0)
            al.addWidget(w, r, 1)
        al.setColumnStretch(1, 1)
        self.adv_box.setVisible(False)
        lay.addWidget(self.adv_box)
        return p

    def _page4(self):
        p, lay = self._page_base("p4_title")
        self.summary = self._obj(QLabel(), "summary")
        self.summary.setWordWrap(True)
        self.summary.setTextFormat(Qt.TextFormat.RichText)
        lay.addWidget(self.summary)
        self.cb_dmg = self.reg(QCheckBox(), "dmg")
        self.cb_zip = self.reg(QCheckBox(), "zip")
        self.cb_sign = self.reg(QCheckBox(), "sign")
        self.cb_sign.setChecked(True)
        self.cb_clean = self.reg(QCheckBox(), "clean")
        opts = QGridLayout()
        opts.addWidget(self.cb_dmg, 0, 0)
        opts.addWidget(self.cb_zip, 0, 1)
        opts.addWidget(self.cb_sign, 1, 0)
        opts.addWidget(self.cb_clean, 1, 1)
        lay.addLayout(opts)

        br = QHBoxLayout()
        self.b_test = self.reg(QPushButton(), "test")
        self.b_test.clicked.connect(lambda: self.start("test"))
        self.b_build = self.reg(QPushButton(), "build")
        self.b_build.setObjectName("build")
        self.b_build.clicked.connect(lambda: self.start("build"))
        self.b_cancel = self.reg(QPushButton(), "cancel")
        self.b_cancel.setObjectName("cancel")
        self.b_cancel.setVisible(False)
        self.b_cancel.clicked.connect(self.cancel)
        br.addWidget(self.b_test)
        br.addStretch()
        br.addWidget(self.b_cancel)
        br.addWidget(self.b_build)
        lay.addLayout(br)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        lay.addWidget(self.progress)
        self.status = self._obj(QLabel(), "status")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        lr = QHBoxLayout()
        self.b_log = QPushButton()
        self.b_log.setObjectName("link")
        self.b_log.clicked.connect(self.toggle_log)
        lr.addWidget(self.b_log)
        lr.addStretch()
        self.b_open = self.reg(QPushButton(), "open_out")
        self.b_open.clicked.connect(self.open_out)
        b_copy = self.reg(QPushButton(), "copy_log")
        b_copy.clicked.connect(lambda: QApplication.clipboard().setText(self.logview.toPlainText()))
        lr.addWidget(self.b_open)
        lr.addWidget(b_copy)
        lay.addLayout(lr)
        self.logview = QPlainTextEdit()
        self.logview.setReadOnly(True)
        self.logview.setMaximumBlockCount(8000)
        mono = QFont("Menlo" if IS_MAC else "Monospace")
        mono.setStyleHint(QFont.StyleHint.Monospace)
        mono.setPointSize(11)
        self.logview.setFont(mono)
        self.logview.setVisible(False)
        lay.addWidget(self.logview, 1)
        lay.addStretch(0)
        return p

    # ---------- navigation ----------
    def has_script(self):
        s = self.script.text().strip()
        return bool(s) and os.path.isfile(s)

    def go(self, i):
        i = max(0, min(3, i))
        cur = self.stack.currentIndex()
        if i > 0 and not self.has_script():
            if cur == 0 and i > cur:
                QMessageBox.information(self, APP_NAME, self.t("no_script"))
            i = 0
        if i >= 2 and not self.name.text().strip():
            QMessageBox.warning(self, APP_NAME, self.t("no_name"))
            i = 1
        if self.worker and self.worker.isRunning() and i != 3:
            return
        self.stack.setCurrentIndex(i)
        for n, b in enumerate(self.step_btns):
            b.setChecked(n == i)
            b.setProperty("done", "true" if n < i else "false")
            b.style().unpolish(b)
            b.style().polish(b)
        self.b_back.setVisible(i > 0)
        self.b_next.setVisible(i < 3)
        self.b_next.setEnabled(self.has_script())
        if i == 3:
            self.refresh_summary()
            if not (self.worker and self.worker.isRunning()) and not self.status.text():
                self.status.setText(self.t("ready"))

    # ---------- refreshers ----------
    def refresh_drop(self):
        if self.has_script():
            self.drop.label.setText(self.t("drop_set").format(f=os.path.basename(self.script.text())))
            self.drop.set_ok(True)
        else:
            self.drop.label.setText(self.t("drop"))
            self.drop.set_ok(False)

    def refresh_recent(self):
        self.recent.clear()
        items = [p for p in self.settings.get("recent", []) if os.path.isfile(p)]
        if not items:
            it = QListWidgetItem(self.t("recent_empty"))
            it.setFlags(Qt.ItemFlag.NoItemFlags)
            self.recent.addItem(it)
            return
        for p in items:
            it = QListWidgetItem(f"🐍  {os.path.basename(p)}    —    {os.path.dirname(p)}")
            it.setData(Qt.ItemDataRole.UserRole, p)
            it.setToolTip(p)
            self.recent.addItem(it)

    def refresh_icon(self):
        if not hasattr(self, "icon_mode"):
            return
        p = self.icon.text().strip()
        self.icon_prev.setPixmap(QPixmap())
        if not p or not os.path.isfile(p):
            self.icon_prev.setText(self.t("no_icon"))
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            png = make_icon_png(p, self.icon_mode.currentData() or "crop", self.icon_round.isChecked())
            pm = QPixmap(png)
            if pm.isNull():
                raise RuntimeError("preview")
            self.icon_prev.setText("")
            self.icon_prev.setPixmap(pm.scaled(156, 156, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            self.icon_prev.setText(self.t("icon_bad"))
            self.append_log(f"⚠ icon: {p}: {e}")
        finally:
            QApplication.restoreOverrideCursor()

    def refresh_summary(self):
        if not hasattr(self, "summary"):
            return
        self.summary.setText(self.t("summary").format(
            name=self.name.text().strip() or "—", ver=self.version.text().strip() or "—",
            libs=len(self.checked_libs()), files=self.datas.count(),
            out=os.path.join(self.out.text().strip(), f"{self.name.text().strip()}.app")))

    def toggle_adv(self):
        self.adv_box.setVisible(not self.adv_box.isVisible())
        self.b_adv.setText(self.t("hide_adv" if self.adv_box.isVisible() else "show_adv"))

    def toggle_log(self, show=None):
        vis = (not self.logview.isVisible()) if show is None else show
        self.logview.setVisible(vis)
        self.b_log.setText(self.t("hide_log" if vis else "show_log"))

    # ---------- drag & drop ----------
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for u in e.mimeData().urls():
            if self.open_path(u.toLocalFile()):
                return

    def open_path(self, p):
        """Άνοιγμα αρχείου (drag & drop, όρισμα, ή ρίψη πάνω στο εικονίδιο της εφαρμογής)."""
        if not p or not os.path.isfile(p):
            return False
        low = p.lower()
        if low.endswith(PROJECT_EXT):
            self.import_project(p)
            return True
        if low.endswith((".py", ".pyw")):
            self.load_script(p)
            self.go(1)
            return True
        if low.endswith(IMAGE_EXTS):
            self.icon.setText(p)
            self.refresh_icon()
            return True
        return False

    # ---------- libs ----------
    def set_libs(self, pkgs, unchecked=()):
        self.libs.clear()
        for pk in pkgs:
            self._add_lib_item(pk, pk not in unchecked)

    def _add_lib_item(self, name, checked=True):
        for i in range(self.libs.count()):
            if self.libs.item(i).text().lower() == name.lower():
                return
        it = QListWidgetItem(name)
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
        self.libs.addItem(it)

    def add_lib(self):
        for n in re.split(r"[,\s]+", self.lib_in.text().strip()):
            if n:
                self._add_lib_item(n)
        self.lib_in.clear()

    def checked_libs(self):
        return [self.libs.item(i).text() for i in range(self.libs.count())
                if self.libs.item(i).checkState() == Qt.CheckState.Checked]

    def all_libs(self):
        return [self.libs.item(i).text() for i in range(self.libs.count())]

    # ---------- pickers ----------
    def _start_dir(self):
        p = self.script.text().strip()
        return os.path.dirname(p) if p else os.path.expanduser("~")

    def pick_script(self):
        p, _ = QFileDialog.getOpenFileName(self, self.t("pick_py"), self._start_dir(), "Python (*.py *.pyw)")
        if p:
            self.load_script(p)
            self.go(1)

    def pick_icon(self):
        p, _ = QFileDialog.getOpenFileName(self, self.t("pick_icon"), self._start_dir(),
                                           "Images (*.png *.jpg *.jpeg *.jfif *.heic *.heif *.webp *.bmp "
                                           "*.gif *.tif *.tiff *.ico *.icns);;All files (*)")
        if p:
            self.icon.setText(p)
            self.refresh_icon()

    def pick_out(self):
        p = QFileDialog.getExistingDirectory(self, self.t("pick_out"), self.out.text() or self._start_dir())
        if p:
            self.out.setText(p)

    def add_data_file(self):
        ps, _ = QFileDialog.getOpenFileNames(self, self.t("pick_data"), self._start_dir())
        for p in ps:
            self.datas.addItem(p)

    def add_data_dir(self):
        p = QFileDialog.getExistingDirectory(self, self.t("pick_dir"), self._start_dir())
        if p:
            self.datas.addItem(p)

    def remove_data(self):
        for it in self.datas.selectedItems():
            self.datas.takeItem(self.datas.row(it))

    def _open_recent(self, item):
        p = item.data(Qt.ItemDataRole.UserRole)
        if p and os.path.isfile(p):
            self.load_script(p)
            self.go(1)

    # ---------- load / detect ----------
    def add_recent(self, path):
        rec = [p for p in self.settings.get("recent", []) if p != path]
        self.settings["recent"] = [path] + rec[:7]
        save_settings(self.settings)
        self.refresh_recent()

    def load_script(self, path, cfg=None):
        if not path or not os.path.isfile(path):
            return
        path = os.path.abspath(path)
        self.script.setText(path)
        folder = os.path.dirname(path)
        stem = os.path.splitext(os.path.basename(path))[0]
        nm, ver = split_name_version(stem)
        saved = cfg or self.settings["projects"].get(path)
        if saved:
            self.apply_cfg(saved)
            if ver != "1.0.0" and not cfg:
                self.version.setText(ver)  # νέα έκδοση στο όνομα αρχείου
        else:
            self.name.setText(nm)
            self.version.setText(ver)
            self.bundle.setText(make_bundle_id(nm))
            self.copyright.setText(DEVELOPER)
            self.icon.setText(find_icon(folder, stem))
            self.out.setText(os.path.join(folder, "MacApp"))
            self.datas.clear()
            self.hidden.clear()
            self.collect.clear()
            self.detect(show=False)
        self.append_log(f"✔ {path}")
        self.add_recent(path)
        self.status.setText("")
        self.refresh_drop()
        self.refresh_icon()
        self.b_next.setEnabled(True)

    def detect(self, show=True):
        s = self.script.text().strip()
        if not s or not os.path.isfile(s):
            if show:
                QMessageBox.information(self, APP_NAME, self.t("no_script"))
            return
        pkgs, win_only = detect_requirements(s)
        unchecked = [self.libs.item(i).text() for i in range(self.libs.count())
                     if self.libs.item(i).checkState() != Qt.CheckState.Checked]
        extra = [l for l in self.all_libs() if l not in pkgs] if show else []
        self.set_libs(pkgs + extra, unchecked)
        msg = self.t("detected").format(n=len(pkgs))
        if win_only:
            msg += "\n\n⚠ " + self.t("win_only").format(l=", ".join(win_only))
        self.append_log(msg)
        if show:
            QMessageBox.information(self, APP_NAME, msg + ("\n\n" + "\n".join(pkgs) if pkgs else ""))

    # ---------- config ----------
    def collect_cfg(self, mode="build"):
        split_c = lambda s: [x.strip() for x in s.split(",") if x.strip()]
        all_l = self.all_libs()
        chk = self.checked_libs()
        return {
            "mode": mode,
            "script": self.script.text().strip(),
            "name": self.name.text().strip(),
            "version": self.version.text().strip(),
            "bundle": self.bundle.text().strip() or make_bundle_id(self.name.text()),
            "copyright": self.copyright.text().strip(),
            "icon": self.icon.text().strip(),
            "icon_mode": self.icon_mode.currentData() or "crop",
            "icon_round": self.icon_round.isChecked(),
            "out": self.out.text().strip() or os.path.join(self._start_dir(), "MacApp"),
            "pkgs": chk,
            "pkgs_off": [l for l in all_l if l not in chk],
            "datas": [self.datas.item(i).text() for i in range(self.datas.count())],
            "hidden": split_c(self.hidden.text()),
            "collect": split_c(self.collect.text()),
            "arch": self.arch.currentText(),
            "dmg": self.cb_dmg.isChecked(),
            "zip": self.cb_zip.isChecked(),
            "sign": self.cb_sign.isChecked(),
            "clean": self.cb_clean.isChecked(),
        }

    def apply_cfg(self, c):
        self.name.setText(c.get("name", ""))
        self.version.setText(c.get("version", "1.0.0"))
        self.bundle.setText(c.get("bundle", "") or make_bundle_id(c.get("name", "")))
        self.copyright.setText(c.get("copyright", DEVELOPER))
        self.icon.setText(c.get("icon", ""))
        self.icon_mode.blockSignals(True)
        self.icon_round.blockSignals(True)
        self.icon_mode.setCurrentIndex(max(self.icon_mode.findData(c.get("icon_mode", "crop")), 0))
        self.icon_round.setChecked(c.get("icon_round", True))
        self.icon_mode.blockSignals(False)
        self.icon_round.blockSignals(False)
        self.out.setText(c.get("out", ""))
        off = c.get("pkgs_off", [])
        self.set_libs(list(c.get("pkgs", [])) + list(off), off)
        self.datas.clear()
        for d in c.get("datas", []):
            self.datas.addItem(d)
        self.hidden.setText(", ".join(c.get("hidden", [])))
        self.collect.setText(", ".join(c.get("collect", [])))
        self.arch.setCurrentIndex(max(self.arch.findText(c.get("arch", "native")), 0))
        self.cb_dmg.setChecked(c.get("dmg", False))
        self.cb_zip.setChecked(c.get("zip", False))
        self.cb_sign.setChecked(c.get("sign", True))
        self.cb_clean.setChecked(c.get("clean", False))
        self.refresh_icon()

    # ---------- import / export ----------
    def export_project(self):
        if not self.has_script():
            QMessageBox.information(self, APP_NAME, self.t("no_script"))
            return
        cfg = self.collect_cfg()
        cfg.pop("mode", None)
        default = os.path.join(os.path.dirname(cfg["script"]),
                               f"{cfg['name'] or 'app'}_v{cfg['version'] or '1.0.0'}{PROJECT_EXT}")
        p, _ = QFileDialog.getSaveFileName(self, self.t("export"), default, f"Py2Mac (*{PROJECT_EXT})")
        if not p:
            return
        if not p.lower().endswith(PROJECT_EXT):
            p += PROJECT_EXT
        base = os.path.dirname(os.path.abspath(p))

        def rel(x):
            try:
                return os.path.relpath(x, base) if x else ""
            except Exception:
                return ""
        data = {"py2mac": APP_VERSION, "saved": datetime.datetime.now().isoformat(timespec="seconds"),
                "config": cfg,
                "relative": {"script": rel(cfg["script"]), "icon": rel(cfg["icon"]), "out": rel(cfg["out"]),
                             "datas": [rel(d) for d in cfg["datas"]]}}
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, APP_NAME, self.t("exported").format(p=p))
        except Exception as e:
            QMessageBox.critical(self, APP_NAME, str(e))

    def import_project(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, self.t("import"), self._start_dir(),
                                                  f"Py2Mac (*{PROJECT_EXT} *.json)")
            if not path:
                return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = data["config"]
            assert isinstance(cfg, dict) and "script" in cfg
        except Exception:
            QMessageBox.warning(self, APP_NAME, self.t("import_bad"))
            return
        base = os.path.dirname(os.path.abspath(path))
        relv = data.get("relative", {})

        def resolve(absp, relp, must_exist=True):
            if absp and (os.path.exists(absp) or not must_exist and os.path.isdir(os.path.dirname(absp))):
                return absp
            if relp:
                cand = os.path.normpath(os.path.join(base, relp))
                if os.path.exists(cand) or not must_exist:
                    return cand
            return absp
        cfg["script"] = resolve(cfg.get("script", ""), relv.get("script"))
        cfg["icon"] = resolve(cfg.get("icon", ""), relv.get("icon"))
        cfg["out"] = resolve(cfg.get("out", ""), relv.get("out"), must_exist=False)
        rd = relv.get("datas", [])
        cfg["datas"] = [resolve(d, rd[i] if i < len(rd) else "") for i, d in enumerate(cfg.get("datas", []))]

        script = cfg["script"]
        if not os.path.isfile(script):
            if QMessageBox.question(self, APP_NAME, self.t("import_missing").format(p=script)) \
                    != QMessageBox.StandardButton.Yes:
                return
            script, _ = QFileDialog.getOpenFileName(self, self.t("pick_py"), base, "Python (*.py *.pyw)")
            if not script:
                return
            cfg["script"] = os.path.abspath(script)
        self.load_script(cfg["script"], cfg=cfg)
        self.settings["projects"][cfg["script"]] = cfg
        save_settings(self.settings)
        self.go(1)
        QMessageBox.information(self, APP_NAME, self.t("imported").format(p=path))

    # ---------- run ----------
    def append_log(self, s):
        self.logview.appendPlainText(s)
        self.logview.moveCursor(QTextCursor.MoveOperation.End)

    def start(self, mode):
        cfg = self.collect_cfg(mode)
        if not os.path.isfile(cfg["script"]):
            QMessageBox.warning(self, APP_NAME, self.t("no_script"))
            return self.go(0)
        if not cfg["name"]:
            QMessageBox.warning(self, APP_NAME, self.t("no_name"))
            return self.go(1)
        if mode == "build":
            if not IS_MAC:
                QMessageBox.warning(self, APP_NAME, self.t("not_mac"))
                return
            final = os.path.join(cfg["out"], f"{cfg['name']}.app")
            if os.path.exists(final) and QMessageBox.question(
                    self, APP_NAME, self.t("overwrite").format(p=final)) != QMessageBox.StandardButton.Yes:
                return
        self.settings["projects"][cfg["script"]] = {k: v for k, v in cfg.items() if k != "mode"}
        save_settings(self.settings)

        self.logview.clear()
        self.append_log(f"{APP_NAME} v{APP_VERSION} — Python {sys.version.split()[0]} — {sys.executable}")
        self.set_busy(True)
        self.worker = Worker(cfg, self.t)
        self.worker.log.connect(self.append_log)
        self.worker.step.connect(self.on_step)
        self.worker.finished_ok.connect(self.on_ok)
        self.worker.failed.connect(self.on_fail)
        self.worker.start()

    def set_busy(self, busy):
        self.b_build.setEnabled(not busy)
        self.b_test.setEnabled(not busy)
        self.b_back.setEnabled(not busy)
        for b in self.step_btns:
            b.setEnabled(not busy)
        self.b_cancel.setVisible(busy)
        if busy:
            self.progress.setRange(0, 0)

    def on_step(self, n, total, text):
        self.progress.setRange(0, total)
        self.progress.setValue(n - 1 if n < total else total)
        self.status.setText(f"[{n}/{total}]  {text}")

    def on_ok(self, final):
        self.set_busy(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.status.setText(self.t("s_done"))
        if not final:
            return
        self.append_log("\n✔ " + final + "\n" + self.t("tip"))
        mb = QMessageBox(self)
        mb.setWindowTitle(APP_NAME)
        mb.setIcon(QMessageBox.Icon.Information)
        mb.setText(self.t("done_ok").format(p=final) + "\n\n" + self.t("tip"))
        b_open = mb.addButton(self.t("open_now"), QMessageBox.ButtonRole.AcceptRole)
        b_run = mb.addButton(self.t("run_now"), QMessageBox.ButtonRole.ActionRole)
        mb.addButton(self.t("close"), QMessageBox.ButtonRole.RejectRole)
        mb.exec()
        if mb.clickedButton() == b_open:
            subprocess.Popen(["open", "-R", final])
        elif mb.clickedButton() == b_run:
            subprocess.Popen(["open", final])

    def on_fail(self, err):
        self.set_busy(False)
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.status.setText("✖ " + err)
        self.append_log("\n✖ " + err)
        self.toggle_log(True)
        QMessageBox.critical(self, APP_NAME, self.t("done_fail").format(e=err))

    def cancel(self):
        if self.worker:
            self.worker.cancel()

    def open_out(self):
        p = self.out.text().strip()
        while p and not os.path.isdir(p):
            p = os.path.dirname(p)
        if p:
            QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def show_about(self):
        QMessageBox.about(self, self.t("about_title"), self.t("about_text").format(
            app=APP_NAME, ver=APP_VERSION, dev=DEVELOPER, venv=VENV_DIR))

    def closeEvent(self, e):
        if self.worker and self.worker.isRunning():
            if QMessageBox.question(self, APP_NAME, self.t("busy_quit")) != QMessageBox.StandardButton.Yes:
                e.ignore()
                return
            self.worker.cancel()
            self.worker.wait(5000)
        e.accept()


class App(QApplication):
    file_opened = pyqtSignal(str)

    def __init__(self, argv):
        super().__init__(argv)
        self.pending = []

    def event(self, e):
        if e.type() == QEvent.Type.FileOpen:  # αρχείο που ρίχτηκε πάνω στο εικονίδιο (macOS)
            self.pending.append(e.file())
            self.file_opened.emit(e.file())
            return True
        return super().event(e)


def main():
    app = App(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE)
    w = MainWindow()
    w.show()
    app.file_opened.connect(w.open_path)
    for f in app.pending:
        w.open_path(f)
    # ορίσματα: python3 ALU_Py2Mac_v1.3.0.pyw MyApp.py   ή   project.py2mac
    for a in sys.argv[1:]:
        if w.open_path(a):
            break
    if ensure_launcher():
        QTimer.singleShot(400, lambda: QMessageBox.information(w, APP_NAME, w.t("launcher_made")))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
