"""Playwright persistent browser session manager."""

from pathlib import Path
from typing import Optional
from playwright.sync_api import sync_playwright, BrowserContext, Page
from rich.console import Console

from fao_transactions.config import settings

console = Console()


class BrowserManager:
    """Manages headed Playwright Chromium instance with persistent context."""

    def __init__(self, profile_dir: Optional[str] = None, headless: Optional[bool] = None):
        self.profile_dir = Path(profile_dir or settings.browser.profile_dir).resolve()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless if headless is not None else settings.browser.headless
        self._playwright = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Page:
        """Launch Chromium with persistent context."""
        console.print(f"[bold cyan]Starting Chromium[/bold cyan] (Profile: {self.profile_dir}, Headless: {self.headless})")
        self._playwright = sync_playwright().start()

        self.context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={
                "width": settings.browser.viewport_width,
                "height": settings.browser.viewport_height,
            },
            slow_mo=settings.browser.slow_mo,
            accept_downloads=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )

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

    def check_and_prompt_captcha(self) -> None:
        """Inspect page for CAPTCHA / Cloudflare challenge, prompt terminal if needed."""
        if not self.page:
            return

        # Give page a short moment to render challenge if any
        self.page.wait_for_timeout(2000)
        content = self.page.content().lower()
        title = self.page.title().lower()

        captcha_indicators = [
            "cloudflare",
            "turnstile",
            "just a moment",
            "vérification",
            "captcha",
            "robot",
            "access denied",
            "security check",
            "challenge",
        ]

        needs_solution = any(ind in title or ind in content for ind in captcha_indicators)

        if needs_solution:
            console.print("\n" + "=" * 70, style="bold yellow")
            console.print("[bold yellow]ATTENTION: ACCESS CHALLENGE / CAPTCHA DETECTED[/bold yellow]")
            console.print("Please switch to the open Chromium window and complete the challenge manually.")
            console.print("=" * 70 + "\n", style="bold yellow")

            # Wait for user input in terminal
            try:
                input(">>> Press [ENTER] in this terminal AFTER you have solved the CAPTCHA in the browser... ")
            except EOFError:
                # If non-interactive stdin, loop wait until challenge is gone
                console.print("[yellow]Non-interactive input detected; polling until page leaves challenge state...[/yellow]")
                self.wait_until_unblocked()

            # Confirm page has transitioned
            self.page.wait_for_timeout(3000)
            console.print("[bold green]Resuming session after manual verification![/bold green]")
        else:
            console.print("[green]No CAPTCHA challenge detected or session already authenticated.[/green]")

    def wait_until_unblocked(self, timeout_seconds: int = 120) -> None:
        """Poll until CAPTCHA or challenge disappears."""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            content = self.page.content().lower()
            title = self.page.title().lower()
            blocked = any(ind in title or ind in content for ind in ["just a moment", "challenge", "turnstile"])
            if not blocked:
                return
            time.sleep(2)
        console.print("[red]Timed out waiting for challenge resolution.[/red]")

    def close(self) -> None:
        """Gracefully close browser and persistent context."""
        if self.context:
            self.context.close()
        if self._playwright:
            self._playwright.stop()
        console.print("[dim]Browser session closed.[/dim]")
