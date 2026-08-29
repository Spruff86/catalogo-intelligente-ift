import sqlite3
import os
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
        
    terms = [t.strip() for t in clean_query.split() if t.strip()]
    
    # Relevance scoring components
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
    
    # Individual term matching in description
    for t in terms:
        score_parts.append("CASE WHEN UPPER(descrizione_articolo) LIKE UPPER(?) THEN 120 ELSE 0 END")
        score_params.append(f"%{t}%")
        
    # Category match
    score_parts.append("CASE WHEN UPPER(gruppo_art) LIKE UPPER(?) THEN 150 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    # Commercial description match
    score_parts.append("CASE WHEN UPPER(descrizione_commerciale) LIKE UPPER(?) THEN 60 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    # Scheda tecnica text match
    score_parts.append("CASE WHEN UPPER(scheda_text) LIKE UPPER(?) THEN 10 ELSE 0 END")
    score_params.append(f"%{clean_query}%")
    
    score_sql = " + ".join(score_parts)
    
    # Filter conditions: all terms must match somewhere (AND logic)
    term_conditions = []
    term_params = []
    for t in terms:
        pat = f"%{t}%"
        term_conditions.append("(cod_art LIKE ? OR descrizione_articolo LIKE ? OR gruppo_art LIKE ? OR descrizione_commerciale LIKE ? OR scheda_text LIKE ?)")
        term_params.extend([pat, pat, pat, pat, pat])
        
    all_conditions = base_conditions + term_conditions
    where_clause = " WHERE " + " AND ".join(all_conditions)
    
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
