import sqlite3
import os
import re
from typing import List, Dict, Any, Optional
import config

def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        cod_art TEXT PRIMARY KEY,
        descrizione_articolo TEXT,
        gruppo_art TEXT,
        um TEXT,
        tipo_peso TEXT,
        unita_imballi TEXT,
        ambiente_cons TEXT,
        shelf_life_it TEXT,
        tempo_cons_gg TEXT,
        minimo_ordine TEXT,
        descrizione_commerciale TEXT,
        prezzo_indicativo TEXT,
        prezzo_contratto TEXT,
        art_attivo TEXT,
        foto_filename TEXT,
        foto_path TEXT,
        scheda_filename TEXT,
        scheda_path TEXT,
        scheda_text TEXT,
        gdrive_foto_id TEXT,
        gdrive_scheda_id TEXT
    )
    """)
    
    # Check if prezzo_contratto column exists (for migrations)
    cursor.execute("PRAGMA table_info(products)")
    cols = [r[1] for r in cursor.fetchall()]
    if "prezzo_contratto" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN prezzo_contratto TEXT")
    if "gdrive_foto_id" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN gdrive_foto_id TEXT")
    if "gdrive_scheda_id" not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN gdrive_scheda_id TEXT")
    
    # Create FTS5 virtual table for full text search
    cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS products_fts USING fts5(
        cod_art,
        descrizione_articolo,
        gruppo_art,
        descrizione_commerciale,
        scheda_text,
        content='products',
        content_rowid='rowid'
    )
    """)
    
    conn.commit()
    conn.close()

def get_categories() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT gruppo_art FROM products WHERE gruppo_art IS NOT NULL AND gruppo_art != '' ORDER BY gruppo_art COLLATE NOCASE")
    cats = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cats

def get_storage_envs() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ambiente_cons FROM products WHERE ambiente_cons IS NOT NULL AND ambiente_cons != '' ORDER BY ambiente_cons")
    envs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return envs

def normalize_italian_term(word: str) -> List[str]:
    """Expands Italian terms with common abbreviations, singular/plural stems with wildcard matching"""
    w = word.lower().strip()
    if not w or len(w) < 2:
        return []
        
    # HoReCa specific domain synonyms & abbreviations
    synonyms_map = {
        "prosciutto": ["%prosc%", "%prosciutt%"],
        "prosciutti": ["%prosc%", "%prosciutt%"],
        "prosc": ["%prosc%", "%prosciutt%"],
        "cotto": ["% cotto%", "%.cotto%", "%cotto %", "%cotto"],
        "cotti": ["% cotto%", "%.cotto%", "%cotto %", "%cotti%"],
        "cotta": ["% cotto%", "%.cotto%", "%cotta%"],
        "crudo": ["%crudo%", "%.crudo%", "%cruda%"],
        "crudi": ["%crudo%", "%.crudo%", "%crudi%"],
        "cruda": ["%crudo%", "%.crudo%", "%cruda%"],
        "mozzarella": ["%mozz%"],
        "mozzarelle": ["%mozz%"],
        "formaggio": ["%formagg%", "%form%"],
        "formaggi": ["%formagg%", "%form%"],
        "farina": ["%farin%"],
        "farine": ["%farin%"],
        "semola": ["%semol%"],
        "semole": ["%semol%"],
        "pomodoro": ["%pomodor%"],
        "pomodori": ["%pomodor%"],
        "pelato": ["%pelat%"],
        "pelati": ["%pelat%"],
        "salame": ["%salam%"],
        "salami": ["%salam%"],
        "carne": ["%carn%"],
        "carni": ["%carn%"],
        "manzo": ["%manz%", "%bovin%"],
        "manzi": ["%manz%", "%bovin%"],
        "scottona": ["%scotton%"],
        "scottone": ["%scotton%"],
        "olio": ["%oli%"],
        "aceto": ["%acet%"],
        "riso": ["%ris%"],
        "pasta": ["%past%"],
        "pizza": ["%pizz%"],
        "pizze": ["%pizz%"]
    }
    
    if w in synonyms_map:
        return synonyms_map[w]
        
    # Common Italian plural to stem rules
    if len(w) > 4 and w.endswith(('i', 'e', 'o', 'a')):
        return [f"%{w[:-1]}%", f"%{w}%"]
            
    return [f"%{w}%"]

def extract_meaningful_tokens(query: str) -> List[str]:
    """Filters out conversational filler and stopwords, leaving meaningful food and technical tokens"""
    conversational_stop_words = {
        "che", "chi", "cosa", "come", "dove", "quando", "perche", "perché", "quale", "quali",
        "posso", "puoi", "possiamo", "potete", "vorrei", "volevo", "desidero", "chiedo",
        "proporre", "consigliare", "consigliami", "consigli", "suggerisci", "suggeriscimi",
        "trovare", "trovami", "cercare", "cerco", "mostrami", "fammi", "vedere", "dimmi",
        "nostro", "nostra", "nostri", "nostre", "vostro", "vostra", "vostri", "vostre",
        "catalogo", "listino", "magazzino", "stock", "disponibili", "disponibile", "abbiamo", "avete",
        "cliente", "clienti", "locale", "locali", "pizzeria", "ristorante", "chef", "pizzaiolo",
        "per", "con", "tra", "fra", "in", "a", "da", "di", "su", "il", "lo", "la", "i", "gli", "le",
        "un", "uno", "una", "del", "dello", "della", "dei", "degli", "delle", "al", "allo", "alla",
        "ai", "agli", "alle", "dal", "dallo", "dalla", "dai", "dagli", "dalle", "nel", "nello",
        "nella", "nei", "negli", "nelle", "sul", "sullo", "sulla", "sui", "sugli", "sulle",
        "piu", "più", "meno", "circa", "indicativamente", "bene", "ottimo", "ideale",
        "indicati", "indicate", "indicato", "indicata", "adatti", "adatte", "adatto", "adatta",
        "ad", "ed", "od", "ore", "ora", "giorni", "giorno", "tempo", "tempi", "senza", "tipo"
    }
    words = re.findall(r'\b[a-zA-Z0-9àèéìòùÀÈÉÌÒÙ]{2,}\b', query.lower())
    return [w for w in words if w not in conversational_stop_words]

def search_products(
    query: str = "", 
    category: str = "", 
    storage_env: str = "", 
    dietary: Optional[str] = None, 
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Searches products strictly by cod_art or descrizione_articolo (product name).
    Does NOT search technical sheets (scheda_text) or commercial descriptions, 
    as explicitly required.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    base_conditions = []
    base_params = []
    
    if category and category != "Tutte":
        base_conditions.append("gruppo_art = ?")
        base_params.append(category)
        
    if storage_env and storage_env != "Tutti":
        base_conditions.append("ambiente_cons = ?")
        base_params.append(storage_env)
        
    if dietary == "senza_glutine":
        base_conditions.append("(scheda_text LIKE '%senza glutine%' OR scheda_text LIKE '%gluten free%' OR scheda_text LIKE '%assenza di glutine%' OR descrizione_articolo LIKE '%S/GLUT%' OR descrizione_articolo LIKE '%SENZA GLUT%')")
    elif dietary == "senza_lattosio":
        base_conditions.append("(scheda_text LIKE '%senza lattosio%' OR scheda_text LIKE '%lactose free%' OR scheda_text LIKE '%assenza di lattosio%' OR descrizione_articolo LIKE '%S/LATT%' OR descrizione_articolo LIKE '%SENZA LATT%')")
        
    clean_query = query.strip()
    limit_clause = f" LIMIT {int(limit)}" if (limit and limit > 0) else ""
    
    if not clean_query:
        where_clause = " WHERE " + " AND ".join(base_conditions) if base_conditions else ""
        sql = f"SELECT * FROM products {where_clause} ORDER BY descrizione_articolo ASC{limit_clause}"
        cursor.execute(sql, base_params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    # Break query into tokens / parts of words
    words = [w.strip() for w in clean_query.split() if w.strip()]
    
    score_parts = []
    score_params = []
    
    # 1. Exact SKU match (highest boost)
    score_parts.append("CASE WHEN UPPER(cod_art) = UPPER(?) THEN 1000 ELSE 0 END")
    score_params.append(clean_query)
    
    # 2. SKU starts with query
    score_parts.append("CASE WHEN UPPER(cod_art) LIKE UPPER(?) THEN 500 ELSE 0 END")
    score_params.append(f"{clean_query}%")
    
    # 3. SKU contains query
    score_parts.append("CASE WHEN UPPER(cod_art) LIKE UPPER(?) THEN 300 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    # 4. Description exact phrase match
    score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 400 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    # 5. Description starts with query
    score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 200 ELSE 0 END")
    score_params.append(f"{clean_query}%")
    
    # Strict matching: every word or piece of word must match ONLY in descrizione_articolo OR cod_art
    term_conditions = []
    term_params = []
    
    for w in words:
        variants = normalize_italian_term(w)
        if not variants:
            variants = [f"%{w}%"]
            
        subconds = []
        for v in variants:
            subconds.append("(cod_art LIKE ? OR descrizione_articolo LIKE ?)")
            term_params.extend([v, v])
            
        sub_str = " OR ".join(subconds)
        term_conditions.append(f"({sub_str})")
        
        # Boost for each token found in descrizione_articolo
        score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 100 ELSE 0 END")
        score_params.append(f"%{w}%")
        
    score_sql = " + ".join(score_parts) if score_parts else "0"
    all_conditions = base_conditions + term_conditions
    where_clause = " WHERE " + " AND ".join(all_conditions) if all_conditions else ""
    all_params = score_params + base_params + term_params
    
    sql = f"""
    SELECT *, ({score_sql}) AS relevance_score
    FROM products
    {where_clause}
    ORDER BY relevance_score DESC, descrizione_articolo ASC{limit_clause}
    """
    
    cursor.execute(sql, all_params)
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results

def get_product_by_code(cod_art: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE UPPER(cod_art) = UPPER(?)", (cod_art.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_catalog_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM products")
    total_products = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM products 
        WHERE (foto_path IS NOT NULL AND foto_path != '') 
           OR (gdrive_foto_id IS NOT NULL AND gdrive_foto_id != '')
    """)
    with_foto = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM products 
        WHERE (scheda_path IS NOT NULL AND scheda_path != '') 
           OR (gdrive_scheda_id IS NOT NULL AND gdrive_scheda_id != '')
    """)
    with_scheda = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE scheda_text IS NOT NULL AND length(scheda_text) > 20")
    with_text = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_products": total_products,
        "with_foto": with_foto,
        "with_scheda": with_scheda,
        "with_text": with_text
    }

def get_all_products_basic() -> List[Dict[str, Any]]:
    """Returns a lightweight list of all products for dropdowns and recipe selectors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cod_art, descrizione_articolo, um, prezzo_indicativo, prezzo_contratto 
        FROM products 
        ORDER BY cod_art ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    items = []
    for r in rows:
        p_str = str(r["prezzo_indicativo"] or "0").replace("€", "").replace(",", ".").strip()
        try:
            p_val = float(p_str)
        except (ValueError, TypeError):
            p_val = 0.0
            
        c_str = str(r["prezzo_contratto"] or "0").replace("€", "").replace(",", ".").strip()
        try:
            c_val = float(c_str)
        except (ValueError, TypeError):
            c_val = 0.0
            
        items.append({
            "cod_art": r["cod_art"],
            "descrizione_articolo": r["descrizione_articolo"],
            "um": r["um"] or "Kg",
            "prezzo_soglia": p_val,
            "prezzo_contratto": c_val
        })
    return items
