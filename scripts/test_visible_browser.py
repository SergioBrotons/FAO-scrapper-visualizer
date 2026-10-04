"""Test visible browser launch with Windows foreground focus."""

import sys
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / ".venv" / "Lib" / "site-packages"))

from playwright.sync_api import sync_playwright

def main():
    print("Lancement du navigateur Chromium en mode fenêtré visible...")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--new-window",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto("https://fao.ge.ch/recherche?rubrique=133", wait_until="domcontentloaded")
        print(f"Page chargée : {page.title()}")
        page.bring_to_front()
        print("Navigateur ouvert sur votre écran. Fermeture automatique dans 15 secondes...")
        time.sleep(15)
        browser.close()

if __name__ == "__main__":
    main()
