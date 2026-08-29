import streamlit as st
import os
import base64
from pathlib import Path
from dotenv import load_dotenv
import database
import ai_assistant
import config

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Catalogo Intelligente Ho.Re.Ca",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern HoReCa theme
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .product-card {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 24px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-blue { background-color: #E0F2FE; color: #0369A1; }
    .badge-green { background-color: #DCFCE7; color: #15803D; }
    .badge-amber { background-color: #FEF3C7; color: #B45309; }
    .badge-purple { background-color: #F3E8FF; color: #7E22CE; }
    .badge-cyan { background-color: #CFFAFE; color: #0E7490; }
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

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/restaurant-menu.png", width=64)
    st.title("Catalogo Intelligente")
    st.caption("AI Assistant & Schede Tecniche")
    
    st.divider()
    
    # API Key Configuration
    st.subheader("🔑 Configurazione Gemini AI")
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    user_api_key = st.text_input(
        "Google Gemini API Key",
        value=env_api_key,
        type="password",
        help="Inserisci la tua Google Gemini API Key per abilitare l'assistente AI e la ricerca web."
    )
    
    active_api_key = user_api_key.strip() or env_api_key
    if active_api_key:
        st.success("API Key attiva", icon="✅")
    else:
        st.warning("Inserisci una Gemini API Key per usare la chat", icon="⚠️")
        
    model_choice = st.selectbox(
        "Modello AI",
        options=["gemini-3.6-flash", "gemini-3.7-flash", "gemini-flash-latest", "gemini-pro-latest"],
        index=0
    )
    
    enable_web_search = st.toggle("🌐 Ricerca Web Google in tempo reale", value=True, help="Permette a Gemini di effettuare ricerche online per ricette, food cost e tendenze HoReCa.")
    
    st.divider()
    
    # Catalog Filters
    st.subheader("🏷️ Filtri Catalogo")
    categories = ["Tutte"] + database.get_categories()
    selected_category = st.selectbox("Categoria Merceologica", categories, index=0)
    
    storage_envs = ["Tutti"] + database.get_storage_envs()
    selected_env = st.selectbox("Ambiente di Conservazione", storage_envs, index=0)
    
    st.divider()
    
    # Stats & Maintenance
    stats = database.get_catalog_stats()
    st.subheader("📊 Dati Catalogo")
    st.write(f"• **Articoli totali:** {stats['total_products']}")
    st.write(f"• **Foto collegate:** {stats['with_foto']}")
    st.write(f"• **Schede PDF collegate:** {stats['with_scheda']}")
    st.write(f"• **Schede con testo estratto:** {stats['with_text']}")
    
    if st.button("🔄 Re-indicizza Catalogo e PDF"):
        with st.spinner("Indicizzazione in corso..."):
            import indexer
            indexer.run_indexing()
            st.success("Indicizzazione completata!")
            st.rerun()

# --- MAIN PAGE HEADER ---
st.markdown('<div class="main-header">🍽️ Catalogo Intelligente & Assistente Ho.Re.Ca</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Risposte tecniche certificate da Schede Tecniche Ufficiali e Consulenza Culinaria con Google Search Grounding</div>', unsafe_allow_html=True)

# Session state initialization
if "chat_focused_sku" not in st.session_state:
    st.session_state.chat_focused_sku = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Top search bar
col_search1, col_search2 = st.columns([3, 1])
with col_search1:
    search_query = st.text_input("🔍 Cerca per Codice Articolo (SKU), Nome o Parola chiave (es. 'farina', 'burrata', 'wagyu', 'pomodoro', 'A001012')", "")
with col_search2:
    limit_results = st.selectbox("Risultati max", [30, 60, 150], index=0)

# Fetch products based on filters and search
products = database.search_products(
    query=search_query,
    category=selected_category,
    storage_env=selected_env,
    limit=limit_results
)

# Tabs
tab_catalog, tab_chat = st.tabs(["📦 Scheda Prodotto & Catalogo", "🤖 Assistente AI Chef & Consulente Tecnico"])

with tab_catalog:
    if not products:
        st.warning(f"Nessun articolo trovato per '{search_query}'. Prova a verificare l'ortografia o a reimpostare i filtri di categoria.")
    else:
        st.success(f"🎯 Trovati **{len(products)}** articoli pertinenti:")
        
        # Product selector
        product_options = {
            f"{p['cod_art']} - {p['descrizione_articolo']} [{p.get('gruppo_art', '')}]": p['cod_art']
            for p in products
        }
        
        selected_label = st.selectbox(
            "Seleziona il prodotto da visualizzare nel dettaglio:",
            options=list(product_options.keys()),
            index=0
        )
        
        selected_sku = product_options[selected_label]
        current_prod = database.get_product_by_code(selected_sku)
        
        if current_prod:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            col_img, col_info = st.columns([1, 2])
            
            with col_img:
                foto_resolved = resolve_file(current_prod.get('foto_path'), current_prod.get('foto_filename'), config.FOTO_DIR)
                if foto_resolved and os.path.exists(foto_resolved):
                    st.image(foto_resolved, use_container_width=True, caption=f"SKU: {current_prod['cod_art']}")
                else:
                    st.info("🖼️ Foto articolo non presente", icon="ℹ️")
                    
                scheda_resolved = resolve_file(current_prod.get('scheda_path'), current_prod.get('scheda_filename'), config.SCHEDE_DIR)
                if scheda_resolved and os.path.exists(scheda_resolved):
                    with open(scheda_resolved, "rb") as f:
                        st.download_button(
                            label="📥 Scarica Scheda Tecnica (PDF)",
                            data=f.read(),
                            file_name=os.path.basename(scheda_resolved),
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.caption("📄 Nessuna scheda tecnica PDF allegata")
            
            with col_info:
                st.subheader(f"{current_prod['descrizione_articolo']}")
                st.markdown(f"**Codice Articolo (SKU):** `{current_prod['cod_art']}`")
                
                # Badges
                badge_html = f"""
                <div>
                    <span class="badge badge-blue">📁 {current_prod.get('gruppo_art', 'N/D')}</span>
                    <span class="badge badge-green">❄️ {current_prod.get('ambiente_cons', 'N/D')}</span>
                    <span class="badge badge-amber">⏳ Shelf-Life: {current_prod.get('shelf_life_it', 'N/D')}</span>
                    <span class="badge badge-purple">⚖️ {current_prod.get('tipo_peso', 'N/D')}</span>
                    <span class="badge badge-cyan">📦 {current_prod.get('unita_imballi', 'N/D')}</span>
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)
                
                st.write("")
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write(f"• **Unità di Misura:** {current_prod.get('um', 'Kg')}")
                    st.write(f"• **Minimo d'Ordine:** {current_prod.get('minimo_ordine', 'N/D')}")
                    st.write(f"• **Tempo Consegna:** {current_prod.get('tempo_cons_gg', 'N/D')} gg")
                with col_d2:
                    if current_prod.get('prezzo_indicativo'):
                        st.write(f"• **Listino / Contratto:** € {current_prod.get('prezzo_indicativo')}")
                    st.write(f"• **Stato Articolo:** {'Attivo' if current_prod.get('art_attivo') == 'Y' else 'Disattivo'}")
                
                if current_prod.get('descrizione_commerciale'):
                    st.info(f"**Descrizione Commerciale:**\n{current_prod['descrizione_commerciale']}")
                
                # Action button to focus product in AI chat
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🎯 Aggancia questo prodotto alla Chat AI", type="primary", use_container_width=True):
                        st.session_state.chat_focused_sku = selected_sku
                        st.toast(f"✅ Articolo {selected_sku} agganciato alla Chat AI!")
                        st.rerun()
                with col_btn2:
                    if st.session_state.chat_focused_sku == selected_sku:
                        if st.button("❌ Rimuovi focus da questo prodotto", use_container_width=True):
                            st.session_state.chat_focused_sku = None
                            st.toast("Focus rimosso: la Chat AI ora risponde su tutto il catalogo generale.")
                            st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Scheda Tecnica Preview Box
            scheda_text = current_prod.get('scheda_text', '').strip()
            if scheda_text:
                with st.expander("📄 Consulta il Testo Estratto della Scheda Tecnica Ufficiale (HACCP, Ingredienti, Allergeni)"):
                    st.text_area("Testo Scheda Tecnica", value=scheda_text, height=250, disabled=True)
            elif current_prod.get('scheda_path'):
                st.info("La scheda tecnica PDF è presente ma non contiene testo scansionabile.")

with tab_chat:
    # Get currently focused product for chat
    focused_sku = st.session_state.get("chat_focused_sku")
    focused_prod = database.get_product_by_code(focused_sku) if focused_sku else None
    
    col_chat_head, col_chat_reset = st.columns([3, 1])
    with col_chat_head:
        if focused_prod:
            st.info(f"🎯 **Prodotto attualmente agganciato:** `{focused_prod['cod_art']}` — **{focused_prod['descrizione_articolo']}**\n\n*(L'AI risponderà basandosi sulla scheda tecnica e sui dati di questo specifico articolo)*")
        else:
            st.success("🌐 **Modalità Generale Attiva:** *Catalogo Generale Ho.Re.Ca*\n\n*(L'AI risponderà su qualsiasi prodotto del catalogo o fornirà consigli culinari generali)*")
            
    with col_chat_reset:
        if focused_prod:
            if st.button("🔓 Sgancia Prodotto (Modalità Generale)", type="secondary", use_container_width=True):
                st.session_state.chat_focused_sku = None
                st.toast("Focus rimosso! Passato alla modalità Catalogo Generale.")
                st.rerun()
            
    st.divider()
    
    # Quick Prompt suggestions
    st.markdown("##### ⚡ Domande Rapide con 1 Click:")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    quick_prompt = None
    with q_col1:
        if st.button("📋 Allergeni & HACCP", use_container_width=True):
            if focused_prod:
                quick_prompt = f"Quali sono gli allergeni, gli ingredienti e le specifiche HACCP indicate nella scheda tecnica del prodotto {focused_prod['cod_art']} ({focused_prod['descrizione_articolo']})?"
            else:
                quick_prompt = "Quali sono le principali linee guida HACCP e gestione allergeni per i prodotti freschi e congelati a catalogo?"
    with q_col2:
        if st.button("❄️ Conservazione & Scongelamento", use_container_width=True):
            if focused_prod:
                quick_prompt = f"Quali sono le modalità di conservazione, shelf-life e le procedure ideali di scongelamento per il prodotto {focused_prod['cod_art']}?"
            else:
                quick_prompt = "Quali sono le procedure corrette di conservazione e catena del freddo per i prodotti HoReCa a catalogo?"
    with q_col3:
        if st.button("🍕 3 Idee per Pizzeria Gourmet", use_container_width=True):
            if focused_prod:
                quick_prompt = f"Suggerisci 3 abbinamenti o ricette creative per pizza gourmet o piatti del ristorante che valorizzino {focused_prod['descrizione_articolo']}, indicando il food cost stimato."
            else:
                quick_prompt = "Suggerisci 3 ricette o pizze gourmet di tendenza utilizzando i migliori prodotti tipici e formaggi a catalogo."
    with q_col4:
        if st.button("🔥 Tendenze & Consigli Chef", use_container_width=True):
            if focused_prod:
                quick_prompt = f"Cerca online le migliori tendenze culinarie attuali su come i grandi chef utilizzano {focused_prod['descrizione_articolo']} e consigliami tecniche di cottura moderne."
            else:
                quick_prompt = "Cerca online i trend gastronomici più forti di quest'anno per ristoranti e pizzerie e quali ingredienti stanno avendo maggior successo."

    st.divider()

    # Direct Input Form in the Main Tab Area
    st.markdown("##### 💬 Fai una domanda all'Assistente:")
    with st.form(key="chat_direct_form", clear_on_submit=True):
        col_in1, col_in2 = st.columns([5, 1])
        with col_in1:
            form_text = st.text_input(
                "Scrivi qui la tua domanda:",
                placeholder="Scrivi qui la tua domanda per lo Chef & Consulente Tecnico...",
                label_visibility="collapsed"
            )
        with col_in2:
            form_submit = st.form_submit_button("Invia 🚀", type="primary", use_container_width=True)

    # Bottom sticky chat input as additional option
    bottom_input = st.chat_input("Oppure scrivi qui in basso la tua domanda...")

    prompt_to_run = quick_prompt or (form_text if form_submit and form_text.strip() else None) or bottom_input

    # Display chat history
    if st.session_state.messages:
        st.markdown("##### 📜 Conversazione:")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🧑‍🍳" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    st.markdown("**🌐 Fonti Web Consultate:**")
                    for s in msg["sources"]:
                        if s.get("url"):
                            st.markdown(f"- [{s['title']}]({s['url']})")

    if prompt_to_run:
        if not active_api_key:
            st.error("⚠️ Inserisci la tua Google Gemini API Key nella barra laterale sinistra per avviare la chat!")
        else:
            # Append user message
            st.session_state.messages.append({"role": "user", "content": prompt_to_run})
            with st.chat_message("user", avatar="🧑‍🍳"):
                st.markdown(prompt_to_run)
                
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("L'assistente sta analizzando la scheda tecnica e preparando la risposta..."):
                    response_data = ai_assistant.generate_ai_response(
                        messages=st.session_state.messages,
                        current_product=focused_prod,
                        api_key=active_api_key,
                        model_name=model_choice,
                        enable_web_search=enable_web_search
                    )
                    
                    st.markdown(response_data["text"])
                    if response_data.get("sources"):
                        st.markdown("**🌐 Fonti Web Consultate:**")
                        for s in response_data["sources"]:
                            if s.get("url"):
                                st.markdown(f"- [{s['title']}]({s['url']})")
                                
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_data["text"],
                        "sources": response_data.get("sources", [])
                    })

    if st.session_state.messages:
        if st.button("🗑️ Pulisci cronologia chat"):
            st.session_state.messages = []
            st.rerun()
