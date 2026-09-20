"""Batch collector and validator for Geneva FAO real-estate transaction notices (rubrique 133)."""

import sys
import time
import random
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import pymupdf

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from fao_transactions.config import settings
from fao_transactions.collector.browser import BrowserManager
from fao_transactions.storage.db import Database
from fao_transactions.parser.pdf_parser import FaoPdfParser

console = Console(legacy_windows=False)


class TransactionBatchCollector:
    """Collects real-estate transaction PDFs across all pages with antibot validation and safety pauses."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        headless: bool = True,
        delay_min: float = 2.5,
        delay_max: float = 4.5,
    ):
        self.output_dir = output_dir or Path("data/raw/transactions")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.db = Database()
        self.parser = FaoPdfParser()

    def _validate_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Verify that downloaded file is a genuine PDF and not an antibot/challenge splash page."""
        if not file_path.exists() or file_path.stat().st_size < 500:
            return {"valid": False, "reason": "File missing or too small (<500B)"}

        # Check magic bytes
        with open(file_path, "rb") as f:
            header = f.read(10)
        if not header.startswith(b"%PDF-"):
            # Check if it is HTML
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2000).lower()
            if any(k in content for k in ["cloudflare", "turnstile", "just a moment", "challenge", "vérification"]):
                return {"valid": False, "reason": "Antibot/Cloudflare HTML challenge page detected"}
            return {"valid": False, "reason": "Invalid magic bytes (not a PDF)"}

        # Verify PyMuPDF can open and read text
        try:
            doc = pymupdf.open(file_path)
            page_count = len(doc)
            text = "\n".join([page.get_text("text") for page in doc])
            doc.close()

            lower = text.lower()
            if "registre foncier" not in lower and "lacc" not in lower and "transaction" not in lower:
                return {
                    "valid": True,
                    "pages": page_count,
                    "warning": "PDF opened but lacks standard real-estate header keywords",
                    "text_sample": text[:150],
                }

            return {"valid": True, "pages": page_count, "text_sample": text[:200]}
        except Exception as e:
            return {"valid": False, "reason": f"PDF corruption / read error: {e}"}

    def run(
        self,
        max_notices: Optional[int] = None,
        max_pages: Optional[int] = None,
        initial_check_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Collect real estate notices across pages.
        If initial_check_only=True, runs a pilot of 5-10 notices to validate integrity.
        """
        limit = 5 if initial_check_only else max_notices
        max_p = 1 if initial_check_only else max_pages

        console.rule("[bold cyan]Geneva FAO Real-Estate Transactions Collector[/bold cyan]")
        console.print(f"Target category: [bold]Registre foncier / Transaction immobilière (rubrique 133)[/bold]")
        console.print(f"Output folder: [dim]{self.output_dir.resolve()}[/dim]")
        console.print(f"Mode: [bold yellow]{'Initial Validation Round (Pilot)' if initial_check_only else 'Full Batch Collection'}[/bold yellow]")
        console.print(f"Safety pause: {self.delay_min:.1f}s - {self.delay_max:.1f}s between requests\n")

        manager = BrowserManager(headless=self.headless)
        page = manager.start()

        stats = {
            "pages_scanned": 0,
            "notices_discovered": 0,
            "downloads_attempted": 0,
            "valid_pdfs": 0,
            "antibot_errors": 0,
            "parsed_records": 0,
            "files": [],
        }

        try:
            base_search = f"{settings.fao.base_url.rstrip('/')}/recherche?rubrique=133"
            current_page_idx = 0

            while True:
                page_url = f"{base_search}&page={current_page_idx}" if current_page_idx > 0 else base_search
                console.print(f"[cyan]Scanning page {current_page_idx + 1}:[/cyan] {page_url}")

                page.goto(page_url, wait_until="domcontentloaded", timeout=60000)
                manager.check_and_prompt_captcha()
                page.wait_for_timeout(2000)

                # Find all notice links on current page
                links = page.eval_on_selector_all(
                    "a[href*='/avis/']",
                    "elements => elements.map(e => e.href)"
                )
                # Deduplicate links preserving order
                unique_links = list(dict.fromkeys(links))
                stats["pages_scanned"] += 1

                if not unique_links:
                    console.print("[yellow]No more notices found on this page. Stopping.[/yellow]")
                    break

                console.print(f"Found [bold]{len(unique_links)}[/bold] transaction notice links on page {current_page_idx + 1}.")

                for notice_url in unique_links:
                    match = re.search(r"/avis/([a-f0-9\-]+)", notice_url)
                    if not match:
                        continue
                    uuid = match.group(1)
                    stats["notices_discovered"] += 1

                    download_url = f"https://fao.ge.ch/avis-download/{uuid}"
                    target_pdf = self.output_dir / f"notice_{uuid}.pdf"

                    # Check if already downloaded and valid
                    if target_pdf.exists() and target_pdf.stat().st_size > 1000:
                        val = self._validate_pdf(target_pdf)
                        if val["valid"]:
                            console.print(f"[dim]Already downloaded & valid: {target_pdf.name}[/dim]")
                            stats["valid_pdfs"] += 1
                            if limit and stats["valid_pdfs"] >= limit:
                                break
                            continue

                    # Download with safety pause
                    pause = random.uniform(self.delay_min, self.delay_max)
                    console.print(f"[dim]Safety pause: {pause:.1f}s...[/dim]")
                    time.sleep(pause)

                    console.print(f"[cyan]Downloading notice PDF:[/cyan] {uuid}")
                    stats["downloads_attempted"] += 1

                    try:
                        with page.expect_download(timeout=60000) as download_info:
                            page.evaluate(f"window.location.href = '{download_url}'")
                        download = download_info.value
                        download.save_as(str(target_pdf))

                        # Validate file immediately
                        validation = self._validate_pdf(target_pdf)
                        if validation["valid"]:
                            stats["valid_pdfs"] += 1
                            console.print(f"[bold green][OK] Valid PDF confirmed:[/bold green] {target_pdf.name} ({target_pdf.stat().st_size / 1024:.1f} KB)")
                            stats["files"].append(str(target_pdf))

                            # Try parsing transaction
                            records = self.parser.parse_pdf(target_pdf)
                            if records:
                                stats["parsed_records"] += len(records)
                                r = records[0]
                                console.print(f"    [green]-> Extracted:[/green] {r.commune} | Parcel {r.parcel_number} | {r.transaction_type or 'Transaction'} | Surface: {r.surface_m2} m2")
                        else:
                            stats["antibot_errors"] += 1
                            console.print(f"[bold red][FAIL] Validation Failed for {target_pdf.name}:[/bold red] {validation.get('reason')}")
                    except Exception as e:
                        console.print(f"[bold red]Error downloading {uuid}:[/bold red] {e}")

                    if limit and stats["valid_pdfs"] >= limit:
                        console.print(f"[green]Reached target limit of {limit} valid transaction PDFs.[/green]")
                        break

                if limit and stats["valid_pdfs"] >= limit:
                    break

                # Check if next page exists
                next_exists = page.query_selector("a[rel='next'], li.pager-next a, .pager__item--next a, ul.pagination li:last-child a")
                if not next_exists or (max_p and current_page_idx + 1 >= max_p):
                    break

                current_page_idx += 1

            # Summary report
            console.rule("[bold green]Validation & Batch Results[/bold green]")
            table = Table(title="Execution Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="bold")
            table.add_row("Pages Scanned", str(stats["pages_scanned"]))
            table.add_row("Notices Discovered", str(stats["notices_discovered"]))
            table.add_row("Downloads Attempted", str(stats["downloads_attempted"]))
            table.add_row("Valid Genuine PDFs", f"[green]{stats['valid_pdfs']}[/green]")
            table.add_row("Antibot / Invalid Errors", f"[red]{stats['antibot_errors']}[/red]")
            table.add_row("Parsed Real-Estate Transactions", f"[bold cyan]{stats['parsed_records']}[/bold cyan]")
            console.print(table)

            return stats

        finally:
            manager.close()
