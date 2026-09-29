"""Playwright persistent browser session manager."""

from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page
from rich.console import Console

from fao_transactions.config import settings

console = Console()


class AntiBotChallengeException(RuntimeError):
    """Raised when anti-bot challenge (Cloudflare, Friendly Captcha) blocks automated scraping."""
    pass


class BrowserManager:
    """Manages headed Playwright Chromium instance with persistent context."""

    def __init__(self, profile_dir: Optional[str] = None, headless: Optional[bool] = None):
        self.profile_dir = Path(profile_dir or settings.browser.profile_dir).expanduser().resolve()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless if headless is not None else settings.browser.headless
        self._playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def _cleanup_profile_locks(self) -> None:
        """Ensure no orphaned Chromium process is locking the user-data-dir."""
        import sys
        import subprocess
        if sys.platform == "win32":
            try:
                profile_name = self.profile_dir.name
                cmd = f"Get-CimInstance Win32_Process | Where-Object {{ $_.CommandLine -like '*{profile_name}*' }} | ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"
                subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, timeout=5)
            except Exception:
                pass
        for lock_name in ["lockfile", "SingletonLock", "SingletonSocket", "SingletonCookie"]:
            lf = self.profile_dir / lock_name
            if lf.exists():
                try:
                    lf.unlink()
                except Exception:
                    pass

    def start(self) -> Page:
        """Launch Google Chrome or Chromium with persistent context."""
        self._cleanup_profile_locks()
        channel = getattr(settings.browser, "channel", "chrome")
        console.print(f"[bold cyan]Starting Browser[/bold cyan] (Channel: {channel or 'bundled'}, Profile: {self.profile_dir}, Headless: {self.headless})")
        self._playwright = sync_playwright().start()

        launch_kwargs = {
            "user_data_dir": str(self.profile_dir),
            "headless": self.headless,
            "viewport": {
                "width": settings.browser.viewport_width,
                "height": settings.browser.viewport_height,
            },
            "slow_mo": settings.browser.slow_mo,
            "accept_downloads": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        }
        if channel:
            launch_kwargs["channel"] = channel

        try:
            self.context = self._playwright.chromium.launch_persistent_context(**launch_kwargs)
        except Exception as e:
            console.print(f"[yellow]Notice on launch: {e}. Re-cleaning locks and retrying...[/yellow]")
            self._cleanup_profile_locks()
            try:
                self.context = self._playwright.chromium.launch_persistent_context(**launch_kwargs)
            except Exception as e2:
                if channel:
                    console.print(f"[yellow]Could not launch with channel '{channel}': {e2}. Falling back to bundled Chromium.[/yellow]")
                    launch_kwargs.pop("channel", None)
                    self._cleanup_profile_locks()
                    self.context = self._playwright.chromium.launch_persistent_context(**launch_kwargs)
                else:
                    raise

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        return self.page

    def navigate_and_handle_captcha(self, url: str) -> None:
        """Navigate to URL and prompt user if CAPTCHA or Cloudflare is detected."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        console.print(f"[bold green]Navigating to:[/bold green] {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Check for CAPTCHA indicators
        self.check_and_prompt_captcha()

    def is_blocked(self) -> bool:
        """Check if current page is blocked by CAPTCHA, Cloudflare, or FAO verification."""
        if not self.page or self.page.is_closed():
            return False
        try:
            url = self.page.url.lower()
            if "/captcha" in url:
                return True
            content = self.page.content().lower()
            title = self.page.title().lower()
            captcha_indicators = [
                "cloudflare",
                "turnstile",
                "just a moment",
                "vérification",
                "captcha",
                "friendly captcha",
                "my-widget-mount",
                "frc-captcha",
                "robot",
                "access denied",
                "security check",
                "challenge",
            ]
            return any(ind in title or ind in content for ind in captcha_indicators)
        except Exception:
            return False

    def check_and_prompt_captcha(self) -> None:
        """Inspect page for CAPTCHA / Cloudflare challenge, prompt terminal if needed."""
        if not self.page or self.page.is_closed():
            return

        try:
            # Give page a short moment to render challenge if any
            self.page.wait_for_timeout(2000)
        except Exception:
            return

        if self.is_blocked():
            console.print("\n" + "=" * 70, style="bold yellow")
            console.print("[bold yellow]ATTENTION: ACCESS CHALLENGE / CAPTCHA DETECTED[/bold yellow]")
            console.print("Please switch to the open Chromium window and complete the Friendly Captcha / challenge.")
            console.print("=" * 70 + "\n", style="bold yellow")

            # Try to auto-start Friendly Captcha if present
            self._try_trigger_friendly_captcha()

            # Wait for user input or poll if non-interactive daemon
            import sys
            if sys.stdin and hasattr(sys.stdin, "isatty") and sys.stdin.isatty():
                try:
                    input(">>> Press [ENTER] in this terminal AFTER you have solved the CAPTCHA in the browser (or wait for auto-detection)... ")
                except EOFError:
                    pass

            self.wait_until_unblocked()

            # Confirm page has transitioned
            try:
                if self.page and not self.page.is_closed():
                    self.page.wait_for_timeout(3000)
                console.print("[bold green]Resuming session after verification![/bold green]")
            except Exception:
                pass
        else:
            console.print("[green]No CAPTCHA challenge detected or session already authenticated.[/green]")

    def _try_trigger_friendly_captcha(self) -> None:
        """Attempt to activate Friendly Captcha widget automatically if possible."""
        try:
            if not self.page or self.page.is_closed():
                return
            for frame in self.page.frames:
                btn = frame.locator("button.frc-button, input[type='button'], .frc-button")
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click(timeout=1000)
                    console.print("[dim]Clicked Friendly Captcha activate button.[/dim]")
        except Exception:
            pass

    def wait_until_unblocked(self, timeout_seconds: int = 180) -> None:
        """Poll until CAPTCHA or challenge disappears."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if not self.page or self.page.is_closed():
                return
            self._try_trigger_friendly_captcha()
            if not self.is_blocked():
                return
            time.sleep(2)
        console.print("[red]Timed out waiting for challenge resolution.[/red]")
        if self.is_blocked():
            raise AntiBotChallengeException(
                "Timed out waiting 180s for anti-bot / Friendly Captcha resolution on page. "
                "Halting process to prevent silent data ingestion failure."
            )

    def close(self) -> None:
        """Gracefully close browser and persistent context."""
        if self.context:
            self.context.close()
        if self._playwright:
            self._playwright.stop()
        console.print("[dim]Browser session closed.[/dim]")
