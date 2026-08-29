import os
import time
from typing import Dict, Any, Optional, List
import config
import database

def get_gemini_client(api_key: Optional[str] = None):
    key = api_key or os.getenv("GEMINI_API_KEY") or config.GEMINI_API_KEY
    if not key:
        return None, "API Key non configurata. Inserisci la tua Google Gemini API Key per iniziare."
        
    try:
        from google import genai
        client = genai.Client(api_key=key)
        return client, None
    except Exception as e:
        return None, f"Errore nell'inizializzazione del client Gemini: {e}"

def retrieve_relevant_catalog_items(user_query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Retrieves the most relevant products and technical sheets for general questions using smart database search"""
    return database.search_products(query=user_query, limit=limit)

def generate_ai_response(
    messages: List[Dict[str, str]],
    current_product: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    enable_web_search: bool = True
) -> Dict[str, Any]:
    """
    Generates a contextual response using Gemini with:
    - Single product focused technical consultation
    - Multi-product General Catalog Technical RAG retrieval
    - Google Search Grounding with 429 quota fallback
    - Multi-model failover & retry
    """
    client, err = get_gemini_client(api_key)
    if err:
        return {
            "text": f"⚠️ {err}",
            "sources": [],
            "grounding_metadata": None
        }

    latest_user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            latest_user_message = msg.get("content", "")
            break

    # Construct context based on focus mode vs general catalog query
    product_context = ""
    if current_product:
        # Single focused product mode
        product_context = f"""
INFORMAZIONI PRODOTTO SPECIFICO SELEZIONATO DALL'UTENTE (MODALITÀ FOCUS):
- Codice Articolo (SKU): {current_product.get('cod_art', 'N/D')}
- Descrizione: {current_product.get('descrizione_articolo', 'N/D')}
- Categoria / Gruppo: {current_product.get('gruppo_art', 'N/D')}
- Unità di Misura: {current_product.get('um', 'N/D')}
- Tipo Peso: {current_product.get('tipo_peso', 'N/D')}
- Unità e Imballi / Confezionamento: {current_product.get('unita_imballi', 'N/D')}
- Ambiente di Conservazione: {current_product.get('ambiente_cons', 'N/D')}
- Shelf Life: {current_product.get('shelf_life_it', 'N/D')}
- Minimo d'Ordine: {current_product.get('minimo_ordine', 'N/D')}
- Descrizione Commerciale: {current_product.get('descrizione_commerciale', 'N/D')}
- Prezzo Indicativo / Listino: {current_product.get('prezzo_indicativo', 'N/D')} €
"""
        scheda_text = current_product.get('scheda_text', '').strip()
        if scheda_text:
            product_context += f"""
TESTO ESTRATTO DALLA SCHEDA TECNICA UFFICIALE (PDF):
\"\"\"
{scheda_text}
\"\"\"
"""
        else:
            product_context += "\n(Nota: Nessun testo di scheda tecnica PDF associato per questo articolo)\n"
    else:
        # General Catalog Query Mode (RAG Dynamic Retrieval)
        retrieved_items = retrieve_relevant_catalog_items(latest_user_message, limit=15)
        if retrieved_items:
            product_context = f"""
ESTRATTO PRODOTTI E SCHEDE TECNICHE DAL CATALOGO AZIENDALE (RISULTATI RICERCA AUTOMATICA):
Sono stati trovati {len(retrieved_items)} articoli pertinenti alla domanda dell'utente. Utilizza questi dati ufficiali per rispondere citando SKU, descrizioni e specifiche tecniche:
"""
            for idx, item in enumerate(retrieved_items, 1):
                scheda_snippet = item.get('scheda_text', '').strip()
                if len(scheda_snippet) > 800:
                    scheda_snippet = scheda_snippet[:800] + "... [continua]"
                    
                product_context += f"""
--- PRODOTTO {idx} ---
- Codice SKU: {item.get('cod_art', 'N/D')}
- Descrizione Articolo: {item.get('descrizione_articolo', 'N/D')}
- Categoria/Gruppo: {item.get('gruppo_art', 'N/D')}
- Conservazione: {item.get('ambiente_cons', 'N/D')}
- Shelf-Life: {item.get('shelf_life_it', 'N/D')}
- Prezzo Indicativo: € {item.get('prezzo_indicativo', 'N/D')} / {item.get('um', 'Kg')}
- Dati Scheda Tecnica Ufficiale PDF:
{scheda_snippet if scheda_snippet else '(Nessun testo scheda tecnica estratto)'}
"""
        else:
            product_context = "\n(Nessun prodotto specifico agganciato. L'utente sta consultando il catalogo in modalità generale)\n"

    system_instruction = f"""
Sei l'Assistente Intelligente e Consulente Tecnico/Culinario di una prestigiosa azienda di distribuzione alimentare Ho.Re.Ca (fornitore ufficiale di ristoranti, pizzerie gourmet, bistrot e gastronomie).

IL TUO RUOLO E OBIETTIVI PRINCIPALI:
1. **Risposte a Domande Trasversali sul Catalogo Generale**:
   - Quando l'utente ti chiede ad esempio *"quali prosciutti cotti senza glutine abbiamo?"*, *"quali farine sono indicate per lievitazioni 40-60 ore?"*, *"quali prodotti senza lattosio abbiamo?"*, *"quali pelati/pomodori per pizza consigli?"*:
   - Analizza attentamente l'**ESTRATTO PRODOTTI E SCHEDE TECNICHE DAL CATALOGO AZIENDALE** fornito qui sotto.
   - Individua gli articoli corrispondenti e cita esplicitamente il **Codice Articolo (SKU)**, la **Descrizione esatta**, e le caratteristiche tecniche oggettive (es. certificazioni Senza Glutine / Senza Lattosio, ingredienti, % resa, allergeni, modalità di utilizzo).

2. **Precisione e Trasparenza Certificata**:
   - Basa i dati tecnici (allergeni, valori nutrizionali, HACCP, conservazione) rigorosamente sui dati del catalogo aziendale e sulle schede tecniche PDF.
   - Non inventare codici articolo: cita solo quelli effettivamente presenti nell'estratto catalogo.

3. **Consulenza Gastronomica di Alto Livello per Chef e Pizzaioli**:
   - Arricchisci sempre le risposte con consigli pratici: utilizzi ottimali, abbinamenti in cucina e pizzeria, food cost ed indicazioni di servizio.

4. **Stile di Risposta**:
   - Professionale, chiaro, strutturato con titoli in grassetto, punti elenco ed emoji sobrie.
   - Evidenzia chiaramente i Codici SKU con backtick (es. `A050808QU`).

{product_context}
"""

    try:
        from google.genai import types

        # Build formatted contents
        formatted_contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            gemini_role = "user" if role == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=content)]
                )
            )

        # Fallback model chain
        models_chain = [model_name]
        for fallback_m in ["gemini-3.6-flash", "gemini-flash-latest", "gemini-3.1-flash-lite", "gemini-3.7-flash"]:
            if fallback_m not in models_chain:
                models_chain.append(fallback_m)

        last_error = None
        response = None

        for target_model in models_chain:
            # Try with web search first if enabled
            if enable_web_search:
                try:
                    config_with_search = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.7,
                        tools=[types.Tool(google_search=types.GoogleSearch())]
                    )
                    response = client.models.generate_content(
                        model=target_model,
                        contents=formatted_contents,
                        config=config_with_search
                    )
                    break
                except Exception as search_err:
                    err_str = str(search_err)
                    if "503" in err_str or "UNAVAILABLE" in err_str:
                        time.sleep(0.3)

            # Standard generation fallback
            try:
                config_standard = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                )
                response = client.models.generate_content(
                    model=target_model,
                    contents=formatted_contents,
                    config=config_standard
                )
                break
            except Exception as gen_err:
                last_error = gen_err
                err_str = str(gen_err)
                if "503" in err_str or "UNAVAILABLE" in err_str or "high demand" in err_str.lower():
                    time.sleep(0.3)
                    continue
                else:
                    continue

        if response is None:
            return {
                "text": f"❌ Si è verificato un errore temporaneo dei server Google: {str(last_error)}. Riprova tra qualche istante.",
                "sources": [],
                "grounding_metadata": None
            }

        response_text = response.text or ""

        # Extract web citations if available
        sources = []
        grounding_meta = None
        try:
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                    grounding_meta = candidate.grounding_metadata
                    if hasattr(grounding_meta, 'grounding_chunks') and grounding_meta.grounding_chunks:
                        for chunk in grounding_meta.grounding_chunks:
                            if hasattr(chunk, 'web') and chunk.web:
                                sources.append({
                                    "title": chunk.web.title or "Fonte Web",
                                    "url": chunk.web.uri or ""
                                })
        except Exception:
            pass

        return {
            "text": response_text,
            "sources": sources,
            "grounding_metadata": grounding_meta
        }

    except Exception as e:
        return {
            "text": f"❌ Si è verificato un errore durante la generazione della risposta AI: {str(e)}",
            "sources": [],
            "grounding_metadata": None
        }
