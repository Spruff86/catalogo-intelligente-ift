import os
import openpyxl
from pypdf import PdfReader
from pathlib import Path
from tqdm import tqdm
import database
import config

def build_file_map(directory: Path, valid_extensions: set):
    """Build a mapping of normalized SKU base to actual file path."""
    file_map = {}
    if not directory.exists():
        print(f"Warning: Directory not found: {directory}")
        return file_map
        
    for f in os.listdir(directory):
        if f.startswith('.'):
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in valid_extensions:
            full_path = directory / f
            base_name = os.path.splitext(f)[0].strip()
            
            # Map exact filename stem
            file_map[base_name.upper()] = str(full_path)
            
            # Also clean variations like _t, _s, _eng, etc.
            clean_name = base_name.replace("_t", "").replace("_s", "").replace("_eng", "").replace("__t", "").replace("_t_1", "").replace("_t ENG", "").strip().upper()
            if clean_name not in file_map:
                file_map[clean_name] = str(full_path)
                
    return file_map

def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        return ""

def run_indexing():
    print("Initializing database...")
    database.init_db()
    
    print("Scanning photo and technical sheet directories...")
    foto_map = build_file_map(config.FOTO_DIR, {'.jpg', '.jpeg', '.png'})
    schede_map = build_file_map(config.SCHEDE_DIR, {'.pdf'})
    
    print(f"Found {len(foto_map)} photo mappings and {len(schede_map)} technical sheet mappings.")
    
    print(f"Reading Excel catalog from {config.DATA_EXCEL_PATH}...")
    wb = openpyxl.load_workbook(config.DATA_EXCEL_PATH, read_only=True, data_only=True)
    ws = wb.active
    
    all_rows = list(ws.iter_rows(values_only=True))
    if not all_rows:
        print("Excel is empty!")
        return
        
    # Find the header row (the first row containing 'Cod_art' or 'Item_Code')
    header_idx = -1
    for i, row in enumerate(all_rows):
        row_str = [str(c).strip() if c is not None else "" for c in row]
        if "Cod_art" in row_str or "Item_Code" in row_str or "Descrizione_articolo" in row_str:
            header_idx = i
            break
            
    if header_idx == -1:
        print("Could not find header row in Excel!")
        return
        
    header = [str(col).strip() if col is not None else "" for col in all_rows[header_idx]]
    data_rows = all_rows[header_idx + 1:]
    print(f"Found header at row {header_idx + 1} with {len(data_rows)} data rows. Columns: {header[:10]}...")
    
    # Map header names to indices
    col_map = {col: i for i, col in enumerate(header)}
    
    def get_val(row, name, default=""):
        idx = col_map.get(name)
        if idx is not None and idx < len(row) and row[idx] is not None:
            v = str(row[idx]).strip()
            if v == "zzz-zzz-zzz-zzz-zzz-zzz":
                return ""
            return v
        return default

    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM products_fts")
    
    products_to_insert = []
    
    print("Processing products and extracting PDF texts...")
    for row in tqdm(data_rows):
        cod_art = get_val(row, "Cod_art") or get_val(row, "Item_Code")
        if not cod_art:
            continue
            
        cod_art_clean = cod_art.strip().upper()
        
        descrizione_articolo = get_val(row, "Descrizione_articolo") or get_val(row, "Item_description")
        gruppo_art = get_val(row, "Gruppo_art") or get_val(row, "Item_Group")
        um = get_val(row, "Um") or get_val(row, "M.U.")
        tipo_peso = get_val(row, "Tipo_peso") or get_val(row, "Weight_note")
        unita_imballi = get_val(row, "Unità_e_imballi") or get_val(row, "Units_and_Packaging")
        ambiente_cons = get_val(row, "Ambiente_cons") or get_val(row, "Storage_Env")
        shelf_life_it = get_val(row, "Shelf_life_IT") or get_val(row, "Shelf_life_LNG")
        tempo_cons_gg = get_val(row, "TempoCons_gg") or get_val(row, "DeliveryTime_days")
        minimo_ordine = get_val(row, "Minimo_ordine") or get_val(row, "Minimum_order")
        descrizione_commerciale = get_val(row, "Descrizione Commerciale") or get_val(row, "Commercial_Description")
        
        # Priority: Prezzo Soglia -> Obiettivo -> Contratto
        prezzo_indicativo = get_val(row, "Soglia") or get_val(row, "Obiettivo") or get_val(row, "Contratto") or get_val(row, "Prz_BP")
        art_attivo = get_val(row, "Art_Attivo", "Y")
        
        # Match Photo
        foto_path = foto_map.get(cod_art_clean, "")
        if not foto_path:
            # try variants
            base_sku = cod_art_clean.replace("PZ", "").replace("FRO", "").replace("CRT", "").replace("QU", "").strip()
            foto_path = foto_map.get(base_sku, "")
            
        foto_filename = os.path.basename(foto_path) if foto_path else ""
        
        # Match Scheda Tecnica
        scheda_path = schede_map.get(cod_art_clean, "")
        if not scheda_path:
            base_sku = cod_art_clean.replace("PZ", "").replace("FRO", "").replace("CRT", "").replace("QU", "").strip()
            scheda_path = schede_map.get(base_sku, "")
            
        scheda_filename = os.path.basename(scheda_path) if scheda_path else ""
        
        # Extract PDF text if scheda exists
        scheda_text = ""
        if scheda_path and os.path.exists(scheda_path):
            scheda_text = extract_pdf_text(scheda_path)
            
        products_to_insert.append((
            cod_art,
            descrizione_articolo,
            gruppo_art,
            um,
            tipo_peso,
            unita_imballi,
            ambiente_cons,
            shelf_life_it,
            tempo_cons_gg,
            minimo_ordine,
            descrizione_commerciale,
            prezzo_indicativo,
            art_attivo,
            foto_filename,
            foto_path,
            scheda_filename,
            scheda_path,
            scheda_text
        ))
        
    print(f"Inserting {len(products_to_insert)} products into database...")
    cursor.executemany("""
    INSERT INTO products (
        cod_art,
        descrizione_articolo,
        gruppo_art,
        um,
        tipo_peso,
        unita_imballi,
        ambiente_cons,
        shelf_life_it,
        tempo_cons_gg,
        minimo_ordine,
        descrizione_commerciale,
        prezzo_indicativo,
        art_attivo,
        foto_filename,
        foto_path,
        scheda_filename,
        scheda_path,
        scheda_text
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, products_to_insert)
    
    # Populate FTS
    print("Building full-text search index...")
    cursor.execute("""
    INSERT INTO products_fts(rowid, cod_art, descrizione_articolo, gruppo_art, descrizione_commerciale, scheda_text)
    SELECT rowid, cod_art, descrizione_articolo, gruppo_art, descrizione_commerciale, scheda_text FROM products
    """)
    
    conn.commit()
    conn.close()
    print("Indexing complete! Database ready.")

if __name__ == "__main__":
    run_indexing()
