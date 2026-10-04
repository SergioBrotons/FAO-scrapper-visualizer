"""Direct interactive launcher that opens Google Chrome visibly on the user's desktop."""

import sys
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / ".venv" / "Lib" / "site-packages"))

from playwright.sync_api import sync_playwright

def main():
    print("=" * 70)
    print("  CYTRIA FAO - OUVERTURE DE GOOGLE CHROME SUR VOTRE ECRAN")
    print("=" * 70)
    print("Connexion au portail officiel FAO Genève (Rubrique 133)...")
    print("Une fenetre Google Chrome va s'ouvrir sur votre bureau.")
    print("Si la verification Captcha apparait, cochez la case directement dans Chrome.")
    print("=" * 70)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=[
                "--start-maximized",
                "--new-window",
                "--window-position=50,50",
                "--disable-blink-features=AutomationControlled",
                "--no-default-browser-check",
            ]
        )
        context = browser.new_context(no_viewport=True)
        page = context.new_page()
        page.goto("https://fao.ge.ch/recherche?rubrique=133", wait_until="domcontentloaded")
        page.bring_to_front()

        print(f"\n[OK] Page chargee dans Chrome : '{page.title()}'")
        print("\n>>> La fenetre Chrome est ouverte sur votre bureau.")
        print(">>> Resolu le captcha dans Chrome puis revenez ici.")
        print(">>> Appuyez sur [ENTREE] dans ce terminal une fois le captcha valide...")
        
        try:
            input()
        except Exception:
            # If non-interactive, wait for redirect
            print("Attente de la validation du captcha (jusqu'a 3 minutes)...")
            start = time.time()
            while time.time() - start < 180:
                content = page.content().lower()
                if "captcha-layout" not in content and "verification par captcha" not in content:
                    print("Captcha valide avec succes !")
                    break
                time.sleep(2)

        print(f"\n[SUCCES] Navigation confirmee : '{page.title()}'")
        print("URL actuelle :", page.url)
        time.sleep(2)
        browser.close()
        print("Session terminee.")

if __name__ == "__main__":
    main()
