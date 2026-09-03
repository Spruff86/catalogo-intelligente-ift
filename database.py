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
        
    clean_lower = clean_query.lower()
    is_gluten_free_query = any(p in clean_lower for p in ["senza glutine", "gluten free", "per celiaci", "no glutine", "senza glut."])
    is_lactose_free_query = any(p in clean_lower for p in ["senza lattosio", "delattosato", "lactose free", "no lattosio", "delattosata"])
    
    # Extract core tokens
    tokens = extract_meaningful_tokens(clean_query)
    numeric_tokens = re.findall(r'\b\d+\b', clean_query)
    
    # Filter tokens if specific allergen query
    filtered_tokens = []
    for t in tokens:
        if is_gluten_free_query and t in ["glutine", "gluten", "celiaci"]:
            continue
        if is_lactose_free_query and t in ["lattosio", "lactose", "delattosato"]:
            continue
        filtered_tokens.append(t)
        
    # Food/domain tokens (non-numeric)
    food_tokens = [t for t in filtered_tokens if not t.isdigit() and len(t) > 2]
    if not food_tokens:
        food_tokens = [t for t in filtered_tokens if len(t) > 1]
    if not food_tokens:
        food_tokens = re.findall(r'\b[a-zA-Z0-9]{2,}\b', clean_lower)
        
    # Helper to execute query with token conditions
    def execute_query(required_tokens: List[str]):
        score_parts = []
        score_params = []
        
        # Exact SKU match
        score_parts.append("CASE WHEN UPPER(cod_art) = UPPER(?) THEN 1000 ELSE 0 END")
        score_params.append(clean_query)
        
        # SKU prefix match
        score_parts.append("CASE WHEN UPPER(cod_art) LIKE UPPER(?) THEN 500 ELSE 0 END")
        score_params.append(f"{clean_query}%")
        
        # Description exact phrase match
        score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 300 ELSE 0 END")
        score_params.append(f"%{clean_query}%")
        
        # Technical relevance boosts in PDF text or description
        for num in numeric_tokens:
            score_parts.append("CASE WHEN (scheda_text LIKE ? OR descrizione_articolo LIKE ?) THEN 250 ELSE 0 END")
            score_params.extend([f"%{num}%", f"%{num}%"])
            
        for kw in ["w350", "w380", "w300", "w 3", "manitoba", "lunga lievitazione", "alta qualita", "dop"]:
            score_parts.append(f"CASE WHEN (scheda_text LIKE '%{kw}%' OR descrizione_articolo LIKE '%{kw}%') THEN 200 ELSE 0 END")
            
        term_conditions = []
        term_params = []
        
        for token in required_tokens:
            variants = normalize_italian_term(token)
            if not variants:
                continue
                
            variant_subconditions = []
            for v in variants:
                # Search product identification fields (NOT allergen cross-contamination text)
                variant_subconditions.append("(cod_art LIKE ? OR descrizione_articolo LIKE ? OR gruppo_art LIKE ? OR descrizione_commerciale LIKE ?)")
                term_params.extend([v, v, v, v])
                
                score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 120 ELSE 0 END")
                score_params.append(v)
                
            if variant_subconditions:
                term_conditions.append(f"({' OR '.join(variant_subconditions)})")
                
        # Dietary / Allergen constraints (searched specifically in technical sheets)
        if is_gluten_free_query:
            term_conditions.append("(scheda_text LIKE '%senza glutine%' OR scheda_text LIKE '%gluten free%' OR scheda_text LIKE '%assenza di glutine%' OR descrizione_articolo LIKE '%S/GLUT%' OR descrizione_articolo LIKE '%SENZA GLUT%')")
            score_parts.append("CASE WHEN (scheda_text LIKE '%senza glutine%' OR scheda_text LIKE '%gluten free%') THEN 300 ELSE 0 END")
            
        if is_lactose_free_query:
            term_conditions.append("(scheda_text LIKE '%senza lattosio%' OR scheda_text LIKE '%lactose free%' OR scheda_text LIKE '%assenza di lattosio%' OR descrizione_articolo LIKE '%S/LATT%' OR descrizione_articolo LIKE '%SENZA LATT%')")
            score_parts.append("CASE WHEN (scheda_text LIKE '%senza lattosio%' OR scheda_text LIKE '%lactose free%') THEN 300 ELSE 0 END")
            
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
        return [dict(row) for row in cursor.fetchall()]

    # 1. Try with food tokens
    results = execute_query(food_tokens)
    
    # 2. If 0, try individual food tokens (e.g. 'farine')
    if not results and len(food_tokens) > 1:
        for single_token in food_tokens:
            single_res = execute_query([single_token])
            if single_res:
                results = single_res
                break

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

def get_all_products_basic() -> List[Dict[str, Any]]:
    """Returns a lightweight list of all products for dropdowns and recipe selectors."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cod_art, descrizione_articolo, um, prezzo_indicativo 
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
        items.append({
            "cod_art": r["cod_art"],
            "descrizione_articolo": r["descrizione_articolo"],
            "um": r["um"] or "Kg",
            "prezzo_soglia": p_val
        })
    return items
