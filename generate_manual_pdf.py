#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore Manuale Operativo Ufficiale Catalogo Intelligente IFT
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
            self.drawRightString(A4[0] - 35, A4[1] - 22, "Guida Agenti & Consulenti Ho.Re.Ca")
            
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(35, A4[1] - 26, A4[0] - 35, A4[1] - 26)

        # Footer (Tutte le pagine)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(35, 30, A4[0] - 35, 30)
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        self.drawString(35, 18, "Documento Riservato ad Uso Interno della Rete Commerciale IFT")
        page_text = f"Pagina {self._pageNumber} di {page_count}"
        self.drawRightString(A4[0] - 35, 18, page_text)
            
        self.restoreState()

def create_manual(output_path="Manuale_Catalogo_Intelligente_IFT.pdf"):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=35,
        rightMargin=35,
        topMargin=36,
        bottomMargin=38
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
        fontSize=20,
        leading=24,
        textColor=c_blue,
        alignment=0
    )
    
    s_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_muted,
        alignment=0
    )
    
    s_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_blue,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    s_h2 = ParagraphStyle(
        'Heading2_Custom',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=c_dark,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )
    
    s_body = ParagraphStyle(
        'Body_Custom',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=4
    )
    
    s_body_bold = ParagraphStyle(
        'BodyBold_Custom',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=c_dark,
        spaceAfter=3
    )
    
    s_bullet = ParagraphStyle(
        'Bullet_Custom',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=c_dark,
        leftIndent=10,
        spaceAfter=2.5
    )

    s_box_text = ParagraphStyle(
        'BoxText',
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=c_dark
    )

    story = []
    
    # =========================================================================
    # PAGINA 1: COPERTINA + EXECUTIVE SUMMARY + INDICE DEI MODULI
    # =========================================================================
    logo_path = "ift_logo.png" if os.path.exists("ift_logo.png") else None
    
    if logo_path:
        logo_img = Image(logo_path, width=4.5*cm, height=2.0*cm)
        logo_img.hAlign = 'LEFT'
        info_p = Paragraph(
            "<b>ITALIAN FOOD TRADING S.R.L.</b><br/>"
            "Via dell'Artigianato, 12 — Verona (VR)<br/>"
            "Distribuzione Alimentare Ho.Re.Ca & Pizzerie Gourmet<br/>"
            "<font color='#1E3A8A'><b>www.italianfoodtrading.it</b></font>",
            ParagraphStyle('HInfo', fontName='Helvetica', fontSize=8, leading=10.5, textColor=c_muted, alignment=2)
        )
        header_table = Table([[logo_img, info_p]], colWidths=[5.5*cm, 13.0*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(header_table)
        
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=0, spaceAfter=10))
    
    story.append(Paragraph("CATALOGO INTELLIGENTE & ASSISTENTE AI", s_cover_title))
    story.append(Spacer(1, 3))
    story.append(Paragraph("<b>Manuale Operativo e Guida Commerciale per la Forza Vendita IFT</b><br/>"
                           "<i>Strumento Mobile & Web integrato con Gestionali Aziendali — Edizione 2026</i>", s_cover_subtitle))
    story.append(Spacer(1, 8))
    
    summary_html = (
        "<b>OBIETTIVO DELLO STRUMENTO:</b><br/>"
        "Il Catalogo Intelligente IFT è progettato per velocizzare ed elevare ogni trattativa commerciale sul territorio. "
        "Permette a ciascun agente di accedere in tempo reale a <b>2.003+ referenze a magazzino</b> con foto HD e schede tecniche "
        "ufficiali, verificare all'istante i <b>Prezzi Soglia</b>, formulare <b>Preventivi aziendali con firma</b>, "
        "effettuare calcoli di <b>Food Cost</b> per i clienti e inviare promozioni via WhatsApp in meno di 30 secondi."
    )
    box_table = Table([[Paragraph(summary_html, s_box_text)]], colWidths=[18.5*cm])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BFDBFE")),
        ('LINELEFT', (0,0), (-1,-1), 4, c_blue),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("MAPPA DELLE FUNZIONALITÀ PRINCIPALI", s_h1))
    
    moduli_data = [
        [Paragraph("<b>Sezione</b>", s_body_bold), Paragraph("<b>Modulo Applicativo</b>", s_body_bold), Paragraph("<b>Funzione Chiave per l'Agente Commerciale</b>", s_body_bold)],
        [Paragraph("<b>1</b>", s_body), Paragraph("<b>📦 Catalogo Prodotti</b>", s_body_bold), Paragraph("Ricerca rapida per SKU o Nome, filtri allergeni/temperatura, schede PDF e sottomenù rapido integrato.", s_body)],
        [Paragraph("<b>2</b>", s_body), Paragraph("<b>💬 Chat Studio AI</b>", s_body_bold), Paragraph("Assistente gastronomico basato sulle schede tecniche reali: farine, maturazioni, abbinamenti, zero allucinazioni.", s_body)],
        [Paragraph("<b>3</b>", s_body), Paragraph("<b>🛒 Preventivi IFT</b>", s_body_bold), Paragraph("Generatore proposte commerciali in PDF aziendale IFT con firma e testo pre-formattato WhatsApp.", s_body)],
        [Paragraph("<b>4</b>", s_body), Paragraph("<b>📊 Food Cost Calculator</b>", s_body_bold), Paragraph("Consulenza per chef: calcolo costo porzione, margini lordi e travaso ingredienti nel carrello preventivo.", s_body)],
        [Paragraph("<b>5</b>", s_body), Paragraph("<b>📲 Offerte Lampo WA</b>", s_body_bold), Paragraph("Pitch persuasivo generato dall'AI pronto da condividere via WhatsApp su singoli prodotti o arrivi freschi.", s_body)],
        [Paragraph("<b>6</b>", s_body), Paragraph("<b>📄 Volantino A4</b>", s_body_bold), Paragraph("Impaginatore automatico a 6 slot promozionali per creare volantini grafici A4 con sconti speciali.", s_body)],
    ]
    t_mod = Table(moduli_data, colWidths=[1.4*cm, 4.6*cm, 12.5*cm])
    t_mod.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_mod)
    
    story.append(PageBreak())

    # =========================================================================
    # PAGINA 2: CATALOGO & RICERCA + SOTTOMENÙ RAPIDO + CHAT STUDIO AI
    # =========================================================================
    story.append(Paragraph("1. CATALOGO PRODOTTI, RICERCA DIRETTA & SOTTOMENÙ", s_h1))
    story.append(Paragraph(
        "Il modulo <b>📦 Catalogo</b> gestisce l'intero assortimento IFT. È ottimizzato per l'uso immediato da tablet o smartphone "
        "senza costringere l'agente a scorrere a fondo pagina: ogni informazione e azione si apre direttamente sotto all'articolo selezionato.",
        s_body
    ))
    
    story.append(Paragraph("Regole e Funzionalità di Ricerca:", s_h2))
    story.append(Paragraph("• <b>Ricerca Esclusiva SKU / Nome:</b> Digitando un codice (es. <i>10203</i>) o una parola (es. <i>burrata</i>, <i>farina</i>, <i>cotto</i>), il sistema ricerca <b>soltanto</b> nei campi Codice Articolo e Descrizione Articolo. Evita qualsiasi falso positivo derivante da contaminazioni o testi HACCP.", s_bullet))
    story.append(Paragraph("• <b>Filtri Rapidi con Chip:</b> Con un tocco puoi filtrare per <i>🌾 Senza Glutine</i> o <i>🥛 Senza Lattosio</i> (con verifica delle dichiarazioni ufficiali di scheda tecnica), oppure isolare gli articoli per temperatura (<i>❄️ Refrigerato</i>, <i>🧊 Congelato</i>, <i>📦 Asciutto</i>).", s_bullet))
    story.append(Paragraph("• <b>Prezzo Soglia Riservato:</b> Il prezzo evidenziato per ciascun articolo è il <b>Prezzo Soglia</b> ufficiale IFT: garantisce all'agente il limite minimo di vendita autorizzato dalla direzione.", s_bullet))
    
    story.append(Paragraph("Il Sottomenù Azioni Rapide (Sotto a Ogni Scheda):", s_h2))
    story.append(Paragraph(
        "Toccando <b>`👁️ Dettaglio`</b> su una card, la scheda mostra il tasto <b>`🔼 Chiudi Dettagli`</b> e apre subito il cassetto operativo:",
        s_body
    ))
    
    actions_desc = [
        [Paragraph("<b>Pulsante</b>", s_body_bold), Paragraph("<b>Azione e Risultato</b>", s_body_bold)],
        [Paragraph("<b>📲 Offerta WA</b>", s_body), Paragraph("Trasferisce l'articolo e il prezzo alla scheda Offerta WhatsApp, predisponendo la bozza del messaggio.", s_body)],
        [Paragraph("<b>📊 Food Cost</b>", s_body), Paragraph("Carica il prodotto nel ricettario Food Cost, impostando la conversione automatica grammi/millilitri.", s_body)],
        [Paragraph("<b>📄 Volantino</b>", s_body), Paragraph("Assegna l'articolo al primo slot disponibile del Volantino promozionale A4 a 6 prodotti.", s_body)],
        [Paragraph("<b>🎯 Chiedi all'AI</b>", s_body), Paragraph("Aggancia il codice all'Assistente AI per consultare la scheda tecnica e ottenere argomentazioni di vendita.", s_body)],
        [Paragraph("<b>📥 Scheda PDF</b>", s_body), Paragraph("Apre o scarica il documento PDF ufficiale depositato dal produttore (valori nutrizionali e allergeni).", s_body)],
        [Paragraph("<b>🛒 Preventivo</b>", s_body), Paragraph("Box integrato con quantità e prezzo modificabile: inserisce l'articolo nella proposta commerciale con un click.", s_body)],
        [Paragraph("<b>📋 Info Tecniche</b>", s_body), Paragraph("Menu a tendina con shelf-life, unità di imballo, minimo d'ordine, giorni di consegna e testo integrale HACCP.", s_body)],
    ]
    t_act = Table(actions_desc, colWidths=[3.8*cm, 14.7*cm])
    t_act.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_act)
    story.append(Spacer(1, 6))

    story.append(Paragraph("2. CHAT STUDIO AI: IL CONSULENTE GASTRONOMICO DEDICATO", s_h1))
    story.append(Paragraph(
        "La scheda <b>💬 Chat AI</b> sfrutta modelli Google Gemini configurati secondo la tassativa regola di <b>Zero-Allucinazioni</b>. "
        "L'assistente risponde solo basandosi su codici e schede tecniche realmente a catalogo:",
        s_body
    ))
    
    ai_box = (
        "• <b>Con Prodotto Agganciato (Focus SKU):</b> L'AI analizza la scheda del prodotto selezionato. Esempio per una farina: "
        "<i>'Qual è la forza W, il P/L e il tempo di maturazione consigliato?'</i>. Esempio per un formaggio: "
        "<i>'È garantita l'assenza di lattosio per intolleranti?'</i> o <i>'Come posso consigliarlo per guarnire una pizza contemporanea?'</i>.<br/>"
        "• <b>Modalità Catalogo Generale:</b> Se nessun prodotto è agganciato, puoi effettuare query complesse: "
        "<i>'Quali 3 prosciutti crudi DOP abbiamo con stagionatura minima 24 mesi?'</i> o <i>'Suggeriscimi una linea di pomodori pelati per pizzeria gourmet'</i>."
    )
    story.append(Table([[Paragraph(ai_box, s_box_text)]], colWidths=[18.5*cm], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDF4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#BBF7D0")),
        ('LINELEFT', (0,0), (-1,-1), 4, colors.HexColor("#16A34A")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 3: PREVENTIVI IFT + FOOD COST CALCULATOR
    # =========================================================================
    story.append(Paragraph("3. PREVENTIVI AZIENDALI IFT: PDF UFFICIALE & WHATSAPP", s_h1))
    story.append(Paragraph(
        "La scheda <b>🛒 Preventivo</b> permette di creare in pochi secondi una proposta economica professionale, "
        "personalizzata con i dati del cliente e i prezzi concordati.",
        s_body
    ))
    story.append(Paragraph("• <b>Composizione Intuitiva:</b> Gli articoli inseriti dal catalogo compaiono in tabella con quantità, unità di misura, imballi e prezzo unitario. Puoi modificare i prezzi al volo o rimuovere articoli con un click.", s_bullet))
    story.append(Paragraph("• <b>Anagrafica Completa:</b> Campi dedicati per Ragione Sociale, Referente, P.IVA, Indirizzo e Note operative di consegna (es. <i>'Consegna martedì mattina entro le 10:00'</i>).", s_bullet))
    story.append(Paragraph("• <b>Esportazione PDF IFT ad Alta Definizione:</b> Cliccando su <i>'📄 Scarica Preventivo PDF'</i>, il motore genera un documento vettoriale aziendale con intestazione ufficiale, logo a colori, tabella articoli ordinata e box per firma di accettazione.", s_bullet))
    story.append(Paragraph("• <b>Condivisione WhatsApp in 1 Click:</b> Cliccando su <i>'📲 Invia su WhatsApp'</i>, il sistema apre l'applicazione di messaggistica con il testo dell'offerta già impaginato, pronto da recapitare al cliente prima di salutarlo.", s_bullet))
    story.append(Spacer(1, 6))

    story.append(Paragraph("4. FOOD COST CALCULATOR: INGEGNERIA DEL MENU E MARGINI", s_h1))
    story.append(Paragraph(
        "Il modulo <b>📊 Food Cost</b> trasforma l'agente commerciale in un <b>consulente di business</b> per la ristorazione. "
        "Permette di scomporre le ricette del cliente per evidenziare la sostenibilità economica delle nostre materie prime.",
        s_body
    ))
    
    fc_table_data = [
        [Paragraph("<b>Elemento di Calcolo</b>", s_body_bold), Paragraph("<b>Spiegazione & Applicazione Pratica</b>", s_body_bold)],
        [Paragraph("<b>Conversione U.M. Intelligente</b>", s_body), Paragraph("Riconosce i listini in Kg o Litri e permette di inserire dosaggi pratici in grammi (g) o millilitri (ml), determinando il costo al grammo al millesimo di euro.", s_body)],
        [Paragraph("<b>Food Cost Netto a Porzione</b>", s_body), Paragraph("Somma il costo esatto degli ingredienti impiegati per singolo piatto o pizza, fornendo la base oggettiva per la trattativa.", s_body)],
        [Paragraph("<b>Target Incidenza % sul Menu</b>", s_body), Paragraph("Configura la percentuale target ideale del locale (es. 25%, 30%, 35%) e genera all'istante il Prezzo di Vendita a Menu Raccomandato.", s_body)],
        [Paragraph("<b>Margine Lordo di Contribuzione</b>", s_body), Paragraph("Visualizza il guadagno netto in euro generato da ogni singola vendita (Prezzo Menu - Food Cost Netto).", s_body)],
        [Paragraph("<b>Travaso nel Preventivo</b>", s_body), Paragraph("Impostando un lotto di coperti (es. 50 o 100 porzioni), un pulsante travasa il fabbisogno complessivo direttamente nel carrello del preventivo commerciale!", s_body)],
    ]
    t_fc = Table(fc_table_data, colWidths=[5.0*cm, 13.5*cm])
    t_fc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_fc)

    story.append(PageBreak())

    # =========================================================================
    # PAGINA 4: OFFERTE LAMPO WA + VOLANTINO A4 + SCENARI OPERATIVI
    # =========================================================================
    story.append(Paragraph("5. OFFERTE LAMPO WHATSAPP & VOLANTINO PROMOZIONALE A4", s_h1))
    
    story.append(Paragraph("Offerta Lampo WhatsApp (Scheda 📲 Offerta WA):", s_h2))
    story.append(Paragraph(
        "Ideale per spingere un arrivo speciale, un lotto fresco o una promozione d'impulso. "
        "Basta inviare l'articolo dal catalogo, impostare il prezzo speciale e cliccare su <b>'Genera Pitch con AI'</b>: "
        "l'assistente elabora un testo commerciale accattivante, con consigli di servizio ed emoji, pronto da inviare ai clienti via WhatsApp.",
        s_body
    ))
    
    story.append(Paragraph("Volantino Promozionale A4 (Scheda 📄 Volantino):", s_h2))
    story.append(Paragraph(
        "Permette di comporre un volantino cartaceo o PDF a <b>6 slot</b> (es. <i>'Speciale Pizze d'Autunno'</i>, <i>'Settimana della Burrata'</i>). "
        "Carica foto ad alta risoluzione, prezzi promozionali, descrizioni ed esporta un PDF A4 professionale con marchio IFT, "
        "ideale da stampare o inviare come allegato.",
        s_body
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("6. SCENARI D'USO SUL TERRITORIO: CASI REALI", s_h1))
    
    scenarios = [
        [Paragraph("<b>Richiesta del Cliente</b>", s_body_bold), Paragraph("<b>Come Risolvere con il Catalogo Intelligente</b>", s_body_bold)],
        [
            Paragraph("<b>Il pizzaiolo cerca una farina per 48h</b>", s_body),
            Paragraph("Cerca <i>'farina'</i>, tocca <i>'🎯 Chiedi all'AI'</i> e chiedi le farine IFT adatte per maturazioni lunghe. Mostragli sul tablet i valori W, proteine e stabilità certificati.", s_body)
        ],
        [
            Paragraph("<b>Ristoratore con richiesta Senza Lattosio</b>", s_body),
            Paragraph("Attiva il filtro <i>'🥛 Senza Lattosio'</i>. Apri il sottomenù del prodotto e scarica la <i>'📥 Scheda PDF'</i> per verificare la certificazione HACCP ufficiale del produttore.", s_body)
        ],
        [
            Paragraph("<b>Trattativa prezzi su un nuovo locale</b>", s_body),
            Paragraph("Inserisci 5-6 referenze cardine con il tasto rapido del sottomenù. Vai su <i>'🛒 Preventivo'</i>, verifica i Prezzi Soglia e invia la proposta WhatsApp prima di uscire dalla cucina.", s_body)
        ],
        [
            Paragraph("<b>Chef dubbioso sul prezzo di un taglio nobile</b>", s_body),
            Paragraph("Apri <i>'📊 Food Cost'</i>, inserisci la grammatura della porzione (es. 150g) e dimostra che l'incidenza sulla portata è contenuta a fronte di un margine lordo elevato.", s_body)
        ],
    ]
    t_scen = Table(scenarios, colWidths=[5.5*cm, 13.0*cm])
    t_scen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_scen)
    story.append(Spacer(1, 10))

    support_box = (
        "<b>NOTE OPERATIVE & SUPPORTO:</b><br/>"
        "L'applicazione è consultabile online da qualsiasi browser (PC, Tablet Android/iPad, Smartphone). "
        "I dati dei prezzi e delle schede tecniche sono sincronizzati costantemente con il gestionale aziendale di "
        "<b>Italian Food Trading S.r.l.</b> Per informazioni o aggiornamenti tecnici, contatta la direzione commerciale."
    )
    story.append(Table([[Paragraph(support_box, s_box_text)]], colWidths=[18.5*cm], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('LINELEFT', (0,0), (-1,-1), 4, c_accent),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Manuale generato con successo: {output_path}")

if __name__ == "__main__":
    out = "Manuale_Catalogo_Intelligente_IFT.pdf"
    if len(sys.argv) > 1:
        out = sys.argv[1]
    create_manual(out)
