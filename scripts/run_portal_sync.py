"""Runner for Cytria multi-portal real-time synchronization with Playwright Chromium."""

import sys
import time
import json
import argparse
from pathlib import Path

# Add project root and src to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / ".venv" / "Lib" / "site-packages"))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fao_transactions.collector.sync_engine import sync_manager


def main():
    parser = argparse.ArgumentParser(description="Cytria Multi-Portal Synchronization Runner")
    parser.add_argument("--mode", default="quick", choices=["quick", "standard", "exhaustive"])
    parser.add_argument("--source", default="ALL", choices=["ALL", "FAO", "CADASTRE", "AGENCY_BI"])
    parser.add_argument("--headed", action="store_true", default=True)
    parser.add_argument("--headless", action="store_true", default=False)
    args = parser.parse_args()

    headed = False if args.headless else True

    options = {
        "source": args.source,
        "headed": headed,
        "fao": args.source in ["FAO", "ALL"],
        "sitg": args.source in ["CADASTRE", "ALL"],
        "agencies": args.source in ["AGENCY_BI", "ALL"],
    }

    start_payload = {
        "type": "start",
        "is_scanning": True,
        "progress_pct": 5,
        "current_step": "Initialisation du moteur de scan...",
        "historical_preserved": 8724,
        "scanned_notices": 0,
        "new_inserted": 0,
        "duplicates_skipped": 0,
        "new_logs": [
            f"[SYS] Démarrage du scan Cytria ({args.mode}, source={args.source}, headed={headed})",
            "[FAO] Mode fenêtré activé : le navigateur Chromium s'ouvre sur le bureau pour validation des accès."
        ]
    }
    state_file = root_dir / "data" / "state" / "sync_status.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    def write_state(data: dict):
        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    write_state(start_payload)

    success = sync_manager.start_scan(mode=args.mode, options=options)
    if not success:
        err_payload = {
            "type": "error",
            "is_scanning": False,
            "progress_pct": 0,
            "current_step": "Erreur : scan déjà en cours.",
            "new_logs": ["[SYS Erreur] Un scan est déjà actif sur le serveur."]
        }
        print(f"CYTRIA_EVENT:{json.dumps(err_payload)}", flush=True)
        write_state(err_payload)
        sys.exit(1)

    last_log_idx = 0
    last_pct = -1
    last_step = ""

    is_interactive = sys.stdout.isatty() if hasattr(sys.stdout, "isatty") else True

    while sync_manager.is_scanning:
        status = sync_manager.get_status()
        all_logs = status.get("logs", [])
        new_logs = all_logs[last_log_idx:]
        last_log_idx = len(all_logs)

        current_pct = status.get("progress_pct", 5)
        current_step = status.get("current_step", "Traitement en cours...")

        # Print human-readable logs to terminal
        for log_line in new_logs:
            print(log_line, flush=True)

        # Update state file and event stream only on meaningful change
        if current_pct != last_pct or current_step != last_step or new_logs:
            last_pct = current_pct
            last_step = current_step

            payload = {
                "type": "progress",
                "is_scanning": True,
                "progress_pct": current_pct,
                "current_step": current_step,
                "historical_preserved": status.get("historical_preserved", 8724),
                "scanned_notices": status.get("scanned_notices", 0),
                "new_inserted": status.get("new_inserted", 0),
                "duplicates_skipped": status.get("duplicates_skipped", 0),
                "logs": all_logs[-35:],
                "new_logs": new_logs,
            }
            if not is_interactive:
                print(f"CYTRIA_EVENT:{json.dumps(payload)}", flush=True)
            write_state(payload)

        time.sleep(0.5)

    final_status = sync_manager.get_status()
    all_logs = final_status.get("logs", [])
    new_logs = all_logs[last_log_idx:]

    for log_line in new_logs:
        print(log_line, flush=True)

    payload = {
        "type": "done",
        "is_scanning": False,
        "progress_pct": 100,
        "current_step": final_status.get("current_step", "Synchronisation terminée avec succès !"),
        "historical_preserved": final_status.get("historical_preserved", 8724),
        "scanned_notices": final_status.get("scanned_notices", 0),
        "new_inserted": final_status.get("new_inserted", 0),
        "duplicates_skipped": final_status.get("duplicates_skipped", 0),
        "logs": all_logs[-35:],
        "new_logs": new_logs,
    }
    if not is_interactive:
        print(f"CYTRIA_EVENT:{json.dumps(payload)}", flush=True)
    write_state(payload)


if __name__ == "__main__":
    main()
