import re
import urllib.parse
from datetime import datetime
from typing import Dict, Any, Optional

import config
import ai_assistant

def get_clean_price(val: Any) -> float:
    """Safely converts price to float."""
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    try:
        clean = str(val).replace('€', '').replace(',', '.').strip()
        return float(clean)
    except (ValueError, TypeError):
        return 0.0

def clean_text(text: str) -> str:
    """Removes weird Excel artifacts like _x0007_ and cleans whitespace."""
    if not text:
        return ""
    # Replace Excel control code artifacts with a neat bullet point
    cleaned = re.sub(r'_x[0-9a-fA-F]{4}_', ' • ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def generate_default_pitch_and_pairing(product: Dict[str, Any]) -> str:
    """
    Generates a realistic, professional fallback culinary presentation and pairing
    using product commercial metadata and category knowledge.
    """
    desc = product.get("descrizione_articolo", "")
    comm = clean_text(product.get("descrizione_commerciale", ""))
    gruppo = product.get("gruppo_art", "").upper()
    env = product.get("ambiente_cons", "")
    
    # If commercial description exists, use it as baseline
    if comm:
        pitch = comm
    else:
        pitch = f"Selezione d'eccellenza garantita da Italian Food Trading S.r.l., ideale per le cucine e i laboratori Ho.Re.Ca più esigenti."

    # Generate tailored pairing based on product category
    desc_upper = desc.upper()
    
    if any(k in desc_upper for k in ["FARINA", "SEMOLA", "W2", "W3", "W4"]):
        pairing = "💡 *Consiglio di Resa:* Ideale per impasti ad alta idratazione e lievitazioni controllate. Garantisce una maglia glutinica tenace, alveolatura ariosa e perfetta digeribilità alla cottura."
    elif any(k in desc_upper for k in ["MOZZARELLA", "FIORDILATTE", "BURRATA", "STRACCIATELLA"]):
        pairing = "💡 *Consiglio di Utilizzo:* Ottima sia a crudo in uscita forno su pizze gourmet che in mantecatura. Conserva un cuore morbido e una freschezza lattica autentica senza rilasciare eccesso di siero."
    elif any(k in desc_upper for k in ["COTTO", "PROSC", "ORAZIO", "BRACE", "CRUDO", "SPECK"]):
        pairing = "💡 *Abbinamento Consigliato:* Straordinario per taglieri gourmet, focacce d'autore o abbinato a formaggi a pasta filata e burrate pugliesi per esaltarne la rotondità aromatica."
    elif any(k in desc_upper for k in ["ROAST", "MANZO", "BEEF", "TAGLIATA", "CARNE"]):
        pairing = "💡 *Consiglio dello Chef:* Perfetto per cotture veloci ad alta temperatura. Resa tenerissima e sapore succoso; splendido con sale Maldon, scaglie di Grana Padano DOP e un filo di olio EVO 100% italiano."
    elif any(k in desc_upper for k in ["OLIO", "EXTRA", "EVO"]):
        pairing = "💡 *Consiglio d'Uso:* Ideale a crudo come tocco finale su primi piatti, vellutate, carni rosse e pizze contemporary per valorizzare gli aromi senza coprire le materie prime."
    elif any(k in desc_upper for k in ["POMODORO", "POLPA", "PELATI", "SAN MARZANO"]):
        pairing = "💡 *Consiglio dello Chef:* Spiccata dolcezza naturale e bassa acidità; garantisce una densità vellutata che non bagna l'impasto in cottura e mantiene un colore rosso vivo invitante."
    else:
        pairing = "💡 *Consiglio dello Chef:* Referenza studiata per offrire massima costanza di resa, abbattere i tempi di preparazione in linea e valorizzare le tue proposte a menu."

    return f"{pitch}\n\n{pairing}"

def generate_ai_pitch_and_pairing(
    product: Dict[str, Any], 
    api_key: Optional[str] = None, 
    model_name: str = config.DEFAULT_GEMINI_MODEL
) -> str:
    """
    Calls Gemini using the official PDF technical sheet text to craft a compelling,
    custom culinary pitch and pairing tip tailored for professional chefs and restaurateurs.
    """
    scheda_text = product.get("scheda_text", "").strip()
    desc = product.get("descrizione_articolo", "")
    comm = product.get("descrizione_commerciale", "")
    gruppo = product.get("gruppo_art", "")
    sku = product.get("cod_art", "")
    
    prompt = f"""
Sei il Master Chef e Direttore Tecnico di Italian Food Trading S.r.l. (Verona).
Crea una BREVE PRESENTAZIONE GASTRONOMICA e un CONSIGLIO DI UTILIZZO / ABBINAMENTO per il seguente articolo a catalogo:

PRODOTTO: {desc} (SKU: {sku})
CATEGORIA: {gruppo}
DESCR. COMMERCIALE: {comm}
DATI SCHEDA TECNICA UFFICIALE:
\"\"\"
{scheda_text[:1500] if scheda_text else 'Dati da catalogo IFT standard'}
\"\"\"

ISTRUZIONI DI STILE:
- Scrivi un testo professionale, invitante e tecnico (massimo 4-5 righe complessive).
- Strutturalo in 2 paragrafi sintetici:
  1. Breve presentazione delle qualità organolettiche e dell'eccellenza della materia prima.
  2. Un consiglio pratico di utilizzo o abbinamento gourmet d'effetto (es. farcitura pizza, impiattamento, accostamento ingredienti o tecnica di cottura).
- Usa formattazione WhatsApp con grassetti (es. *croccantezza*, *idratazione*).
- NON inventare codici o marchi esterni.
"""
    try:
        res = ai_assistant.generate_ai_response(
            messages=[{"role": "user", "content": prompt}],
            current_product=product,
            api_key=api_key,
            model_name=model_name,
            enable_web_search=False
        )
        text = res.get("text", "").strip()
        if text and not text.startswith("⚠️"):
            return text
    except Exception:
        pass
        
    return generate_default_pitch_and_pairing(product)

def build_flash_offer_message(
    product: Dict[str, Any],
    offer_price: float,
    customer_name: str = "",
    agent_name: str = "Italian Food Trading",
    offer_style: str = "🔥 Opportunità Speciale",
    custom_pitch: str = ""
) -> str:
    """
    Builds an elegant, ready-to-send WhatsApp commercial flash offer message.
    """
    sku = product.get("cod_art", "")
    desc = product.get("descrizione_articolo", "")
    um = product.get("um", "Kg")
    imballo = product.get("unita_imballi", "")
    cons = product.get("ambiente_cons", "")
    
    greeting = f"Ciao *{customer_name.strip()}*," if customer_name.strip() else "Gentile Cliente,"
    
    # Style badges
    style_badge = "🔥 *OPPORTUNITÀ DEL GIORNO*"
    if "Esclusiva" in offer_style:
        style_badge = "⭐ *OFFERTA RISERVATA IN ESCLUSIVA*"
    elif "Chef" in offer_style:
        style_badge = "👨‍🍳 *CONSIGLIO SPECIALE DELLO CHEF*"
    elif "Promo" in offer_style:
        style_badge = "⚡ *PROMOZIONE FLASH A LISTINO*"
        
    pitch_text = custom_pitch.strip() if custom_pitch.strip() else generate_default_pitch_and_pairing(product)
    
    lines = [
        f"🇮🇹 *ITALIAN FOOD TRADING S.r.l.*",
        f"{style_badge}",
        f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        f"📦 *{desc}*",
        f"🔖 Codice Articolo: `{sku}`",
        f"🏷️ *Prezzo Offerto: € {offer_price:.2f} / {um}*",
    ]
    
    lines.append("")
    lines.append("✨ *PRESENTAZIONE & CONSIGLIO DI UTILIZZO:*")
    lines.append(pitch_text)
    lines.append("")
    lines.append("⚖️ _Disponibilità immediata a magazzino. Per ordini o per bloccare un lotto alla prossima consegna, rispondimi pure direttamente a questo messaggio!_")
    lines.append("")
    lines.append(f"A disposizione,\n*{agent_name}*\nItalian Food Trading S.r.l. (Verona)")
    
    return "\n".join(lines)

def get_flash_offer_url(message: str, phone: str = "") -> str:
    """Encodes message and returns a direct api.whatsapp.com URL preserving UTF-8 emojis without 302 redirect corruption."""
    encoded = urllib.parse.quote(message)
    clean_phone = "".join(filter(str.isdigit, phone))
    if clean_phone:
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded}"
    return f"https://api.whatsapp.com/send?text={encoded}"
