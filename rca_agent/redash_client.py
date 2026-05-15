import os
import time
import json
import hashlib
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REDASH_BASE_URL = os.getenv("REDASH_BASE_URL")
REDASH_API_KEY = os.getenv("REDASH_API_KEY")

CACHE_DIR = Path(".cache/redash")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours


def _cache_key(query_id: int, params: dict):
    raw = json.dumps(
        {"query_id": query_id, "params": params},
        sort_keys=True,
        default=str,
    )
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def _read_cache(cache_file: Path):
    if not cache_file.exists():
        return None

    age = time.time() - cache_file.stat().st_mtime
    if age > CACHE_TTL_SECONDS:
        return None

    return json.loads(cache_file.read_text(encoding="utf-8"))


def _write_cache(cache_file: Path, rows):
    cache_file.write_text(
        json.dumps(rows, indent=2, default=str),
        encoding="utf-8",
    )


def run_redash_query(query_id: int, params: dict, use_cache: bool = True):
    cache_file = CACHE_DIR / f"{_cache_key(query_id, params)}.json"

    if use_cache:
        cached_rows = _read_cache(cache_file)
        if cached_rows is not None:
            print(f"Cache hit: query {query_id}")
            return cached_rows

    headers = {"Authorization": f"Key {REDASH_API_KEY}"}

    url = f"{REDASH_BASE_URL}/api/queries/{query_id}/results"

    response = requests.post(
        url,
        headers=headers,
        json={"parameters": params, "max_age": 0},
        timeout=90,
    )

    if response.status_code != 200:
        print("REDASH ERROR:")
        print(response.text)
        response.raise_for_status()

    data = response.json()

    if "query_result" in data:
        rows = data["query_result"]["data"]["rows"]
        _write_cache(cache_file, rows)
        return rows

    job = data.get("job")
    if not job:
        raise Exception(f"Unexpected Redash response: {data}")

    job_id = job["id"]

    for _ in range(90):
        job_url = f"{REDASH_BASE_URL}/api/jobs/{job_id}"
        job_response = requests.get(job_url, headers=headers, timeout=30)
        job_response.raise_for_status()

        job_data = job_response.json()["job"]

        if job_data["status"] == 3:
            query_result_id = job_data["query_result_id"]

            result_url = f"{REDASH_BASE_URL}/api/query_results/{query_result_id}"
            result_response = requests.get(result_url, headers=headers, timeout=30)
            result_response.raise_for_status()

            result_data = result_response.json()
            rows = result_data["query_result"]["data"]["rows"]

            _write_cache(cache_file, rows)
            return rows

        if job_data["status"] == 4:
            raise Exception(f"Redash query failed: {job_data}")

        time.sleep(1)

    raise TimeoutError("Redash query timed out after 90 seconds")