#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

os.makedirs("screenshots", exist_ok=True)

port = 8503
proc = subprocess.Popen([
    ".venv/bin/streamlit", "run", "app.py",
    f"--server.port={port}",
    "--server.address=127.0.0.1",
    "--server.headless=true",
    "--browser.gatherUsageStats=false"
], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

time.sleep(3)

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            headless=True
        )
        context = browser.new_context(
            viewport={"width": 1200, "height": 800},
            device_scale_factor=2
        )
        page = context.new_page()
        page.goto(f"http://127.0.0.1:{port}")
        
        # 1. Login
        page.wait_for_selector('input[type="password"]', timeout=15000)
        page.fill('input[type="password"]', 'ift')
        page.click('button:has-text("Accedi al Catalogo")')
        time.sleep(4)
        
        # 2. Catalogo tab (default)
        print("Tab Catalogo...")
        time.sleep(2)
        page.screenshot(path="screenshots/01_catalogo.png")
        
        # Open Sottomenù on first product card
        btn_det = page.locator("button:has-text('👁️ Dettaglio')").first
        if btn_det.count() > 0:
            print("Apertura Dettaglio...")
            btn_det.click()
            time.sleep(2)
            page.screenshot(path="screenshots/02_sottomenu.png")
            
        # Helper to click tabs by index or text
        tabs = page.locator('button[role="tab"]')
        n_tabs = tabs.count()
        print(f"Trovate {n_tabs} schede tab.")
        for i in range(n_tabs):
            tab_name = tabs.nth(i).inner_text().strip()
            print(f"Tab {i}: {tab_name}")
            
        # Tab 1: Chat AI
        if n_tabs > 1:
            print("Click Tab Chat AI...")
            tabs.nth(1).click()
            time.sleep(2)
            page.screenshot(path="screenshots/03_chat_ai.png")
            
        # Tab 2: Preventivo
        if n_tabs > 2:
            print("Click Tab Preventivo...")
            tabs.nth(2).click()
            time.sleep(2)
            page.screenshot(path="screenshots/04_preventivo.png")
            
        # Tab 3: Food Cost
        if n_tabs > 3:
            print("Click Tab Food Cost...")
            tabs.nth(3).click()
            time.sleep(2)
            page.screenshot(path="screenshots/05_food_cost.png")
            
        # Tab 4: Offerta WA
        if n_tabs > 4:
            print("Click Tab Offerta WA...")
            tabs.nth(4).click()
            time.sleep(2)
            page.screenshot(path="screenshots/06_offerta_wa.png")
            
        # Tab 5: Volantino
        if n_tabs > 5:
            print("Click Tab Volantino...")
            tabs.nth(5).click()
            time.sleep(2)
            page.screenshot(path="screenshots/07_volantino.png")

        browser.close()
        print("Catture completate!")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except Exception:
        proc.kill()
