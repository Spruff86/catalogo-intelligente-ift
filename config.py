import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Base directory of the repository
BASE_DIR = Path(__file__).parent.resolve()

# Excel Catalog Path
DATA_EXCEL_PATH = BASE_DIR / "Dati per catalogo intelligente aggiornati al 2026-08-29.xlsx"

# Database Path
DB_PATH = BASE_DIR / "catalogo_horeca.db"

# Local Google Drive paths (fallback for local Mac development)
LOCAL_GDRIVE_MEDIA = Path("/Users/federicoprovolo/Library/CloudStorage/GoogleDrive-provolo.federico@gmail.com/Il mio Drive/Documenti/ITALIAN FOOD TRADING/Cataloghi/Foto e schede tecniche")

# Relative paths if copied into repository
REPO_FOTO_DIR = BASE_DIR / "Foto articoli"
REPO_SCHEDE_DIR = BASE_DIR / "Schede tecniche"

# Resolved Media Folders
FOTO_DIR = REPO_FOTO_DIR if REPO_FOTO_DIR.exists() else (LOCAL_GDRIVE_MEDIA / "Foto articoli")
SCHEDE_DIR = REPO_SCHEDE_DIR if REPO_SCHEDE_DIR.exists() else (LOCAL_GDRIVE_MEDIA / "Schede tecniche")

# AI Configuration
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
