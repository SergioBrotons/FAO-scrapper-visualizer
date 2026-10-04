import sys
import time
sys.path.insert(0, 'src')
sys.path.insert(0, '.venv/Lib/site-packages')
from playwright.sync_api import sync_playwright

p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page()
page.goto('https://fao.ge.ch/recherche?rubrique=133', wait_until="networkidle")

widget_frame = None
for frame in page.frames:
    if "widget" in frame.url:
        widget_frame = frame
        break

if widget_frame:
    print("Found widget frame!")
    btn = widget_frame.query_selector("button, .frc-button")
    if btn:
        print("Clicking Friendly Captcha start button...")
        btn.click()
        
        # Wait up to 20 seconds for the puzzle to finish and redirect
        for i in range(20):
            time.sleep(1)
            text = widget_frame.inner_text("body")
            print(f"[{i+1}s] Widget state: {text[:60].strip()}")
            if "terminé" in text.lower() or "completed" in text.lower() or "succès" in text.lower() or "success" in text.lower():
                print("PUZZLE COMPLETED!")
                time.sleep(2)
                break

print("Current page URL:", page.url)
print("Page contains captcha-layout?:", "captcha-layout" in page.content().lower())

browser.close()
p.stop()
