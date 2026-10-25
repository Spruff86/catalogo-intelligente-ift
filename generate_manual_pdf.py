#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore Manuale Operativo Ufficiale Catalogo Intelligente IFT con Screenshot
Italian Food Trading S.r.l. - Verona
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Canvas per numerazione pagine a due passaggi e intestazione/piè di pagina continuo."""
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Pagine successive alla copertina)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(35, A4[1] - 22, "ITALIAN FOOD TRADING S.R.L.  |  MANUALE OPERATIVO CATALOGO INTELLIGENTE")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawRightString(A4[0] - 35, A4[1] - 22, "Guida Illustrata Agenti Ho.Re.Ca")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(35, A4[1] - 26, A4[0] - 35, A4[1] - 26)

        # Footer (Tutte le pagine)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(35, 26, A4[0] - 35, 26)
        
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(35, 16, "Documento Riservato ad Uso Interno della Rete Commerciale Italian Food Trading S.r.l.")
        page_text = f"Pagina {self._pageNumber} di {page_count}"
        self.drawRightString(A4[0] - 35, 16, page_text)
            
        self.restoreState()

def create_manual(output_path="Manuale_Catalogo_Intelligente_IFT.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=32,
        bottomMargin=32
    )
    
    # Palette Aziendale IFT
    c_blue = colors.HexColor("#1E3A8A")       # Royal Navy IFT
    c_accent = colors.HexColor("#D97706")     # Oro / Ambra
    c_dark = colors.HexColor("#1E293B")       # Slate Scuro
    c_muted = colors.HexColor("#475569")      # Grigio Medio
    c_border = colors.HexColor("#E2E8F0")     # Bordo Chiaro

    styles = getSampleStyleSheet()
    
    s_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_blue,
        alignment=0
    )
    
    s_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_muted,
        alignment=0
    )
    
    s_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=c_blue,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True
    )
    
    s_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_dark,
        spaceBefore=4,
        spaceAfter=2,
        keepWithNext=True
    )
    
    s_body = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=c_dark,
        spaceAfter=3
    )
    
    s_body_bold = ParagraphStyle(
        'BodyBold_Custom',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11.5,
        textColor=c_dark,
        spaceAfter=2
    )
    
    s_bullet = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=c_dark,
        leftIndent=8,
        spaceAfter=2
    )

    s_box_text = ParagraphStyle(
        'BoxText',
        fontName='Helvetica',
        fontSize=7.8,
        leading=11,
        textColor=c_dark
    )

    s_caption = ParagraphStyle(
        'Caption',
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=c_muted,
        alignment=1, # Centered
        spaceAfter=4
    )

    story = []
    
    def add_screenshot(img_path, width_cm=14.0, height_cm=9.33, caption=""):
        if os.path.exists(img_path):
            img = Image(img_path, width=width_cm*cm, height=height_cm*cm)
            img.hAlign = 'CENTER'
            story.append(img)
            if caption:
                story.append(Spacer(1, 2))
                story.append(Paragraph(caption, s_caption))
            story.append(Spacer(1, 4))
    
    # =========================================================================
    # PAGINA 1: COPERTINA & PANORAMICA DEL CATALOGO
    # =========================================================================
    logo_path = "ift_logo.png" if os.path.exists("ift_logo.png") else None
    if logo_path:
        logo_img = Image(logo_path, width=4.2*cm, height=1.9*cm)
        logo_img.hAlign = 'LEFT'
        info_p = Paragraph(
            "<b>ITALIAN FOOD TRADING S.R.L.</b><br/>"
            "Via dell'Artigianato, 12 — Verona (VR)<br/>"
            "Distribuzione Alimentare per Ristoranti e Pizzerie Gourmet<br/>"
            "<font color='#1E3A8A'><b>www.italianfoodtrading.it</b></font>",
            ParagraphStyle('HInfo', fontName='Helvetica', fontSize=7.5, leading=10, textColor=c_muted, alignment=2)
        )
        header_table = Table([[logo_img, info_p]], colWidths=[5.5*cm, 13.0*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=8))
    
    story.append(Paragraph("CATALOGO INTELLIGENTE & ASSISTENTE AI", s_cover_title))
    story.append(Paragraph("<b>Manuale Operativo Illustrato per la Forza Vendita e Clienti IFT</b> — <i>Edizione 2026</i>", s_cover_subtitle))
    story.append(Spacer(1, 6))
    
    summary_html = (
        "<b>LA TUA CENTRALE COMMERCIALE DIGITALE TASCABILE:</b><br/>"
        "Il Catalogo Intelligente IFT riunisce in un'unica applicazione per tablet e smartphone oltre <b>2.003 referenze ufficiali</b> "
        "con foto HD, schede tecniche HACCP e <b>Prezzi Soglia Riservati</b> sempre aggiornati. "
        "In pochi tocchi puoi consultare il magazzino, ricevere consulenza tecnica dall'AI su impasti e abbinamenti, "
        "creare preventivi formali con firma, calcolare il Food Cost per gli chef e inviare offerte promozionali su WhatsApp."
    )
    box_table = Table([[Paragraph(summary_html, s_box_text)]], colWidths=[18.5*cm])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINELEFT', (0,0), (-1,-1), 4, c_blue),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 6))
    
    # Screenshot 1: Overview
    add_screenshot("screenshots/framed_01.jpg", width_cm=14.5, height_cm=8.5, 
                   caption="Figura 1: Schermata Principale del Catalogo con barra di ricerca, chip filtri e griglia prodotti con Prezzi Soglia.")
    
    # Tabella Moduli
    moduli_data = [
        [Paragraph("<b>Sezione</b>", s_body_bold), Paragraph("<b>Modulo</b>", s_body_bold), Paragraph("<b>Cosa ti permette di fare durante la visita</b>", s_body_bold)],
        [Paragraph("1", s_body), Paragraph("<b>📦 Catalogo</b>", s_body_bold), Paragraph("Ricerca rapida mirata per codice/nome, filtri allergeni e sottomenù operativo integrato.", s_body)],
        [Paragraph("2", s_body), Paragraph("<b>💬 Chat AI</b>", s_body_bold), Paragraph("Consulenza su forza farine (W), maturazioni, allergeni e abbinamenti culinari (Zero Allucinazioni).", s_body)],
        [Paragraph("3", s_body), Paragraph("<b>🛒 Preventivo</b>", s_body_bold), Paragraph("Proposte economiche personalizzate con esportazione PDF vettoriale con firma e testo WhatsApp.", s_body)],
        [Paragraph("4", s_body), Paragraph("<b>📊 Food Cost</b>", s_body_bold), Paragraph("Ingegneria del piatto: calcolo costo netto porzione, margini lordi e travaso ingredienti nel carrello.", s_body)],
        [Paragraph("5", s_body), Paragraph("<b>📲 Offerta WA</b>", s_body_bold), Paragraph("Pitch persuasivo generato dall'AI pronto per essere inviato al cliente in un click.", s_body)],
        [Paragraph("6", s_body), Paragraph("<b>📄 Volantino</b>", s_body_bold), Paragraph("Impaginazione automatica a 6 slot di offerte promozionali in formato grafico A4 stampabile.", s_body)],
    ]
    t_mod = Table(moduli_data, colWidths=[1.0*cm, 3.8*cm, 13.7*cm])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_mod)
    
    story.append(PageBreak())

    # =========================================================================
    # PAGINA 2: CATALOGO & IL NUOVO SOTTOMENÙ OPERATIVO
    # =========================================================================
    story.append(Paragraph("1. CATALOGO PRODOTTI & IL NUOVO SOTTOMENÙ RAPIDO", s_h1))
    story.append(Paragraph(
        "La scheda <b>📦 Catalogo</b> è stata ottimizzata per eliminare qualsiasi perdita di tempo. "
        "Non è più necessario scorrere fino a fondo pagina per visualizzare le opzioni: con un solo tocco su <b>`👁️ Dettaglio`</b> "
        "la card si espande istantaneamente mostrando il <b>Sottomenù Azioni Rapide</b>.",
        s_body
    ))
    
    # Screenshot 2: Sottomenu
    add_screenshot("screenshots/framed_02.jpg", width_cm=14.5, height_cm=8.5, 
                   caption="Figura 2: Sottomenù Azioni Rapide integrato direttamente sotto alla card del prodotto.")
    
    story.append(Paragraph("Funzionalità Chiave della Ricerca e della Card:", s_h2))
    story.append(Paragraph("• <b>Ricerca Esclusiva SKU / Nome:</b> Digitando una parola (es. <i>'burrata'</i>) o un codice (es. <i>'10203'</i>), il motore valuta esclusivamente il codice articolo o la denominazione, senza generare falsi positivi dalle descrizioni o dai testi HACCP.", s_bullet))
    story.append(Paragraph("• <b>Filtri Allergeni Rapidi:</b> I tasti rapidi <i>'🌾 Senza Glutine'</i> e <i>'🥛 Senza Lattosio'</i> effettuano una scansione mirata sulle dichiarazioni ufficiali delle schede tecniche del produttore.", s_bullet))
    story.append(Paragraph("• <b>Prezzo Soglia Garantito:</b> Il prezzo mostrato è il Prezzo Soglia riservato, proteggendo l'agente da errori di marginalità durante la trattativa.", s_bullet))
    
    actions_desc = [
        [Paragraph("<b>Pulsante</b>", s_body_bold), Paragraph("<b>Cosa Fa con un Singolo Click</b>", s_body_bold)],
        [Paragraph("<b>📲 Offerta WA</b>", s_body), Paragraph("Trasferisce articolo e prezzo nella scheda Offerta WhatsApp per generare il pitch commerciale.", s_body)],
        [Paragraph("<b>📊 Food Cost</b>", s_body), Paragraph("Aggiunge l'articolo come ingrediente nel Food Cost con conversione automatica del prezzo in g/ml.", s_body)],
        [Paragraph("<b>📄 Volantino</b>", s_body), Paragraph("Inserisce l'articolo nel primo slot disponibile del Volantino promozionale a 6 posizioni.", s_body)],
        [Paragraph("<b>🎯 Chiedi all'AI</b>", s_body), Paragraph("Collega il prodotto alla Chat AI per consultare la scheda tecnica ufficiale (valori W, allergeni, abbinamenti).", s_body)],
        [Paragraph("<b>📥 Scheda PDF</b>", s_body), Paragraph("Scarica o apre il documento ufficiale depositato del produttore con tabella nutrizionale completa.", s_body)],
        [Paragraph("<b>🛒 Preventivo</b>", s_body), Paragraph("Box per impostare quantità e prezzo personalizzato e aggiungerlo subito alla proposta commerciale.", s_body)],
        [Paragraph("<b>📋 Info Tecniche</b>", s_body), Paragraph("Menu a tendina con shelf-life, unità imballo, minimo d'ordine, giorni di consegna e testo HACCP.", s_body)],
    ]
    t_act = Table(actions_desc, colWidths=[3.5*cm, 15.0*cm])
    t_act.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_act)

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 3: STUDIO CONSULENZA & CHAT AI
    # =========================================================================
    story.append(Paragraph("2. CHAT STUDIO AI: CONSULENTE GASTRONOMICO TASCABILE", s_h1))
    story.append(Paragraph(
        "La scheda <b>💬 Chat AI</b> mette a disposizione un assistente specializzato per il settore Ho.Re.Ca basato su Google Gemini. "
        "È istruito tassativamente con la politica di <b>Zero-Allucinazioni</b>: non cita mai prodotti inventati o codici inesistenti, "
        "ma risponde unicamente sui dati ufficiali del nostro magazzino.",
        s_body
    ))
    
    # Screenshot 3: Chat AI
    add_screenshot("screenshots/framed_03.jpg", width_cm=14.5, height_cm=8.5, 
                   caption="Figura 3: Schermata Chat AI con banner di focus articolo e consulenza gastronomica tecnica in tempo reale.")
    
    story.append(Paragraph("Due Modalità di Utilizzo durante la Visita:", s_h2))
    
    ai_box = (
        "• <b>MODALITÀ FOCUS PRODOTTO (Target SKU):</b><br/>"
        "Quando clicchi su <i>'🎯 Chiedi all'AI'</i> da un articolo, l'assistente visualizza un banner blu di aggancio. "
        "Puoi porre domande tecniche approfondite, ad esempio:<br/>"
        "&nbsp;&nbsp;— <i>'Qual è la forza W, l'assorbimento e il tempo di maturazione consigliato per questa farina?'</i><br/>"
        "&nbsp;&nbsp;— <i>'Come posso proporre questa mozzarella fior di latte a un pizzaiolo che cuoce in forno a legna a 450°C?'</i><br/>"
        "&nbsp;&nbsp;— <i>'È certificato senza lattosio per clienti intolleranti?'</i><br/><br/>"
        "• <b>MODALITÀ CATALOGO GENERALE:</b><br/>"
        "Senza alcun prodotto agganciato, puoi formulare domande trasversali su tutto il listino IFT:<br/>"
        "&nbsp;&nbsp;— <i>'Quali 3 prosciutti cotti Alta Qualità abbiamo disponibili a catalogo?'</i><br/>"
        "&nbsp;&nbsp;— <i>'Consigliami una selezione di formaggi tipici veneti per un tagliere da aperitivo gourmet.'</i>"
    )
    story.append(Table([[Paragraph(ai_box, s_box_text)]], colWidths=[18.5*cm], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BBF7D0")),
        ('LINELEFT', (0,0), (-1,-1), 4, colors.HexColor("#16A34A")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 4: PREVENTIVI AZIENDALI IFT
    # =========================================================================
    story.append(Paragraph("3. PREVENTIVI AZIENDALI IFT: PDF UFFICIALE & WHATSAPP", s_h1))
    story.append(Paragraph(
        "Nella scheda <b>🛒 Preventivo</b> puoi completare una proposta commerciale in pochi secondi prima ancora di uscire dal locale del cliente, "
        "eliminando i tempi morti di rientro in ufficio.",
        s_body
    ))
    
    # Screenshot 4: Preventivo
    add_screenshot("screenshots/framed_04.jpg", width_cm=14.5, height_cm=8.5, 
                   caption="Figura 4: Modulo Preventivi con riepilogo articoli inseriti, totale calcolato e pulsanti di esportazione rapida.")
    
    story.append(Paragraph("Il Flusso Operativo in 4 Semplici Passaggi:", s_h2))
    story.append(Paragraph("1. <b>Aggiunta Rapida dal Catalogo:</b> Nel sottomenù di ogni prodotto imposti quantità e prezzo concordato, cliccando su <i>'➕ Aggiungi al Preventivo'</i>.", s_bullet))
    story.append(Paragraph("2. <b>Compilazione Anagrafica Cliente:</b> Inserisci Ragione Sociale, Referente, P.IVA, Indirizzo e note operative per la consegna (es. <i>'Consegna martedì entro le 10:30'</i>).", s_bullet))
    story.append(Paragraph("3. <b>Generazione PDF Vettoriale IFT:</b> Con un click su <i>'📄 Scarica Preventivo PDF'</i> viene creato all'istante il documento aziendale elegante con logo IFT a colori, tabella chiara e box firme per l'accettazione immediata.", s_bullet))
    story.append(Paragraph("4. <b>Invio WhatsApp Istantaneo:</b> Cliccando su <i>'📲 Invia su WhatsApp'</i> il sistema apre l'applicazione di messaggistica con il riepilogo completo di codici, quantità e prezzi pronto da inoltrare al titolare.", s_bullet))
    
    p_box = (
        "<b>SUGGERIMENTO COMMERCIALE PER L'AGENTE:</b><br/>"
        "Inviare il preventivo formattato su WhatsApp prima di risalire in auto aumenta del <b>40% il tasso di chiusura immediata</b>. "
        "Il cliente riceve subito le condizioni pattuite, con SKU chiari e prezzi trasparenti."
    )
    story.append(Table([[Paragraph(p_box, s_box_text)]], colWidths=[18.5*cm], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FFFBEB")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FDE68A")),
        ('LINELEFT', (0,0), (-1,-1), 4, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 5: FOOD COST CALCULATOR
    # =========================================================================
    story.append(Paragraph("4. FOOD COST CALCULATOR: INGEGNERIA DEL MENU E MARGINI", s_h1))
    story.append(Paragraph(
        "Il modulo <b>📊 Food Cost</b> è la tua leva strategica più potente con chef e pizzaioli: ti permette di spostare "
        "il confronto dal mero <i>prezzo al chilo</i> al <b>costo reale a porzione</b> e al <b>margine di profitto</b>.",
        s_body
    ))
    
    # Screenshot 5: Food Cost
    add_screenshot("screenshots/framed_05.jpg", width_cm=14.5, height_cm=8.5, 
                   caption="Figura 5: Calcolatore Food Cost con inserimento dosaggi in grammi/ml, calcolo marginalità e travaso lotti.")
    
    story.append(Paragraph("Come Guidare il Cliente nel Calcolo Economico:", s_h2))
    
    fc_table_data = [
        [Paragraph("<b>Parametro</b>", s_body_bold), Paragraph("<b>Significato Operativo & Formula</b>", s_body_bold)],
        [Paragraph("<b>Conversione U.M.</b>", s_body), Paragraph("I prodotti a listino in Kg o Litri vengono convertiti automaticamente in grammi (g) o millilitri (ml), calcolando il costo esatto al millesimo di euro.", s_body)],
        [Paragraph("<b>Food Cost Netto</b>", s_body), Paragraph("Somma millimetrica dei costi degli ingredienti usati nel singolo piatto (es. 80g fiordilatte + 100g pomodoro + 60g crudo = <b>€ 1,85</b>).", s_body)],
        [Paragraph("<b>Incidenza Target (%)</b>", s_body), Paragraph("Percentuale ideale di incidenza materie prime sul prezzo a menu (tipicamente 25%-30% per pizzerie e bistrot).", s_body)],
        [Paragraph("<b>Prezzo Raccomandato</b>", s_body), Paragraph("Prezzo di vendita a menu suggerito dal sistema per raggiungere la marginalità target (<i>Food Cost / Incidenza Target</i>).", s_body)],
        [Paragraph("<b>Margine Lordo</b>", s_body), Paragraph("Guadagno netto in cassa per ogni singola porzione venduta (<i>Prezzo Menu - Food Cost Netto</i>).", s_body)],
        [Paragraph("<b>Travaso nel Preventivo</b>", s_body), Paragraph("Impostando un lotto di produzione (es. 100 pizze o 50 coperti), il pulsante travasa il fabbisogno complessivo direttamente nel Preventivo!", s_body)],
    ]
    t_fc = Table(fc_table_data, colWidths=[4.2*cm, 14.3*cm])
    t_fc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_fc)

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 6: OFFERTE LAMPO WA, VOLANTINO A4 & SCENARI DI VENDITA
    # =========================================================================
    story.append(Paragraph("5. OFFERTE LAMPO WA & VOLANTINO PROMOZIONALE A4", s_h1))
    story.append(Paragraph(
        "Due strumenti grafici per promuovere arrivi speciali, lotti freschi di giornata o campagne tematiche settimanali.",
        s_body
    ))
    
    # Due screenshot affiancati in tabella
    img_wa = Image("screenshots/framed_06.jpg", width=8.8*cm, height=5.8*cm)
    img_flyer = Image("screenshots/framed_07.jpg", width=8.8*cm, height=5.8*cm)
    
    pair_table = Table([
        [img_wa, img_flyer],
        [Paragraph("Figura 6: Offerta Lampo WhatsApp con AI Pitch.", s_caption), 
         Paragraph("Figura 7: Volantino A4 con 6 slot promozionali.", s_caption)]
    ], colWidths=[9.2*cm, 9.2*cm])
    pair_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(pair_table)
    story.append(Spacer(1, 4))
    
    story.append(Paragraph("6. CASI PRATICI E BEST PRACTICE SUL TERRITORIO", s_h1))
    
    scenarios = [
        [Paragraph("<b>Scenario Reale</b>", s_body_bold), Paragraph("<b>Azione Consigliata con il Catalogo Intelligente</b>", s_body_bold)],
        [
            Paragraph("<b>Il pizzaiolo cerca una farina per 48h</b>", s_body),
            Paragraph("Cerca <i>'farina'</i>, tocca <i>'🎯 Chiedi all'AI'</i> e chiedi quali referenze reggono 48-60h di idratazione. Mostragli dal tablet i valori W e la stabilità da scheda ufficiale.", s_body)
        ],
        [
            Paragraph("<b>Ristoratore con richiesta Senza Lattosio</b>", s_body),
            Paragraph("Attiva il filtro <i>'🥛 Senza Lattosio'</i>. Apri il sottomenù e tocca <i>'📥 Scheda PDF'</i> per verificare e mostrare la certificazione HACCP ufficiale del produttore.", s_body)
        ],
        [
            Paragraph("<b>Chef scettico sul costo di un salume</b>", s_body),
            Paragraph("Apri <i>'📊 Food Cost'</i>, inserisci la grammatura esatta (es. 60g) e dimostra che l'incidenza sul piatto è di soli € 0,85 a fronte di un prezzo a menu di € 14,00.", s_body)
        ],
    ]
    t_scen = Table(scenarios, colWidths=[5.5*cm, 13.0*cm])
    t_scen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_scen)
    story.append(Spacer(1, 4))

    # Box Installazione Icona Schermata Home (Android & Apple)
    story.append(Paragraph("7. COME SALVARE L'ICONA SULLA SCHERMATA HOME (COME VERA APP)", s_h1))
    
    install_data = [
        [
            Paragraph("<b>🤖 DISPOSITIVI ANDROID (Google Chrome)</b>", s_body_bold),
            Paragraph("<b>🍏 DISPOSITIVI APPLE (Safari su iPhone / iPad)</b>", s_body_bold)
        ],
        [
            Paragraph(
                "1. Apri il link del catalogo su <b>Google Chrome</b>.<br/>"
                "2. Tocca l'icona con i <b>3 puntini</b> in alto a destra <b>(⋮)</b>.<br/>"
                "3. Seleziona <b>'Aggiungi a schermata Home'</b> (o <i>'Installa app'</i>).<br/>"
                "4. Conferma con <b>'Aggiungi'</b>.<br/>"
                "<i>L'icona IFT comparirà sulla tua Home aprendosi a schermo intero senza barre del browser!</i>",
                s_box_text
            ),
            Paragraph(
                "1. Apri il link del catalogo su <b>Safari</b>.<br/>"
                "2. Tocca il tasto <b>Condividi</b> in basso al centro <b>[ ↑ ]</b> (in alto su iPad).<br/>"
                "3. Scorri l'elenco verso il basso e tocca <b>'Aggiungi alla schermata Home'</b> <b>[ + ]</b>.<br/>"
                "4. Tocca <b>'Aggiungi'</b> in alto a destra.<br/>"
                "<i>Troverai l'icona tra le tue app preferite, pronta all'avvio istantaneo con 1 tocco!</i>",
                s_box_text
            )
        ]
    ]
    t_inst = Table(install_data, colWidths=[9.2*cm, 9.2*cm])
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#F0FDF4")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#F8FAFC")),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor("#F0FDF4")),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_inst)
    story.append(Spacer(1, 4))

    support_box = (
        "<b>ACCESSO & SUPPORTO TECNICO IFT:</b><br/>"
        "L'applicazione è sincronizzata costantemente con i server aziendali di <b>Italian Food Trading S.r.l.</b> "
        "Per chiarimenti, aggiornamenti listini o assistenza commerciale, contatta la direzione IFT (Verona)."
    )
    story.append(Table([[Paragraph(support_box, s_box_text)]], colWidths=[18.5*cm], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINELEFT', (0,0), (-1,-1), 4, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Manuale illustrato generato con successo: {output_path}")

if __name__ == "__main__":
    out = "Manuale_Catalogo_Intelligente_IFT.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    create_manual(out)
