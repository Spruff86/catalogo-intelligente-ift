import os
import time
from typing import Dict, Any, Optional, List
import config

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

def generate_ai_response(
    messages: List[Dict[str, str]],
    current_product: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
    model_name: str = "gemini-3.6-flash",
    enable_web_search: bool = True
) -> Dict[str, Any]:
    """
    Generates a contextual response using Gemini 3.6 Flash (fast & stable) with:
    - Smart Google Search Grounding with fallback
    - Multi-model failover & retry
    """
    client, err = get_gemini_client(api_key)
    if err:
        return {
            "text": f"⚠️ {err}",
            "sources": [],
            "grounding_metadata": None
        }

    # Construct context from product
    product_context = ""
    if current_product:
        product_context = f"""
INFORMAZIONI PRODOTTO SELEZIONATO DALL'UTENTE:
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
            product_context += "\n(Nota: Nessun testo di scheda tecnica PDF associato o disponibile per questo articolo)\n"

    system_instruction = f"""
Sei l'Assistente Intelligente e Consulente Tecnico/Culinario di una rinomata azienda di distribuzione alimentare Ho.Re.Ca (fornitore ufficiale di ristoranti, pizzerie, bistrot e gastronomie).

IL TUO RUOLO E OBIETTIVO:
1. **Precisione Tecnica Assoluta**:
   - Per domande su allergeni, ingredienti, valori nutrizionali, modalità di conservazione, shelf-life, HACCP, temperature o packaging, fai riferimento esclusivo e rigoroso ai dati ufficiali del catalogo e della scheda tecnica forniti nel contesto.
   - Se un dettaglio tecnico normativo/allergenico non è presente nella scheda tecnica fornita, dichiaralo chiaramente senza inventarlo.

2. **Consulenza Culinaria & Business per Ristoratori e Pizzaioli**:
   - Per domande su utilizzi in cucina, abbinamenti per pizze gourmet o piatti del ristorante, tecniche di cottura, food cost, conservazione o tendenze gastronomiche, sfrutta le tue ampie competenze culinarie per fornire consigli pratici, aggiornati, creativi e professionali per chef e pizzaioli.
   - Suggerisci abbinamenti creativi ma professionali, indicando passaggi chiave per la preparazione.

3. **Stile di Risposta**:
   - Tono professionale, cortese, competente e orientato al cliente HoReCa.
   - Formatta le risposte con titoli chiari, elenchi puntati ed emoji sobrie per facilitare la lettura veloce.
   - Quando appropriato, distingui chiaramente tra:
     📋 **Specifiche Tecniche Ufficiali** (dalla scheda tecnica)
     💡 **Consigli dello Chef & Utilizzi Consigliati** (dall'esperienza culinaria)

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
