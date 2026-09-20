import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table

from fao_transactions.config import settings
from fao_transactions.collector.browser import BrowserManager

console = Console(legacy_windows=False)


def download_quotidiennes(limit: int = 3, headless: bool = False) -> List[Path]:
    """Download the latest daily editions (Quotidiennes) from FAO Geneva."""
    raw_dir = Path(settings.storage.raw_pdf_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    manager = BrowserManager(headless=headless)
    page = manager.start()

    downloaded_files: List[Path] = []

    try:
        url = f"{settings.fao.base_url.rstrip('/')}/quotidiennes"
        console.rule("[bold cyan]Fetching FAO Quotidiennes[/bold cyan]")
        console.print(f"Target URL: [bold]{url}[/bold]")

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        manager.check_and_prompt_captcha()
        page.wait_for_timeout(3000)

        # Find all download links matching /dwnlquotidienne/
        links = page.eval_on_selector_all(
            "a[href*='dwnlquotidienne']",
            "elements => elements.map(e => ({ text: e.innerText.trim(), href: e.href }))"
        )

        console.print(f"[green]Found {len(links)} quotidienne download links.[/green]")

        table = Table(title="Available Quotidiennes")
        table.add_column("Title / Date", style="cyan")
        table.add_column("Download URL", style="dim")

        for item in links[:limit]:
            table.add_row(item["text"] or "Quotidienne", item["href"])
        console.print(table)

        # Download each PDF
        for idx, item in enumerate(links[:limit]):
            href = item["href"]
            title_text = item["text"] or f"quotidienne_{idx+1}"
            safe_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in title_text).strip("_")
            target_path = raw_dir / f"{safe_name}.pdf"

            if target_path.exists() and target_path.stat().st_size > 1000:
                console.print(f"[yellow]File already exists:[/yellow] {target_path.name}")
                downloaded_files.append(target_path)
                continue

            console.print(f"[cyan]Downloading:[/cyan] {title_text} -> {target_path.name}")
            try:
                with page.expect_download(timeout=60000) as download_info:
                    # Navigate or trigger click
                    page.evaluate(f"window.location.href = '{href}'")
                download = download_info.value
                download.save_as(str(target_path))
                console.print(f"[bold green][OK] Saved:[/bold green] {target_path.name} ({target_path.stat().st_size / 1024:.1f} KB)")
                downloaded_files.append(target_path)
            except Exception as e:
                console.print(f"[red]Error downloading {href}:[/red] {e}")

        return downloaded_files

    finally:
        manager.close()
