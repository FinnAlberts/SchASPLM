"""Module-level CSV logger (convenience API only).

Usage:
    from utils import logger
    logger.init_logger(folder, filename, problem_ID, max_fix_attempts=0)
    logger.log(fix_attempt_count=1, correct_syntax=True)

This simplified logger maintains an internal statement_block counter (starts at 1 on init)
and writes rows to CSV with header:
    datetimestamp, max_fix_attempts (k), problem_ID, statement_block, fix_attempt_count, correct_syntax

This module intentionally exposes only the convenience functions `init_logger` and `log`.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Optional


# Module state
_folder: Optional[str] = None
_filename: Optional[str] = None
_filepath: Optional[str] = None
_problem_ID: Optional[str] = None
_time_stamp: Optional[str] = None
_max_fix_attempts: int = 0
_statement_block: int = 1


def _ensure_header():
    """Ensure the CSV exists and has the expected header. This does not attempt migration.
    If the file exists but has a different header, it will be left as-is and rows will be appended.
    """
    if _filepath is None:
        return
    
    expected_header = ['datetimestamp', 'max_fix_attempts (k)', 'problem_ID', 'model', 'temperature', 'top_p', 'seed', 'statement_block', 'fix_attempt_count', 'correct_syntax']
    if not os.path.exists(_filepath) or os.path.getsize(_filepath) == 0:
        parent = os.path.dirname(_filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(_filepath, 'w', newline='', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(expected_header)


def init_logger(filename: str, problem_ID: str, max_fix_attempts: int = 0, *, model: str | None = None, temperature: float | None = None, top_p: float | None = None, seed: int | None = None) -> None:
    """Initialize module-level logger state.

    - filename: path to the CSV file (can include directories). Parent folder will be created automatically.
    - problem_ID: identifier for the problem
    - max_fix_attempts: integer k (default 0)
    """
    global _folder, _filename, _filepath, _problem_ID, _time_stamp, _max_fix_attempts, _statement_block
    # New optional module-level metadata
    global _model, _temperature, _top_p, _seed

    _filename = filename
    # compute absolute path for clarity
    _filepath = os.path.abspath(_filename)
    _folder = os.path.dirname(_filepath)
    _problem_ID = problem_ID
    _time_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        _max_fix_attempts = int(max_fix_attempts)
    except Exception:
        _max_fix_attempts = 0

    _statement_block = 1

    # store optional metadata for inclusion in each row
    _model = str(model) if model is not None else None
    try:
        _temperature = float(temperature) if temperature is not None else None
    except Exception:
        _temperature = None
    try:
        _top_p = float(top_p) if top_p is not None else None
    except Exception:
        _top_p = None
    try:
        _seed = int(seed) if seed is not None else None
    except Exception:
        _seed = None

    _ensure_header()


def log(fix_attempt_count: int = 0, correct_syntax: bool = False) -> None:
    """Append a single CSV row using the module-level logger state.

    If the logger hasn't been initialized, prints a message and does nothing.
    """
    global _statement_block
    if _filepath is None or _problem_ID is None or _time_stamp is None:
        print("PLEASE FIRST CALL init_logger(folder, filename, problem_ID). The logger must be initialized before logging.")
        return

    correct_val = 1 if correct_syntax else 0
    # Use stored metadata values; if None, write empty string for CSV cleanliness
    model_val = _model if '_model' in globals() and _model is not None else ''
    temp_val = _temperature if '_temperature' in globals() and _temperature is not None else ''
    top_p_val = _top_p if '_top_p' in globals() and _top_p is not None else ''
    seed_val = _seed if '_seed' in globals() and _seed is not None else ''

    # New ordering: datetimestamp, max_fix_attempts (k), problem_ID, model, temperature, top_p, seed, statement_block, fix_attempt_count, correct_syntax
    row = [_time_stamp, _max_fix_attempts, _problem_ID, model_val, temp_val, top_p_val, seed_val, _statement_block, fix_attempt_count, correct_val]

    with open(_filepath, 'a', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(row)

    _statement_block += 1
