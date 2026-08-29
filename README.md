# 🍽️ Catalogo Intelligente Ho.Re.Ca con Google Gemini & Web Grounding

Applicazione interattiva per la consultazione del catalogo prodotti Ho.Re.Ca., dotata di:
- **Motore di ricerca avanzato su SQLite + FTS5** per oltre 2.000 referenze.
- **Visualizzazione Foto Articoli** e **Consultazione/Download Schede Tecniche PDF**.
- **Assistente AI con doppio focus**:
  1. *Consulenza Tecnica*: estrazione e risposta puntuale su allergeni, modalità di conservazione, shelf-life, conformità e HACCP direttamente dalle schede tecniche ufficiali.
  2. *Consulenza Culinaria & Business*: suggerimenti di ricette, abbinamenti per pizze gourmet e ristorazione, food cost e tendenze tramite Google Search Grounding in tempo reale.

---

## 🚀 Come Avviare l'Applicazione

### 1. Attiva l'ambiente virtuale:
```bash
source .venv/bin/activate
```

### 2. Configura la tua API Key (opzionale se inserita via web):
Crea un file `.env` a partire da `.env.example`:
```bash
cp .env.example .env
# Inserisci la tua chiave GEMINI_API_KEY nel file .env
```
*(Puoi anche inserire la chiave direttamente nella barra laterale sinistra dell'applicazione).*

### 3. Avvia Streamlit:
```bash
streamlit run app.py
```

L'applicazione si aprirà automaticamente nel browser all'indirizzo `http://localhost:8501`.
