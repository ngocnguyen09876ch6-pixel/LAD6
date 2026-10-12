from datetime import datetime
from src.api_client import fetch_all_pages
from src.config import ROOT
from src.logger import get_logger
import json
log = get_logger(__name__)


def run():
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_dir = ROOT / "data" / "raw" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_payloads = []

    rows = fetch_all_pages(
        resource="orders",
        page_size=100,
        raw_payloads=raw_payloads,
    )
    raw_file = raw_dir / "orders.json"

    with raw_file.open("w", encoding="utf-8") as f:
        json.dump(raw_payloads, f, ensure_ascii=False, indent=2)

    log.info("RAW saved to %s", raw_file)

    log.info(
        "Fetched resource=orders rows=%s pages=%s run_id=%s",
        len(rows),
        len(raw_payloads),
        run_id,
    )
if __name__ == "__main__":
    run()