import os
import re
import time
from typing import List, Dict, Any, Optional
import config
import database

def get_client(api_key: Optional[str] = None):
    """Initializes Google GenAI client."""
    from google import genai
    key = api_key or config.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None
    return genai.Client(api_key=key)

def retrieve_relevant_catalog_items(user_query: str, limit: int = 15) -> List[Dict[str, Any]]:
    """Performs dynamic keyword extraction and hybrid search across products and technical sheet PDFs."""
    return database.search_products(user_query, limit=limit)

def generate_ai_response(
    messages: List[Dict[str, str]], 
    current_product: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model_name: str = config.DEFAULT_GEMINI_MODEL,
    enable_web_search: bool = True
) -> Dict[str, Any]:
    """Generates streaming/complete response with multi-model fallback and rate-limit backoff."""
    client = get_client(api_key)
    if not client:
        return {
            "text": "⚠️ **Chiave API Google Gemini non configurata.**\n\nInserisci la tua API Key nella barra laterale sinistra per sbloccare le funzionalità di consulenza AI.",
            "grounding_chunks": []
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
- Prezzo Soglia / Listino Ufficiale: € {current_product.get('prezzo_indicativo', 'N/D')} / {current_product.get('um', 'Kg')}
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
ESTRATTO PRODOTTI E SCHEDE TECNICHE DAL CATALOGO AZIENDALE (RISULTATI REALI DI MAGAZZINO):
Sono presenti a magazzino i seguenti {len(retrieved_items)} articoli. Fai riferimento ESCLUSIVAMENTE a questi prodotti reali:
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
- Prezzo Soglia: € {item.get('prezzo_indicativo', 'N/D')} / {item.get('um', 'Kg')}
- Dati Scheda Tecnica Ufficiale PDF:
{scheda_snippet if scheda_snippet else '(Nessun testo scheda tecnica estratto)'}
"""
        else:
            product_context = "\n(Nessun prodotto corrispondente trovato nell'estratto. Se la domanda richiede prodotti a catalogo, avvisa che non risultano disponibili)\n"

    system_instruction = f"""
Sei l'Assistente Tecnico e Commerciale Ufficiale di Italian Food Trading S.r.l. (Verona), fornitore d'eccellenza per il settore Ho.Re.Ca (ristoranti, pizzerie, bistrot).

REGOLE TASSATIVE DI INTEGRITÀ AZIENDALE E CATALOGO:
1. **CODICI ARTICOLO (SKU) E PRODOTTI REALI**:
   - Cita ESCLUSIVAMENTE ed OBBLIGATORIAMENTE i codici SKU (es. `A110419QU`, `A110174`) e i nomi degli articoli presenti nell'ESTRATTO CATALOGO AZIENDALE fornito qui sotto.
   - È SEVERAMENTE VIETATO inventare codici articolo o proporre codici/marchi trovati su Google o da fonti esterne che NON siano presenti nell'estratto fornito.
   - È SEVERAMENTE VIETATO citare voci amministrative, cespiti (es. `ZC...`), supplementi logistici o di trasporto (es. `S3...`), o spese/costi interni (es. `T0...`). Proponi esclusivamente generi alimentari e referenze merci vendibili a listino.
   - Per ogni prodotto consigliato, indica sempre il **Codice SKU**, la **Descrizione esatta**, il **Prezzo Soglia** e la motivazione tecnica (es. W, proteine, ore di lievitazione indicate in scheda).

2. **CONSULENZA TECNICA E PROFESSIONALE PER CHEF E PIZZAIOLI**:
   - Spiega con competenza perché una determinata farina o prodotto è idoneo per la lavorazione richiesta.
   - Usa la ricerca web Google SOLO per arricchire consigli di metodo (idratazione, lievito madre/birra, gestione temperature), MAI per inventare referenze di magazzino.

3. **STRUTTURA DELLA RISPOSTA**:
   - Accogliente, professionale, formattata chiaramente con titoli, sezioni, codici SKU in evidenza (`SKU`) e consigli applicativi.

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

        # Fallback model list across multiple model families to avoid shared quota limits
        candidate_models = [
            model_name,
            "gemini-3.6-flash",
            "gemini-2.5-flash",
            "gemini-flash-latest",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-3.7-flash"
        ]
        seen = set()
        models_to_try = [m for m in candidate_models if not (m in seen or seen.add(m))]

        last_error = None
        for current_model in models_to_try:
            for use_search in ([enable_web_search, False] if enable_web_search else [False]):
                try:
                    tools = []
                    if use_search:
                        tools.append(types.Tool(google_search=types.GoogleSearch()))

                    config_obj = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.2,
                        tools=tools if tools else None,
                    )

                    response = client.models.generate_content(
                        model=current_model,
                        contents=formatted_contents,
                        config=config_obj
                    )

                    # Extract text safely
                    text_result = ""
                    grounding_chunks = []
                    
                    if response.text:
                        text_result = response.text
                    elif response.candidates and response.candidates[0].content:
                        parts = response.candidates[0].content.parts
                        text_parts = [p.text for p in parts if p.text]
                        text_result = "".join(text_parts)

                    if response.candidates and len(response.candidates) > 0:
                        cand = response.candidates[0]
                        if cand.grounding_metadata and cand.grounding_metadata.grounding_chunks:
                            for chunk in cand.grounding_metadata.grounding_chunks:
                                if chunk.web:
                                    grounding_chunks.append({
                                        "title": chunk.web.title or "Google Web Source",
                                        "url": chunk.web.uri
                                    })

                    return {
                        "text": text_result,
                        "grounding_chunks": grounding_chunks,
                        "model_used": current_model
                    }

                except Exception as e:
                    err_str = str(e)
                    last_error = e
                    # If rate limited (429) or temporary server error (503), back off and try fallback
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "503" in err_str or "404" in err_str:
                        time.sleep(2.0)
                        continue
                    else:
                        break

        # If all models exceeded rate limits
        err_msg = str(last_error)
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return {
                "text": "⏱️ **Limite di richieste al minuto raggiunto (Google API 429 Quota).**\n\nL'account Google Gemini gratuito consente un numero massimo di richieste al minuto. **Attendi 10-15 secondi e riprova** cliccando di nuovo o selezionando un altro modello nella barra laterale sinistra.",
                "grounding_chunks": []
            }

        return {
            "text": f"⚠️ Si è verificato un errore durante la generazione della risposta: {str(last_error)}",
            "grounding_chunks": []
        }

    except Exception as e:
        return {
            "text": f"⚠️ Errore di configurazione AI: {str(e)}",
            "grounding_chunks": []
        }
