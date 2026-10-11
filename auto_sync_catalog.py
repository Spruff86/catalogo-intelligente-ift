import os
import re
import urllib.parse
import requests
from pathlib import Path
import config
import database
import indexer

GDRIVE_EXCEL_FOLDER_ID = "1vTx6HKVrGbeGld7UQHFsbILiRnSrWD_C"

def fetch_latest_excel_from_gdrive(dest_dir: Path) -> Path:
    """Scrapes the public Google Drive folder and downloads the most recent Excel file."""
    print(f"Checking Google Drive folder {GDRIVE_EXCEL_FOLDER_ID} for latest Excel file...")
    url = f"https://drive.google.com/drive/folders/{GDRIVE_EXCEL_FOLDER_ID}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    r.raise_for_status()

    # Unescape HTML
    text = r.text.encode("utf-8", errors="ignore").decode("unicode_escape", errors="ignore")

    # Match files matching pattern [\"file_id\",[\"folder_id\"],\"Dati per catalogo...xlsx\"
    pattern = r'\[\"([a-zA-Z0-9_-]{25,})\",\[\"' + GDRIVE_EXCEL_FOLDER_ID + r'\"\],\"(Dati per catalogo[^\"]*\.xlsx)\"'
    matches = re.findall(pattern, text)

    if not matches:
        raise RuntimeError("No Excel files found in Google Drive folder.")

    # Sort matches by filename to get the latest date
    matches = sorted(matches, key=lambda x: x[1], reverse=True)
    latest_file_id, latest_filename = matches[0]
    print(f"Found latest file on Drive: '{latest_filename}' (ID: {latest_file_id})")

    dest_path = dest_dir / latest_filename
    if dest_path.exists():
        print(f"File {latest_filename} already downloaded.")
        return dest_path

    download_url = f"https://drive.google.com/uc?id={latest_file_id}&export=download"
    print(f"Downloading from {download_url}...")
    res = requests.get(download_url, headers=headers, stream=True)
    res.raise_for_status()

    with open(dest_path, "wb") as f:
        for chunk in res.iter_content(chunk_size=32768):
            f.write(chunk)

    print(f"Download complete: {dest_path} ({os.path.getsize(dest_path)} bytes)")
    return dest_path


def main():
    print("=== AVVIO SINCRONIZZAZIONE AUTOMATICA CATALOGO ===")
    base_dir = config.BASE_DIR
    latest_excel = fetch_latest_excel_from_gdrive(base_dir)

    # Aggiorna il percorso nel file config per indexer
    config.DATA_EXCEL_PATH = latest_excel

    print(f"Avvio re-indicizzazione database da: {latest_excel.name}...")
    indexer.run_indexing()
    print("=== SINCRONIZZAZIONE COMPLETATA CON SUCCESSO ===")


if __name__ == "__main__":
    main()
