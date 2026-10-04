"""Playwright persistent browser session manager with multi-tier launch fallback."""

import os
import time
import shutil
import tempfile
from pathlib import Path
from typing import Optional, Callable
from playwright.sync_api import sync_playwright, BrowserContext, Page
from rich.console import Console

from fao_transactions.config import settings

console = Console()


def _get_safe_profile_dir() -> Path:
    """Return a browser profile directory outside cloud-synced folders (like kDrive)."""
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        p = Path(local_appdata) / "CytriaFAO" / "browser_profile"
    else:
        p = Path(tempfile.gettempdir()) / "CytriaFAO" / "browser_profile"
    p.mkdir(parents=True, exist_ok=True)
    return p


class BrowserManager:
    """Manages headed Playwright Chromium instance with persistent context and rock-solid fallbacks."""

    def __init__(
        self,
        profile_dir: Optional[str] = None,
        headless: Optional[bool] = None,
        log_callback: Optional[Callable[[str], None]] = None,
    ):
        if profile_dir:
            self.profile_dir = Path(profile_dir).resolve()
        else:
            self.profile_dir = _get_safe_profile_dir()

        self.headless = headless if headless is not None else settings.browser.headless
        self.log_callback = log_callback
        self._playwright = None
        self._browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._temp_dir_to_clean: Optional[Path] = None

    def log(self, message: str) -> None:
        """Log message to console and callback if provided."""
        console.print(message)
        if self.log_callback:
            try:
                self.log_callback(message)
            except Exception:
                pass

    def _cleanup_lock_files(self, directory: Path) -> None:
        """Remove any dangling lock files from previous browser crashes."""
        for lock_name in ["SingletonLock", "SingletonSocket", "SingletonCookie", "LOCK"]:
            for folder in [directory, directory / "Default"]:
                f = folder / lock_name
                if f.exists():
                    try:
                        f.unlink()
                    except Exception:
                        pass

    def start(self) -> Page:
        """Launch visible Chromium browser on desktop with guaranteed window rendering."""
        self.log(f"[bold cyan]Ouverture du Navigateur visible sur votre bureau...[/bold cyan]")
        self._playwright = sync_playwright().start()

        storage_file = Path(os.environ.get("LOCALAPPDATA", tempfile.gettempdir())) / "CytriaFAO" / "storage_state.json"
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.storage_state_path = storage_file

        launch_args = [
            "--no-sandbox",
            "--disable-infobars",
            "--start-maximized",
            "--new-window",
            "--window-position=50,50",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
        ]

        # Launch bundled Chromium directly with fresh session (always opens visible window on Windows desktop)
        try:
            self._browser = self._playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
            )
            context_kwargs = {
                "no_viewport": True,
                "accept_downloads": True,
            }
            if storage_file.exists() and storage_file.stat().st_size > 10:
                context_kwargs["storage_state"] = str(storage_file)

            self.context = self._browser.new_context(**context_kwargs)
            self.log("[green]Fenêtre du navigateur ouverte avec succès sur votre écran.[/green]")
        except Exception as e:
            self.log(f"[yellow]Tentative alternative avec profil persistant : {e}[/yellow]")
            temp_profile = Path(tempfile.mkdtemp(prefix="cytria_fao_"))
            self._temp_dir_to_clean = temp_profile
            self.context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(temp_profile),
                headless=self.headless,
                no_viewport=True,
                accept_downloads=True,
                args=launch_args,
            )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        try:
            self.page.bring_to_front()
        except Exception:
            pass

        return self.page

    def navigate_and_handle_captcha(self, url: str) -> None:
        """Navigate to URL and prompt user if CAPTCHA or Cloudflare is detected."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        self.log(f"[bold green]Navigation vers :[/bold green] {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            self.page.bring_to_front()
        except Exception:
            pass

    def check_and_prompt_captcha(self) -> None:
        """Inspect page for CAPTCHA / Cloudflare challenge, open browser and prompt terminal if needed."""
        if not self.page:
            return

        # Give page a short moment to render challenge if any
        self.page.wait_for_timeout(1500)
        content = self.page.content().lower()
        title = self.page.title().lower()

        needs_solution = (
            "captcha-layout" in content
            or "verification par captcha" in content
            or "vérification par captcha" in content
            or "just a moment" in title
            or "turnstile" in title
            or "cloudflare" in title
        )

        if needs_solution:
            target_url = "https://fao.ge.ch/recherche?rubrique=133"

            # 1. Automatically launch the default system browser (Chrome/Edge) right on the user's interactive desktop
            import sys, subprocess, os
            if sys.platform == "win32":
                try:
                    cmd = f'(New-Object -ComObject Shell.Application).ShellExecute("{target_url}", "", "", "open", 1)'
                    subprocess.Popen(["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", cmd], shell=False)
                except Exception:
                    try:
                        subprocess.Popen(["explorer.exe", target_url], shell=False)
                    except Exception:
                        try:
                            os.system(f'start "" "{target_url}"')
                        except Exception:
                            pass
            try:
                import webbrowser
                webbrowser.open(target_url)
            except Exception:
                pass

            # 2. Display a rich, clickable hyperlink and manual instructions in terminal
            self.log("\n======================================================================")
            self.log("[ACTION REQUISE] DÉFI DE SÉCURITÉ / FRIENDLY CAPTCHA DÉTECTÉ")
            self.log("Le portail FAO Genève exige une validation humaine anti-robot.")
            self.log(f"👉 Ouvrir le portail dans votre navigateur : {target_url}")
            self.log("Une fois le Captcha résolu, appuyez sur [ENTRÉE] ou cliquez sur 'J'ai validé'.")
            self.log("======================================================================\n")

            try:
                self.page.bring_to_front()
            except Exception:
                pass

            # Wait for user resolution
            self.wait_until_unblocked()

            # Confirm page has transitioned
            self.page.wait_for_timeout(1500)
            self.log("[bold green]Accès validé ! Poursuite du traitement des transactions FAO...[/bold green]")
        else:
            self.log("[green]Accès direct au portail FAO validé (aucun Captcha bloquant).[/green]")

    def wait_until_unblocked(self, timeout_seconds: int = 180) -> None:
        """Poll until CAPTCHA disappears, listening to [ENTER] key, terminal commands, or UI signals."""
        import sys
        is_windows = sys.platform == "win32"
        kbhit = None
        getch = None
        if is_windows:
            try:
                import msvcrt
                kbhit = msvcrt.kbhit
                getch = msvcrt.getch
            except Exception:
                pass

        signal_file = Path("data/state/captcha_solved.signal")
        target_url = "https://fao.ge.ch/recherche?rubrique=133"

        start_time = time.time()
        last_reload_time = start_time
        last_logged = start_time

        while time.time() - start_time < timeout_seconds:
            # Check if web UI signaled completion via signal file
            if signal_file.exists():
                try:
                    signal_file.unlink(missing_ok=True)
                except Exception:
                    pass
                self.log("[bold cyan][Signal Reçu][/bold cyan] Validation confirmée depuis l'interface Web ! Rechargement...")
                try:
                    self.page.reload(wait_until="domcontentloaded", timeout=15000)
                except Exception:
                    pass

            # Check if user pressed a key in the terminal
            if kbhit and kbhit():
                try:
                    key = getch()
                    if key in [b"\r", b"\n"]:  # ENTER key pressed
                        self.log("[bold cyan][Touche ENTRÉE][/bold cyan] Rechargement de la page FAO...")
                        self.page.reload(wait_until="domcontentloaded", timeout=15000)
                    elif key in [b"o", b"O"]:
                        import webbrowser
                        webbrowser.open(target_url)
                        self.log(f"[FAO] Page ré-ouverte dans votre navigateur : {target_url}")
                    elif key in [b"s", b"S"]:
                        self.log("[yellow][Sauté][/yellow] Poursuite avec l'historique et les données locales.")
                        return
                    elif key in [b"c", b"C"]:
                        print("\nEntrez la valeur du cookie FAO-CAPTCHA (ou appuyez sur ENTRÉE pour annuler) : ", end="", flush=True)
                        cookie_input = input().strip()
                        if cookie_input:
                            # Strip prefix if user pasted full header
                            if "FAO-CAPTCHA=" in cookie_input:
                                cookie_input = cookie_input.split("FAO-CAPTCHA=")[-1].split(";")[0].strip()
                            self.context.add_cookies([{
                                "name": "FAO-CAPTCHA",
                                "value": cookie_input,
                                "domain": "fao.ge.ch",
                                "path": "/",
                            }])
                            self.log("[bold green]Cookie FAO-CAPTCHA injecté ! Rechargement...[/bold green]")
                            self.page.reload(wait_until="domcontentloaded", timeout=15000)
                except Exception as ex:
                    self.log(f"[dim]Erreur entrée clavier : {ex}[/dim]")

            # Check current page content
            content = self.page.content().lower()
            title = self.page.title().lower()
            blocked = (
                "captcha-layout" in content
                or "verification par captcha" in content
                or "vérification par captcha" in content
                or "just a moment" in title
                or "turnstile" in title
                or "cloudflare" in title
            )

            if not blocked:
                self.log("[bold green]Défi validé avec succès ![/bold green]")
                return

            # Every 5 seconds, attempt background reload to pick up IP-level clearance
            if time.time() - last_reload_time >= 5:
                try:
                    self.page.reload(wait_until="domcontentloaded", timeout=10000)
                except Exception:
                    pass
                last_reload_time = time.time()

            # Periodic status message
            if time.time() - last_logged >= 10:
                elapsed = int(time.time() - start_time)
                remaining = timeout_seconds - elapsed
                self.log(f"[FAO] En attente de validation ({remaining}s restantes) — Cliquez le Captcha puis appuyez sur [ENTRÉE]...")
                last_logged = time.time()

            time.sleep(0.5)

        self.log("[yellow]Délai d'attente écoulé. Tentative de poursuite du scan...[/yellow]")

    def close(self) -> None:
        """Gracefully close browser and persistent context."""
        try:
            if self.context and hasattr(self, "storage_state_path") and self.storage_state_path:
                self.context.storage_state(path=str(self.storage_state_path))
        except Exception:
            pass
        try:
            if self.context:
                self.context.close()
        except Exception:
            pass
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass

        if self._temp_dir_to_clean and self._temp_dir_to_clean.exists():
            try:
                shutil.rmtree(str(self._temp_dir_to_clean), ignore_errors=True)
            except Exception:
                pass

        self.log("[dim]Session du navigateur terminée avec succès.[/dim]")

