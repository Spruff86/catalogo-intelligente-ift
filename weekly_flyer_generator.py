import io
import os
import re
import urllib.parse
from typing import List, Dict, Any, Optional
from pathlib import Path
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime, timedelta
import config

def escape_xml(text: Any) -> str:
    """Safely cleans and escapes text for ReportLab XML Paragraphs."""
    if text is None:
        return ""
    s = str(text)
    # Clean openpyxl/Excel artifacts like _x0007_
    s = re.sub(r'_x[0-9a-fA-F]{4}_', ' ', s)
    # Escape XML entities
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
    return s.strip()

def generate_weekly_flyer_pdf(
    slots: List[Dict[str, Any]],
    logo_path: Optional[str] = None,
    validity_dates: Optional[str] = None
) -> bytes:
    """
    Generates a professional 1-page A4 vertical (portrait) PDF flyer
    containing a 2x3 grid of 6 promotional products for Ho.Re.Ca professionals.
    
    Guaranteed to fit strictly on a single A4 page.
    """
    buffer = io.BytesIO()
    
    # A4 Portrait: 595.28 x 841.89 pt
    # Margins: left=24, right=24 -> printable width = 547.28 pt
    # Margins: top=20, bottom=18 -> printable height = 803.89 pt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=24,
        rightMargin=24,
        topMargin=20,
        bottomMargin=18
    )
    
    # Typography Styles
    style_title = ParagraphStyle(
        'FlyerTitle',
        fontName='Helvetica-Bold',
        fontSize=16.5,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        alignment=1
    )
    style_sub = ParagraphStyle(
        'FlyerSub',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#D97706'), # Warm Amber/Gold
        alignment=1
    )
    style_note = ParagraphStyle(
        'FlyerNote',
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#64748B'),
        alignment=1
    )
    style_sku = ParagraphStyle(
        'CardSku',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor('#D97706')
    )
    style_name = ParagraphStyle(
        'CardName',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor('#0F172A')
    )
    style_desc = ParagraphStyle(
        'CardDesc',
        fontName='Helvetica',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor('#475569')
    )
    style_price = ParagraphStyle(
        'CardPrice',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.white,
        alignment=1
    )
    style_placeholder = ParagraphStyle(
        'CardPlaceholder',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1
    )

    elements = []

    # 1. Header Section
    logo_element = None
    if logo_path and os.path.exists(logo_path):
        try:
            with PILImage.open(logo_path) as lim:
                lw, lh = lim.size
            max_lw, max_lh = 110, 36
            l_ratio = min(max_lw / lw, max_lh / lh)
            logo_element = RLImage(logo_path, width=lw * l_ratio, height=lh * l_ratio)
        except Exception:
            logo_element = None

    if not logo_element:
        logo_element = Paragraph(
            '<b><font color="#0F172A" size="11">ITALIAN FOOD</font><br/><font color="#D97706" size="10">TRADING</font></b>',
            style_title
        )

    if not validity_dates:
        today = datetime.now().date()
        m = today - timedelta(days=today.weekday())
        s = m + timedelta(days=5)
        mesi_it = {
            1: 'GENNAIO', 2: 'FEBBRAIO', 3: 'MARZO', 4: 'APRILE', 5: 'MAGGIO', 6: 'GIUGNO',
            7: 'LUGLIO', 8: 'AGOSTO', 9: 'SETTEMBRE', 10: 'OTTOBRE', 11: 'NOVEMBRE', 12: 'DICEMBRE'
        }
        if m.month == s.month and m.year == s.year:
            validity_dates = f"DA LUNEDÌ {m.day} A SABATO {s.day} {mesi_it[s.month]} {s.year}"
        elif m.year == s.year:
            validity_dates = f"DA LUNEDÌ {m.day} {mesi_it[m.month]} A SABATO {s.day} {mesi_it[s.month]} {s.year}"
        else:
            validity_dates = f"DA LUNEDÌ {m.day} {mesi_it[m.month]} {m.year} A SABATO {s.day} {mesi_it[s.month]} {s.year}"

    header_text = [
        Paragraph('<b>OFFERTE LAMPO DELLA SETTIMANA</b>', style_title),
        Spacer(1, 2),
        Paragraph(f'<b>VALIDITÀ: {escape_xml(validity_dates)}</b>', style_sub),
        Spacer(1, 2),
        Paragraph('Prezzi netti riservati Ho.Re.Ca • Salvo esaurimento scorte • Ordini al tuo agente', style_note)
    ]

    header_table = Table([[logo_element, header_text]], colWidths=[115, 432])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))

    # Divider bar
    div_table = Table([['']], colWidths=[547], rowHeights=[2])
    div_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#D97706')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(div_table)
    elements.append(Spacer(1, 6))

    # 2. Product Card Builder
    def build_card(slot: Optional[Dict[str, Any]], w: float = 266, h: float = 224) -> Table:
        # Check if slot has a valid product
        if not slot or not slot.get('cod_art'):
            # Empty placeholder slot
            ph_content = [
                Spacer(1, 80),
                Paragraph('<b>PROMOZIONE SETTIMANALE</b>', style_sub),
                Spacer(1, 4),
                Paragraph('Spazio disponibile per nuova offerta lampo', style_placeholder),
                Spacer(1, 80)
            ]
            ph_table = Table([[ph_content]], colWidths=[w], rowHeights=[h])
            ph_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
            ]))
            return ph_table

        sku = escape_xml(slot.get('cod_art', ''))
        raw_name = slot.get('descrizione_articolo', '') or ''
        # Truncate title cleanly to avoid 3-line overflow
        if len(raw_name) > 65:
            raw_name = raw_name[:62].strip() + '...'
        name = escape_xml(raw_name)

        um = escape_xml(slot.get('um', 'Kg') or 'Kg')

        # Price formatting
        raw_p = slot.get('prezzo', 0)
        try:
            p_val = float(str(raw_p).replace('€', '').replace(',', '.').strip())
            price_str = f"€ {p_val:.2f}"
        except (ValueError, TypeError):
            price_str = f"€ {escape_xml(raw_p)}"

        # Short commercial description
        raw_desc = slot.get('descrizione_commerciale', '') or ''
        clean_d = re.sub(r'_x[0-9a-fA-F]{4}_', ' ', raw_desc).strip()
        if not clean_d:
            clean_d = "Referenza premium selezionata per la ristorazione professionale."
        if len(clean_d) > 105:
            clean_d = clean_d[:102].strip() + '...'
        clean_desc_xml = escape_xml(clean_d)

        # Image processing
        foto_path = slot.get('foto_path', '')
        if not (foto_path and os.path.exists(foto_path)) and slot.get('cod_art') and hasattr(config, 'FOTO_DIR') and config.FOTO_DIR.exists():
            sku_raw = str(slot.get('cod_art', '')).strip().upper()
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.PNG']:
                cand = config.FOTO_DIR / f"{sku_raw}{ext}"
                if cand.exists():
                    foto_path = str(cand)
                    break

        img_element = None
        if foto_path and os.path.exists(foto_path):
            try:
                with PILImage.open(foto_path) as im:
                    iw, ih = im.size
                max_w, max_h = 246, 100
                ratio = min(max_w / iw, max_h / ih)
                img_element = RLImage(foto_path, width=iw * ratio, height=ih * ratio)
            except Exception:
                img_element = None

        if not img_element:
            img_element = Paragraph('<font color="#94A3B8"><i>Foto da catalogo</i></font>', style_placeholder)

        img_table = Table([[img_element]], colWidths=[246], rowHeights=[102])
        img_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Price banner
        price_p = Paragraph(
            f'<font color="#F59E0B"><b>OFFERTA:</b></font> <font color="#FFFFFF" size="11.5"><b>{price_str}</b></font> <font color="#CBD5E1" size="7.5">/ {um}</font>',
            style_price
        )
        price_table = Table([[price_p]], colWidths=[246], rowHeights=[26])
        price_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0F172A')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Card inner table
        card_inner = Table([
            [img_table],
            [Paragraph(f'<b>CODICE ART. {sku}</b>', style_sku)],
            [Paragraph(f'<b>{name}</b>', style_name)],
            [Paragraph(clean_desc_xml, style_desc)],
            [price_table]
        ], colWidths=[246], rowHeights=[102, 13, 26, 24, 26])

        card_inner.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        card_outer = Table([[card_inner]], colWidths=[w], rowHeights=[h])
        card_outer.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        return card_outer

    # Pad or slice slots to ensure exactly 6 slots
    normalized_slots = list(slots)[:6]
    while len(normalized_slots) < 6:
        normalized_slots.append(None)

    # 3. 2x3 Grid Table
    grid_rows = []
    for row_idx in range(3):
        slot_left = normalized_slots[row_idx * 2]
        slot_right = normalized_slots[row_idx * 2 + 1]
        c1 = build_card(slot_left, w=266, h=224)
        c2 = build_card(slot_right, w=266, h=224)
        grid_rows.append([c1, '', c2])

    grid_table = Table(grid_rows, colWidths=[266, 15, 266], rowHeights=[224, 224, 224])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(grid_table)
    elements.append(Spacer(1, 5))

    # 4. Footer
    footer_p = Paragraph(
        'Italian Food Trading S.r.l. — Via Sommacampagna 63/E, 37137 Verona (VR) • Tel. 045 8622115 • Prezzi netti, IVA esclusa • Salvo esaurimento scorte',
        style_note
    )
    elements.append(footer_p)

    # Build document
    doc.build(elements)
    return buffer.getvalue()


def generate_flyer_whatsapp_message(
    slots: List[Dict[str, Any]],
    validity_dates: str,
    client_name: str = ""
) -> str:
    """
    Generates an engaging, professional promotional WhatsApp message
    listing the weekly flyer offer items with emojis, SKU, prices and descriptions.
    """
    lines = [
        "🇮🇹 *ITALIAN FOOD TRADING S.r.l.*",
        "⚡ *OFFERTE LAMPO DELLA SETTIMANA*",
        f"📅 *Validità:* {validity_dates.strip()}"
    ]
    if client_name and client_name.strip():
        lines.append(f"👤 Destinatario: *{client_name.strip()}*")

    lines.append("")
    lines.append("Gentile Chef, ti segnaliamo le opportunità esclusive selezionate per questa settimana:")
    lines.append("")

    active_items = [s for s in slots if s and s.get("cod_art")]
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

    for idx, item in enumerate(active_items):
        num_emoji = number_emojis[idx] if idx < len(number_emojis) else f"{idx+1}."
        sku = item.get("cod_art", "")
        name = item.get("descrizione_articolo", "").strip()
        um = item.get("um", "Kg") or "Kg"
        raw_p = item.get("prezzo", 0)
        try:
            p_val = float(str(raw_p).replace('€', '').replace(',', '.').strip())
            price_str = f"€ {p_val:.2f}"
        except (ValueError, TypeError):
            price_str = f"€ {raw_p}"

        desc = (item.get("descrizione_commerciale", "") or "").strip()
        # Clean Excel artifacts
        desc = re.sub(r'_x[0-9a-fA-F]{4}_', ' ', desc).strip()

        lines.append(f"{num_emoji} *{name}*")
        lines.append(f"   🔖 Cod. Art.: `{sku}`")
        lines.append(f"   🏷️ Prezzo Offerta: *{price_str} / {um}*")
        if desc:
            lines.append(f"   📝 _{desc}_")
        lines.append("")

    lines.append("⚖️ _Prezzi netti riservati Ho.Re.Ca • Salvo esaurimento scorte._")
    lines.append("📞 Rispondi direttamente a questo messaggio per bloccare subito la fornitura!")
    lines.append("📎 _In allegato trovi il volantino grafico ufficiale in formato PDF._")

    return "\n".join(lines)


def get_flyer_whatsapp_url(message: str, phone_number: str = "") -> str:
    """
    Generates a direct api.whatsapp.com click-to-chat URL preserving UTF-8 emojis.
    """
    encoded = urllib.parse.quote(message)
    clean_phone = "".join(filter(str.isdigit, phone_number))
    if clean_phone:
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded}"
    return f"https://api.whatsapp.com/send?text={encoded}"

