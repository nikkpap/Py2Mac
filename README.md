# 🍏 ALU Py2Mac

**Κάνε την Python εφαρμογή σου κανονική εφαρμογή Mac (.app) — με λίγα κλικ.**
*Turn your Python app into a real Mac app (.app) — in a few clicks.*

Developer: **Nikolaos K. Paridis (aka nikkpap)** — ALU DEV TEAM
Τρέχουσα έκδοση / Current version: **v1.3.0** → `ALU_Py2Mac_v1.3.0.pyw`

---

## 🇬🇷 Ελληνικά

### Τι κάνει
Του δίνεις ένα αρχείο `.py` / `.pyw` και σου βγάζει έτοιμο **`.app`** για macOS (και, αν θέλεις, **`.dmg`** ή **`.zip`** για να το μοιράσεις).

- **Οδηγός 4 βημάτων:** Αρχείο → Στοιχεία → Βιβλιοθήκες → Δημιουργία
- **Drag & drop:** σύρε το `.py` μέσα στο παράθυρο ή πάνω στο εικονίδιο της εφαρμογής
- **Αυτόματος εντοπισμός βιβλιοθηκών:** διαβάζει τα `import` και το `requirements.txt`, αντιστοιχίζει τα σωστά ονόματα pip (π.χ. `cv2` → `opencv-python`, `PIL` → `Pillow`) και παραλείπει όσες είναι μόνο για Windows
- **Εικονίδιο από οποιαδήποτε εικόνα:** JPG, PNG, HEIC (iPhone), WEBP, BMP, GIF, TIFF, ICO, ICNS — σε οποιοδήποτε μέγεθος. Την κόβει τετράγωνη, τη φέρνει σε στυλ macOS και φτιάχνει το `.icns` μόνη της, με προεπισκόπηση
- **Έκδοση & όνομα από το όνομα αρχείου:** `MyApp_v1.2.3.py` → όνομα `MyApp`, έκδοση `1.2.3`
- **Εισαγωγή / Εξαγωγή ρυθμίσεων** σε αρχείο `.py2mac` (λειτουργεί και αν μεταφέρεις τον φάκελο σε άλλο Mac)
- **Πρόσφατα projects**, Ελληνικά / English
- **Χωρίς Terminal:** στην πρώτη εκκίνηση φτιάχνει την εφαρμογή «ALU Py2Mac» στις Εφαρμογές και στην Επιφάνεια εργασίας

### Εγκατάσταση & πρώτη εκκίνηση
1. Χρειάζεσαι Python 3.9+ ([python.org](https://www.python.org/downloads/macos/)).
2. Κατέβασε το `ALU_Py2Mac_v1.3.0.pyw`.
3. Άνοιξε το **Terminal**, γράψε `python3 ` (με κενό), σύρε το αρχείο μέσα και πάτα **Enter**.
4. Την πρώτη φορά εγκαθιστά μόνο του ό,τι χρειάζεται (PyQt6, PyInstaller, Pillow) σε δικό του ιδιωτικό περιβάλλον — 1-3 λεπτά. Μετά το Terminal κλείνει μόνο του.
5. Από εκεί και πέρα άνοιγε το **«ALU Py2Mac»** από τις Εφαρμογές ή την Επιφάνεια εργασίας, με διπλό κλικ.

### 💡 Συμβουλές
- Αν σε άλλο Mac βγει «δεν μπορεί να ανοίξει»: **δεξί κλικ στο .app → Άνοιγμα → Άνοιγμα**.
- Αν η εφαρμογή σου διαβάζει εικόνες/αρχεία, πρόσθεσέ τα στο βήμα 3 («Αρχεία/φάκελοι»).
- Αν κάτι αποτύχει, άνοιξε τις «Λεπτομέρειες» στο βήμα 4 και πάτα «Αντιγραφή».
- Log: `~/Library/Application Support/ALU_Py2Mac/py2mac.log`

---

## 🇬🇧 English

### What it does
Give it a `.py` / `.pyw` file and it builds a ready-to-run macOS **`.app`** (optionally a **`.dmg`** or **`.zip`** for distribution).

- **4-step wizard:** File → Details → Libraries → Build
- **Drag & drop** onto the window or onto the app icon
- **Library auto-detection** from `import`s and `requirements.txt`, with correct pip names; Windows-only libraries are skipped
- **Icon from any image** (JPG, PNG, HEIC, WEBP, BMP, GIF, TIFF, ICO, ICNS, any size): auto square crop, macOS-style rounded icon, `.icns` generated automatically, live preview
- **Name & version from the file name:** `MyApp_v1.2.3.py` → `MyApp`, `1.2.3`
- **Import / Export settings** as `.py2mac` files (portable between Macs)
- Recent projects, Greek / English UI
- **No Terminal:** on first run it creates an "ALU Py2Mac" app in Applications and on the Desktop

### Install & first run
1. Python 3.9+ ([python.org](https://www.python.org/downloads/macos/)).
2. Download `ALU_Py2Mac_v1.3.0.pyw`.
3. Open **Terminal**, type `python3 ` (with a space), drag the file in, press **Enter**.
4. The first run installs everything it needs (PyQt6, PyInstaller, Pillow) into its own private environment (1-3 minutes), then the Terminal window closes.
5. From then on, open **"ALU Py2Mac"** from Applications or the Desktop with a double-click.

### 💡 Tips
- If another Mac says the app "can't be opened": **right-click the .app → Open → Open**.
- If your app reads images/files, add them in step 3 ("Files/folders").
- If something fails, open "Details" in step 4 and press "Copy".
- Log: `~/Library/Application Support/ALU_Py2Mac/py2mac.log`

---

## Changelog
- **v1.3.0** — No Terminal: runs in the background, creates the "ALU Py2Mac" app (Applications + Desktop), drop files onto the app icon
- **v1.2.0** — Icon from any image (crop/fit, macOS style, HEIC support, live preview)
- **v1.1.0** — 4-step wizard UI, Import/Export `.py2mac`, recent projects, checkable library list
- **v1.0.0** — First version: `.py` → `.app` with PyInstaller, auto-installed dependencies, `.dmg` / `.zip`, ad-hoc signing

© Nikolaos K. Paridis (aka nikkpap) — ALU DEV TEAM
