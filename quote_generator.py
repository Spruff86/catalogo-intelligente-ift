import io
import os
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas supporting two-pass total page count rendering in footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Footer line
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 40, A4[0] - 40, 40)
        
        # Footer text
        footer_left = "Italian Food Trading S.r.l. — Offerta Commerciale Riservata"
        footer_right = f"Pagina {self._pageNumber} di {page_count}"
        
        self.drawString(40, 26, footer_left)
        self.drawRightString(A4[0] - 40, 26, footer_right)
        self.restoreState()


def generate_quote_pdf(
    quote_data: Dict[str, Any],
    logo_path: Optional[str] = None
) -> bytes:
    """
    Generates a professional corporate PDF quotation using ReportLab.
    Returns the generated PDF as raw bytes.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=35,
        bottomMargin=55
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy
    c_secondary = colors.HexColor("#D97706")  # Gold/Amber
    c_accent = colors.HexColor("#059669")     # Emerald Green
    c_dark = colors.HexColor("#1E293B")       # Dark Slate
    c_muted = colors.HexColor("#64748B")      # Slate Muted
    c_bg_light = colors.HexColor("#F8FAFC")   # Light Gray
    c_border = colors.HexColor("#E2E8F0")     # Light Border
    
    # Custom Typography Styles
    style_title = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary
    )
    
    style_company = ParagraphStyle(
        'CompanyInfo',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
        alignment=2 # Right aligned
    )
    
    style_customer_title = ParagraphStyle(
        'CustomerBoxTitle',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=c_primary
    )
    
    style_customer_text = ParagraphStyle(
        'CustomerBoxText',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark
    )
    
    style_th = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    )
    
    style_th_right = ParagraphStyle(
        'TableHeaderRight',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=2
    )
    
    style_th_center = ParagraphStyle(
        'TableHeaderCenter',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    
    style_td = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_dark
    )
    
    style_td_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=c_primary
    )
    
    style_td_right = ParagraphStyle(
        'TableCellRight',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_dark,
        alignment=2
    )
    
    style_td_center = ParagraphStyle(
        'TableCellCenter',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_dark,
        alignment=1
    )
    
    style_notes = ParagraphStyle(
        'NotesStyle',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_muted
    )
    
    elements = []
    
    # -------------------------------------------------------------
    # 1. HEADER SECTION (Logo on Left, Company Data on Right)
    # -------------------------------------------------------------
    logo_element = None
    if logo_path and os.path.exists(logo_path):
        try:
            # Scaled to appropriate width/height maintaining aspect ratio
            logo_element = Image(logo_path, width=4.5*cm, height=2.8*cm)
        except Exception:
            logo_element = Paragraph("<b>ITALIAN FOOD TRADING</b>", style_title)
    else:
        logo_element = Paragraph("<b>ITALIAN FOOD TRADING</b>", style_title)
        
    company_text = """
    <b>ITALIAN FOOD TRADING S.R.L.</b><br/>
    Via dell'Artigianato 29 • 37066 Caselle di Sommacampagna (VR)<br/>
    Tel. +39 045 8581452 • Email: ordini@italianfoodtrading.com<br/>
    P.IVA / C.F.: IT 03478920234 • Web: www.italianfoodtrading.com
    """
    company_p = Paragraph(company_text, style_company)
    
    header_table = Table(
        [[logo_element, company_p]],
        colWidths=[6.5*cm, 12.0*cm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=12))
    
    # -------------------------------------------------------------
    # 2. DOCUMENT TITLE & METADATA / CUSTOMER INFO BOX
    # -------------------------------------------------------------
    customer = quote_data.get("customer", {})
    doc_number = quote_data.get("doc_number", f"PREV-{datetime.now().strftime('%Y%m%d-%H%M')}")
    doc_date = quote_data.get("doc_date", datetime.now().strftime("%d/%m/%Y"))
    validity = quote_data.get("validity", "30 giorni")
    agent_name = quote_data.get("agent_name", "Forza Vendita IFT")
    
    customer_html = f"""
    <b>DESTINATARIO / CLIENTE:</b><br/>
    <b>Ragione Sociale:</b> {customer.get('name', 'Gentile Cliente')}<br/>
    <b>Referente / Locale:</b> {customer.get('contact', 'N/D')}<br/>
    <b>Città / Indirizzo:</b> {customer.get('address', 'N/D')}<br/>
    <b>Telefono / Email:</b> {customer.get('phone_email', 'N/D')}
    """
    
    doc_details_html = f"""
    <b>DETTAGLI PREVENTIVO:</b><br/>
    <b>N° Preventivo:</b> <font color="#0F172A"><b>{doc_number}</b></font><br/>
    <b>Data Emissione:</b> {doc_date}<br/>
    <b>Validità Offerta:</b> {validity}<br/>
    <b>Agente di Riferimento:</b> {agent_name}
    """
    
    box_p_cust = Paragraph(customer_html, style_customer_text)
    box_p_doc = Paragraph(doc_details_html, style_customer_text)
    
    info_table = Table(
        [[box_p_cust, box_p_doc]],
        colWidths=[9.5*cm, 9.0*cm]
    )
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 14))
    
    # -------------------------------------------------------------
    # 3. PRODUCTS TABLE
    # -------------------------------------------------------------
    items = quote_data.get("items", [])
    
    table_data = [
        [
            Paragraph("#", style_th_center),
            Paragraph("Codice SKU", style_th),
            Paragraph("Descrizione Articolo & Formato", style_th),
            Paragraph("U.M.", style_th_center),
            Paragraph("Quantità", style_th_center),
            Paragraph("Prezzo Unit.", style_th_right),
            Paragraph("Totale Riga", style_th_right)
        ]
    ]
    
    total_net = 0.0
    for idx, item in enumerate(items, 1):
        sku = item.get("cod_art", "")
        desc = item.get("descrizione_articolo", "")
        um = item.get("um", "Kg")
        packaging = item.get("unita_imballi", "")
        
        try:
            qty = float(item.get("quantita", 1))
        except (ValueError, TypeError):
            qty = 1.0
            
        try:
            price = float(item.get("prezzo_unitario", 0))
        except (ValueError, TypeError):
            price = 0.0
            
        row_total = qty * price
        total_net += row_total
        
        desc_full = f"<b>{desc}</b>"
        if packaging:
            desc_full += f"<br/><font color='#64748B' size='7.5'><i>{packaging}</i></font>"
            
        table_data.append([
            Paragraph(str(idx), style_td_center),
            Paragraph(f"<b>{sku}</b>", style_td_bold),
            Paragraph(desc_full, style_td),
            Paragraph(um, style_td_center),
            Paragraph(f"{qty:g}", style_td_center),
            Paragraph(f"€ {price:.2f}", style_td_right),
            Paragraph(f"<b>€ {row_total:.2f}</b>", style_td_right)
        ])
        
    # Table column widths (Sum = 18.5 cm)
    col_widths = [0.8*cm, 2.4*cm, 8.5*cm, 1.2*cm, 1.6*cm, 2.0*cm, 2.0*cm]
    
    prod_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    t_style = [
        ('BACKGROUND', (0, 0), (-1, 0), c_dark),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
    ]
    
    # Alternate row colors
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), c_bg_light))
            
    prod_table.setStyle(TableStyle(t_style))
    elements.append(prod_table)
    elements.append(Spacer(1, 12))
    
    # -------------------------------------------------------------
    # 4. TOTALS & SUMMARY SECTION
    # -------------------------------------------------------------
    iva_rate = quote_data.get("iva_rate", 10.0) # Standard food VAT 10%
    try:
        iva_rate = float(iva_rate)
    except (ValueError, TypeError):
        iva_rate = 10.0
        
    iva_amount = total_net * (iva_rate / 100.0)
    total_gross = total_net + iva_amount
    
    notes_text = quote_data.get("notes", "Merce soggetta a disponibilità di magazzino. Resa franco destino per ordini conformi al minimo d'ordine. Pagamento come da accordi commerciali.")
    
    notes_p = Paragraph(f"""
    <b>NOTE E CONDIZIONI DI FORNITURA:</b><br/>
    {notes_text}<br/><br/>
    <font color='#64748B' size='7'>I prezzi indicati sono al netto di eventuali promozioni attive non cumulabili e salvo variazioni di listino.</font>
    """, style_notes)
    
    totals_data = [
        [Paragraph("Totale Imponibile:", style_td_bold), Paragraph(f"€ {total_net:.2f}", style_td_right)],
        [Paragraph(f"IVA ({iva_rate:g}%):", style_td), Paragraph(f"€ {iva_amount:.2f}", style_td_right)],
        [Paragraph("<b>TOTALE OFFERTA:</b>", style_title), Paragraph(f"<b><font size='13' color='#0F172A'>€ {total_gross:.2f}</font></b>", style_td_right)]
    ]
    
    totals_table = Table(totals_data, colWidths=[4.2*cm, 3.8*cm])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_secondary),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, c_border),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    summary_block = Table(
        [[notes_p, totals_table]],
        colWidths=[10.2*cm, 8.3*cm]
    )
    summary_block.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    elements.append(KeepTogether([
        summary_block,
        Spacer(1, 16),
        # Signature block
        Table(
            [
                [
                    Paragraph("<b>Firma per Italian Food Trading S.r.l.</b><br/><br/>_________________________________", style_notes),
                    Paragraph("<b>Timbro e Firma per Accettazione Cliente</b><br/><br/>_________________________________", style_notes)
                ]
            ],
            colWidths=[9.25*cm, 9.25*cm]
        )
    ]))
    
    # Build Document with dynamic footer
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_whatsapp_message(quote_data: Dict[str, Any]) -> str:
    """
    Generates a cleanly formatted WhatsApp message ready to be shared.
    """
    customer = quote_data.get("customer", {})
    doc_number = quote_data.get("doc_number", f"PREV-{datetime.now().strftime('%Y%m%d')}")
    items = quote_data.get("items", [])
    
    cust_name = customer.get("name", "Gentile Cliente")
    agent = quote_data.get("agent_name", "Italian Food Trading")
    
    lines = [
        f"🇮🇹 *ITALIAN FOOD TRADING S.r.l.*",
        f"📋 *PREVENTIVO COMMERCIALE N° {doc_number}*",
        f"👤 Destinatario: *{cust_name}*",
        f"👨‍💼 Agente: *{agent}*",
        f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "🛒 *ARTICOLI SELEZIONATI:*"
    ]
    
    total_net = 0.0
    for idx, item in enumerate(items, 1):
        sku = item.get("cod_art", "")
        desc = item.get("descrizione_articolo", "")
        um = item.get("um", "Kg")
        
        try:
            qty = float(item.get("quantita", 1))
            price = float(item.get("prezzo_unitario", 0))
        except (ValueError, TypeError):
            qty, price = 1.0, 0.0
            
        row_tot = qty * price
        total_net += row_tot
        
        lines.append(f"{idx}. `{sku}` — *{desc}*")
        lines.append(f"   ▫️ Q.tà: *{qty:g} {um}* × € {price:.2f} = *€ {row_tot:.2f}*")
        
    iva_rate = float(quote_data.get("iva_rate", 10.0))
    iva_val = total_net * (iva_rate / 100.0)
    total_gross = total_net + iva_val
    
    lines.append("")
    lines.append(f"💰 *Totale Imponibile:* € {total_net:.2f}")
    lines.append(f"🧾 *IVA ({iva_rate:g}%):* € {iva_val:.2f}")
    lines.append(f"✨ *TOTALE PREVENTIVO:* *€ {total_gross:.2f}*")
    
    notes = quote_data.get("notes")
    if notes:
        lines.append("")
        lines.append(f"📝 Note: _{notes}_")
        
    lines.append("")
    lines.append("Grazie per aver scelto Italian Food Trading S.r.l. (Verona)!")
    
    return "\n".join(lines)


def get_whatsapp_url(quote_data: Dict[str, Any], phone_number: str = "") -> str:
    """Generates a wa.me click-to-chat URL with the encoded quote text."""
    msg = generate_whatsapp_message(quote_data)
    encoded = urllib.parse.quote(msg)
    clean_phone = "".join(filter(str.isdigit, phone_number))
    if clean_phone:
        return f"https://wa.me/{clean_phone}?text={encoded}"
    return f"https://wa.me/?text={encoded}"
