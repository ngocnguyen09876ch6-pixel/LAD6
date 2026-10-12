import requests
import time
from src.config import SETTINGS
from src.logger import get_logger

log = get_logger(__name__)
def get(resource: str, page: int = 1, page_size: int = 100,updated_after: str | None = None) -> dict:
    url = f"{SETTINGS.api_url.rstrip('/')}/{resource.lstrip('/')}"
    headers = {"X-API-Key": SETTINGS.api_key}
    params = {"page": page, "page_size": page_size}
    if updated_after is not None:
        params["updated_after"] = updated_after
    max_retries = 3
    backoff_seconds = 1
    for attempt in range(1, max_retries + 2): #thử 4 lần 3 lần đấu nếu lỗi thì retry đến lần 4 thì error
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=10,
            )

            response.raise_for_status()
            payload = response.json()
            return payload

        except (requests.RequestException, ValueError) as exc:
    
            if attempt > max_retries:
                raise RuntimeError(
                 f"API failed after {max_retries} attempts: {resource} page {page}") from exc

            wait_seconds = backoff_seconds * (2 ** (attempt - 1))

            log.warning(
                "API request failed: resource=%s page=%s attempt=%s/%s "
                "error=%s retry_in=%ss",
                resource,
                page,
                attempt,
                max_retries,
                exc,
                wait_seconds,
            )

            time.sleep(wait_seconds)

def fetch_all_pages(
    resource: str,
    page_size: int = 100,
    updated_after: str | None = None,
    raw_payloads: list[dict] | None = None,
):
    page = 1
    rows = []
    while True:
        payload = get(resource, page=page, page_size=page_size, updated_after=updated_after)
        page_rows = payload.get("data", [])
        rows.extend(page_rows)
        log.info(
            "resource=%s page=%s rows=%s total_so_far=%s",
            resource,
            page,
            len(page_rows),
            len(rows)
            )
        if raw_payloads is not None:
            raw_payloads.append(payload)
        if not payload.get("has_next"):
            break
        page += 1
    return rows
   