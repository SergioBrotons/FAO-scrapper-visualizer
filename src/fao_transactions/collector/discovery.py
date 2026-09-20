"""FAO Geneva portal discovery module.

Inspects https://fao.ge.ch using Playwright, validates access,
handles potential CAPTCHA/bot checks, and saves DOM/snapshots.
"""

from pathlib import Path
import json
from rich.console import Console
from rich.table import Table

from fao_transactions.config import settings
from fao_transactions.collector.browser import BrowserManager

console = Console()


def run_discovery(url: str = None) -> dict:
    """Run interactive discovery on FAO portal."""
    target_url = url or settings.fao.base_url
    discovery_dir = Path(settings.storage.discovery_dir)
    discovery_dir.mkdir(parents=True, exist_ok=True)

    console.rule("[bold cyan]FAO Portal Access & Discovery[/bold cyan]")
    console.print(f"Target: [bold]{target_url}[/bold]")
    console.print(f"Discovery artifacts directory: [dim]{discovery_dir.resolve()}[/dim]\n")

    manager = BrowserManager()
    page = manager.start()

    results = {
        "url": target_url,
        "title": None,
        "status": "unknown",
        "links_found": 0,
        "forms_found": 0,
        "artifacts": {},
    }

    try:
        manager.navigate_and_handle_captcha(target_url)

        # Allow extra time for client-side rendering / redirects
        page.wait_for_timeout(3000)

        title = page.title()
        current_url = page.url
        results["title"] = title
        results["current_url"] = current_url

        console.print(f"[green]✔ Loaded page:[/green] {title}")
        console.print(f"[dim]Final URL:[/dim] {current_url}\n")

        # Capture screenshot
        screenshot_path = discovery_dir / "fao_portal.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        results["artifacts"]["screenshot"] = str(screenshot_path)
        console.print(f"[green]✔ Screenshot saved:[/green] {screenshot_path.name}")

        # Capture HTML content
        html_path = discovery_dir / "fao_portal.html"
        html_content = page.content()
        html_path.write_text(html_content, encoding="utf-8")
        results["artifacts"]["html"] = str(html_path)
        console.print(f"[green]✔ HTML snapshot saved:[/green] {html_path.name}")

        # Extract navigation links and search forms
        links = page.eval_on_selector_all(
            "a[href]",
            "elements => elements.map(e => ({ text: e.innerText.trim(), href: e.href }))"
        )
        # Filter for relevant keywords
        keywords = ["mutation", "propriete", "registre", "foncier", "immeuble", "avis", "recherche", "fao"]
        relevant_links = [
            l for l in links
            if any(k in (l["text"] or "").lower() or k in (l["href"] or "").lower() for k in keywords)
        ]

        forms = page.eval_on_selector_all(
            "form",
            "elements => elements.map(e => ({ action: e.action, method: e.method, id: e.id, inputs: e.querySelectorAll('input, select, button').length }))"
        )

        results["links_found"] = len(links)
        results["relevant_links"] = relevant_links[:20]
        results["forms_found"] = len(forms)
        results["forms"] = forms

        # Save summary JSON
        summary_path = discovery_dir / "discovery_summary.json"
        summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        results["artifacts"]["summary"] = str(summary_path)

        # Print report
        table = Table(title="Relevant Links Detected")
        table.add_column("Text", style="cyan")
        table.add_column("URL", style="dim")

        for l in relevant_links[:10]:
            table.add_row(l["text"] or "(no text)", l["href"])

        if relevant_links:
            console.print(table)
        else:
            console.print("[yellow]No specific mutation/cadastral links found on top-level home page.[/yellow]")

        results["status"] = "success"
        console.print("\n[bold green]Discovery completed successfully![/bold green]")
        return results

    except Exception as e:
        console.print(f"[bold red]Discovery failed:[/bold red] {e}")
        results["status"] = "failed"
        results["error"] = str(e)
        raise
    finally:
        manager.close()
