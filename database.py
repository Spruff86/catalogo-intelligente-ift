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
        art_attivo TEXT,
        foto_filename TEXT,
        foto_path TEXT,
        scheda_filename TEXT,
        scheda_path TEXT,
        scheda_text TEXT
    )
    """)
    
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
    cursor.execute("SELECT DISTINCT gruppo_art FROM products WHERE gruppo_art IS NOT NULL AND gruppo_art != '' ORDER BY gruppo_art")
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
        "cotto": ["%cott%"],
        "cotti": ["%cott%"],
        "cotta": ["%cott%"],
        "crudo": ["%crud%"],
        "crudi": ["%crud%"],
        "cruda": ["%crud%"],
        "mozzarella": ["%mozz%"],
        "mozzarelle": ["%mozz%"],
        "formaggio": ["%formagg%", "%form%"],
        "formaggi": ["%formagg%", "%form%"],
        "farina": ["%farin%"],
        "farine": ["%farin%"],
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

def search_products(query: str = "", category: str = "", storage_env: str = "", limit: Optional[int] = None) -> List[Dict[str, Any]]:
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
        
    clean_query = query.strip()
    limit_clause = f" LIMIT {int(limit)}" if (limit and limit > 0) else ""
    
    if not clean_query:
        where_clause = " WHERE " + " AND ".join(base_conditions) if base_conditions else ""
        sql = f"SELECT * FROM products {where_clause} ORDER BY descrizione_articolo ASC{limit_clause}"
        cursor.execute(sql, base_params)
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
        
    # Check for special dietary / allergen filters in query
    clean_lower = clean_query.lower()
    is_gluten_free_query = any(p in clean_lower for p in ["senza glutine", "gluten free", "per celiaci", "no glutine", "senza glut."])
    is_lactose_free_query = any(p in clean_lower for p in ["senza lattosio", "delattosato", "lactose free", "no lattosio", "delattosata"])
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z0-9àèéìòùÀÈÉÌÒÙ]{2,}\b', clean_query)
    
    # Filter out conversational filler and stopwords
    stop_words = {
        "quali", "quale", "cosa", "come", "dove", "sono", "abbiamo", "catalogo", 
        "indicati", "indicate", "indicato", "indicata", "consigliami", "trovami",
        "vorrei", "sapere", "dimmi", "elenco", "tutti", "tutte", "degli", "delle",
        "della", "dello", "agli", "alle", "alla", "allo", "nella", "nello", "nelle",
        "negli", "questo", "questa", "questi", "queste", "nostro", "nostra", "nostri",
        "nostre", "vostro", "vostra", "vostri", "vostre", "senza", "avessimo", "avete",
        "avere", "presenti", "presente", "trovare", "cercare", "cerco", "volevo", "nel",
        "sul", "sulla", "sulle", "sugli", "sui", "per", "con", "tra", "fra"
    }
    
    # Filter search words
    search_words = []
    for w in words:
        wl = w.lower()
        if is_gluten_free_query and wl in ["glutine", "gluten", "celiaci"]:
            continue
        if is_lactose_free_query and wl in ["lattosio", "lactose", "delattosato", "delattosati"]:
            continue
        if wl not in stop_words:
            search_words.append(w)
            
    if not search_words:
        # If all were filtered out, keep nouns
        search_words = [w for w in words if w.lower() not in {"quali", "quale", "abbiamo", "catalogo", "avessimo", "nel"}]
        
    score_parts = []
    score_params = []
    
    # Exact SKU match (highest weight)
    score_parts.append("CASE WHEN UPPER(cod_art) = UPPER(?) THEN 1000 ELSE 0 END")
    score_params.append(clean_query)
    
    # SKU prefix match
    score_parts.append("CASE WHEN UPPER(cod_art) LIKE UPPER(?) THEN 500 ELSE 0 END")
    score_params.append(f"{clean_query}%")
    
    # Description exact phrase match
    score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 300 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    term_conditions = []
    term_params = []
    
    for word in search_words:
        variants = normalize_italian_term(word)
        if not variants:
            continue
            
        variant_subconditions = []
        for v in variants:
            variant_subconditions.append("(cod_art LIKE ? OR descrizione_articolo LIKE ? OR gruppo_art LIKE ? OR descrizione_commerciale LIKE ? OR scheda_text LIKE ?)")
            term_params.extend([v, v, v, v, v])
            
            score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 120 ELSE 0 END")
            score_params.append(v)
            
        if variant_subconditions:
            term_conditions.append(f"({' OR '.join(variant_subconditions)})")
            
    # Apply dietary / allergen constraints if requested
    if is_gluten_free_query:
        term_conditions.append("(scheda_text LIKE '%senza glutine%' OR scheda_text LIKE '%gluten free%' OR scheda_text LIKE '%assenza di glutine%' OR descrizione_articolo LIKE '%S/GLUT%' OR descrizione_articolo LIKE '%SENZA GLUT%')")
        score_parts.append("CASE WHEN (scheda_text LIKE '%senza glutine%' OR scheda_text LIKE '%gluten free%') THEN 250 ELSE 0 END")
        
    if is_lactose_free_query:
        term_conditions.append("(scheda_text LIKE '%senza lattosio%' OR scheda_text LIKE '%lactose free%' OR scheda_text LIKE '%assenza di lattosio%' OR descrizione_articolo LIKE '%S/LATT%' OR descrizione_articolo LIKE '%SENZA LATT%')")
        score_parts.append("CASE WHEN (scheda_text LIKE '%senza lattosio%' OR scheda_text LIKE '%lactose free%') THEN 250 ELSE 0 END")
        
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
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

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
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE foto_path IS NOT NULL AND foto_path != ''")
    with_foto = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE scheda_path IS NOT NULL AND scheda_path != ''")
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
