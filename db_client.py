"""
Shared Supabase REST client for all Yukioh Okami tools.
Uses the PostgREST API directly via requests — no Supabase Python SDK needed.
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

_env_path = Path(__file__).resolve().parent / ".env"

def _load_env():
    url = os.environ.get("VITE_SUPABASE_URL", "")
    key = os.environ.get("VITE_SUPABASE_ANON_KEY", "")
    if not url or not key:
        try:
            with open(_env_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        k, _, v = line.partition("=")
                        k, v = k.strip(), v.strip()
                        if k in ("VITE_SUPABASE_URL", "VITE_SUPABASE_ANON_KEY"):
                            os.environ.setdefault(k, v)
        except Exception:
            pass
    return os.environ.get("VITE_SUPABASE_URL", ""), os.environ.get("VITE_SUPABASE_ANON_KEY", "")

SUPABASE_URL, SUPABASE_KEY = _load_env()
HAS_DB = bool(SUPABASE_URL and SUPABASE_KEY)

_REST_BASE = f"{SUPABASE_URL}/rest/v1" if SUPABASE_URL else ""
_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
} if HAS_DB else {}


def _insert(table: str, row: dict) -> bool:
    if not HAS_DB:
        return False
    try:
        resp = requests.post(
            f"{_REST_BASE}/{table}",
            headers=_HEADERS,
            json=row,
            timeout=10,
        )
        return resp.status_code in (200, 201)
    except Exception:
        return False


def _update(table: str, filters: dict, updates: dict) -> bool:
    if not HAS_DB:
        return False
    try:
        url = f"{_REST_BASE}/{table}"
        for col, val in filters.items():
            url += f"?{col}=eq.{val}"
        resp = requests.patch(url, headers={**_HEADERS, "Prefer": "return=minimal"}, json=updates, timeout=10)
        return resp.status_code in (200, 204)
    except Exception:
        return False


def _select(table: str, columns: str = "*", filters: dict = None, limit: int = 100):
    if not HAS_DB:
        return []
    try:
        url = f"{_REST_BASE}/{table}?select={columns}&limit={limit}"
        if filters:
            for col, val in filters.items():
                url += f"&{col}=eq.{val}"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception:
        return []


# ── Public API ──────────────────────────────────────────────

def log_license_verification(user_key, hwid, status, modname=None, credit=None,
                             expiry=None, token=None, failure_reason=None):
    row = {
        "user_key": user_key,
        "hwid": hwid,
        "status": status,
        "modname": modname,
        "credit": credit,
        "expiry": expiry,
        "token": token,
        "failure_reason": failure_reason,
    }
    return _insert("license_verifications", row)


def log_found_key(key_value, key_type, source_file=None, key_offset=None,
                  confidence=0.0, description=None, finder_tool=None):
    row = {
        "key_value": key_value,
        "key_type": key_type,
        "source_file": source_file,
        "key_offset": key_offset,
        "confidence": confidence,
        "description": description,
        "finder_tool": finder_tool,
    }
    return _insert("found_keys", row)


def log_pak_operation(operation, input_path=None, output_path=None, pak_stem=None,
                      file_count=0, status="success", error_message=None, duration_ms=None):
    row = {
        "operation": operation,
        "input_path": input_path,
        "output_path": output_path,
        "pak_stem": pak_stem,
        "file_count": file_count,
        "status": status,
        "error_message": error_message,
        "duration_ms": duration_ms,
    }
    return _insert("pak_operations", row)


def start_tool_session(tool_name, hwid=None, version=None, authenticated=False):
    row = {
        "tool_name": tool_name,
        "hwid": hwid,
        "version": version,
        "authenticated": authenticated,
    }
    ok = _insert("tool_sessions", row)
    return ok


def end_tool_session(tool_name, hwid):
    updates = {"ended_at": datetime.now().isoformat()}
    return _update("tool_sessions", {"tool_name": tool_name, "hwid": hwid}, updates)


def get_found_keys(key_type=None, limit=100):
    filters = {"key_type": key_type} if key_type else None
    return _select("found_keys", "key_value,key_type,source_file,found_at", filters, limit)


def get_pak_operations(pak_stem=None, limit=50):
    filters = {"pak_stem": pak_stem} if pak_stem else None
    return _select("pak_operations", "operation,status,file_count,operation_at", filters, limit)
