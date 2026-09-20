"""Command Line Interface for Geneva Property Transactions Pipeline."""

import sys
from typing import Optional

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import typer
from rich.console import Console

app = typer.Typer(
    name="fao-transactions",
    help="Geneva FAO Real-Estate Transactions Pipeline and SITG Cadastral Geodata Enricher",
    add_completion=False,
)
console = Console(legacy_windows=False)


@app.command()
def discover(
    url: Optional[str] = typer.Option(
        None,
        "--url",
        "-u",
        help="Target FAO portal URL (defaults to configured FAO base URL)",
    )
):
    """Discover FAO portal structure, test Playwright browser session, and handle CAPTCHAs."""
    from fao_transactions.collector.discovery import run_discovery

    try:
        run_discovery(url=url)
    except Exception as e:
        console.print(f"[bold red]Discovery command exited with error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def collect_transactions(
    pilot: bool = typer.Option(False, "--pilot", "-p", help="Initial validation round (5 notices) to test data vs antibot"),
    limit: Optional[int] = typer.Option(None, "--limit", "-l", help="Maximum number of transaction PDFs to download"),
    max_pages: Optional[int] = typer.Option(None, "--max-pages", help="Maximum search pages to scan"),
    delay_min: float = typer.Option(2.5, "--delay-min", help="Minimum safety pause in seconds"),
    delay_max: float = typer.Option(4.5, "--delay-max", help="Maximum safety pause in seconds"),
    headless: bool = typer.Option(True, "--headless/--headed", help="Run browser in headless or headed mode"),
):
    """Download official Geneva real-estate transaction PDFs with safety pauses and validation."""
    from fao_transactions.collector.transaction_batch import TransactionBatchCollector

    collector = TransactionBatchCollector(
        headless=headless,
        delay_min=delay_min,
        delay_max=delay_max,
    )
    collector.run(
        max_notices=limit,
        max_pages=max_pages,
        initial_check_only=pilot,
    )


@app.command()
def collect(
    limit: int = typer.Option(3, "--limit", "-l", help="Number of recent publications to download"),
    headless: bool = typer.Option(False, "--headless", help="Run browser in headless mode"),
):
    """Download latest FAO Quotidienne PDF publications."""
    from fao_transactions.collector.downloader import download_quotidiennes

    downloaded = download_quotidiennes(limit=limit, headless=headless)
    console.print(f"[bold green]Downloaded {len(downloaded)} files.[/bold green]")


@app.command()
def parse(
    pdf_path: str = typer.Argument(..., help="Path to an FAO notice PDF file"),
):
    """Parse an FAO PDF notice and display extracted transactions."""
    from pathlib import Path
    from fao_transactions.parser.pdf_parser import FaoPdfParser

    file_path = Path(pdf_path)
    if not file_path.exists():
        console.print(f"[bold red]File not found:[/bold red] {pdf_path}")
        raise typer.Exit(code=1)

    parser = FaoPdfParser()
    records = parser.parse_pdf(file_path)
    console.print(f"[bold green]Parsed {len(records)} transaction records from {file_path.name}.[/bold green]")
    for idx, r in enumerate(records[:10]):
        console.print(f"[bold cyan]#{idx+1}:[/bold cyan] Commune={r.commune} | Parcel={r.parcel_number} | Price={r.price_raw} (CHF {r.price_chf}) | Surface={r.surface_m2}m²")


@app.command()
def enrich(
    commune: str = typer.Argument(..., help="Commune name (e.g., 'Carouge' or 'Genève')"),
    parcel: str = typer.Argument(..., help="Parcel number (e.g., '1234')"),
    section: Optional[str] = typer.Option(None, "--section", "-s", help="Cadastral section for Genève (e.g., 'Plainpalais')"),
):
    """Query SITG cadastral geodata for a specific parcel."""
    from fao_transactions.cadastre.sitg_client import SitgClient

    client = SitgClient()
    console.print(f"Querying SITG for [bold]{commune}[/bold] parcel [bold]{parcel}[/bold]...")
    feature = client.query_parcel(commune=commune, parcel_number=parcel, section=section)
    if feature:
        props = feature.get("properties", {})
        console.print(f"[bold green][OK] Parcel Found![/bold green]")
        console.print(f"  [cyan]EGRID:[/cyan] {props.get('EGRID')}")
        console.print(f"  [cyan]IdentDN:[/cyan] {props.get('IDENTDN')}")
        console.print(f"  [cyan]Surface cadastrale:[/cyan] {props.get('SUPERFICIE') or props.get('SURFACE')} m2")
        console.print(f"  [cyan]Centroid LV95:[/cyan] {feature.get('centroid_lv95')}")
        console.print(f"  [cyan]Centroid WGS84 (lat/lon):[/cyan] {feature.get('centroid_wgs84')}")
    else:
        console.print("[yellow]No parcel found in SITG for this query.[/yellow]")

@app.command()
def enrich_all(
    workers: int = typer.Option(8, "--workers", "-w", help="Number of concurrent worker threads for SITG REST queries"),
    export_deliverables: bool = typer.Option(True, "--export/--no-export", help="Automatically regenerate CSV/Excel/GeoJSON exports after enrichment"),
):
    """Enrich all transactions in SQLite with official SITG cadastral geodata (coordinates, surfaces, EGRID)."""
    from fao_transactions.cadastre.enricher import CadastralEnricher
    from fao_transactions.processor import UnifiedBatchProcessor

    enricher = CadastralEnricher()
    enricher.enrich_all(workers=workers)
    enricher.enrich_zoning_and_buildings(workers=workers * 2)
    if export_deliverables:
        proc = UnifiedBatchProcessor()
        proc.export_data()


@app.command()
def enrich_zones(
    workers: int = typer.Option(16, "--workers", "-w", help="Number of concurrent worker threads for SITG REST queries"),
    export_deliverables: bool = typer.Option(True, "--export/--no-export", help="Automatically regenerate CSV/Excel/GeoJSON exports after enrichment"),
):
    """Enrich all geocoded transactions with Geneva zoning (SIT_ZONE_AMENAG) and building attributes (CAD_BATIMENT_HORSOL)."""
    from fao_transactions.cadastre.enricher import CadastralEnricher
    from fao_transactions.processor import UnifiedBatchProcessor

    enricher = CadastralEnricher()
    enricher.enrich_zoning_and_buildings(workers=workers)
    if export_deliverables:
        proc = UnifiedBatchProcessor()
        proc.export_data()


@app.command()
def process_all(
    workers: int = typer.Option(4, "--workers", "-w", help="Number of CPU workers for multiprocessing parsing"),
    export_deliverables: bool = typer.Option(True, "--export/--no-export", help="Automatically generate CSV/Excel/GeoJSON exports"),
):
    """Batch parse all 8,700+ transaction PDFs (both Registre Foncier and LDTR archives) and save to SQLite."""
    from fao_transactions.processor import UnifiedBatchProcessor

    proc = UnifiedBatchProcessor()
    records = proc.parse_all_pdfs(workers=workers)
    if records:
        proc.save_to_database(records)
        if export_deliverables:
            proc.export_data()


@app.command()
def generate_map(
    output_path: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output path for the HTML map"),
):
    """Generate a standalone interactive HTML map with Swisstopo layers, SITG zoning, and transaction cards."""
    from fao_transactions.visualization.map_builder import build_interactive_map

    map_path = build_interactive_map(output_path=output_path)
    console.print(f"[bold green][OK] Interactive map generated:[/bold green] {map_path}")


@app.command()
def export(
    with_map: bool = typer.Option(True, "--map/--no-map", help="Also generate the interactive HTML map"),
):
    """Export current SQLite database records to CSV, Excel, GeoJSON, and interactive HTML map."""
    from fao_transactions.processor import UnifiedBatchProcessor
    from fao_transactions.visualization.map_builder import build_interactive_map

    proc = UnifiedBatchProcessor()
    proc.export_data()
    if with_map:
        build_interactive_map()


@app.command()
def scan(
    mode: str = typer.Option("quick", "--mode", "-m", help="Scan mode: 'quick' (recent), 'standard', or 'exhaustive'"),
):
    """Run incremental multi-portal scan with SHA-256 deduplication and historic data preservation."""
    from fao_transactions.collector.sync_engine import sync_manager
    import time

    console.rule("[bold #C9A24D]Starting Cytria Portal Scan & Refresh[/bold #C9A24D]")
    sync_manager.start_scan(mode=mode)
    
    while sync_manager.is_scanning:
        status = sync_manager.get_status()
        console.print(f"[{status['progress_pct']}%] {status['current_step']}", end="\r")
        time.sleep(0.5)

    status = sync_manager.get_status()
    console.print(f"\n[bold green][OK] Scan completed:[/bold green] {status['new_inserted']} new records, {status['duplicates_skipped']} duplicates preserved.")


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to serve the interactive web intelligence visualizer"),
):
    """Start local Cytria Intelligence web server with REST synchronization API."""
    from fao_transactions.server import run_server
    run_server(port=port)


def main():
    app()


if __name__ == "__main__":
    main()

