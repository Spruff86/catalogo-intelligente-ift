import io
import os
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
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
        self.line(35, 40, A4[0] - 35, 40)
        
        # Footer text
        footer_left = "Italian Food Trading S.r.l. — Proposta Commerciale & Listino Offerta"
        footer_right = f"Pagina {self._pageNumber} di {page_count}"
        
        self.drawString(35, 26, footer_left)
        self.drawRightString(A4[0] - 35, 26, footer_right)
        self.restoreState()


def generate_quote_pdf(
    quote_data: Dict[str, Any],
    logo_path: Optional[str] = None
) -> bytes:
    """
    Generates a professional corporate PDF quotation using ReportLab without quote totals.
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
    
    # Custom Palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy
    c_secondary = colors.HexColor("#D97706")  # Gold/Amber
    c_dark = colors.HexColor("#1E293B")       # Dark Slate
    c_muted = colors.HexColor("#64748B")      # Slate Muted
    c_bg_light = colors.HexColor("#F8FAFC")   # Light Gray
    c_border = colors.HexColor("#E2E8F0")     # Light Border
    
    # Custom Typography Styles
    style_title = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary
    )
    
    style_company = ParagraphStyle(
        'CompanyInfo',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark,
        alignment=2 # Right aligned
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
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor("#047857"),
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
        leading=11.5,
        textColor=c_dark
    )
    
    elements = []
    
    # -------------------------------------------------------------
    # 1. HEADER SECTION (Logo on Left, Company Data on Right)
    # -------------------------------------------------------------
    logo_element = None
    if logo_path and os.path.exists(logo_path):
        try:
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
        colWidths=[6.5*cm, 12.5*cm]
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=c_primary, spaceBefore=2, spaceAfter=10))
    
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
        colWidths=[10.0*cm, 9.0*cm]
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
    elements.append(Spacer(1, 12))
    
    # -------------------------------------------------------------
    # 3. PRODUCTS TABLE (WITHOUT TOTAL COLUMN)
    # -------------------------------------------------------------
    items = quote_data.get("items", [])
    
    table_data = [
        [
            Paragraph("#", style_th_center),
            Paragraph("Codice SKU", style_th),
            Paragraph("Descrizione Articolo & Formato", style_th),
            Paragraph("U.M.", style_th_center),
            Paragraph("Q.tà Indicativa", style_th_center),
            Paragraph("Prezzo Offerto", style_th_right)
        ]
    ]
    
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
            
        desc_full = f"<b>{desc}</b>"
            
        table_data.append([
            Paragraph(str(idx), style_td_center),
            Paragraph(f"<b>{sku}</b>", style_td_bold),
            Paragraph(desc_full, style_td),
            Paragraph(um, style_td_center),
            Paragraph(f"{qty:g}", style_td_center),
            Paragraph(f"€ {price:.2f} / {um}", style_td_right)
        ])
        
    # Table column widths (Sum = 19.0 cm)
    col_widths = [0.8*cm, 2.5*cm, 9.7*cm, 1.4*cm, 2.2*cm, 2.4*cm]
    
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
    
    for r in range(1, len(table_data)):
        if r % 2 == 0:
            t_style.append(('BACKGROUND', (0, r), (-1, r), c_bg_light))
            
    prod_table.setStyle(TableStyle(t_style))
    elements.append(prod_table)
    elements.append(Spacer(1, 14))
    
    # -------------------------------------------------------------
    # 4. NOTES & TERMS OF SUPPLY (WEIGHT-BASED NOTICE)
    # -------------------------------------------------------------
    notes_text = quote_data.get("notes", "Resa franco destino. Pagamento come da accordi commerciali. Merce soggetta a disponibilità.")
    
    notes_box_html = f"""
    <b>NOTE E CONDIZIONI DI FORNITURA:</b><br/>
    {notes_text}<br/><br/>
    <font color='#475569' size='7.5'>
    • <b>Prezzi Unitari Netti:</b> I prezzi indicati sono al netto di IVA e franco destino per consegne conformi al minimo d'ordine.<br/>
    • <b>Prodotti a Peso Variabile:</b> Trattandosi di un preventivo indicativo per prodotti alimentari Ho.Re.Ca (salumi, formaggi, carni e ittico), la fatturazione finale avverrà in base al <b>peso effettivo riscontrato al momento della consegna</b>.<br/>
    • <b>Validità:</b> Offerta valida fino alla data indicata, salvo esaurimento scorte e variazioni straordinarie di listino.
    </font>
    """
    notes_p = Paragraph(notes_box_html, style_notes)
    
    notes_table = Table([[notes_p]], colWidths=[19.0*cm])
    notes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_bg_light),
        ('BOX', (0, 0), (-1, -1), 1, c_secondary),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    elements.append(KeepTogether([
        notes_table,
        Spacer(1, 18),
        # Signatures
        Table(
            [
                [
                    Paragraph("<b>Firma per Italian Food Trading S.r.l.</b><br/><br/>_________________________________", style_notes),
                    Paragraph("<b>Timbro e Firma per Accettazione Cliente</b><br/><br/>_________________________________", style_notes)
                ]
            ],
            colWidths=[9.5*cm, 9.5*cm]
        )
    ]))
    
    # Build Document with dynamic footer
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_whatsapp_message(quote_data: Dict[str, Any]) -> str:
    """
    Generates a cleanly formatted WhatsApp message without absolute quote totals.
    """
    customer = quote_data.get("customer", {})
    doc_number = quote_data.get("doc_number", f"PREV-{datetime.now().strftime('%Y%m%d')}")
    items = quote_data.get("items", [])
    
    cust_name = customer.get("name", "Gentile Cliente")
    agent = quote_data.get("agent_name", "Italian Food Trading")
    
    lines = [
        f"🇮🇹 *ITALIAN FOOD TRADING S.r.l.*",
        f"📋 *PROPOSTA COMMERCIALE N° {doc_number}*",
        f"👤 Destinatario: *{cust_name}*",
        f"👨‍💼 Agente: *{agent}*",
        f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}",
        "",
        "🛒 *LISTINO ARTICOLI IN OFFERTA:*"
    ]
    
    for idx, item in enumerate(items, 1):
        sku = item.get("cod_art", "")
        desc = item.get("descrizione_articolo", "")
        um = item.get("um", "Kg")
        
        try:
            qty = float(item.get("quantita", 1))
            price = float(item.get("prezzo_unitario", 0))
        except (ValueError, TypeError):
            qty, price = 1.0, 0.0
            
        lines.append(f"{idx}. `{sku}` — *{desc}*")
        lines.append(f"   ▫️ Prezzo Offerto: *€ {price:.2f} / {um}* (Q.tà indicativa: {qty:g} {um})")
        
    lines.append("")
    lines.append("⚖️ _Nota: Per i prodotti a peso variabile, la fatturazione avverrà in base al peso effettivo alla consegna._")
    
    notes = quote_data.get("notes")
    if notes:
        lines.append("")
        lines.append(f"📝 Note: _{notes}_")
        
    lines.append("")
    lines.append("Grazie per aver scelto Italian Food Trading S.r.l. (Verona)!")
    
    return "\n".join(lines)


def get_whatsapp_url(quote_data: Dict[str, Any], phone_number: str = "") -> str:
    """Generates a direct api.whatsapp.com click-to-chat URL preserving UTF-8 emojis."""
    msg = generate_whatsapp_message(quote_data)
    encoded = urllib.parse.quote(msg)
    clean_phone = "".join(filter(str.isdigit, phone_number))
    if clean_phone:
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded}"
    return f"https://api.whatsapp.com/send?text={encoded}"
