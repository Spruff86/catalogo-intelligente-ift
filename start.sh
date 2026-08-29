#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
echo "Avvio Catalogo Intelligente..."
streamlit run app.py --server.port=8501 --server.headless=false
