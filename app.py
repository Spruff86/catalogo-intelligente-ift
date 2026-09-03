import os
import streamlit as st
from PIL import Image
from pathlib import Path
from typing import Optional
import base64
from datetime import datetime

import config
import database
import ai_assistant
import quote_generator
import food_cost_calculator
import urllib.parse

# Page configuration
st.set_page_config(
    page_title="Catalogo Intelligente — Italian Food Trading",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme and UI Overhaul
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Preserve Streamlit Material Icons ligatures */
    span[data-testid="stIconMaterial"], 
    [class*="material-icons"], 
    [class*="MaterialSymbols"], 
    .material-symbols-rounded, 
    .material-symbols-outlined,
    [data-baseweb="icon"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
        speak: none;
        font-style: normal;
        font-weight: normal;
        font-variant: normal;
        text-transform: none;
        line-height: 1;
        -webkit-font-smoothing: antialiased;
    }
    
    /* Top Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        border-radius: 16px;
        padding: 24px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
        background: linear-gradient(90deg, #FFFFFF 0%, #F1F5F9 50%, #E2E8F0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        font-weight: 400;
        margin-bottom: 16px;
    }
    
    .hero-stats-row {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
    }
    
    .hero-pill {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #F8FAFC;
        backdrop-filter: blur(8px);
    }
    
    /* Product Card Styling */
    .product-title-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.25;
        margin-bottom: 6px;
    }
    
    .sku-badge {
        display: inline-block;
        background: #F1F5F9;
        color: #475569;
        border: 1px solid #CBD5E1;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-bottom: 12px;
        letter-spacing: 0.05em;
    }
    
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    
    .badge-category { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-refrigerato { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-congelato { background: #F0F9FF; color: #0369A1; border: 1px solid #BAE6FD; }
    .badge-asciutto { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .badge-shelflife { background: #FAF5FF; color: #6B21A8; border: 1px solid #E9D5FF; }
    .badge-packaging { background: #F8FAFC; color: #334155; border: 1px solid #E2E8F0; }
    
    .price-tag-box {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        padding: 10px 14px;
        border-radius: 10px;
        margin-top: 10px;
    }
    
    .price-value-text {
        font-size: 1.35rem;
        font-weight: 800;
        color: #15803D;
    }
    
    /* Focus State Indicator */
    .focus-alert-active {
        background: #EFF6FF;
        border: 1px solid #93C5FD;
        border-left: 5px solid #2563EB;
        padding: 12px 16px;
        border-radius: 10px;
        color: #1E3A8A;
        margin-bottom: 16px;
    }
    
    .focus-alert-general {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-left: 5px solid #16A34A;
        padding: 12px 16px;
        border-radius: 10px;
        color: #14532D;
        margin-bottom: 16px;
    }

    /* Food Cost Metric Card Styling */
    .fc-metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .fc-metric-val {
        font-size: 1.45rem;
        font-weight: 800;
        margin-top: 2px;
    }

    /* Quotation Summary Box */
    .quote-total-box {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border-radius: 12px;
        padding: 18px 22px;
        color: white;
        margin-top: 12px;
        margin-bottom: 16px;
        border: 1px solid #334155;
    }

    .quote-total-amount {
        font-size: 1.6rem;
        font-weight: 800;
        color: #FBBF24;
    }
    
    /* Clean Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        transition: all 0.2s ease !important;
    }
    
    /* Buttons */
    .stButton>button, .stDownloadButton>button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton>button:hover, .stDownloadButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px -2px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Helper to resolve image/PDF paths across Local and Cloud
def resolve_file(stored_path: str, filename: str, fallback_dir: Path) -> Optional[str]:
    if stored_path and os.path.exists(stored_path):
        return stored_path
    if filename and fallback_dir.exists():
        candidate = fallback_dir / filename
        if candidate.exists():
            return str(candidate)
    return None

# Initialize database if needed
if not config.DB_PATH.exists():
    database.init_db()

# Helper to load company logo
def get_company_logo_b64() -> str:
    logo_path = Path(__file__).parent / "ift_logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return "https://www.italianfoodtrading.com/wp-content/uploads/2025/03/logo-header.png"

company_logo_b64 = get_company_logo_b64()

# Session state initialization
if "chat_focused_sku" not in st.session_state:
    st.session_state.chat_focused_sku = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "quote_items" not in st.session_state:
    st.session_state.quote_items = []
if "quote_customer" not in st.session_state:
    st.session_state.quote_customer = {
        "name": "",
        "contact": "",
        "address": "",
        "phone_email": "",
        "agent_name": "Agente Italian Food Trading",
        "iva_rate": 10.0,
        "notes": "Resa franco destino. Pagamento come da accordi commerciali. Merce soggetta a disponibilità. Fatturazione al peso effettivo alla consegna.",
        "validity": "30 giorni",
        "doc_number": f"PREV-{datetime.now().strftime('%Y%m%d')}-01"
    }

# Food Cost Session State
if "recipe_name" not in st.session_state:
    st.session_state.recipe_name = "Pizza Gourmet Orazio alla Brace & Burrata"
if "recipe_category" not in st.session_state:
    st.session_state.recipe_category = "Pizzeria Gourmet"
if "recipe_portions" not in st.session_state:
    st.session_state.recipe_portions = 1
if "recipe_target_pct" not in st.session_state:
    st.session_state.recipe_target_pct = 28.0
if "recipe_actual_price" not in st.session_state:
    st.session_state.recipe_actual_price = 13.50
if "recipe_ingredients" not in st.session_state:
    st.session_state.recipe_ingredients = [
        dict(x) for x in food_cost_calculator.RECIPE_TEMPLATES["🌟 Pizza Gourmet Orazio alla Brace & Burrata"]["ingredients"]
    ]

# Product Comparison Session State
if "compare_skus" not in st.session_state:
    st.session_state.compare_skus = ["A110419QU", "A110414QU"]
if "compare_ai_analysis" not in st.session_state:
    st.session_state.compare_ai_analysis = None

# --- SIDEBAR OVERHAUL ---
with st.sidebar:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px; background: #FFFFFF; padding: 10px 12px; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
        <img src="{company_logo_b64}" style="height: 36px; width: auto; object-fit: contain;">
        <div>
            <div style="font-weight: 800; font-size: 1.05rem; color: #0F172A; line-height: 1.1;">Italian Food Trading</div>
            <div style="font-size: 0.78rem; color: #64748B;">S.r.l. — Verona</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # API Key Configuration Card
    st.markdown("##### ⚡ Motore Intelligenza Artificiale")
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="La tua chiave API è salvata e protetta localmente."
    )
    
    active_api_key = user_api_key.strip() or env_api_key
    if active_api_key:
        st.markdown("""
        <div style="background:#ECFDF5; border:1px solid #A7F3D0; padding:6px 12px; border-radius:8px; font-size:0.8rem; color:#065F46; font-weight:600; margin-bottom:10px;">
            🟢 API Key Connessa & Attiva
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#FEF2F2; border:1px solid #FECACA; padding:6px 12px; border-radius:8px; font-size:0.8rem; color:#991B1B; font-weight:600; margin-bottom:10px;">
            ⚠️ Inserisci API Key per usare l'AI
        </div>
        """, unsafe_allow_html=True)
        
    model_choice = st.selectbox(
        "Modello LLM",
        options=["gemini-3.6-flash", "gemini-2.5-flash", "gemini-3.7-flash", "gemini-flash-latest", "gemini-pro-latest"],
        index=0,
        help="Gemini 3.6 Flash o 2.5 Flash garantiscono massima velocità e stabilità."
    )
    
    enable_web_search = st.toggle("🌐 Ricerca Web Google in tempo reale", value=True, help="Ricerca abbinamenti, ricette gourmet e tendenze in tempo reale.")
    
    st.divider()
    
    # Catalog Filters
    st.markdown("##### 🏷️ Filtri Catalogo")
    categories = ["Tutte"] + database.get_categories()
    selected_category = st.selectbox("Categoria Merceologica", categories, index=0)
    
    storage_envs = ["Tutti"] + database.get_storage_envs()
    selected_env = st.selectbox("Ambiente di Conservazione", storage_envs, index=0)
    
    st.divider()
    
    # Stats Card
    stats = database.get_catalog_stats()
    st.markdown(f"""
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 14px; border-radius:10px; font-size:0.82rem; color:#475569;">
        <div style="font-weight:700; color:#1E293B; margin-bottom:6px;">📊 Stato Catalogo</div>
        <div>📦 <b>{stats['total_products']:,}</b> Prodotti indicizzati</div>
        <div>📸 <b>{stats['with_foto']:,}</b> Foto collegate</div>
        <div>📄 <b>{stats['with_scheda']:,}</b> Schede PDF archiviate</div>
        <div>🧠 <b>{stats['with_text']:,}</b> Schede con testo AI</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    if st.button("🔄 Sincronizza & Re-indicizza", use_container_width=True):
        with st.spinner("Indicizzazione in corso..."):
            import indexer
            indexer.run_indexing()
            st.success("Catalogo sincronizzato!")
            st.rerun()

# --- HERO HEADER BANNER ---
st.markdown(f"""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
        <div>
            <div class="hero-title" style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
                <span>🍴 Catalogo Intelligente Ho.Re.Ca.</span>
                <span style="display: inline-flex; align-items: center; background: rgba(255, 255, 255, 0.95); padding: 4px 12px; border-radius: 10px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.12);">
                    <img src="{company_logo_b64}" alt="Italian Food Trading S.r.l. Verona" style="height: 34px; width: auto; object-fit: contain;">
                </span>
            </div>
            <div class="hero-subtitle">Italian Food Trading S.r.l. (Verona) • Consulenza Tecnica Certificata, Preventivi PDF & Assistente AI Ho.Re.Ca</div>
        </div>
    </div>
    <div class="hero-stats-row">
        <div class="hero-pill">📦 {stats['total_products']:,} Articoli a Catalogo</div>
        <div class="hero-pill">📸 {stats['with_foto']:,} Foto HD</div>
        <div class="hero-pill">📄 {stats['with_scheda']:,} Schede Tecniche PDF</div>
        <div class="hero-pill">🛒 {len(st.session_state.quote_items)} Articoli in Preventivo</div>
        <div class="hero-pill">⚡ Modello: {model_choice}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Full-width search bar (no limit dropdown)
search_query = st.text_input("🔍 Ricerca Intelligente Articoli (SKU, nome, ingrediente es. 'farina', 'burrata', 'wagyu', 'A001012')", "")

# Fetch all matching products without artificial limits
products = database.search_products(
    query=search_query,
    category=selected_category,
    storage_env=selected_env,
    limit=None
)

# Tabs Definition
quote_count = len(st.session_state.quote_items)
quote_tab_label = f"📑 Preventivo & Ordine ({quote_count})" if quote_count > 0 else "📑 Preventivo & Ordine"

compare_count = len(st.session_state.compare_skus)
compare_tab_label = f"⚖️ Confronto ({compare_count})" if compare_count > 0 else "⚖️ Confronto Prodotti"

tab_catalog, tab_chat, tab_quote, tab_foodcost, tab_compare = st.tabs([
    "📦 Scheda Prodotto & Catalogo", 
    "🤖 Studio Consulenza & Chat AI", 
    quote_tab_label,
    "📊 Calcolatore Food Cost",
    compare_tab_label
])

# =========================================================================
# TAB 1: SCHEDA PRODOTTO & CATALOGO
# =========================================================================
with tab_catalog:
    if not products:
        st.warning(f"Nessun articolo trovato per '{search_query}'. Prova a verificare l'ortografia o a selezionare 'Tutte' nei filtri di categoria.")
    else:
        st.markdown(f"🎯 Trovati **{len(products)}** articoli disponibili:")
        
        # Product selector
        product_options = {
            f"{p['cod_art']} — {p['descrizione_articolo']} [{p.get('gruppo_art', '')}]": p['cod_art']
            for p in products
        }
        
        selected_label = st.selectbox(
            "Seleziona il prodotto per aprire la scheda tecnica dettagliata:",
            options=list(product_options.keys()),
            index=0,
            label_visibility="collapsed"
        )
        
        selected_sku = product_options[selected_label]
        current_prod = database.get_product_by_code(selected_sku)
        
        if current_prod:
            # Card Container
            with st.container(border=True):
                col_img, col_info = st.columns([1, 2], gap="large")
                
                with col_img:
                    foto_resolved = resolve_file(current_prod.get('foto_path'), current_prod.get('foto_filename'), config.FOTO_DIR)
                    if foto_resolved and os.path.exists(foto_resolved):
                        st.image(foto_resolved, use_container_width=True)
                        st.caption(f"Codice SKU: `{current_prod['cod_art']}`")
                    else:
                        st.markdown("""
                        <div style="background:#F1F5F9; border:2px dashed #CBD5E1; border-radius:12px; height:200px; display:flex; flex-direction:column; align-items:center; justify-content:center; color:#94A3B8; margin-bottom:8px;">
                            <span style="font-size:2.5rem;">📷</span>
                            <span style="font-size:0.85rem; font-weight:600; margin-top:6px;">Foto non disponibile</span>
                        </div>
                        """, unsafe_allow_html=True)
                        st.caption(f"Codice SKU: `{current_prod['cod_art']}`")
                
                with col_info:
                    st.markdown(f'<div class="product-title-text">{current_prod["descrizione_articolo"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<span class="sku-badge">SKU: {current_prod["cod_art"]}</span>', unsafe_allow_html=True)
                    
                    # Dynamic Environment Badge Color
                    env_class = "badge-refrigerato" if "refrigerato" in current_prod.get('ambiente_cons', '').lower() else ("badge-congelato" if "congelato" in current_prod.get('ambiente_cons', '').lower() else "badge-asciutto")
                    
                    st.markdown(f"""
                    <div style="margin-bottom: 8px;">
                        <span class="badge-pill badge-category">📁 {current_prod.get('gruppo_art', 'N/D')}</span>
                        <span class="badge-pill {env_class}">❄️ {current_prod.get('ambiente_cons', 'N/D')}</span>
                        <span class="badge-pill badge-shelflife">⏳ Shelf-Life: {current_prod.get('shelf_life_it', 'N/D')}</span>
                        <span class="badge-pill badge-packaging">⚖️ {current_prod.get('tipo_peso', 'N/D')}</span>
                        <span class="badge-pill badge-packaging">📦 {current_prod.get('unita_imballi', 'N/D')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Key details grid
                    col_d1, col_d2 = st.columns(2)
                    with col_d1:
                        st.markdown(f"• **Unità di Misura:** `{current_prod.get('um', 'Kg')}`")
                        st.markdown(f"• **Minimo d'Ordine:** `{current_prod.get('minimo_ordine', 'N/D')}`")
                        st.markdown(f"• **Tempo Consegna:** `{current_prod.get('tempo_cons_gg', 'N/D')} giorni`")
                    with col_d2:
                        st.markdown(f"• **Stato Articolo:** `{'Attivo a Listino' if current_prod.get('art_attivo') == 'Y' else 'Disattivo'}`")
                        if current_prod.get('prezzo_indicativo'):
                            st.markdown(f"""
                            <div class="price-tag-box">
                                <div style="font-size:0.75rem; color:#047857; font-weight:600;">Prezzo Soglia:</div>
                                <div class="price-value-text">€ {current_prod.get('prezzo_indicativo')} / {current_prod.get('um', 'Kg')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    if current_prod.get('descrizione_commerciale'):
                        st.markdown(f"""
                        <div style="background:#FFFBEB; border-left:4px solid #F59E0B; padding:8px 12px; border-radius:6px; font-size:0.88rem; color:#451A03; margin-top:6px; margin-bottom:8px;">
                            <b>Descrizione Commerciale:</b><br>{current_prod['descrizione_commerciale']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Action buttons in single clean row
                    st.write("")
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.2, 1])
                    with btn_col1:
                        if st.session_state.chat_focused_sku == selected_sku:
                            if st.button("❌ Sgancia AI", use_container_width=True):
                                st.session_state.chat_focused_sku = None
                                st.toast("Focus rimosso! Passato al catalogo generale.")
                                st.rerun()
                        else:
                            if st.button("🎯 Aggancia AI", type="primary", use_container_width=True):
                                st.session_state.chat_focused_sku = selected_sku
                                st.toast(f"✅ Articolo {selected_sku} agganciato alla Chat AI!")
                                st.rerun()
                                
                    with btn_col2:
                        in_compare = selected_sku in st.session_state.compare_skus
                        if in_compare:
                            if st.button("⚖️ Rimuovi Confronto", use_container_width=True):
                                st.session_state.compare_skus.remove(selected_sku)
                                st.toast(f"Rimosso {selected_sku} dal confronto!")
                                st.rerun()
                        else:
                            if st.button("⚖️ Aggiungi a Confronto", use_container_width=True):
                                if len(st.session_state.compare_skus) >= 4:
                                    st.warning("Puoi confrontare al massimo 4 articoli contemporaneamente.")
                                else:
                                    st.session_state.compare_skus.append(selected_sku)
                                    st.toast(f"✅ Aggiunto {selected_sku} al confronto! (Totale: {len(st.session_state.compare_skus)})")
                                    st.rerun()
                                
                    with btn_col3:
                        scheda_resolved = resolve_file(current_prod.get('scheda_path'), current_prod.get('scheda_filename'), config.SCHEDE_DIR)
                        if scheda_resolved and os.path.exists(scheda_resolved):
                            with open(scheda_resolved, "rb") as f:
                                st.download_button(
                                    label="📥 Scheda PDF",
                                    data=f.read(),
                                    file_name=os.path.basename(scheda_resolved),
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        else:
                            st.button("📄 Nessun PDF", disabled=True, use_container_width=True)

                    # --- ADD TO QUOTE QUICK SECTION ---
                    st.divider()
                    st.markdown("##### 🛒 Aggiungi questo articolo al Preventivo:")
                    try:
                        raw_p = str(current_prod.get('prezzo_indicativo', '0')).replace(',', '.').strip()
                        default_p = float(raw_p) if raw_p else 0.0
                    except ValueError:
                        default_p = 0.0
                        
                    q_col_qty, q_col_prc, q_col_btn = st.columns([1, 1.2, 1.8])
                    with q_col_qty:
                        add_qty = st.number_input(
                            f"Q.tà ({current_prod.get('um', 'Kg')})",
                            min_value=0.1,
                            value=1.0,
                            step=1.0,
                            key=f"qty_sel_{selected_sku}"
                        )
                    with q_col_prc:
                        add_price = st.number_input(
                            "Prezzo (€)",
                            min_value=0.0,
                            value=default_p,
                            step=0.10,
                            format="%.2f",
                            key=f"prc_sel_{selected_sku}"
                        )
                    with q_col_btn:
                        st.write("")
                        st.write("")
                        if st.button("➕ Aggiungi al Preventivo", use_container_width=True, key=f"btn_add_{selected_sku}"):
                            # Check if already in items
                            existing = next((i for i in st.session_state.quote_items if i["cod_art"] == selected_sku), None)
                            if existing:
                                existing["quantita"] += add_qty
                                existing["prezzo_unitario"] = add_price
                            else:
                                st.session_state.quote_items.append({
                                    "cod_art": selected_sku,
                                    "descrizione_articolo": current_prod.get("descrizione_articolo", ""),
                                    "unita_imballi": current_prod.get("unita_imballi", ""),
                                    "um": current_prod.get("um", "Kg"),
                                    "quantita": add_qty,
                                    "prezzo_unitario": add_price
                                })
                            st.toast(f"✅ Aggiunto {selected_sku} al Preventivo! (Totale articoli: {len(st.session_state.quote_items)})")
                            st.rerun()

            # Scheda Tecnica Full-Width Section below product card
            scheda_text = current_prod.get('scheda_text', '').strip()
            if scheda_text:
                st.write("")
                with st.expander("Consulta il Testo Ufficiale della Scheda Tecnica (HACCP, Ingredienti, Allergeni)", expanded=False):
                    st.text_area("Testo Integrale Scheda Tecnica", value=scheda_text, height=220, disabled=True, label_visibility="collapsed")
            elif current_prod.get('scheda_path'):
                st.info("ℹ️ La scheda tecnica PDF è presente per il download ma non contiene testo scansionabile.")

# =========================================================================
# TAB 2: STUDIO CONSULENZA & CHAT AI
# =========================================================================
with tab_chat:
    focused_sku = st.session_state.get("chat_focused_sku")
    focused_prod = database.get_product_by_code(focused_sku) if focused_sku else None
    
    col_chat_head, col_chat_reset = st.columns([3, 1])
    with col_chat_head:
        if focused_prod:
            st.markdown(f"""
            <div class="focus-alert-active">
                <div style="font-weight:700; font-size:1.05rem;">🎯 Prodotto Attualmente Agganciato:</div>
                <div style="font-size:0.95rem; margin-top:2px;"><code>{focused_prod['cod_art']}</code> — <b>{focused_prod['descrizione_articolo']}</b></div>
                <div style="font-size:0.8rem; color:#3B82F6; margin-top:4px;">L'assistente utilizzerà i dati esatti della scheda tecnica ufficiale e cercherà abbinamenti specifici.</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="focus-alert-general">
                <div style="font-weight:700; font-size:1.05rem;">🌐 Modalità Generale Attiva: Interrogazione su Tutto il Catalogo</div>
                <div style="font-size:0.85rem; color:#166534; margin-top:2px;">Puoi fare qualsiasi domanda tecnica trasversale (es. <i>"Quali farine sono adatte a 40-60h di lievitazione?"</i>, <i>"Quali formaggi senza lattosio abbiamo?"</i>).</div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_chat_reset:
        if focused_prod:
            st.write("")
            if st.button("🔓 Sgancia Prodotto (Modalità Generale)", use_container_width=True):
                st.session_state.chat_focused_sku = None
                st.toast("Focus rimosso! Passato alla modalità Catalogo Generale.")
                st.rerun()
            
    # Quick Prompt suggestions
    st.markdown("##### ⚡ Domande Rapide con 1 Click:")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_prompt = None
    
    if focused_prod:
        with q_col1:
            if st.button("📋 Allergeni & HACCP", use_container_width=True):
                quick_prompt = f"Quali sono gli allergeni, gli ingredienti e le specifiche HACCP indicate nella scheda tecnica del prodotto {focused_prod['cod_art']} ({focused_prod['descrizione_articolo']})?"
        with q_col2:
            if st.button("❄️ Conservazione & Scongelamento", use_container_width=True):
                quick_prompt = f"Quali sono le modalità di conservazione, shelf-life e le procedure ideali di scongelamento per il prodotto {focused_prod['cod_art']}?"
        with q_col3:
            if st.button("🍕 3 Idee per Pizzeria Gourmet", use_container_width=True):
                quick_prompt = f"Suggerisci 3 abbinamenti o ricette creative per pizza gourmet o piatti del ristorante che valorizzino {focused_prod['descrizione_articolo']}, indicando il food cost stimato."
        with q_col4:
            if st.button("🔥 Tendenze & Consigli Chef", use_container_width=True):
                quick_prompt = f"Cerca online le migliori tendenze culinarie attuali su come i grandi chef utilizzano {focused_prod['descrizione_articolo']} e consigliami tecniche di cottura moderne."
    else:
        with q_col1:
            if st.button("🌾 Farine Lievitazione 40-60h", use_container_width=True):
                quick_prompt = "Quali farine a catalogo sono indicate per lievitazioni e maturazioni tra 40 e 60 ore? Indicami i codici SKU, indice di forza W, contenuto proteico e consigli di impasto."
        with q_col2:
            if st.button("🧀 Senza Lattosio & Veg", use_container_width=True):
                quick_prompt = "Quali formaggi e latticini a catalogo sono delattosati / senza lattosio o adatti a vegetariani? Cita codici SKU e tipologie."
        with q_col3:
            if st.button("🍕 Pelati e Pomodori Pizza", use_container_width=True):
                quick_prompt = "Quali varietà di pomodori pelati, polpe e San Marzano DOP abbiamo a catalogo ideali per pizza napoletana e romana?"
        with q_col4:
            if st.button("🥩 Tagli Carne per CBT", use_container_width=True):
                quick_prompt = "Quali tagli di carne bovina o suina a catalogo sono ideali per cotture a bassa temperatura (CBT) o frollature lunghe?"

    st.write("")

    # Direct Input Form
    with st.form(key="chat_direct_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns([5, 1])
        with col_in1:
            form_text = st.text_input(
                "Scrivi qui la tua domanda:",
                placeholder="Fai qualsiasi domanda tecnica sul catalogo o chiedi consigli allo Chef & Consulente...",
                label_visibility="collapsed"
            )
        with col_in2:
            form_submit = st.form_submit_button("Invia 🚀", type="primary", use_container_width=True)

    bottom_input = st.chat_input("Oppure scrivi qui in basso la tua domanda...")
    prompt_to_run = quick_prompt or (form_text if form_submit and form_text.strip() else None) or bottom_input

    # Display chat history
    if st.session_state.messages:
        st.markdown("##### 💬 Conversazione:")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🧑‍🍳" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    st.markdown("""
                    <div style="background:#F1F5F9; border-left:4px solid #3B82F6; padding:8px 12px; border-radius:6px; font-size:0.85rem; margin-top:8px;">
                        <b>🌐 Fonti e Approfondimenti Web Consultati:</b>
                    </div>
                    """, unsafe_allow_html=True)
                    for s in msg["sources"]:
                        if s.get("url"):
                            st.markdown(f"- 🔗 [{s['title']}]({s['url']})")

    if prompt_to_run:
        if not active_api_key:
            st.error("⚠️ Inserisci la tua Google Gemini API Key nella barra laterale sinistra per avviare la chat!")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_to_run})
            with st.chat_message("user", avatar="🧑‍🍳"):
                st.markdown(prompt_to_run)
                
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("L'assistente sta analizzando il catalogo e le schede tecniche..."):
                    response_data = ai_assistant.generate_ai_response(
                        messages=st.session_state.messages,
                        current_product=focused_prod,
                        api_key=active_api_key,
                        model_name=model_choice,
                        enable_web_search=enable_web_search
                    )
                    
                    st.markdown(response_data["text"])
                    if response_data.get("sources"):
                        st.markdown("""
                        <div style="background:#F1F5F9; border-left:4px solid #3B82F6; padding:8px 12px; border-radius:6px; font-size:0.85rem; margin-top:8px;">
                            <b>🌐 Fonti e Approfondimenti Web Consultati:</b>
                        </div>
                        """, unsafe_allow_html=True)
                        for s in response_data["sources"]:
                            if s.get("url"):
                                st.markdown(f"- 🔗 [{s['title']}]({s['url']})")
                                
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_data["text"],
                        "sources": response_data.get("sources", [])
                    })

    if st.session_state.messages:
        st.write("")
        if st.button("🗑️ Pulisci cronologia conversazione"):
            st.session_state.messages = []
            st.rerun()

# =========================================================================
# TAB 3: GENERATORE PREVENTIVI & ORDINI RAPIDI
# =========================================================================
with tab_quote:
    st.markdown("### 📑 Generatore di Preventivi PDF & Ordini Rapidi")
    st.caption("Compila offerte personalizzate per i tuoi clienti, calcola i totali ed esporta il documento PDF ufficiale o condividi su WhatsApp.")
    
    if not st.session_state.quote_items:
        st.info("🛒 **Il preventivo è attualmente vuoto.**\n\nNaviga nel catalogo (Tab 1), seleziona i prodotti desiderati e clicca su **`➕ Aggiungi al Preventivo`** per compilare l'offerta.")
    else:
        col_q_cust, col_q_items = st.columns([1.1, 1.9], gap="large")
        
        # --- LEFT: CUSTOMER & OFFER DETAILS ---
        with col_q_cust:
            with st.container(border=True):
                st.markdown("##### 👤 Dati Cliente & Destinatario")
                cust_name = st.text_input(
                    "Ragione Sociale / Nome Locale *", 
                    value=st.session_state.quote_customer.get("name", ""),
                    placeholder="es. Ristorante Pizzeria Belvedere S.r.l."
                )
                cust_contact = st.text_input(
                    "Referente / Chef / P.IVA", 
                    value=st.session_state.quote_customer.get("contact", ""),
                    placeholder="es. Chef Marco Rossi"
                )
                cust_address = st.text_input(
                    "Città / Indirizzo Consegna", 
                    value=st.session_state.quote_customer.get("address", ""),
                    placeholder="es. Via Garibaldi 12, Verona (VR)"
                )
                cust_phone = st.text_input(
                    "Telefono / Email Cliente (per WhatsApp)", 
                    value=st.session_state.quote_customer.get("phone_email", ""),
                    placeholder="es. +39 340 1234567"
                )
                
                st.markdown("##### 📋 Dettagli Preventivo")
                doc_num = st.text_input(
                    "Numero Preventivo", 
                    value=st.session_state.quote_customer.get("doc_number", f"PREV-{datetime.now().strftime('%Y%m%d')}-01")
                )
                agent_name = st.text_input(
                    "Nome Agente / Commerciale", 
                    value=st.session_state.quote_customer.get("agent_name", "Forza Vendita IFT")
                )
                validity = st.selectbox(
                    "Validità Offerta", 
                    options=["15 giorni", "30 giorni", "60 giorni", "Fino a esaurimento scorte"], 
                    index=1
                )
                notes = st.text_area(
                    "Note e Condizioni di Consegna", 
                    value=st.session_state.quote_customer.get("notes", "Resa franco destino. Pagamento come da accordi commerciali. Merce soggetta a disponibilità. Fatturazione al peso effettivo alla consegna."),
                    height=90
                )
                
                # Save state
                st.session_state.quote_customer = {
                    "name": cust_name,
                    "contact": cust_contact,
                    "address": cust_address,
                    "phone_email": cust_phone,
                    "doc_number": doc_num,
                    "agent_name": agent_name,
                    "validity": validity,
                    "notes": notes
                }

        # --- RIGHT: ITEMS LIST & ACTIONS ---
        with col_q_items:
            st.markdown(f"##### 🛒 Articoli in Offerta ({len(st.session_state.quote_items)} referenze):")
            
            items_to_remove = []
            
            for idx, it in enumerate(st.session_state.quote_items):
                with st.container(border=True):
                    r_col1, r_col2, r_col3, r_col4 = st.columns([4.2, 1.4, 1.8, 0.6])
                    
                    with r_col1:
                        st.markdown(f"<b>`{it['cod_art']}`</b> — {it['descrizione_articolo']}", unsafe_allow_html=True)
                            
                    with r_col2:
                        new_qty = st.number_input(
                            f"Q.tà ({it.get('um', 'Kg')})",
                            min_value=0.1,
                            value=float(it.get("quantita", 1.0)),
                            step=1.0,
                            key=f"q_edit_qty_{idx}"
                        )
                        it["quantita"] = new_qty
                        
                    with r_col3:
                        new_prc = st.number_input(
                            f"Prezzo (€/{it.get('um', 'Kg')})",
                            min_value=0.0,
                            value=float(it.get("prezzo_unitario", 0.0)),
                            step=0.10,
                            format="%.2f",
                            key=f"q_edit_prc_{idx}"
                        )
                        it["prezzo_unitario"] = new_prc
                        
                    with r_col4:
                        st.write("")
                        if st.button("🗑️", key=f"del_item_{idx}", help="Rimuovi articolo"):
                            items_to_remove.append(idx)

            # Process removals
            if items_to_remove:
                for rem_idx in sorted(items_to_remove, reverse=True):
                    st.session_state.quote_items.pop(rem_idx)
                st.rerun()

            st.write("")

            # --- EXPORT & SHARE ACTIONS ---
            st.markdown("##### 🚀 Azioni di Esportazione & Condivisione:")
            
            quote_payload = {
                "doc_number": doc_num,
                "doc_date": datetime.now().strftime("%d/%m/%Y"),
                "validity": validity,
                "agent_name": agent_name,
                "customer": {
                    "name": cust_name if cust_name else "Gentile Cliente",
                    "contact": cust_contact,
                    "address": cust_address,
                    "phone_email": cust_phone
                },
                "items": st.session_state.quote_items,
                "notes": notes
            }
            
            # Generate Default Message Text from all current items
            default_wa_text = quote_generator.generate_whatsapp_message(quote_payload)
            
            # Auto-sync WhatsApp text whenever quote items or customer data change
            current_quote_sig = f"{len(st.session_state.quote_items)}|" + "|".join([
                f"{i.get('cod_art')}:{i.get('quantita')}:{i.get('prezzo_unitario')}" for i in st.session_state.quote_items
            ]) + f"|{cust_name}|{agent_name}|{doc_num}"
            
            if st.session_state.get("last_wa_quote_sig") != current_quote_sig:
                st.session_state.last_wa_quote_sig = current_quote_sig
                st.session_state["wa_message_editor"] = default_wa_text
            
            # Editable WhatsApp Section
            st.write("")
            with st.expander("💬 Personalizza / Copia Messaggio WhatsApp", expanded=True):
                wa_head_col, wa_regen_col = st.columns([3, 1.2])
                with wa_head_col:
                    st.caption("Puoi modificare liberamente il testo qui sotto (es. aggiungere saluti o note particolari) prima di inviarlo o copiarlo.")
                with wa_regen_col:
                    if st.button("🔄 Rigenera Testo", help="Ricarica il testo automatico con tutti gli articoli attuali", use_container_width=True):
                        st.session_state["wa_message_editor"] = default_wa_text
                        st.rerun()
                        
                edited_wa_text = st.text_area(
                    "Testo Messaggio WhatsApp (Modificabile & Copiabile)", 
                    value=st.session_state.get("wa_message_editor", default_wa_text),
                    height=220,
                    key="wa_message_editor",
                    help="Modifica il testo come preferisci: il pulsante 'Invia su WhatsApp' userà la tua versione modificata."
                )
                
                # 1-Click Copy Box
                st.markdown("**📋 Testo pronto per copia rapida:**")
                st.code(edited_wa_text, language="markdown")

            # Build URL using the edited text
            clean_phone = "".join(filter(str.isdigit, cust_phone))
            encoded_text = urllib.parse.quote(edited_wa_text)
            wa_url = f"https://wa.me/{clean_phone}?text={encoded_text}" if clean_phone else f"https://wa.me/?text={encoded_text}"

            btn_pdf_col, btn_wa_col, btn_clr_col = st.columns([1.5, 1.5, 1])
            
            with btn_pdf_col:
                logo_file = "ift_logo.png" if os.path.exists("ift_logo.png") else None
                try:
                    pdf_bytes = quote_generator.generate_quote_pdf(quote_payload, logo_path=logo_file)
                    st.download_button(
                        label="📥 Scarica Proposta PDF",
                        data=pdf_bytes,
                        file_name=f"Offerta_{doc_num}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Errore generazione PDF: {e}")
                    
            with btn_wa_col:
                st.link_button("📲 Invia su WhatsApp", url=wa_url, use_container_width=True)
                
            with btn_clr_col:
                if st.button("🗑️ Svuota Tutto", use_container_width=True):
                    st.session_state.quote_items = []
                    if "wa_message_editor" in st.session_state:
                        del st.session_state["wa_message_editor"]
                    if "last_wa_quote_sig" in st.session_state:
                        del st.session_state["last_wa_quote_sig"]
                    st.toast("Preventivo svuotato!")
                    st.rerun()

# =========================================================================
# TAB 4: CALCOLATORE DI FOOD COST & INGEGNERIA DEL MENU
# =========================================================================
with tab_foodcost:
    st.markdown("### 📊 Calcolatore di Food Cost & Ingegneria del Menu")
    st.caption("Componi ricette con i prodotti reali del catalogo IFT, analizza il costo per porzione, simula i margini di profitto lordo e travasa gli ingredienti nel preventivo.")
    
    # -------------------------------------------------------------
    # 1. TEMPLATE SELECTION BAR
    # -------------------------------------------------------------
    with st.container(border=True):
        tpl_col1, tpl_col2 = st.columns([3, 1.2])
        with tpl_col1:
            template_options = ["-- Seleziona o mantieni ricetta corrente --"] + list(food_cost_calculator.RECIPE_TEMPLATES.keys())
            chosen_tpl = st.selectbox(
                "⚡ Carica una Ricetta Iconica Preimpostata:",
                options=template_options,
                index=0
            )
        with tpl_col2:
            st.write("")
            st.write("")
            if chosen_tpl != "-- Seleziona o mantieni ricetta corrente --":
                if st.button("📥 Carica Ricetta", use_container_width=True, type="primary"):
                    tpl_data = food_cost_calculator.RECIPE_TEMPLATES[chosen_tpl]
                    st.session_state.recipe_name = tpl_data["name"]
                    st.session_state.recipe_category = tpl_data["category"]
                    st.session_state.recipe_portions = tpl_data["portions"]
                    st.session_state.recipe_target_pct = tpl_data["target_pct"]
                    st.session_state.recipe_actual_price = tpl_data["actual_price"]
                    st.session_state.recipe_ingredients = [dict(x) for x in tpl_data["ingredients"]]
                    st.toast(f"Caricata ricetta: {tpl_data['name']}!")
                    st.rerun()

    # -------------------------------------------------------------
    # 2. RECIPE CONFIGURATION & FINANCIAL PARAMETERS
    # -------------------------------------------------------------
    with st.container(border=True):
        st.markdown("##### 🍽️ Dettagli Piatto & Parametri Economici")
        c_r1, c_r2, c_r3, c_r4, c_r5 = st.columns([3.2, 2.0, 1.2, 1.8, 1.8])
        
        with c_r1:
            st.session_state.recipe_name = st.text_input(
                "Nome Ricetta / Piatto", 
                value=st.session_state.recipe_name
            )
        with c_r2:
            cat_list = ["Pizzeria Gourmet", "Pizzeria Classica", "Primi Piatti", "Secondi Piatti", "Antipasti & Taglieri", "Bistrot & Panini", "Dessert"]
            current_cat_idx = cat_list.index(st.session_state.recipe_category) if st.session_state.recipe_category in cat_list else 0
            st.session_state.recipe_category = st.selectbox(
                "Categoria Portata", 
                options=cat_list,
                index=current_cat_idx
            )
        with c_r3:
            st.session_state.recipe_portions = st.number_input(
                "Resa (Porzioni)", 
                min_value=1, 
                value=int(st.session_state.recipe_portions), 
                step=1
            )
        with c_r4:
            st.session_state.recipe_target_pct = st.number_input(
                "Target Food Cost %", 
                min_value=10.0, 
                max_value=60.0, 
                value=float(st.session_state.recipe_target_pct), 
                step=1.0, 
                format="%.1f",
                help="Lo standard ideale nella ristorazione/pizzeria è tra il 25% e il 30%."
            )
        with c_r5:
            st.session_state.recipe_actual_price = st.number_input(
                "Prezzo Menu (€ IVA 10% inc.)", 
                min_value=0.5, 
                value=float(st.session_state.recipe_actual_price), 
                step=0.50, 
                format="%.2f",
                help="Prezzo di vendita al pubblico sul menu del ristorante o pizzeria."
            )

    # Calculate Recipe Financial Summary
    summary = food_cost_calculator.calculate_recipe_summary(
        ingredients=st.session_state.recipe_ingredients,
        target_food_cost_pct=st.session_state.recipe_target_pct,
        actual_selling_price_gross=st.session_state.recipe_actual_price,
        vat_rate=10.0,
        portions=st.session_state.recipe_portions
    )

    # -------------------------------------------------------------
    # 3. KPI METRICS DASHBOARD
    # -------------------------------------------------------------
    st.write("")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    
    with m_col1:
        st.markdown(f"""
        <div class="fc-metric-card" style="border-left: 5px solid #0F172A;">
            <div style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase;">Food Cost / Porzione</div>
            <div class="fc-metric-val" style="color:#0F172A;">€ {summary['food_cost_per_portion']:.2f}</div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">Totale Ricetta: <b>€ {summary['total_recipe_cost']:.2f}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col2:
        st.markdown(f"""
        <div class="fc-metric-card" style="border-left: 5px solid #2563EB;">
            <div style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase;">Prezzo Menu Consigliato</div>
            <div class="fc-metric-val" style="color:#2563EB;">€ {summary['recommended_selling_price_gross']:.2f}</div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">Target <b>{summary['target_food_cost_pct']:g}%</b> (IVA 10% inc.)</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col3:
        st.markdown(f"""
        <div class="fc-metric-card" style="border-left: 5px solid #16A34A;">
            <div style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase;">Margine Lordo / Piatto</div>
            <div class="fc-metric-val" style="color:#16A34A;">€ {summary['gross_margin_per_portion']:.2f}</div>
            <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">Netto IVA: <b>€ {summary['actual_selling_price_net']:.2f}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
    with m_col4:
        st.markdown(f"""
        <div class="fc-metric-card" style="border-left: 5px solid {summary['status_color']};">
            <div style="font-size:0.8rem; font-weight:700; color:#64748B; text-transform:uppercase;">Food Cost % Reale</div>
            <div class="fc-metric-val" style="color:{summary['status_color']};">{summary['actual_food_cost_pct']:.1f}%</div>
            <div style="font-size:0.75rem; font-weight:600; color:{summary['status_color']}; margin-top:2px;">{summary['status_label']}</div>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 4. INGREDIENTS LIST & LIVE BREAKDOWN
    # -------------------------------------------------------------
    st.write("")
    st.markdown(f"##### 📋 Distinta Base Ingredienti ({len(st.session_state.recipe_ingredients)} componenti):")
    
    ingredients_to_delete = []
    
    for idx, ing in enumerate(st.session_state.recipe_ingredients):
        with st.container(border=True):
            r_col_ing, r_col_qty, r_col_um, r_col_prc, r_col_tot, r_col_del = st.columns([3.6, 1.2, 1.1, 1.4, 1.8, 0.6])
            
            with r_col_ing:
                sku_txt = f"`{ing['cod_art']}` " if ing.get('cod_art') else ""
                st.markdown(f"<b>{sku_txt}{ing['name']}</b>", unsafe_allow_html=True)
                
            with r_col_qty:
                new_q = st.number_input(
                    "Dosaggio",
                    min_value=0.01,
                    value=float(ing.get("quantity", 100)),
                    step=10.0 if str(ing.get("unit", "g")).lower() in ["g", "ml"] else 1.0,
                    key=f"ing_q_{idx}"
                )
                ing["quantity"] = new_q
                
            with r_col_um:
                units_list = ["g", "Kg", "ml", "L", "Pz", "etto", "fetta"]
                current_u_idx = units_list.index(ing.get("unit", "g")) if ing.get("unit", "g") in units_list else 0
                new_u = st.selectbox(
                    "Unità",
                    options=units_list,
                    index=current_u_idx,
                    key=f"ing_u_{idx}"
                )
                ing["unit"] = new_u
                
            with r_col_prc:
                price_um = ing.get("price_um", "Kg")
                new_p = st.number_input(
                    f"Prezzo (€/{price_um})",
                    min_value=0.0,
                    value=float(ing.get("unit_price", 0.0)),
                    step=0.50,
                    format="%.2f",
                    key=f"ing_p_{idx}"
                )
                ing["unit_price"] = new_p
                
            # Calculate row cost
            row_cost = food_cost_calculator.calculate_ingredient_cost(new_q, new_u, new_p, price_um)
            row_pct = (row_cost / summary["total_recipe_cost"] * 100.0) if summary["total_recipe_cost"] > 0 else 0.0
            
            with r_col_tot:
                st.write("")
                st.markdown(f"<div style='font-size:1.05rem; font-weight:800; color:#0F172A; text-align:right;'>€ {row_cost:.2f} <span style='font-size:0.75rem; font-weight:600; color:#64748B;'>({row_pct:.1f}%)</span></div>", unsafe_allow_html=True)
                st.progress(min(1.0, max(0.0, row_pct / 100.0)))
                
            with r_col_del:
                st.write("")
                if st.button("🗑️", key=f"del_ing_{idx}", help="Rimuovi ingrediente"):
                    ingredients_to_delete.append(idx)

    if ingredients_to_delete:
        for del_i in sorted(ingredients_to_delete, reverse=True):
            st.session_state.recipe_ingredients.pop(del_i)
        st.rerun()

    # -------------------------------------------------------------
    # 5. ADD INGREDIENT FROM IFT CATALOG
    # -------------------------------------------------------------
    st.write("")
    with st.expander("➕ Aggiungi un Nuovo Ingrediente dal Catalogo IFT", expanded=False):
        st.markdown("Seleziona una delle **2.003 referenze IFT a listino** con il suo *Prezzo Soglia* ufficiale precaricato:")
        
        all_catalog_prods = database.get_all_products_basic()
        prod_options = ["-- Seleziona Prodotto a Catalogo --"] + [
            f"{p['cod_art']} — {p['descrizione_articolo']} (€ {p['prezzo_soglia']:.2f} / {p['um']})"
            for p in all_catalog_prods
        ]
        
        add_col_prod, add_col_qty, add_col_um, add_col_btn = st.columns([3.5, 1.2, 1.1, 1.5])
        
        with add_col_prod:
            chosen_cat_prod = st.selectbox("Cerca o Seleziona Prodotto IFT", options=prod_options, index=0)
            
        with add_col_qty:
            add_ing_qty = st.number_input("Dosaggio", min_value=0.01, value=100.0, step=10.0, key="add_cat_qty")
            
        with add_col_um:
            add_ing_um = st.selectbox("Unità Misura", options=["g", "Kg", "ml", "L", "Pz", "etto", "fetta"], index=0, key="add_cat_um")
            
        with add_col_btn:
            st.write("")
            st.write("")
            if st.button("➕ Inserisci in Ricetta", use_container_width=True, key="btn_add_to_recipe"):
                if chosen_cat_prod != "-- Seleziona Prodotto a Catalogo --":
                    sku_part = chosen_cat_prod.split(" — ")[0].strip()
                    matched_prod = database.get_product_by_code(sku_part)
                    if matched_prod:
                        st.session_state.recipe_ingredients.append({
                            "cod_art": matched_prod["cod_art"],
                            "name": matched_prod["descrizione_articolo"],
                            "quantity": add_ing_qty,
                            "unit": add_ing_um,
                            "unit_price": float(matched_prod.get("prezzo_soglia", 0.0) or 0.0),
                            "price_um": matched_prod.get("um", "Kg")
                        })
                        st.toast(f"✅ Inserito {matched_prod['cod_art']} nella ricetta!")
                        st.rerun()
                else:
                    st.warning("Seleziona prima un prodotto dal menu a tendina.")

    # -------------------------------------------------------------
    # 6. MONTHLY PROFIT SIMULATOR
    # -------------------------------------------------------------
    st.write("")
    with st.container(border=True):
        st.markdown("##### 📈 Simulatore di Redditività & Profitto Mensile")
        st.caption("Stima il volume di vendite per questo piatto e visualizza il margine lordo generato per il locale:")
        
        sim_col_slider, sim_col_res1, sim_col_res2 = st.columns([2.5, 1.5, 1.5])
        
        with sim_col_slider:
            daily_portions = st.slider(
                "Porzioni / Coperti venduti al giorno:",
                min_value=5,
                max_value=200,
                value=30,
                step=5
            )
            days_open = st.number_input("Giorni di apertura al mese:", min_value=1, max_value=31, value=26, step=1)
            
        monthly_portions = daily_portions * days_open
        monthly_revenue = monthly_portions * summary["actual_selling_price_net"]
        monthly_profit = monthly_portions * summary["gross_margin_per_portion"]
        
        with sim_col_res1:
            st.markdown(f"""
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:12px; border-radius:10px; text-align:center;">
                <div style="font-size:0.78rem; color:#64748B; font-weight:700;">INCASSO MENSILE NETTO</div>
                <div style="font-size:1.35rem; font-weight:800; color:#0F172A; margin-top:4px;">€ {monthly_revenue:,.2f}</div>
                <div style="font-size:0.75rem; color:#64748B; margin-top:2px;">su {monthly_portions} piatti/mese</div>
            </div>
            """, unsafe_allow_html=True)
            
        with sim_col_res2:
            st.markdown(f"""
            <div style="background:#F0FDF4; border:1px solid #BBF7D0; padding:12px; border-radius:10px; text-align:center;">
                <div style="font-size:0.78rem; color:#166534; font-weight:700;">PROFITTO LORDO MENSILE</div>
                <div style="font-size:1.35rem; font-weight:800; color:#15803D; margin-top:4px;">€ {monthly_profit:,.2f}</div>
                <div style="font-size:0.75rem; color:#166534; margin-top:2px;">Margine vivo d'esercizio</div>
            </div>
            """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # 7. STRATEGIC ACTIONS (QUOTE INTEGRATION & AI OPTIMIZER)
    # -------------------------------------------------------------
    st.write("")
    st.markdown("##### 🚀 Azioni Strategiche:")
    
    act_col1, act_col2, act_col3 = st.columns([1.8, 1.8, 1.0])
    
    with act_col1:
        if st.button("🛒 Travasa Ingredienti nel Preventivo", type="primary", use_container_width=True):
            added_count = 0
            for item in st.session_state.recipe_ingredients:
                sku = item.get("cod_art")
                if sku and sku != "EXTRA":
                    # Retrieve full product details from DB if available
                    db_prod = database.get_product_by_code(sku)
                    desc = db_prod.get("descrizione_articolo", item.get("name", "")) if db_prod else item.get("name", "")
                    imballi = db_prod.get("unita_imballi", "") if db_prod else ""
                    um_val = item.get("price_um") or (db_prod.get("um") if db_prod else "Kg")
                    unit_p = float(item.get("unit_price", 0.0))
                    if unit_p <= 0 and db_prod and db_prod.get("prezzo_indicativo"):
                        try:
                            unit_p = float(str(db_prod["prezzo_indicativo"]).replace("€", "").replace(",", ".").strip())
                        except (ValueError, TypeError):
                            unit_p = 0.0
                    
                    # Add/update in quote session state with standard unit of measure and price per Kg/UM
                    existing = next((q for q in st.session_state.quote_items if q["cod_art"] == sku), None)
                    if existing:
                        existing["prezzo_unitario"] = unit_p
                        existing["um"] = um_val
                    else:
                        st.session_state.quote_items.append({
                            "cod_art": sku,
                            "descrizione_articolo": desc,
                            "unita_imballi": imballi,
                            "um": um_val,
                            "quantita": 1.0,
                            "prezzo_unitario": unit_p
                        })
                    added_count += 1
                    
            if added_count > 0:
                st.toast(f"✅ Travasati con successo {added_count} articoli nel Preventivo con prezzo al Kg/U.M.!")
                st.rerun()
            else:
                st.warning("Nessun articolo con codice SKU valido da travasare.")
                
    with act_col2:
        if st.button("🤖 Chiedi all'AI di Ottimizzare il Food Cost", use_container_width=True):
            # Formulate structured prompt for Gemini
            recipe_items_desc = ", ".join([f"{i['name']} ({i['quantity']} {i['unit']})" for i in st.session_state.recipe_ingredients])
            prompt_ai = (
                f"Analizza il Food Cost per la ricetta '{st.session_state.recipe_name}' ({st.session_state.recipe_category}):\n"
                f"- Costo ingredienti per porzione: € {summary['food_cost_per_portion']:.2f}\n"
                f"- Prezzo di vendita a menu: € {summary['actual_selling_price_gross']:.2f} (Food Cost: {summary['actual_food_cost_pct']:.1f}%)\n"
                f"- Ingredienti attuali: {recipe_items_desc}\n\n"
                f"Suggeriscimi strategie gastronomiche e alternative di prodotti dal catalogo Italian Food Trading S.r.l. per ottimizzare il Food Cost, ridurre gli sprechi e aumentare la marginalità lorda per il ristoratore."
            )
            st.session_state.messages.append({"role": "user", "content": prompt_ai})
            st.toast("Richiesta inviata all'Assistente AI! Apri il Tab 2 per consultare i consigli dello chef AI.")
                
    with act_col3:
        if st.button("🗑️ Svuota Ricetta", use_container_width=True):
            st.session_state.recipe_ingredients = []
            st.toast("Ricetta svuotata!")
            st.rerun()

# =========================================================================
# TAB 5: CONFRONTO PRODOTTI SIDE-BY-SIDE & SCHEDE TECNICHE
# =========================================================================
with tab_compare:
    st.markdown("### ⚖️ Confronto Prodotti Side-by-Side con Schede Tecniche")
    st.caption("Confronta da 2 a 4 referenze del catalogo IFT affiancate, consulta le schede tecniche ufficiali, analizza allergeni e genera perizie comparative con l'Intelligenza Artificiale.")
    
    # -------------------------------------------------------------
    # 1. PRESET COMPARISON SHORTCUTS & CONTROLS
    # -------------------------------------------------------------
    with st.container(border=True):
        st.markdown("##### ⚡ Confronti Rapidi Preimpostati:")
        pr_col1, pr_col2, pr_col3, pr_col4, pr_col5 = st.columns(5)
        
        with pr_col1:
            if st.button("🌾 Farine Lievitazione (W410 / W350 / W250)", use_container_width=True):
                st.session_state.compare_skus = ["A110419QU", "A110413QU", "A110414QU"]
                st.session_state.compare_ai_analysis = None
                st.rerun()
        with pr_col2:
            if st.button("🍖 Prosciutti Cotti (Orazio vs Alta Qualità)", use_container_width=True):
                # Search for 2 prosciutti cotti
                st.session_state.compare_skus = ["A050922", "A050901"]
                st.session_state.compare_ai_analysis = None
                st.rerun()
        with pr_col3:
            if st.button("🧀 Mozzarella vs Burrata Pugliese", use_container_width=True):
                st.session_state.compare_skus = ["A060101", "A060401"]
                st.session_state.compare_ai_analysis = None
                st.rerun()
        with pr_col4:
            if st.button("🥩 Carni Bovine Grass Fed vs Nazionali", use_container_width=True):
                st.session_state.compare_skus = ["A001012", "A001001"]
                st.session_state.compare_ai_analysis = None
                st.rerun()
        with pr_col5:
            if st.button("🗑️ Svuota Tutto", use_container_width=True):
                st.session_state.compare_skus = []
                st.session_state.compare_ai_analysis = None
                st.toast("Confronto svuotato!")
                st.rerun()

    # -------------------------------------------------------------
    # 2. PRODUCT SLOTS SELECTION
    # -------------------------------------------------------------
    all_basic_items = database.get_all_products_basic()
    item_lookup_options = ["-- Seleziona Articolo a Catalogo --"] + [
        f"{p['cod_art']} — {p['descrizione_articolo']} (€ {p['prezzo_soglia']:.2f} / {p['um']})"
        for p in all_basic_items
    ]
    
    # Clean up compare SKUs
    valid_compare_skus = [sku for sku in st.session_state.compare_skus if database.get_product_by_code(sku)]
    if len(valid_compare_skus) != len(st.session_state.compare_skus):
        st.session_state.compare_skus = valid_compare_skus

    # Slot selector form
    with st.expander("🛠️ Gestisci / Cambia Articoli nei Singoli Slot di Confronto", expanded=(len(st.session_state.compare_skus) == 0)):
        st.caption("Seleziona da 2 a 4 prodotti da confrontare contemporaneamente:")
        
        # Determine number of slots to show
        num_slots = max(2, min(4, len(st.session_state.compare_skus) + 1))
        slot_cols = st.columns(num_slots)
        
        updated_skus = []
        for s_idx in range(num_slots):
            with slot_cols[s_idx]:
                current_sku = st.session_state.compare_skus[s_idx] if s_idx < len(st.session_state.compare_skus) else None
                default_option_idx = 0
                if current_sku:
                    for opt_i, opt_text in enumerate(item_lookup_options):
                        if opt_text.startswith(f"{current_sku} —"):
                            default_option_idx = opt_i
                            break
                            
                chosen_opt = st.selectbox(
                    f"Slot {s_idx + 1}:",
                    options=item_lookup_options,
                    index=default_option_idx,
                    key=f"slot_sel_{s_idx}"
                )
                
                if chosen_opt != "-- Seleziona Articolo a Catalogo --":
                    extracted_sku = chosen_opt.split(" — ")[0].strip()
                    if extracted_sku not in updated_skus:
                        updated_skus.append(extracted_sku)
                        
        if updated_skus != st.session_state.compare_skus:
            if st.button("✅ Applica Modifiche Selezione", type="primary"):
                st.session_state.compare_skus = updated_skus
                st.session_state.compare_ai_analysis = None
                st.rerun()

    # -------------------------------------------------------------
    # 3. SIDE-BY-SIDE COMPARISON CARDS
    # -------------------------------------------------------------
    compare_products = [database.get_product_by_code(sku) for sku in st.session_state.compare_skus if database.get_product_by_code(sku)]
    
    if not compare_products:
        st.info("💡 **Nessun prodotto selezionato per il confronto.**\n\nPuoi cliccare su uno dei pulsanti di **Confronto Rapido** in alto, selezionare i prodotti dagli slot, oppure cliccare su **`⚖️ Aggiungi a Confronto`** direttamente dalle schede prodotto nel Tab 1.")
    else:
        st.write("")
        st.markdown(f"#### 📊 Confronto Diretto ({len(compare_products)} referenze affiancate):")
        
        # Calculate lowest price
        prices_list = []
        for p in compare_products:
            raw_p = str(p.get('prezzo_indicativo', '0')).replace('€', '').replace(',', '.').strip()
            try:
                p_val = float(raw_p)
                if p_val > 0:
                    prices_list.append(p_val)
            except (ValueError, TypeError):
                pass
        min_price = min(prices_list) if prices_list else 0.0

        grid_cols = st.columns(len(compare_products), gap="medium")
        
        for c_idx, prod in enumerate(compare_products):
            with grid_cols[c_idx]:
                with st.container(border=True):
                    # Photo
                    photo_resolved = resolve_file(prod.get('foto_path'), prod.get('foto_filename'), config.FOTO_DIR)
                    if photo_resolved and os.path.exists(photo_resolved):
                        st.image(photo_resolved, use_container_width=True)
                    else:
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #1E293B, #0F172A); height: 180px; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: #64748B; font-size: 0.85rem; text-align: center; padding: 10px;">
                            <div>📸 Foto HD non presente</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("")
                    # SKU & Title
                    st.markdown(f"<span class='sku-badge'>{prod['cod_art']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div style='font-size:1.05rem; font-weight:800; color:#0F172A; line-height:1.2; min-height:48px;'>{prod['descrizione_articolo']}</div>", unsafe_allow_html=True)
                    
                    # Price Box
                    try:
                        raw_p = str(prod.get('prezzo_indicativo', '0')).replace('€', '').replace(',', '.').strip()
                        p_val = float(raw_p)
                    except (ValueError, TypeError):
                        p_val = 0.0
                        
                    is_best_price = (p_val > 0 and abs(p_val - min_price) < 0.001 and len(prices_list) > 1)
                    best_badge = "<span style='background:#DCFCE7; color:#15803D; font-size:0.75rem; font-weight:700; padding:2px 6px; border-radius:4px; margin-left:6px;'>⭐ Miglior Prezzo</span>" if is_best_price else ""
                    
                    st.markdown(f"""
                    <div style="background:#F0FDF4; border:1px solid #BBF7D0; padding:10px 12px; border-radius:8px; margin-top:8px; margin-bottom:12px;">
                        <div style="font-size:0.75rem; color:#166534; font-weight:700;">PREZZO SOGLIA: {best_badge}</div>
                        <div style="font-size:1.3rem; font-weight:800; color:#15803D;">€ {p_val:.2f} <span style="font-size:0.85rem; font-weight:600; color:#475569;">/ {prod.get('um', 'Kg')}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Logistic Badges
                    env = prod.get('ambiente_cons', '')
                    badge_cls = "badge-asciutto"
                    if "SURG" in env.upper() or "CONG" in env.upper():
                        badge_cls = "badge-congelato"
                    elif "REFR" in env.upper() or "FRES" in env.upper():
                        badge_cls = "badge-refrigerato"
                        
                    st.markdown(f"""
                    <div style="font-size:0.82rem; color:#334155; line-height:1.6; margin-bottom:12px;">
                        <div>🌡️ <b>Conservazione:</b> <span class="badge-pill {badge_cls}">{env if env else 'Non specificato'}</span></div>
                        <div>⏱️ <b>Shelf-life:</b> {prod.get('shelf_life_it', 'N/D')} ({prod.get('tempo_cons_gg', 'N/D')} gg consegna)</div>
                        <div>📦 <b>Formato/Imballo:</b> {prod.get('unita_imballi', 'N/D')}</div>
                        <div>🏷️ <b>Gruppo:</b> {prod.get('gruppo_art', 'N/D')}</div>
                        <div>🚚 <b>Minimo Ordine:</b> {prod.get('minimo_ordine', 'N/D')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Technical Sheet Section
                    st.markdown("---")
                    st.markdown("<b>📄 Scheda Tecnica & HACCP:</b>", unsafe_allow_html=True)
                    
                    scheda_res = resolve_file(prod.get('scheda_path'), prod.get('scheda_filename'), config.SCHEDE_DIR)
                    if scheda_res and os.path.exists(scheda_res):
                        with open(scheda_res, "rb") as f_pdf:
                            st.download_button(
                                label=f"📥 Scarica Scheda PDF",
                                data=f_pdf.read(),
                                file_name=os.path.basename(scheda_res),
                                mime="application/pdf",
                                use_container_width=True,
                                key=f"dl_comp_pdf_{prod['cod_art']}"
                            )
                    else:
                        st.button("📄 Nessun PDF allegato", disabled=True, use_container_width=True, key=f"no_pdf_{prod['cod_art']}")
                        
                    scheda_t = prod.get('scheda_text', '').strip()
                    if scheda_t:
                        with st.expander("👁️ Testo Integrale Scheda (HACCP & Allergeni)", expanded=False):
                            st.text_area(
                                "Testo Scheda",
                                value=scheda_t,
                                height=200,
                                disabled=True,
                                key=f"txt_comp_{prod['cod_art']}",
                                label_visibility="collapsed"
                            )
                    else:
                        st.caption("ℹ️ Nessun testo OCR estratto per questo articolo.")
                        
                    # Quick Quote & Focus Actions
                    st.write("")
                    act_c1, act_c2 = st.columns(2)
                    with act_c1:
                        if st.button("🛒 A Preventivo", use_container_width=True, key=f"btn_cp_add_{prod['cod_art']}"):
                            existing = next((q for q in st.session_state.quote_items if q["cod_art"] == prod["cod_art"]), None)
                            if existing:
                                existing["quantita"] += 1.0
                            else:
                                st.session_state.quote_items.append({
                                    "cod_art": prod["cod_art"],
                                    "descrizione_articolo": prod.get("descrizione_articolo", ""),
                                    "unita_imballi": prod.get("unita_imballi", ""),
                                    "um": prod.get("um", "Kg"),
                                    "quantita": 1.0,
                                    "prezzo_unitario": p_val
                                })
                            st.toast(f"✅ Aggiunto {prod['cod_art']} al Preventivo!")
                            st.rerun()
                            
                    with act_c2:
                        if st.button("🎯 Focus AI", use_container_width=True, key=f"btn_cp_focus_{prod['cod_art']}"):
                            st.session_state.chat_focused_sku = prod["cod_art"]
                            st.toast(f"✅ Articolo {prod['cod_art']} agganciato all'Assistente AI!")

        # -------------------------------------------------------------
        # 4. AI COMPARATIVE TECHNICAL ANALYSIS
        # -------------------------------------------------------------
        st.write("")
        st.markdown("---")
        st.markdown("#### 🤖 Perizia Comparativa Specialistica con Assistente AI")
        st.caption("L'assistente esamina contemporaneamente le schede tecniche, i valori di resa gastronomica, gli allergeni e le caratteristiche organolettiche di tutti i prodotti a confronto:")
        
        if st.button("⚡ Genera Perizia Comparativa con Intelligenza Artificiale", type="primary", use_container_width=True):
            with st.spinner("Analisi tecnica delle schede e generazione perizia comparativa in corso..."):
                # Prepare contextual prompt with full technical text of compared products
                products_context = []
                for p in compare_products:
                    t_desc = (
                        f"PRODOTTO SKU: {p['cod_art']}\n"
                        f"Nome: {p['descrizione_articolo']}\n"
                        f"Gruppo: {p.get('gruppo_art', '')}\n"
                        f"Prezzo Soglia: € {p.get('prezzo_indicativo', '0')} / {p.get('um', 'Kg')}\n"
                        f"Conservazione: {p.get('ambiente_cons', '')}\n"
                        f"Shelf-life: {p.get('shelf_life_it', '')} ({p.get('tempo_cons_gg', '')} gg)\n"
                        f"Formato Imballo: {p.get('unita_imballi', '')}\n"
                        f"TESTO SCHEDA TECNICA UFFICIALE (HACCP/Ingredienti/Allergeni):\n{p.get('scheda_text', 'Scheda non disponibile')[:2500]}\n"
                        f"-----------------------------------------"
                    )
                    products_context.append(t_desc)
                    
                full_compare_prompt = (
                    "Esegui una perizia comparativa tecnica, gastronomica e commerciale approfondita sui seguenti prodotti a catalogo di Italian Food Trading S.r.l.:\n\n"
                    + "\n\n".join(products_context) + "\n\n"
                    "Struttura la tua risposta in 4 sezioni chiare ed eleganti in formato Markdown:\n"
                    "1. 🍕 **Analisi Tecnica & Resa in Cucina/Pizzeria**: Differenze di prestazioni, forza/consistenza, tenuta in cottura o lievitazione, umidità e lavorabilità.\n"
                    "2. ⚠️ **Confronto Allergeni, Certificazioni & HACCP**: Dichiarazioni allergeni, glutine, lattosio, tracciabilità e shelf-life.\n"
                    "3. 💰 **Valutazione Economica & Food Cost**: Rapporto qualità/prezzo, incidenza per porzione e convenienza d'impiego.\n"
                    "4. 💡 **Consiglio di Vendita per l'Agente**: A quale specifica tipologia di locale/chef proporre ciascun articolo (es. Pizzeria Gourmet vs Ristorante Tradizionale vs Bistrot) per massimizzare la soddisfazione del cliente."
                )
                
                analysis_res = ai_assistant.generate_ai_response(
                    messages=[{"role": "user", "content": full_compare_prompt}],
                    current_product=None,
                    api_key=user_api_key if user_api_key else env_api_key,
                    model_name=model_choice,
                    enable_web_search=enable_grounding
                )
                st.session_state.compare_ai_analysis = analysis_res["text"]
                st.rerun()

        if st.session_state.get("compare_ai_analysis"):
            st.markdown("""
            <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-left:5px solid #2563EB; padding:20px; border-radius:12px; margin-top:16px;">
                <div style="font-weight:800; font-size:1.15rem; color:#0F172A; margin-bottom:12px;">📑 Risultato Perizia Comparativa AI:</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state.compare_ai_analysis)
