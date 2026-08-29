import streamlit as st
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional
import database
import ai_assistant
import config

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Catalogo Intelligente Ho.Re.Ca | AI Assistant",
    page_icon="🍴",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN PREMIUM HORECA CSS THEME ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700&display=swap" rel="stylesheet">

<style>
    /* Global Typography - preserve Streamlit Material Icons */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3 {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Ensure Streamlit and Material icons are never overridden by custom fonts */
    [data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined, [translate="no"], i {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }
    
    h1, h2, h3, .hero-title {
        font-family: 'Outfit', sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Main Container background */
    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #334155 100%);
        border-radius: 18px;
        padding: 26px 30px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 16px 20px -5px rgba(15, 23, 42, 0.12);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        background: linear-gradient(90deg, #FFFFFF 0%, #FDE68A 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 0.98rem;
        color: #94A3B8;
        margin-top: 6px;
        margin-bottom: 14px;
    }
    
    .hero-stats-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
    }
    
    .hero-pill {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #E2E8F0;
    }
    
    .product-title-text {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    
    .sku-badge {
        display: inline-block;
        font-family: ui-monospace, monospace !important;
        background: #F1F5F9;
        color: #475569;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid #CBD5E1;
        margin-bottom: 8px;
    }
    
    .price-tag-box {
        background: #ECFDF5;
        border: 1px solid #A7F3D0;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 6px;
        margin-bottom: 8px;
    }
    
    .price-value-text {
        font-size: 1.25rem;
        font-weight: 800;
        color: #065F46;
    }
    
    /* Badges */
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 6px;
    }
    
    .badge-category { background: #EFF6FF; color: #1D4ED8; border: 1px solid #DBEAFE; }
    .badge-refrigerato { background: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-congelato { background: #F0FDF4; color: #0284C7; border: 1px solid #BAE6FD; }
    .badge-asciutto { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .badge-shelflife { background: #FAF5FF; color: #7E22CE; border: 1px solid #F3E8FF; }
    .badge-packaging { background: #F8FAFC; color: #334155; border: 1px solid #CBD5E1; }

    /* Focus Alert Banner */
    .focus-alert-active {
        background: #EFF6FF;
        border: 1px solid #93C5FD;
        border-radius: 12px;
        padding: 14px 18px;
        color: #1E40AF;
        margin-bottom: 16px;
    }
    
    .focus-alert-general {
        background: #F0FDF4;
        border: 1px solid #86EFAC;
        border-radius: 12px;
        padding: 14px 18px;
        color: #166534;
        margin-bottom: 16px;
    }

    /* Action Buttons styling */
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
        options=["gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest", "gemini-pro-latest"],
        index=0,
        help="Gemini 3.6 Flash garantisce massima velocità e stabilità."
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
            <div class="hero-subtitle">Italian Food Trading S.r.l. (Verona) • Consulenza Tecnica Certificata & Assistente AI Ho.Re.Ca</div>
        </div>
    </div>
    <div class="hero-stats-row">
        <div class="hero-pill">📦 {stats['total_products']:,} Articoli a Catalogo</div>
        <div class="hero-pill">📸 {stats['with_foto']:,} Foto HD</div>
        <div class="hero-pill">📄 {stats['with_scheda']:,} Schede Tecniche PDF</div>
        <div class="hero-pill">⚡ Modello: {model_choice}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Session state initialization
if "chat_focused_sku" not in st.session_state:
    st.session_state.chat_focused_sku = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Full-width search bar (no limit dropdown)
search_query = st.text_input("🔍 Ricerca Intelligente Articoli (SKU, nome, ingrediente es. 'farina', 'burrata', 'wagyu', 'A001012')", "")

# Fetch all matching products without artificial limits
products = database.search_products(
    query=search_query,
    category=selected_category,
    storage_env=selected_env,
    limit=None
)

# Tabs
tab_catalog, tab_chat = st.tabs(["📦 Scheda Prodotto & Catalogo", "🤖 Studio Consulenza & Chat AI"])

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
                    btn_col1, btn_col2 = st.columns([1, 1])
                    with btn_col1:
                        if st.session_state.chat_focused_sku == selected_sku:
                            if st.button("❌ Rimuovi focus AI", use_container_width=True):
                                st.session_state.chat_focused_sku = None
                                st.toast("Focus rimosso! Passato al catalogo generale.")
                                st.rerun()
                        else:
                            if st.button("🎯 Aggancia alla Chat AI", type="primary", use_container_width=True):
                                st.session_state.chat_focused_sku = selected_sku
                                st.toast(f"✅ Articolo {selected_sku} agganciato alla Chat AI! Vai al tab Chat.")
                                st.rerun()
                                
                    with btn_col2:
                        scheda_resolved = resolve_file(current_prod.get('scheda_path'), current_prod.get('scheda_filename'), config.SCHEDE_DIR)
                        if scheda_resolved and os.path.exists(scheda_resolved):
                            with open(scheda_resolved, "rb") as f:
                                st.download_button(
                                    label="📥 Scarica Scheda PDF",
                                    data=f.read(),
                                    file_name=os.path.basename(scheda_resolved),
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                        else:
                            st.button("📄 Nessun PDF allegato", disabled=True, use_container_width=True)

            # Scheda Tecnica Full-Width Section below product card
            scheda_text = current_prod.get('scheda_text', '').strip()
            if scheda_text:
                st.write("")
                with st.expander("Consulta il Testo Ufficiale della Scheda Tecnica (HACCP, Ingredienti, Allergeni)", expanded=False):
                    st.text_area("Testo Integrale Scheda Tecnica", value=scheda_text, height=220, disabled=True, label_visibility="collapsed")
            elif current_prod.get('scheda_path'):
                st.info("ℹ️ La scheda tecnica PDF è presente per il download ma non contiene testo scansionabile.")

with tab_chat:
    # Get currently focused product for chat
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
            
    # Quick Prompt suggestions with styled chips
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
        # General Catalog Quick Prompts
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

    # Direct Input Form in the Main Tab Area
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

    # Bottom sticky chat input as additional option
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
            # Append user message
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
