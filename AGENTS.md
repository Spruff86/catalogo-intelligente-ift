# 🤖 AGENTS.md — Catalogo Intelligente & Assistente Ho.Re.Ca
**Azienda**: Italian Food Trading S.r.l. (Verona, Italia)  
**Dominio**: Distribuzione alimentare Ho.Re.Ca (Ristoranti, Pizzerie Gourmet, Bistrot, Gastronomie)  
**Tecnologie Principali**: Python 3.9+, Streamlit, SQLite (FTS5), Google Gemini API (`google-genai`), OpenPyXL, PyPDF, Android (Kotlin / WebView).

---

## 🎯 Obiettivo del Progetto
Fornire alla forza vendita, agli agenti sul territorio e ai clienti di **Italian Food Trading S.r.l.** uno strumento intelligente, accessibile via Web e su Tablet Android (APK), per:
1. **Consultare 2.003+ referenze a listino** con foto HD, schede tecniche PDF ufficiali e prezzi soglia aggiornati.
2. **Effettuare ricerche avanzate** con comprensione del linguaggio naturale italiano, abbreviazioni di settore (`PROSC.COTTO`, `MOZZ.`, `A.Q.`) e filtri allergeni/dietetici (`Senza Glutine`, `Senza Lattosio`).
3. **Ricevere consulenza tecnica e gastronomica in tempo reale dall'Assistente AI** su schede HACCP, tempi di lievitazione/forza farine ($W$, proteine), abbinamenti culinari e food cost, con garanzia assoluta di citazione dei soli codici SKU reali a magazzino.

---

## 🏗️ Architettura del Codebase

```text
├── app.py                     # Frontend Streamlit: UI moderna, Hero banner, Product card, Chat studio AI, Preventivi
├── quote_generator.py         # Motore ReportLab: Generatore Preventivi PDF aziendali IFT & export WhatsApp
├── database.py                # Database SQLite, FTS5, stemming morfologico italiano, ranking pertinenza
├── ai_assistant.py            # RAG Engine, integrazione Gemini (3.6/2.5 Flash), failover e rate-limit handler
├── indexer.py                 # Pipeline di indicizzazione Excel -> SQLite + estrazione testo PDF schede
├── config.py                  # Configurazione percorsi portabili (Locale Mac / Cloud / Server)
├── catalogo_horeca.db         # Database SQLite pre-indicizzato (12 MB)
├── ift_logo.png               # Logo ufficiale trasparente di Italian Food Trading S.r.l.
├── start.sh                   # Script di avvio rapido per ambiente locale
├── requirements.txt           # Dipendenze Python (Streamlit, ReportLab, Google-GenAI, ecc.)
├── android-app/               # Progetto nativo Android per Tablet (WebView + PDF Downloader)
│   ├── app/src/main/
│   │   ├── AndroidManifest.xml
│   │   ├── java/.../MainActivity.kt
│   │   └── res/...
│   ├── build.gradle
│   └── settings.gradle
└── .github/workflows/
    └── build_apk.yml          # Pipeline CI/CD GitHub Actions per compilare l'APK Android in cloud
```

---

## 📋 Specifiche dei Moduli e Flussi Dati

### 1. `quote_generator.py`
- **Motore PDF Vettoriale**: Generazione tramite `reportlab` in memoria (`io.BytesIO`) con layout aziendale IFT (Navy/Oro), logo ufficiale, box anagrafica cliente, tabella articoli con formattazione automatica dei testi, totali/IVA e riquadro firme.
- **Integrazione WhatsApp**: Funzione `generate_whatsapp_message()` e `get_whatsapp_url()` per comporre e inviare con un click preventivi pre-formattati con codici SKU, quantità e prezzi.

### 1. `database.py`
- **Tabelle**: `products` (dati anagrafici, logistici, prezzi, percorsi foto/schede, testo PDF estratto) e `products_fts` (FTS5 full-text).
- **Riconoscimento Linguistico**: Funzione `normalize_italian_term()` per mappare sinonimi ed abbreviazioni Ho.Re.Ca (es. *prosciutti* ➔ `%prosc%`, *mozzarelle* ➔ `%mozz%`, *farine* ➔ `%farin%`).
- **Filtri Allergeni Intelligenti**: Se la query contiene `senza glutine` o `senza lattosio`, il motore esegue una scansione mirata sulle dichiarazioni ufficiali delle schede tecniche PDF.
- **Isolamento dei Token**: Separazione dei termini gastronomici identificativi rispetto alle parole discorsive per evitare falsi positivi da contaminazione crociata HACCP.

### 2. `ai_assistant.py`
- **Modelli Supportati**: Default `gemini-3.6-flash`, con fallback automatico su `gemini-2.5-flash`, `gemini-flash-latest`, `gemini-3.5-flash`.
- **Risoluzione Rate Limit (429)**: Backoff automatico con pausa di 2 secondi, failover tra diverse famiglie di modelli Google e disattivazione selettiva del web grounding in caso di quota satura.
- **Regola Zero-Hallucination**: Istruzioni di sistema tassative per impedire all'AI di inventare codici SKU o citare articoli da ricerche esterne non presenti a magazzino.

### 3. `indexer.py`
- **Priorità Prezzo**: Estrae e registra il **`Prezzo Soglia`** (colonna 27 del file Excel) come prezzo ufficiale per tutti i 2.003 articoli.
- **Mappatura Media**: Associazione automatica basata sul codice SKU per foto (`.jpg`, `.png`) e schede tecniche (`.pdf`).

---

## 🔒 Regole Tassative per gli Agenti AI (Codice e UI)

1. **Integrità dei Codici SKU e Prezzi**:
   - I prezzi mostrati nell'app e citati dall'assistente devono essere sempre i **Prezzi Soglia** ricavati dal gestionale Excel.
   - Non inventare mai codici SKU.
2. **Integrità dello Stile Streamlit**:
   - Non applicare mai regole CSS generiche `font-family: ... !important` su tag globali `span` o `div`, poiché sovrascrivono i font glyph di Material Symbols compromettendo la resa delle icone native di Streamlit.
3. **Portabilità Locale e Cloud**:
   - Utilizzare sempre le funzioni di risoluzione percorsi in `config.py` e `app.py` (`resolve_file`) per garantire il funzionamento sia sui percorsi locali di Google Drive che in ambienti containerizzati cloud.

---

## 🛠️ Comandi Operativi Utili

```bash
# Avvio locale dell'applicazione Streamlit
./start.sh

# Re-indicizzazione completa catalogo da Excel e PDF
.venv/bin/python3 indexer.py

# Verifica consistenza database
.venv/bin/python3 -c "import database; print(database.get_catalog_stats())"
```
