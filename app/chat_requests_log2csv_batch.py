#!/usr/bin/env python3
"""Batch script to convert chat request logs into CSV output.

Usage:
    python app/chat_request_logs2csv_batch.py --log-dir ./logs [--overwrite]

The script searches the specified log directory for all files named
``chat-request.logs.<timestamp>`` and produces matching CSV files named
``chat-request.csv.<timestamp>`` containing the ``timestamp``, ``query`` and
``answer`` fields from each JSON log entry.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Any, Dict, Iterable, List


DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"

CSV_DIR = Path("csv")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert chat-requests log entries into CSV format."
    )
    parser.add_argument(
        "--log-dir",
        default=DEFAULT_LOG_DIR,
        type=Path,
        help="Directory containing chat-requests log files. Defaults to ./logs.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite existing CSV files if present.",
    )
    return parser.parse_args()


def discover_log_files(log_dir: Path) -> List[Path]:
    """Return all chat-requests log files within the log directory."""

    return sorted(log_dir.glob("chat-requests.log.*"))


def setup_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_path = log_dir / f"chat_requests_log2csv_batch.log.{timestamp}"

    logger = logging.getLogger("chat_requests_log2csv_batch")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Reset handlers to avoid duplicate logs when running in-process tests.
    if logger.handlers:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def extract_records(log_file: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []

    def _to_single_line(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        return value.replace("\r", " \\r ").replace("\n", " \\n ")

    with log_file.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            entry = line.strip()
            if not entry:
                continue
            try:
                payload: Dict[str, Any] = json.loads(entry)
            except json.JSONDecodeError:
                continue

            JST = ZoneInfo("Asia/Tokyo")

            timestamp_str = payload.get("timestamp")
            dt_utc = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=timezone.utc)
            timestamp_jst = dt_utc.astimezone(JST).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            query = payload.get("query")
            answer = payload.get("answer")

            records.append({
                "timestamp": timestamp_str,
                "timestamp_jst": timestamp_jst,
                "query": _to_single_line(query),
                "answer": _to_single_line(answer),
            })
    return records


def write_csv(csv_file: Path, records: Iterable[Dict[str, Any]]) -> None:
    csv_file.parent.mkdir(parents=True, exist_ok=True)
    ## excel
    with csv_file.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["timestamp", "timestamp_jst", "query", "answer"],
            quoting=csv.QUOTE_ALL,
        )
        #writer.writeheader() #ファイル結合しやすいように、ヘッダーを出力しない
        for record in records:
            writer.writerow(record)


def main() -> int:
    args = parse_arguments()
    log_dir: Path = args.log_dir
    overwrite: bool = args.overwrite


    logger = setup_logger(log_dir)

    log_files = discover_log_files(log_dir)
    if not log_files:
        logger.warning("対象のログファイルが見つかりません: %s", log_dir)
        return 1

    exit_code = 0
    for log_file in log_files:
        if not log_file.exists():
            logger.warning("ログファイルが見つかりません: %s", log_file)
            exit_code = 1
            continue

        timestamp_suffix = log_file.name.split("chat-requests.log.", 1)[-1]
        csv_file = CSV_DIR / f"chat-requests.{timestamp_suffix}.csv"

        if csv_file.exists():
            if overwrite:
                logger.info("既存のCSVファイルを上書きします: %s", csv_file)
                csv_file.unlink()
            else:
                logger.debug("CSVファイルが既に存在します: %s", csv_file)
                continue

        records = extract_records(log_file)
        write_csv(csv_file, records)
        logger.info("出力が完了しました: %s", csv_file)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())