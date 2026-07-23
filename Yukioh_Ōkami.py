#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# YUKIOH ŌKAMI TOOL v4.5 - ULTIMATE PAK + LUA MODDING SUITE
# SECURE HWID + GITHUB KEY SYSTEM - FULL WORKING VERSION
# ALL PUBG VERSIONS SUPPORTED - ANY SIZE REPACK
# Fully developed by @Yukira_12
# ============================================================

import os
import sys
import gc
import re
import mmap
import json
import math
import time
import zlib
import struct
import shutil
import zipfile
import fnmatch
import hashlib
import traceback
import itertools as it
import subprocess
import tempfile
import atexit
import uuid
import datetime
import random
import inspect
import ssl
from collections import defaultdict
from functools import lru_cache
from pathlib import PurePath, Path
from datetime import datetime
from threading import Thread
from queue import Queue
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any

try:
    import certifi
    HAS_CERTIFI = True
except ImportError:
    HAS_CERTIFI = False

try:
    import db_client
except ImportError:
    db_client = None

# ============================================================
# PACKAGE IMPORTS CHECK
# ============================================================

try:
    import gmalg
    from Crypto.Cipher import AES
    from Crypto.Cipher.AES import MODE_CBC
    from Crypto.Hash import SHA1
    from Crypto.Util.Padding import unpad, pad
    from zstandard import ZstdDecompressor, ZstdCompressor, ZstdCompressionDict, DICT_TYPE_AUTO
    HAS_PAK_DEPS = True
except ImportError as e:
    HAS_PAK_DEPS = False
    _PAK_IMPORT_ERROR = str(e)

try:
    import colorama
    colorama.init(autoreset=True)
except ImportError:
    pass

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn, TaskProgressColumn, TimeRemainingColumn
    from rich import box as rich_box
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.align import Align
    from rich.layout import Layout
    from rich.markup import escape
    from rich.box import HEAVY_EDGE, ROUNDED, DOUBLE_EDGE
    console = Console()
except ImportError:
    class DummyConsole:
        def print(self, *args, **kwargs): print(*args)
        def input(self, *args, **kwargs): return input(*args)
    console = DummyConsole()

# ============================================================
# UTILITIES
# ============================================================

if not hasattr(it, 'batched'):
    def batched(iterable, n):
        import itertools
        if n < 1:
            raise ValueError('n must be at least one')
        it_obj = iter(iterable)
        while batch := tuple(itertools.islice(it_obj, n)):
            yield batch
    it.batched = batched

# ============================================================
# CONSTANTS
# ============================================================

# XOR KEYS FOR LUA
GFP_XOR_KEY_64BIT = bytes([
    0x00, 0x07, 0xAF, 0x1E, 0x03, 0xF2, 0xF2, 0xA2,
    0x52, 0x33, 0x43, 0x36, 0xF1, 0x30, 0x48, 0xB6,
    0xF3, 0x52, 0xE2, 0x32, 0x52, 0x12, 0xD6, 0xF3,
    0x52, 0x53, 0x32, 0x42, 0xB1, 0xF3, 0x67, 0x72,
])
GFP_XOR_KEY_32BIT = bytes([
    0x07, 0x14, 0xEE, 0x2A, 0x42, 0xD3, 0xA5, 0xE4,
    0xB6, 0xB6, 0xE6, 0xF0, 0x7E, 0xC5, 0x51, 0x0E,
    0xEB, 0x44, 0xB9, 0xF5, 0xE5, 0x01, 0x20, 0xAE,
    0x3E, 0x00, 0x18, 0xFE, 0x00, 0x00, 0x00, 0x00,
])
OLD_XOR_KEY = bytes([
    0xEF, 0xC1, 0x71, 0x3E, 0xE3, 0x34, 0x7D, 0x24,
    0x58, 0xE1, 0x9A, 0x38, 0x4F, 0xA4, 0x6D, 0x08,
    0x64, 0x70, 0xAC, 0xF2, 0xBC, 0xE6, 0x2E, 0x41,
    0x4F, 0x00, 0x83, 0xE7, 0xE7, 0x0B, 0x20, 0x07,
])
ALL_LUA_KEYS = {
    "64-bit GFP": GFP_XOR_KEY_64BIT,
    "32-bit GFP": GFP_XOR_KEY_32BIT,
    "Old Key": OLD_XOR_KEY,
}
DEFAULT_LUA_KEY = GFP_XOR_KEY_64BIT

# PAK Constants
ZUC_KEY = bytes.fromhex('01010101010101010101010101010101')
ZUC_IV = bytes.fromhex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

RSA_MOD_1 = bytes.fromhex(
    'CBE8B9F2504050EF9831B719E9A6249A6D238505ADE909BDE78C180DED6072A0C3347B8AF4780E1F212D952D82D4BF7F233C1ECA499E1F9D9A85B4FAD759F54BABC1666C5DE411EA9E4B2374425DD6C6F54333BBC8F2610FE6063E4D0D6C21A671A8F7C3740555E5DC06D4E1691C456DB4116C0C012BF7B206E8311AAAEC689952BF804EF638F09D5822B4117B114208F14DEB459E80CB770E5B0D7978E21F5E6CED4999D3583108221A7AB28B960277ADB5690A332784019D9C195BE4EA9EA0A09459010F236465DE0D59C3EF7324E954E1118D93EE19F299760C2CDB963CE87973EA5ECC9BBE81C27D4C7C8572AC07E9BCEAC9BD72AB7A56A3C0AD736ABCE4')
RSA_MOD_2 = bytes.fromhex(
    '7F58E8A39A4DA4E87357DDD650EAA16D3B5CE95B213D1030A662566444796A78A84AE9AC3DBFFDE7F41094896696835DAF13B89E6EC2B84963B1B1BAF7151DA245C3FBFAE2A6AE18B2684D03F9229DE2C91440F2A3A3BCDE1E5680C16722A88039C73560D5D43F4B6562C2EEA5B1D926D86B51108A2643C70FB74D6442CE3A08339B8FD8F660AE88129B7AB8C46F2FA58124485CCCB1E987B05A6DA65A01858ED3F89905449AE42BB07290FCB9994BF22E26610BCABB9804783A3B9587917F3D97316EDDA15C5E13F79066407B55A93B291B68A4AC42A98D6E35FED84B14A792D154E62028DDAD20FC301951E5924BE9AD62FB719DD94CC30CAB871BEC4377A8')

SIMPLE1_DECRYPT_KEY = 121
SIMPLE2_DECRYPT_KEY = bytes.fromhex('E55B4ED1')
SIMPLE2_BLOCK_SIZE = 16

SM4_SECRET_4 = 'eb691efea914241317a8'
SM4_SECRET_2 = 'Q0hVTKey$as*1ZFlQCiA'
SM4_SECRET_NEW = [
    'xG2qW5lP7lV2iN5fN5pG', 'xT1cJ6dL5wC0kK1rB4dK',
    'qC4jS5bZ6fL5xE6nD4zA', 'gD4jQ2aL3bS3lC3xT0iW',
    'xU1yQ8wE9zY3gZ3bT5aE', 'uQ3cO2dX7xY4xU7gH7iS',
    'gW1fR0jK6wQ4oN0oK1kZ', 'aJ4pV7iZ7pU4wP2aC2cZ',
    'cX6jT3cM2oT3vK0kJ1qN', 'iT2vS0cS6yT6cZ1sE1lO',
    'hM1pH9iY8wM9hT4lN5uJ', 'kG6bC8jK0fL0dE4sH4mL',
    'dB6lB3vE0eZ8wM8rI0aC', 'tP7sP7nI9rA2vQ4cV5yQ',
    'aT0cL1yN4pT3sZ7eM2vY', 'uV6fU8fC9zN3mP5dH8mN'
]

EM_SIMPLE1 = 1
EM_SIMPLE2 = 16
EM_SM4_2 = 2
EM_SM4_4 = 4
EM_SM4_NEW_BASE = 31
EM_SM4_NEW_MASK = ~EM_SM4_NEW_BASE
EM_UNKNOWN_17 = 17
CM_NONE = 0
CM_ZLIB = 1
CM_ZSTD = 6
CM_ZSTD_DICT = 8
CM_MASK = 15

TOOL_NAME = 'Yukioh_Ōkami_v4.5'
TOOL_VERSION = "v4.5"

# ============================================================
# FOLDER STRUCTURE
# ============================================================

# Main tool directory
BASE_DIR = Path.cwd() / TOOL_NAME

# PAK Type Folders
PAK_TYPES = ['ZSDIC', 'MINI_OBB', 'OD_PAK', 'GAMEPATCH']
SUB_FOLDERS = ['INPUT', 'UNPACKED', 'EDITED', 'REPACKED', 'SEARCH_RESULTS', 'COMPARE_DAT']

# 120 FPS Folders
FPS_ROOT = BASE_DIR / '120_FPS'
FPS_GAMES = ['BGMI', 'PUBG']
FPS_SUBS = ['INPUT_PAK', 'OUTPUT_PAK', 'EDITED_DAT']

# AntiReset Folders
ANTIRESET_DIR = BASE_DIR / 'ANTIRESET'
ORG_OBB_DIR = ANTIRESET_DIR / 'ORG_OBB'
MODDED_OBB_DIR = ANTIRESET_DIR / 'MODDED_OBB'

# Encrypt/Decrypt Folders
ENC_DEC_DIR = BASE_DIR / 'ENC_DEC'
ENC_TYPES = ['NORMAL_ENC', 'CUSTOM_ENC', 'DECRYPT']
ENC_SUBS = ['INPUT', 'OUTPUT']

# Split/Merge Folders
SPLIT_MERGE_DIR = BASE_DIR / 'SPLIT_MERGE'
SPLIT_DIR = SPLIT_MERGE_DIR / 'SPLIT'
MERGE_DIR = SPLIT_MERGE_DIR / 'MERGE'

# Auto Config Folders
AUTO_CONFIG_DIR = BASE_DIR / 'AUTO_CONFIG'
AUTO_PRESETS = ['HEADSHOT', 'WHITE_BODY', 'NO_GRASS', 'MASTER_BALTIC']

# LUA Folders
LUA_ORIGINAL_DIR = BASE_DIR / 'LUA' / 'ORIGINAL'
LUA_DECOMPILED_DIR = BASE_DIR / 'LUA' / 'DECOMPILED'
LUA_EDIT_DIR = BASE_DIR / 'LUA' / 'EDITED'
LUA_COMPILED_DIR = BASE_DIR / 'LUA' / 'COMPILED'

# Only keep MANIFEST_DIR for debugging
MANIFEST_DIR = BASE_DIR / 'Manifest'

# Auth
AUTH_CONFIG_FILE = BASE_DIR / "config.json"
_auth_data = None

# ============================================================
# SECURE GITHUB KEY SYSTEM WITH HWID - API ONLY
# ============================================================

GITHUB_CONFIG = {
    "repo_url": "https://api.github.com/repos/Himesh-Shah93/yukioh_keys/contents/keys.json",
    "token": "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",
    "cache_file": BASE_DIR / "keys_cache.enc",
    "cache_expiry_hours": 24,
    "allow_offline": True,
}

# ============================================================
# TELEGRAM CONTACT INFO
# ============================================================

SUPPORT_CONTACT = "@Yukira_12"

# ============================================================
# 🔐 SECURITY FUNCTIONS
# ============================================================

# ============================================================
# RATE LIMITER - Prevent brute force attacks
# ============================================================

class RateLimiter:
    """Prevent brute force attacks on key verification"""
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self.attempts = defaultdict(list)
        self.max_attempts = max_attempts
        self.window = window_seconds
        self.locked_keys = {}
        self.lock_duration = 1800  # 30 minutes lockout
    
    def check(self, key: str) -> tuple:
        """
        Check if key is allowed to attempt authentication
        Returns: (allowed, message)
        """
        now = time.time()
        
        # Check if key is locked out
        if key in self.locked_keys:
            lock_time = self.locked_keys[key]
            if now - lock_time < self.lock_duration:
                remaining = int(self.lock_duration - (now - lock_time))
                return False, f"Key locked for {remaining} seconds. Too many failed attempts."
            else:
                # Remove lock after duration
                del self.locked_keys[key]
                self.attempts[key] = []
        
        # Clean old attempts
        self.attempts[key] = [t for t in self.attempts[key] if now - t < self.window]
        
        # Check if max attempts exceeded
        if len(self.attempts[key]) >= self.max_attempts:
            # Lock the key
            self.locked_keys[key] = now
            return False, f"Too many failed attempts. Key locked for {self.lock_duration // 60} minutes."
        
        return True, "Allowed"
    
    def record_attempt(self, key: str, success: bool):
        """Record authentication attempt"""
        now = time.time()
        
        if success:
            # Reset attempts on success
            self.attempts[key] = []
            if key in self.locked_keys:
                del self.locked_keys[key]
        else:
            # Record failed attempt
            self.attempts[key].append(now)
    
    def get_status(self, key: str) -> dict:
        """Get status of a key"""
        now = time.time()
        attempts = len([t for t in self.attempts[key] if now - t < self.window])
        is_locked = key in self.locked_keys
        
        return {
            'attempts': attempts,
            'max_attempts': self.max_attempts,
            'is_locked': is_locked,
            'remaining_attempts': self.max_attempts - attempts if not is_locked else 0
        }

# Create global instance
auth_rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)

# ============================================================
# ANTI-DEBUG PROTECTION
# ============================================================

def anti_debug_check() -> bool:
    """
    Check for debuggers and reverse engineering tools
    Returns True if debugger detected
    """
    # 1. Check for Python debugger
    if sys.gettrace() is not None:
        console.print("[red]❌ Debugger detected![/red]")
        return True
    
    # 2. Check for common debugger processes
    try:
        if HAS_PSUTIL:
            debugger_processes = [
                'IDA', 'ida.exe', 'ida64.exe', 'idag.exe', 'idag64.exe',
                'OllyDbg', 'ollydbg.exe',
                'x64dbg', 'x32dbg.exe', 'x64dbg.exe',
                'dnSpy', 'dnspy.exe',
                'Cheat Engine', 'cheatengine-x86_64.exe', 'cheatengine.exe',
                'Process Hacker', 'procexp.exe', 'procexp64.exe',
                'Immunity Debugger', 'immunitydebugger.exe',
                'WinDbg', 'windbg.exe',
                'GDB', 'gdb.exe',
                'Radare2', 'r2.exe',
                'Binary Ninja', 'binaryninja.exe',
                'Ghidra', 'ghidra.exe',
                'Wireshark', 'wireshark.exe'
            ]
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name']:
                        proc_name_lower = proc.info['name'].lower()
                        for debugger in debugger_processes:
                            if debugger.lower() in proc_name_lower:
                                console.print(f"[red]❌ Debugger detected: {proc.info['name']}[/red]")
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    except:
        pass
    
    # 3. Check for common debugger environment variables
    debug_env_vars = ['PYTHONDEBUG', 'PYTHONHASHSEED', 'PYTHONMALLOC']
    for env_var in debug_env_vars:
        if os.environ.get(env_var):
            console.print(f"[red]❌ Debug environment detected: {env_var}[/red]")
            return True
    
    # 4. Check for virtual machine (optional - just warning)
    try:
        import platform
        if platform.system() == 'Windows':
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_ComputerSystem():
                    vm_detected = any(x in item.Model for x in ['VirtualBox', 'VMware', 'VBox', 'Virtual Machine'])
                    if vm_detected:
                        console.print("[yellow]⚠️ Running in Virtual Machine[/yellow]")
                        # Don't exit, just warn
            except:
                pass
    except:
        pass
    
    return False

# ============================================================
# CODE INTEGRITY CHECK
# ============================================================

def check_code_integrity() -> bool:
    """
    Check if critical functions have been modified
    Returns True if integrity is OK
    """
    critical_functions = [
        'verify_key_github',
        'check_auth',
        'get_hwid',
        'admin_hwid_manager'
    ]
    
    try:
        for func_name in critical_functions:
            if func_name in globals():
                func = globals()[func_name]
                try:
                    source = inspect.getsource(func)
                    
                    # Check for obvious modifications
                    if 'bypass' in source.lower():
                        console.print(f"[red]❌ Code integrity compromised in {func_name} (bypass detected)[/red]")
                        return False
                    
                    # Check for hardcoded return True in auth functions
                    if func_name in ['verify_key_github', 'check_auth']:
                        if 'return True' in source and 'verify_key_github' in source:
                            # This is normal, but check for suspicious patterns
                            lines = source.split('\n')
                            for line in lines:
                                stripped = line.strip()
                                if stripped.startswith('return True') and 'if' not in stripped and 'else' not in stripped:
                                    # Could be suspicious if at top level
                                    pass
                except:
                    # If we can't get source, assume OK
                    pass
    except:
        # If we can't check, assume OK (don't block)
        pass
    
    return True

# ============================================================
# SECURE SESSION FOR NETWORK REQUESTS
# ============================================================

def get_secure_session() -> requests.Session:
    """
    Create a secure requests session with SSL verification
    """
    session = requests.Session()
    
    # SSL verification
    if HAS_CERTIFI:
        session.verify = certifi.where()
    else:
        session.verify = True  # Default SSL verification
    
    # Set secure headers
    session.headers.update({
        'User-Agent': f'Yukioh-Okami/{TOOL_VERSION}',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    
    # Timeout settings
    session.timeout = (10, 30)  # connect timeout, read timeout
    
    return session

# ============================================================
# RATE LIMITER STATUS - Admin Command
# ============================================================

def show_rate_limiter_status():
    """Show current rate limiter status for debugging"""
    console.print(Panel('[bold cyan]📊 RATE LIMITER STATUS[/bold cyan]', border_style='cyan'))
    
    table = Table(box=rich_box.SIMPLE)
    table.add_column('Key', style='bold cyan')
    table.add_column('Attempts', style='yellow', justify='center')
    table.add_column('Locked', style='red', justify='center')
    table.add_column('Remaining', style='green', justify='center')
    
    for key, attempts in auth_rate_limiter.attempts.items():
        now = time.time()
        recent_attempts = len([t for t in attempts if now - t < auth_rate_limiter.window])
        is_locked = key in auth_rate_limiter.locked_keys
        remaining = auth_rate_limiter.max_attempts - recent_attempts
        
        table.add_row(
            key[:20] + '...' if len(key) > 20 else key,
            str(recent_attempts),
            '🔒 Locked' if is_locked else '✅ Free',
            str(remaining) if not is_locked else '0'
        )
    
    console.print(table)

# ============================================================
# PERMANENT HWID SYSTEM - UPGRADED (10+ Sources)
# ============================================================

def get_hwid() -> str:
    """Get permanent HWID - harder to spoof with multiple sources"""
    hwid_file = BASE_DIR / ".hwid"
    if hwid_file.exists():
        try:
            saved_hwid = hwid_file.read_text().strip()
            if saved_hwid and saved_hwid.startswith("YUKIOH_"):
                return saved_hwid
        except:
            pass
    
    console.print("[dim]🔧 Generating permanent HWID for this device...[/dim]")
    
    hwid_parts = []
    
    # 1. Motherboard Serial (harder to spoof)
    try:
        if sys.platform == 'win32':
            import subprocess
            result = subprocess.run(['wmic', 'baseboard', 'get', 'serialnumber'], 
                                   capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                mb_serial = lines[1].strip()
                if mb_serial and mb_serial != 'SerialNumber':
                    hwid_parts.append(f"MB_{mb_serial[:16]}")
    except:
        pass
    
    # 2. BIOS UUID (Windows)
    try:
        if sys.platform == 'win32':
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                r"SOFTWARE\Microsoft\Cryptography")
            guid = winreg.QueryValueEx(key, "MachineGuid")[0]
            hwid_parts.append(f"BIOS_{guid[:16]}")
    except:
        pass
    
    # 3. Disk Drive Serial
    try:
        if sys.platform == 'win32':
            import subprocess
            result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'],
                                   capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                disk_serial = lines[1].strip()
                if disk_serial:
                    hwid_parts.append(f"DISK_{disk_serial[:16]}")
    except:
        pass
    
    # 4. MAC Address
    try:
        mac = uuid.getnode()
        if mac != 0xffffffffffff:
            hwid_parts.append(f"MAC_{mac:012x}")
    except:
        pass
    
    # 5. CPU Serial (Windows)
    try:
        if sys.platform == 'win32':
            import subprocess
            result = subprocess.run(['wmic', 'cpu', 'get', 'processorid'], 
                                   capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                cpu_id = lines[1].strip()
                if cpu_id and cpu_id != 'ProcessorId':
                    hwid_parts.append(f"CPU_{cpu_id[:16]}")
    except:
        pass
    
    # 6. Machine ID (Linux)
    try:
        if sys.platform == 'linux':
            with open('/var/lib/dbus/machine-id', 'r') as f:
                machine_id = f.read().strip()
                if machine_id:
                    hwid_parts.append(f"SYS_{machine_id[:16]}")
        elif sys.platform == 'darwin':
            import subprocess
            result = subprocess.run(['ioreg', '-l'], capture_output=True, text=True, timeout=5)
            import re
            match = re.search(r'IOPlatformUUID" = "([^"]+)"', result.stdout)
            if match:
                hwid_parts.append(f"MAC_{match.group(1)[:16]}")
    except:
        pass
    
    # 7. Volume Serial (Windows)
    try:
        if sys.platform == 'win32':
            import subprocess
            result = subprocess.run(['vol', 'C:'], capture_output=True, text=True, timeout=5)
            import re
            match = re.search(r'([A-F0-9]{4}-[A-F0-9]{4})', result.stdout)
            if match:
                hwid_parts.append(f"VOL_{match.group(1).replace('-', '')}")
    except:
        pass
    
    # 8. Boot ID (Linux)
    try:
        if sys.platform == 'linux':
            with open('/proc/sys/kernel/random/boot_id', 'r') as f:
                boot_id = f.read().strip()
                if boot_id:
                    hwid_parts.append(f"BOOT_{boot_id[:16]}")
    except:
        pass
    
    # 9. System UUID (Linux)
    try:
        if sys.platform == 'linux':
            import subprocess
            result = subprocess.run(['dmidecode', '-s', 'system-uuid'], 
                                   capture_output=True, text=True, timeout=5)
            if result.stdout.strip():
                hwid_parts.append(f"UUID_{result.stdout.strip()[:16]}")
    except:
        pass
    
    # 10. Random Fallback (last resort)
    if not hwid_parts:
        import random
        rand_hwid = ''.join(random.choices('0123456789ABCDEF', k=16))
        hwid_parts.append(f"RND_{rand_hwid}")
    
    # Combine all parts and create SHA256 hash
    combined = "_".join(hwid_parts)
    final_hwid = hashlib.sha256(combined.encode()).hexdigest()[:16]
    final_hwid = f"YUKIOH_{final_hwid.upper()}"
    
    # Save to file (PERMANENT)
    try:
        hwid_file.write_text(final_hwid)
        console.print(f"[green]✅ Permanent HWID: {final_hwid}[/green]")
    except Exception as e:
        console.print(f"[red]⚠ Could not save HWID: {e}[/red]")
    
    return final_hwid

def _get_cache_key() -> bytes:
    hwid = get_hwid()
    salt = b"YUKIOH_CACHE_SALT_2025"
    return hashlib.pbkdf2_hmac('sha256', hwid.encode(), salt, 100000, dklen=32)

def encrypt_cache_data(data: dict) -> bytes:
    key = _get_cache_key()
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    json_data = json.dumps(data, indent=2).encode('utf-8')
    padded_data = pad(json_data, AES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return iv + encrypted

def decrypt_cache_data(encrypted_data: bytes) -> dict:
    if len(encrypted_data) < 16:
        return None
    key = _get_cache_key()
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(encrypted_data[16:])
    try:
        unpadded = unpad(decrypted, AES.block_size)
        return json.loads(unpadded.decode('utf-8'))
    except:
        return None

# ============================================================
# UPDATED get_keys_from_github() WITH SECURE SESSION
# ============================================================

def get_keys_from_github() -> dict:
    if not HAS_REQUESTS:
        console.print("[red]⚠ requests module not installed![/red]")
        return load_encrypted_cache()
    
    headers = {
        "Authorization": f"token {GITHUB_CONFIG['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        console.print("[dim]Fetching from GitHub API...[/dim]")
        
        # Use secure session
        session = get_secure_session()
        response = session.get(GITHUB_CONFIG["repo_url"], headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            import base64
            content = base64.b64decode(data['content']).decode('utf-8')
            keys_data = json.loads(content)
            
            encrypted = encrypt_cache_data(keys_data)
            with open(GITHUB_CONFIG['cache_file'], 'wb') as f:
                f.write(encrypted)
            
            console.print("[green]✅ Keys downloaded from GitHub successfully![/green]")
            return keys_data
            
        elif response.status_code == 401:
            console.print("[red]❌ GitHub authentication failed! Check your token.[/red]")
            return load_encrypted_cache()
        elif response.status_code == 404:
            console.print("[red]❌ Repository or keys.json not found![/red]")
            return load_encrypted_cache()
        else:
            console.print(f"[red]❌ GitHub error: HTTP {response.status_code}[/red]")
            return load_encrypted_cache()
            
    except requests.exceptions.Timeout:
        console.print("[yellow]⚠ Connection timeout. Trying cached keys...[/yellow]")
        return load_encrypted_cache()
    except requests.exceptions.ConnectionError:
        console.print("[yellow]⚠ Cannot reach GitHub. Trying cached keys...[/yellow]")
        return load_encrypted_cache()
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return load_encrypted_cache()

def load_encrypted_cache() -> dict:
    cache_file = GITHUB_CONFIG['cache_file']
    if not cache_file.exists():
        console.print("[yellow]⚠ No cache found.[/yellow]")
        return None
    try:
        with open(cache_file, 'rb') as f:
            encrypted_data = f.read()
        keys_data = decrypt_cache_data(encrypted_data)
        if not keys_data:
            console.print("[red]❌ Failed to decrypt cache![/red]")
            return None
        if 'timestamp' in keys_data:
            cache_time = datetime.fromisoformat(keys_data['timestamp'])
            hours_diff = (datetime.now() - cache_time).total_seconds() / 3600
            if hours_diff <= GITHUB_CONFIG['cache_expiry_hours']:
                console.print("[green]✅ Using encrypted cache[/green]")
                return keys_data
            elif GITHUB_CONFIG['allow_offline']:
                console.print(f"[yellow]⚠ Cache expired ({round(hours_diff, 1)} hours old) - offline mode[/yellow]")
                return keys_data
        return keys_data
    except Exception as e:
        console.print(f"[red]❌ Cache read error: {e}[/red]")
        return None

# ============================================================
# UPDATED verify_key_github() WITH RATE LIMITING
# ============================================================

def verify_key_github(user_key: str) -> dict:
    """Verify a key against GitHub with HWID check + EXPIRY CHECK + RATE LIMITING"""
    console.print("[dim]🔍 Verifying key...[/dim]")
    
    # Rate limiting check
    allowed, message = auth_rate_limiter.check(user_key)
    if not allowed:
        return {'status': False, 'reason': 'Rate limited', 'message': message}
    
    keys_data = get_keys_from_github()
    
    if not keys_data:
        return {'status': False, 'reason': 'No keys available'}
    
    # Check if key exists
    key_info = keys_data.get('keys', {}).get(user_key)
    
    if not key_info:
        auth_rate_limiter.record_attempt(user_key, False)
        return {'status': False, 'reason': 'Invalid key'}
    
    # Check status
    if key_info.get('status') != 'active':
        auth_rate_limiter.record_attempt(user_key, False)
        return {'status': False, 'reason': f"Key status: {key_info.get('status')}"}
    
    # ============================================================
    # 🔐 EXPIRY CHECK - FIXED (Invalid date = expired)
    # ============================================================
    expiry_str = key_info.get('expiry')
    if expiry_str and expiry_str != 'N/A':
        try:
            # Try to parse the date
            expiry_date = datetime.fromisoformat(expiry_str.replace(' ', 'T'))
            
            # Check if expired
            if expiry_date < datetime.now():
                auth_rate_limiter.record_attempt(user_key, False)
                return {
                    'status': False, 
                    'reason': 'Key expired',
                    'message': f'❌ Your key expired on {expiry_str}. Contact {SUPPORT_CONTACT} to renew.',
                    'expiry': expiry_str
                }
        except ValueError:
            # ✅ FIX: Invalid date format = treat as expired
            auth_rate_limiter.record_attempt(user_key, False)
            return {
                'status': False, 
                'reason': 'Invalid expiry date',
                'message': f'❌ Invalid expiry date format: {expiry_str}. Contact {SUPPORT_CONTACT} to fix your key.',
                'expiry': expiry_str
            }
        except Exception:
            # ✅ Any other error = treat as expired
            auth_rate_limiter.record_attempt(user_key, False)
            return {
                'status': False, 
                'reason': 'Expiry check failed',
                'message': f'❌ Could not verify expiry date. Contact {SUPPORT_CONTACT}.',
                'expiry': expiry_str
            }
    
    # ============================================================
    # 🔐 HWID VERIFICATION
    # ============================================================
    
    # Get current user's HWID
    user_hwid = get_hwid()
    console.print(f"[dim]Your HWID: {user_hwid[:12]}...[/dim]")
    
    # Check if HWID verification is required
    hwid_required = keys_data.get('settings', {}).get('hwid_required', True)
    
    if hwid_required:
        authorized_hwids = key_info.get('authorized_hwids', [])
        
        # If no authorized HWIDs defined, key is invalid (security)
        if not authorized_hwids:
            auth_rate_limiter.record_attempt(user_key, False)
            return {
                'status': False, 
                'reason': 'HWID_NOT_AUTHORIZED',
                'message': 'Key valid but no authorized devices found. Contact support.'
            }
        
        # Check if user's HWID is authorized
        if user_hwid not in authorized_hwids:
            auth_rate_limiter.record_attempt(user_key, False)
            return {
                'status': False, 
                'reason': 'HWID_NOT_AUTHORIZED',
                'message': f'Your device (HWID: {user_hwid[:12]}...) is not authorized for this key. Contact {SUPPORT_CONTACT} to get access.',
                'user_hwid': user_hwid,
                'key': user_key
            }
        
        console.print(f"[dim]✅ HWID Verified: {user_hwid[:12]}...[/dim]")
    
    # ✅ Success - Record success and reset attempts
    auth_rate_limiter.record_attempt(user_key, True)
    
    # Key is valid
    return {
        'status': True,
        'modname': key_info.get('modname', 'Yukioh Ōkami TOOL v4.5'),
        'credit': key_info.get('credit', '0'),
        'expiry': key_info.get('expiry', 'N/A'),
        'type': key_info.get('type', 'free'),
        'banner_color': key_info.get('banner_color', 'bright_cyan'),
        'banner_art': key_info.get('banner_art', []),
        'data': key_info,
        'user_hwid': user_hwid
    }

def load_saved_auth() -> dict:
    if AUTH_CONFIG_FILE.exists():
        try:
            with open(AUTH_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_auth(key: str, modname: str, credit: str, expiry: str, key_type: str):
    data = {
        'key': key,
        'modname': modname,
        'credit': credit,
        'expiry': expiry,
        'type': key_type,
        'saved_at': datetime.now().isoformat()
    }
    with open(AUTH_CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clear_saved_auth():
    if AUTH_CONFIG_FILE.exists():
        AUTH_CONFIG_FILE.unlink()

def _ensure_base_dirs():
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    for pak_type in PAK_TYPES:
        pak_dir = BASE_DIR / pak_type
        for sub in SUB_FOLDERS:
            (pak_dir / sub).mkdir(parents=True, exist_ok=True)
        compare_dir = pak_dir / 'COMPARE_DAT'
        for sub in ['Original_PAK', 'Modded_PAK', 'Modified_Files']:
            (compare_dir / sub).mkdir(parents=True, exist_ok=True)
    for game in FPS_GAMES:
        game_dir = FPS_ROOT / game
        for sub in FPS_SUBS:
            (game_dir / sub).mkdir(parents=True, exist_ok=True)
    for d in [ORG_OBB_DIR, MODDED_OBB_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for enc_type in ENC_TYPES:
        enc_dir = ENC_DEC_DIR / enc_type
        for sub in ENC_SUBS:
            (enc_dir / sub).mkdir(parents=True, exist_ok=True)
    for d in [SPLIT_DIR, MERGE_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for preset in AUTO_PRESETS:
        (AUTO_CONFIG_DIR / preset).mkdir(parents=True, exist_ok=True)
    for d in [LUA_ORIGINAL_DIR, LUA_DECOMPILED_DIR, LUA_EDIT_DIR, LUA_COMPILED_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# FANCY UI BANNER - v4.5 KEPT
# ============================================================

ACCENT = "bright_cyan"
GOLD = "bright_yellow"
TEAL = "bright_green"
DIM = "bright_black"
RED = "bright_red"
PINK = "bright_magenta"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

_DEFAULT_BANNER_ART = [
    r"""
                ██╗   ██╗██╗   ██╗██╗  ██╗██╗ ██████╗ ██╗  ██╗
                ╚██╗ ██╔╝██║   ██║██║ ██╔╝██║██╔═══██╗██║  ██║
                 ╚████╔╝ ██║   ██║█████╔╝ ██║██║   ██║███████║
                  ╚██╔╝  ██║   ██║██╔═██╗ ██║██║   ██║██╔══██║
                   ██║   ╚██████╔╝██║  ██╗██║╚██████╔╝██║  ██║
                   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝
                                                                                
                🐺 Yukioh_Ōkami — PUBG/BGMI PAK Modding Tool v4.5 🐺
                ═══════════════════════════════════════════════
"""
]

def _get_banner_art(auth_data) -> list:
    if auth_data:
        raw = auth_data.get('banner_art', [])
        if raw:
            if isinstance(raw, str):
                return raw.split('\n')
            if isinstance(raw, list) and len(raw) >= 3:
                return raw
    return _DEFAULT_BANNER_ART

def show_banner(auth_data=None, show_menu=False):
    clear_screen()
    
    current_hwid = get_hwid()
    hwid_display = current_hwid[:12] + "..." if len(current_hwid) > 12 else current_hwid

    if auth_data is None:
        modname = "Yukioh Ōkami TOOL v4.5"
        credit = "0"
        expiry = "N/A"
        status = "NOT LOGGED IN"
        status_color = "red"
        key_type = "none"
    else:
        modname = auth_data.get('modname', 'Yukioh Ōkami TOOL v4.5')
        credit = auth_data.get('credit', '0')
        expiry = auth_data.get('expiry', 'N/A')
        status = "ACTIVE"
        status_color = "green"
        key_type = auth_data.get('type', 'free')
        try:
            if expiry and expiry != 'N/A':
                exp_date = datetime.fromisoformat(expiry.replace(' ', 'T'))
                expiry = exp_date.strftime('%Y-%m-%d')
        except:
            pass

    banner_color = auth_data.get('banner_color', ACCENT) if auth_data else ACCENT
    console.print()
    for line in _get_banner_art(auth_data):
        console.print(Align.center(f"[bold {banner_color}]{line}[/]"))

    console.print(Align.center(f"[bold {GOLD}]  ━━━  P A K  +  L U A  T O O L  v4.5  ━━━[/]"))
    console.print(Align.center(f"[dim]          Secure HWID Key System  ·  Built by @Yukira_12[/dim]"))
    console.print()

    W = 52

    def _pad(label, value):
        plain_len = 2 + len(label) + 1 + len(value)
        return max(W - plain_len - 1, 1)

    def row(label, value, val_color):
        p = _pad(label, value)
        return f"[bold {ACCENT}]║[/]  [bold white]{label}[/bold white] [bold {val_color}]{value}[/bold {val_color}]{' ' * p}[bold {ACCENT}]║[/]"

    def row_center(text, color=DIM):
        p_total = W - len(text)
        pl = p_total // 2
        pr = p_total - pl
        return f"[bold {ACCENT}]║[/]{' ' * pl}[{color}]{text}[/{color}]{' ' * pr}[bold {ACCENT}]║[/]"

    type_badge = {
        'free': '[bold green]FREE[/bold green]',
        'vip': '[bold magenta]VIP[/bold magenta]',
        'premium': '[bold gold]PREMIUM[/bold gold]',
        'admin': '[bold red]ADMIN[/bold red]',
        'none': '[bold red]NONE[/bold red]'
    }.get(key_type, '[bold white]UNKNOWN[/bold white]')

    console.print(Align.center(f"[bold {ACCENT}]╔{'═'*W}╗[/]"))
    console.print(Align.center(f"[bold {ACCENT}]╠{'═'*W}╣[/]"))
    console.print(Align.center(row("  [*] STATUS :", status, status_color)))
    console.print(Align.center(row("  [-] TYPE   :", type_badge, "bright_green")))
    console.print(Align.center(row("  [-] HWID   :", hwid_display, "yellow")))
    console.print(Align.center(row("  [-] SERVER :", modname, GOLD)))
    console.print(Align.center(row("  [-] CREDIT :", credit, "bright_green")))
    console.print(Align.center(row("  [-] EXPIRY :", expiry, ACCENT)))
    console.print(Align.center(f"[bold {ACCENT}]╠{'═'*W}╣[/]"))
    console.print(Align.center(row_center("UNPACK  ·  REPACK  ·  COMPILE  ·  DECOMPILE")))
    console.print(Align.center(f"[bold {ACCENT}]╚{'═'*W}╝[/]"))
    console.print()
    if show_menu:
        _draw_menu()

def show_login_screen():
    clear_screen()
    console.print()
    for line in _DEFAULT_BANNER_ART:
        console.print(Align.center(f"[bold {GOLD}]{line}[/]"))
    console.print(Align.center(f"[bold {ACCENT}]  ━━━  P A K  +  L U A  TOOL  v4.5  ━━━[/]"))
    console.print(Align.center(f"[dim]          Secure HWID Key System  ·  Built by @Yukira_12[/dim]"))
    console.print()

    W = 52
    console.print(Align.center(f"[bold {GOLD}]╔{'═'*W}╗[/]"))
    console.print(Align.center(f"[bold {GOLD}]╠{'═'*W}╣[/]"))
    title_pad = (W - len("[ GITHUB KEY REQUIRED ]")) // 2
    console.print(Align.center(f"[bold {GOLD}]║[/]{' ' * title_pad}[bold red][ GITHUB KEY REQUIRED ][/bold red]{' ' * (W - title_pad - len('[ GITHUB KEY REQUIRED ]'))}[bold {GOLD}]║[/]"))
    console.print(Align.center(f"[bold {GOLD}]╠{'═'*W}╣[/]"))
    instr = "Enter your key below to continue"
    ip = (W - len(instr)) // 2
    console.print(Align.center(f"[bold {GOLD}]║[/]{' ' * ip}[cyan]{instr}[/cyan]{' ' * (W - ip - len(instr))}[bold {GOLD}]║[/]"))
    console.print(Align.center(f"[bold {GOLD}]╚{'═'*W}╝[/]"))
    console.print()

def check_auth() -> dict:
    global _auth_data
    if _auth_data is not None:
        return _auth_data

    saved = load_saved_auth()
    saved_key = saved.get('key')

    if saved_key:
        console.print("[dim]Checking saved key with GitHub...[/dim]")
        result = verify_key_github(saved_key)
        if result.get('status') == True:
            _auth_data = {
                'key': saved_key,
                'modname': result.get('modname', 'Yukioh Ōkami TOOL v4.5'),
                'credit': result.get('credit', '0'),
                'expiry': result.get('expiry', 'N/A'),
                'type': result.get('type', 'free'),
                'banner_color': result.get('banner_color', 'bright_cyan'),
                'banner_art': result.get('banner_art', []),
                'user_hwid': result.get('user_hwid', '')
            }
            console.print("[green]✅ Auto-login successful![/green]")
            return _auth_data
        else:
            reason = result.get('reason', '')
            if reason == 'Key expired':
                console.print(f"[red]❌ {result.get('message', '')}[/red]")
                console.print(f"[yellow]📱 Contact {SUPPORT_CONTACT} to renew your key[/yellow]")
                clear_saved_auth()
            elif reason == 'HWID_NOT_AUTHORIZED':
                console.print(f"[red]❌ {result.get('message', '')}[/red]")
                console.print(f"[yellow]📱 Contact {SUPPORT_CONTACT} with your HWID to get access[/yellow]")
                console.print(f"[dim]Your HWID: {get_hwid()}[/dim]")
                clear_saved_auth()
            elif reason == 'Rate limited':
                console.print(f"[yellow]⚠️ {result.get('message', '')}[/yellow]")
            else:
                console.print(f"[yellow]Saved key invalid: {reason}[/yellow]")
                clear_saved_auth()

    show_login_screen()
    while True:
        user_key = Prompt.ask("[bold cyan]Enter your key[/bold cyan]").strip()
        if not user_key:
            console.print("[red]Key cannot be empty![/red]")
            continue

        with Progress(SpinnerColumn(), TextColumn("[cyan]Verifying with GitHub...[/cyan]"), transient=True) as prog:
            prog.add_task("", total=None)
            result = verify_key_github(user_key)

        if result.get('status') == True:
            modname = result.get('modname', 'Yukioh Ōkami TOOL v4.5')
            credit = result.get('credit', '0')
            expiry = result.get('expiry', 'N/A')
            key_type = result.get('type', 'free')
            save_auth(user_key, modname, credit, expiry, key_type)
            _auth_data = {
                'key': user_key,
                'modname': modname,
                'credit': credit,
                'expiry': expiry,
                'type': key_type,
                'banner_color': result.get('banner_color', 'bright_cyan'),
                'banner_art': result.get('banner_art', []),
                'user_hwid': result.get('user_hwid', '')
            }
            console.print(f"[bold {TEAL}]  [OK]  Login successful![/bold {TEAL}]")
            time.sleep(0.8)
            return _auth_data
        else:
            reason = result.get('reason', '')
            if reason == 'Key expired':
                console.print(Panel(
                    f"[red]❌ {result.get('message', '')}[/red]\n\n"
                    f"[yellow]📱 Contact {SUPPORT_CONTACT} to renew your key[/yellow]",
                    title="[bold red]KEY EXPIRED[/bold red]",
                    border_style="red"
                ))
            elif reason == 'HWID_NOT_AUTHORIZED':
                console.print(Panel(
                    f"[red]❌ {result.get('message', '')}[/red]\n\n"
                    f"[yellow]📱 Contact {SUPPORT_CONTACT} with your HWID[/yellow]\n"
                    f"[dim]Your HWID: {get_hwid()}[/dim]\n"
                    f"[dim]Key: {user_key}[/dim]",
                    title="[bold red]HWID NOT AUTHORIZED[/bold red]",
                    border_style="red"
                ))
            elif reason == 'Rate limited':
                console.print(Panel(
                    f"[yellow]⚠️ {result.get('message', '')}[/yellow]",
                    title="[bold yellow]RATE LIMITED[/bold yellow]",
                    border_style="yellow"
                ))
            else:
                console.print(Panel(
                    f"[red]❌ Login failed: {reason}[/red]\n\n"
                    f"[yellow]Contact {SUPPORT_CONTACT} for support.[/yellow]",
                    title="[bold red]LOGIN FAILED[/bold red]",
                    border_style="red"
                ))

# ============================================================
# PUSH KEYS TO GITHUB - ADMIN FUNCTION (UPDATED WITH SECURE SESSION)
# ============================================================

def push_keys_to_github(keys_data: dict) -> bool:
    if not HAS_REQUESTS:
        console.print("[red]⚠ requests module not installed![/red]")
        return False
    
    headers = {
        "Authorization": f"token {GITHUB_CONFIG['token']}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        console.print("[dim]Getting file info from GitHub...[/dim]")
        
        # Use secure session
        session = get_secure_session()
        response = session.get(GITHUB_CONFIG["repo_url"], headers=headers, timeout=15)
        
        sha = None
        if response.status_code == 200:
            data = response.json()
            sha = data.get('sha')
            console.print("[dim]✅ File exists, updating...[/dim]")
        elif response.status_code == 404:
            console.print('[yellow]⚠ File not found, will create new[/yellow]')
        else:
            console.print(f'[red]❌ Failed to get file info: HTTP {response.status_code}[/red]')
            return False
        
        import base64
        content = json.dumps(keys_data, indent=2).encode('utf-8')
        encoded_content = base64.b64encode(content).decode('utf-8')
        
        payload = {
            "message": f"Update keys.json - HWID management via Admin Tool @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "content": encoded_content,
            "branch": "main"
        }
        
        if sha:
            payload["sha"] = sha
        
        console.print("[dim]Pushing to GitHub...[/dim]")
        response = session.put(GITHUB_CONFIG["repo_url"], headers=headers, json=payload, timeout=15)
        
        if response.status_code in [200, 201]:
            console.print('[green]✅ Successfully updated keys.json on GitHub[/green]')
            if GITHUB_CONFIG['cache_file'].exists():
                GITHUB_CONFIG['cache_file'].unlink()
                console.print('[dim]Cache cleared for next sync[/dim]')
            return True
        else:
            console.print(f'[red]❌ Failed to update: HTTP {response.status_code}[/red]')
            if response.status_code == 422:
                console.print('[yellow]⚠ File may have been modified. Try refreshing.[/yellow]')
            return False
            
    except Exception as e:
        console.print(f'[red]❌ Error: {e}[/red]')
        return False

# ============================================================
# ADMIN HWID MANAGER - COMPLETE WITH ADD/REMOVE + AUTO DELETE
# ============================================================

def auto_delete_expired_keys(keys_data: dict) -> int:
    """Auto delete keys that have expired"""
    removed_count = 0
    keys = keys_data.get('keys', {})
    expired_keys = []
    
    for key_name, key_info in keys.items():
        expiry_str = key_info.get('expiry', 'N/A')
        if expiry_str and expiry_str != 'N/A':
            try:
                expiry_date = datetime.fromisoformat(expiry_str.replace(' ', 'T'))
                if expiry_date < datetime.now():
                    expired_keys.append(key_name)
                    removed_count += 1
            except:
                pass
    
    for key_name in expired_keys:
        del keys_data['keys'][key_name]
        console.print(f'[dim]🗑️ Removed expired key: {key_name}[/dim]')
    
    return removed_count

def admin_hwid_manager():
    console.print(Panel(
        f'[bold red]🔐 ADMIN HWID MANAGER[/bold red]\n'
        f'Manage authorized devices for keys\n'
        f'Contact: {SUPPORT_CONTACT}',
        border_style='red'
    ))
    
    if not _auth_data or _auth_data.get('type') != 'admin':
        console.print('[red]❌ Admin access required![/red]')
        console.print(f'[yellow]Contact {SUPPORT_CONTACT} for admin access.[/yellow]')
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    
    keys_data = get_keys_from_github()
    if not keys_data:
        console.print('[red]❌ Cannot fetch keys[/red]')
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    
    expired_removed = auto_delete_expired_keys(keys_data)
    if expired_removed > 0:
        console.print(f'[yellow]✅ Auto-removed {expired_removed} expired key(s)[/yellow]')
        push_keys_to_github(keys_data)
        keys_data = get_keys_from_github()
    
    while True:
        clear_screen()
        show_banner(_auth_data)
        
        console.print(Panel('[bold cyan]📋 KEYS & AUTHORIZED HWIDs[/bold cyan]', border_style='cyan'))
        
        table = Table(box=rich_box.SIMPLE)
        table.add_column('#', style='bold yellow', width=4, justify='center')
        table.add_column('Key', style='bold cyan')
        table.add_column('Type', style='yellow')
        table.add_column('Expiry', style='red')
        table.add_column('Authorized HWIDs', style='green')
        table.add_column('Count', style='white', justify='center')
        
        key_list = list(keys_data.get('keys', {}).items())
        for idx, (key_name, key_info) in enumerate(key_list, 1):
            hwids = key_info.get('authorized_hwids', [])
            expiry = key_info.get('expiry', 'N/A')
            hwid_str = '\n'.join(hwids[:3]) + (f'\n... +{len(hwids)-3} more' if len(hwids) > 3 else '')
            table.add_row(
                str(idx),
                key_name[:20] + '...' if len(key_name) > 20 else key_name,
                key_info.get('type', 'free'),
                expiry,
                hwid_str or '[dim]None[/dim]',
                str(len(hwids))
            )
        
        console.print(table)
        console.print(f'\n[dim]Your HWID: {get_hwid()}[/dim]')
        
        console.print('\n[bold cyan]━━━ OPTIONS ━━━[/bold cyan]')
        console.print('  [bold green][1][/bold green] ➕ Add HWID to a key')
        console.print('  [bold green][2][/bold green] ➖ Remove HWID from a key')
        console.print('  [bold green][3][/bold green] 👤 Show your HWID')
        console.print('  [bold green][4][/bold green] 🔄 Refresh keys from GitHub')
        console.print('  [bold green][5][/bold green] 🗑️ Auto Delete Expired Keys')
        console.print('  [bold green][6][/bold green] 📊 Rate Limiter Status')
        console.print('  [bold red][0][/bold red] ⬅ Back')
        
        choice = Prompt.ask('[bold yellow]Select[/bold yellow]', choices=['1', '2', '3', '4', '5', '6', '0'], default='0')
        
        if choice == '0':
            break
        elif choice == '3':
            console.print(f'\n[bold green]Your HWID:[/bold green] {get_hwid()}')
            console.print('[dim]Copy this to add to any key[/dim]')
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            continue
        elif choice == '4':
            console.print('[cyan]🔄 Refreshing keys from GitHub...[/cyan]')
            keys_data = get_keys_from_github()
            if keys_data:
                console.print('[green]✅ Keys refreshed![/green]')
            else:
                console.print('[red]❌ Failed to refresh keys[/red]')
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            continue
        elif choice == '5':
            console.print('[yellow]🗑️ Auto deleting expired keys...[/yellow]')
            removed = auto_delete_expired_keys(keys_data)
            if removed > 0:
                console.print(f'[green]✅ Removed {removed} expired key(s)[/green]')
                push_keys_to_github(keys_data)
                keys_data = get_keys_from_github()
            else:
                console.print('[green]✅ No expired keys found[/green]')
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            continue
        elif choice == '6':
            show_rate_limiter_status()
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            continue
        
        console.print(f'\n[bold cyan]━━━ SELECT KEY ━━━[/bold cyan]')
        for idx, (key_name, key_info) in enumerate(key_list, 1):
            hwids = key_info.get('authorized_hwids', [])
            hwid_count = len(hwids)
            expiry = key_info.get('expiry', 'N/A')
            console.print(f'  [yellow]{idx}[/yellow]. {key_name[:30]} [dim]({key_info.get("type", "free")})[/dim] [green]({hwid_count} HWIDs)[/green] [red]Exp: {expiry}[/red]')
        
        try:
            key_idx = int(Prompt.ask(f'[bold yellow]Enter key number (1-{len(key_list)})[/bold yellow]')) - 1
            if key_idx < 0 or key_idx >= len(key_list):
                console.print('[red]❌ Invalid selection[/red]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            selected_key, selected_info = key_list[key_idx]
        except ValueError:
            console.print('[red]❌ Invalid input[/red]')
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            continue
        
        current_hwids = selected_info.get('authorized_hwids', [])
        
        if choice == '1':
            console.print(f'\n[bold cyan]━━━ ADD HWID TO: {selected_key} ━━━[/bold cyan]')
            console.print(f'[dim]Current HWIDs: {current_hwids if current_hwids else "None"}[/dim]')
            
            hwid_to_add = Prompt.ask('[bold green]Enter HWID to add[/bold green]').strip()
            if not hwid_to_add:
                console.print('[red]❌ HWID cannot be empty![/red]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            
            if hwid_to_add in current_hwids:
                console.print(f'[yellow]⚠ HWID already exists for this key[/yellow]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            
            console.print(f'\n[dim]Key: {selected_key}[/dim]')
            console.print(f'[dim]HWID to add: {hwid_to_add}[/dim]')
            confirm = Prompt.ask('[bold yellow]Confirm add? (y/n)[/bold yellow]', choices=['y', 'n'], default='y')
            if confirm.lower() != 'y':
                console.print('[dim]Cancelled[/dim]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            
            current_hwids.append(hwid_to_add)
            selected_info['authorized_hwids'] = current_hwids
            keys_data['keys'][selected_key] = selected_info
            
            console.print('[cyan]📤 Uploading to GitHub...[/cyan]')
            if push_keys_to_github(keys_data):
                console.print(f'[green]✅ HWID added to {selected_key}[/green]')
                console.print(f'[dim]HWID: {hwid_to_add}[/dim]')
                keys_data = get_keys_from_github()
            else:
                console.print('[red]❌ Failed to update GitHub[/red]')
            
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            
        elif choice == '2':
            if not current_hwids:
                console.print('[yellow]⚠ No HWIDs to remove for this key[/yellow]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            
            console.print(f'\n[bold cyan]━━━ REMOVE HWID FROM: {selected_key} ━━━[/bold cyan]')
            for idx, hwid in enumerate(current_hwids, 1):
                console.print(f'  [yellow]{idx}[/yellow]. {hwid}')
            
            try:
                hwid_idx = int(Prompt.ask('[bold red]Select HWID to remove (number)[/bold red]')) - 1
                if hwid_idx < 0 or hwid_idx >= len(current_hwids):
                    console.print('[red]❌ Invalid selection[/red]')
                    Prompt.ask('\n[white]Press Enter...[/white]', default='')
                    continue
                
                removed_hwid = current_hwids[hwid_idx]
                
                console.print(f'\n[dim]Key: {selected_key}[/dim]')
                console.print(f'[dim]HWID to remove: {removed_hwid}[/dim]')
                confirm = Prompt.ask('[bold yellow]Confirm remove? (y/n)[/bold yellow]', choices=['y', 'n'], default='y')
                if confirm.lower() != 'y':
                    console.print('[dim]Cancelled[/dim]')
                    Prompt.ask('\n[white]Press Enter...[/white]', default='')
                    continue
                
                removed_hwid = current_hwids.pop(hwid_idx)
                selected_info['authorized_hwids'] = current_hwids
                keys_data['keys'][selected_key] = selected_info
                
                console.print('[cyan]📤 Uploading to GitHub...[/cyan]')
                if push_keys_to_github(keys_data):
                    console.print(f'[green]✅ HWID removed from {selected_key}[/green]')
                    console.print(f'[dim]Removed: {removed_hwid}[/dim]')
                    keys_data = get_keys_from_github()
                else:
                    console.print('[red]❌ Failed to update GitHub[/red]')
                
            except ValueError:
                console.print('[red]❌ Invalid input[/red]')
            
            Prompt.ask('\n[white]Press Enter...[/white]', default='')

# ============================================================
# MEMORY MANAGER
# ============================================================

class MemoryManager:
    @staticmethod
    def get_available_ram_mb() -> int:
        if HAS_PSUTIL:
            try: return int(psutil.virtual_memory().available / 1024 / 1024)
            except Exception: pass
        return 512

    @staticmethod
    def should_use_mmap(file_size_bytes: int) -> bool:
        available_mb = MemoryManager.get_available_ram_mb()
        file_mb = file_size_bytes / 1024 / 1024
        threshold_mb = min(available_mb * 0.4, 200)
        return file_mb > threshold_mb

    @staticmethod
    def print_memory_status():
        if not HAS_PSUTIL: return
        try:
            mem = psutil.virtual_memory()
            total_mb = mem.total / 1024 / 1024
            avail_mb = mem.available / 1024 / 1024
            pct = mem.percent
            color = "green" if pct < 60 else ("yellow" if pct < 80 else "red")
            console.print(f"  [{color}]RAM: {avail_mb:.0f}MB free / {total_mb:.0f}MB total ({pct:.1f}% used)[/{color}]")
        except Exception: pass

    @staticmethod
    def force_gc(): gc.collect()

# ============================================================
# MMAP FILE READER
# ============================================================

class MmapFileReader:
    def __init__(self, file_path: Path):
        self._path = file_path
        self._file_size = file_path.stat().st_size
        self._f = None
        self._mmap = None
        self._buffer = None
        self._use_mmap = MemoryManager.should_use_mmap(self._file_size)
        file_mb = self._file_size / 1024 / 1024
        avail_mb = MemoryManager.get_available_ram_mb()
        if self._use_mmap:
            console.print(f"[cyan]Large file: {file_mb:.1f}MB (RAM: {avail_mb:.0f}MB) — using mmap I/O[/cyan]")
            self._open_mmap()
        else:
            console.print(f"[cyan]Loading {file_mb:.1f}MB file into memory...[/cyan]")
            self._load_direct()

    def _open_mmap(self):
        try:
            self._f = open(self._path, 'rb')
            self._mmap = mmap.mmap(self._f.fileno(), 0, access=mmap.ACCESS_READ)
            self._buffer = memoryview(self._mmap)
            console.print("[green]mmap active — RAM safe mode ON[/green]")
        except Exception as e:
            console.print(f"[yellow]mmap failed ({e}), falling back to direct load[/yellow]")
            self._fallback_chunked_load()

    def _load_direct(self):
        with open(self._path, 'rb') as f:
            self._buffer = memoryview(f.read())

    def _fallback_chunked_load(self):
        console.print("[yellow]Direct load — may use more RAM[/yellow]")
        try:
            with open(self._path, 'rb') as f:
                self._buffer = memoryview(f.read())
        except MemoryError:
            console.print("[red]CRITICAL: Not enough RAM![/red]")
            raise

    @property
    def buffer(self): return self._buffer

    def close(self):
        if self._mmap:
            try: self._mmap.close()
            except Exception: pass
        if self._f:
            try: self._f.close()
            except Exception: pass
        self._buffer = None
        MemoryManager.force_gc()

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
    def __del__(self): self.close()

# ============================================================
# SM4 IMPLEMENTATION (COMPLETE)
# ============================================================

_S_BOX = bytes([
    0x34, 0x66, 0x25, 0x74, 0x89, 0x78, 0xE4, 0xA9, 0x5A, 0x41, 0xBC, 0x7A, 0xD6, 0x16, 0x21, 0x23,
    0x4D, 0x61, 0xDA, 0x94, 0x9B, 0xDF, 0x13, 0x3C, 0x69, 0x3A, 0x31, 0x0A, 0x5F, 0xD7, 0x99, 0x95,
    0xF1, 0xAE, 0x72, 0x3D, 0x07, 0x60, 0x24, 0xB6, 0x98, 0xEE, 0xC4, 0xA2, 0x2D, 0x88, 0xDD, 0x8D,
    0x04, 0xEA, 0xBB, 0x11, 0xCA, 0x3E, 0x5D, 0xA1, 0xF6, 0x3F, 0xB0, 0x97, 0x80, 0x47, 0x2B, 0xA6,
    0xE6, 0xF7, 0xD9, 0xB1, 0x59, 0xC0, 0x7C, 0xBE, 0x54, 0x28, 0xB7, 0x7E, 0x4F, 0xF8, 0x43, 0x6E,
    0xA0, 0x50, 0x0E, 0xF5, 0x90, 0xB8, 0xFB, 0xA3, 0x7B, 0x62, 0x19, 0x46, 0x03, 0x2A, 0xB9, 0x8F,
    0x9F, 0x77, 0xB4, 0x5B, 0x83, 0x87, 0x08, 0xEB, 0xE2, 0x1E, 0x42, 0xF0, 0x0F, 0xE8, 0x71, 0x6A,
    0x75, 0xAD, 0x55, 0x1F, 0xB5, 0xAB, 0x33, 0xFA, 0x7F, 0x15, 0xBD, 0x85, 0xD8, 0x06, 0x68, 0xB3,
    0x52, 0x30, 0x48, 0x0B, 0x00, 0xED, 0xEF, 0xB2, 0x57, 0x8E, 0xE7, 0x6C, 0xD5, 0xE5, 0x2E, 0x53,
    0x82, 0x05, 0xF9, 0x81, 0xF4, 0x56, 0xBF, 0x8C, 0x4B, 0xE3, 0xDB, 0x4A, 0x91, 0x4C, 0x2C, 0xD3,
    0x40, 0x29, 0x4E, 0x20, 0x14, 0x36, 0x79, 0x09, 0x6F, 0xD1, 0x37, 0xE0, 0x39, 0x0C, 0x8A, 0x92,
    0x38, 0x12, 0x35, 0x6D, 0xE1, 0xFD, 0x93, 0x9A, 0x17, 0xD4, 0xC9, 0x9C, 0x6B, 0x84, 0x26, 0x9D,
    0xAF, 0x76, 0xC1, 0x9E, 0xD0, 0x96, 0xC5, 0xCB, 0xE9, 0x73, 0x49, 0xD2, 0xCD, 0x64, 0xC3, 0xC7,
    0x01, 0x7D, 0xF3, 0xAC, 0xFC, 0xDE, 0xA4, 0x44, 0x32, 0x1B, 0xC2, 0xBA, 0x1C, 0x02, 0xC6, 0x27,
    0x45, 0x8B, 0xF2, 0x18, 0xA7, 0x10, 0x51, 0x1D, 0xC8, 0xCF, 0x63, 0xFF, 0x2F, 0x0D, 0x58, 0xCE,
    0x65, 0xA5, 0xDC, 0x1A, 0x3B, 0x86, 0xFE, 0x22, 0x5C, 0xA8, 0x5E, 0x67, 0xAA, 0xEC, 0x70, 0xCC
])

_FK = [0x46970E9C, 0x4BC0685E, 0x59056186, 0xBCA2491E]
_CK = [
    0x000EB92B, 0x3A0AE783, 0x9E3B5C67, 0xADDBDABF, 0x7B7484CB, 0x49156C63,
    0xC79AB5E7, 0x79EC9CFF, 0x1725BEAB, 0x2FB89CA3, 0x24808AD7, 0xDDD28B1F,
    0x4740DA4B, 0xBBC3EA73, 0x247B30E7, 0x91BE385F, 0x0401248B, 0x45FCD3A3,
    0x530B4CE7, 0xC68DD35F, 0xE3D16C2B, 0x4F698C13, 0x6B92C747, 0x769EFB1F,
    0x4C73BE9B, 0xC942B193, 0xAD80D827, 0x372FB33F, 0x13CB6AAB, 0x2BDC0AA3,
    0x17A4A247, 0xD5E96CAF
]

def ROL32(x, n):
    return (x << n) & 0xFFFFFFFF | (x >> (32 - n))

def _BS(X):
    return ((_S_BOX[(X >> 24) & 0xff] << 24) |
            (_S_BOX[(X >> 16) & 0xff] << 16) |
            (_S_BOX[(X >> 8) & 0xff] << 8) |
            (_S_BOX[X & 0xff]))

def _T0(X):
    X = _BS(X)
    return X ^ ROL32(X, 2) ^ ROL32(X, 10) ^ ROL32(X, 18) ^ ROL32(X, 24)

def _T1(X):
    X = _BS(X)
    return X ^ ROL32(X, 13) ^ ROL32(X, 23)

def _key_expand(key: bytes, rkey: list):
    K0 = int.from_bytes(key[0:4], "big") ^ _FK[0]
    K1 = int.from_bytes(key[4:8], "big") ^ _FK[1]
    K2 = int.from_bytes(key[8:12], "big") ^ _FK[2]
    K3 = int.from_bytes(key[12:16], "big") ^ _FK[3]
    for i in range(0, 32, 4):
        K0 = K0 ^ _T1(K1 ^ K2 ^ K3 ^ _CK[i])
        rkey[i] = K0
        K1 = K1 ^ _T1(K2 ^ K3 ^ K0 ^ _CK[i + 1])
        rkey[i + 1] = K1
        K2 = K2 ^ _T1(K3 ^ K0 ^ K1 ^ _CK[i + 2])
        rkey[i + 2] = K2
        K3 = K3 ^ _T1(K0 ^ K1 ^ K2 ^ _CK[i + 3])
        rkey[i + 3] = K3

class SM4:
    @classmethod
    def key_length(cls): return 16
    @classmethod
    def block_length(cls): return 16

    def __init__(self, key: bytes):
        if len(key) != self.key_length():
            raise ValueError(f'Key must be {self.key_length()} bytes')
        self._key = key
        self._rkey = [0] * 32
        _key_expand(self._key, self._rkey)
        self._block_buffer = bytearray()

    def encrypt(self, block: bytes) -> bytes:
        if len(block) != self.block_length():
            raise ValueError(f'Block must be {self.block_length()} bytes')
        RK = self._rkey
        X0 = int.from_bytes(block[0:4], "big")
        X1 = int.from_bytes(block[4:8], "big")
        X2 = int.from_bytes(block[8:12], "big")
        X3 = int.from_bytes(block[12:16], "big")
        for i in range(0, 32, 4):
            X0 = X0 ^ _T0(X1 ^ X2 ^ X3 ^ RK[i])
            X1 = X1 ^ _T0(X2 ^ X3 ^ X0 ^ RK[i + 1])
            X2 = X2 ^ _T0(X3 ^ X0 ^ X1 ^ RK[i + 2])
            X3 = X3 ^ _T0(X0 ^ X1 ^ X2 ^ RK[i + 3])
        BUFFER = self._block_buffer
        BUFFER.clear()
        BUFFER.extend(X3.to_bytes(4, "big"))
        BUFFER.extend(X2.to_bytes(4, "big"))
        BUFFER.extend(X1.to_bytes(4, "big"))
        BUFFER.extend(X0.to_bytes(4, "big"))
        return bytes(BUFFER)

    def decrypt(self, block: bytes) -> bytes:
        if len(block) != self.block_length():
            raise ValueError(f'Block must be {self.block_length()} bytes')
        RK = self._rkey
        X0 = int.from_bytes(block[0:4], "big")
        X1 = int.from_bytes(block[4:8], "big")
        X2 = int.from_bytes(block[8:12], "big")
        X3 = int.from_bytes(block[12:16], "big")
        for i in range(0, 32, 4):
            X0 = X0 ^ _T0(X1 ^ X2 ^ X3 ^ RK[31 - i])
            X1 = X1 ^ _T0(X2 ^ X3 ^ X0 ^ RK[30 - i])
            X2 = X2 ^ _T0(X3 ^ X0 ^ X1 ^ RK[29 - i])
            X3 = X3 ^ _T0(X0 ^ X1 ^ X2 ^ RK[28 - i])
        BUFFER = self._block_buffer
        BUFFER.clear()
        BUFFER.extend(X3.to_bytes(4, "big"))
        BUFFER.extend(X2.to_bytes(4, "big"))
        BUFFER.extend(X1.to_bytes(4, "big"))
        BUFFER.extend(X0.to_bytes(4, "big"))
        return bytes(BUFFER)

# ============================================================
# MISC / READER / WRITER
# ============================================================

class Misc:
    @staticmethod
    def pad_to_n(data: bytes, n: int) -> bytes:
        assert n > 0
        padding = n - len(data) % n
        return data if padding == n else data + b'\x00' * padding
    @staticmethod
    def align_up(x: int, n: int) -> int:
        return (x + n - 1) // n * n

class Reader:
    def __init__(self, buffer, cursor=0):
        self._buffer = buffer
        self._cursor = cursor
    def u1(self, move_cursor=True): return self.unpack('B', move_cursor=move_cursor)[0]
    def u4(self, move_cursor=True): return self.unpack('<I', move_cursor=move_cursor)[0]
    def u8(self, move_cursor=True): return self.unpack('<Q', move_cursor=move_cursor)[0]
    def i1(self, move_cursor=True): return self.unpack('b', move_cursor=move_cursor)[0]
    def i4(self, move_cursor=True): return self.unpack('<i', move_cursor=move_cursor)[0]
    def i8(self, move_cursor=True): return self.unpack('<q', move_cursor=move_cursor)[0]
    def s(self, n: int, move_cursor=True): return self.unpack(f'{n}s', move_cursor=move_cursor)[0]
    def unpack(self, f, offset=0, move_cursor=True):
        x = struct.unpack_from(f, self._buffer, self._cursor + offset)
        if move_cursor:
            self._cursor += struct.calcsize(f)
        return x
    def string(self, move_cursor=True) -> str:
        length = self.i4(move_cursor=move_cursor)
        if length == 0: return str()
        assert length > 0
        offset = 0 if move_cursor else 4
        return self.unpack(f'{length}s', offset=offset, move_cursor=move_cursor)[0].rstrip(b'\x00').decode()

class Writer:
    def __init__(self):
        self._buffer = bytearray()
    def u1(self, v): self.pack('B', v)
    def u4(self, v): self.pack('<I', v)
    def u8(self, v): self.pack('<Q', v)
    def i1(self, v): self.pack('b', v)
    def i4(self, v): self.pack('<i', v)
    def i8(self, v): self.pack('<q', v)
    def s(self, data: bytes): self._buffer.extend(data)
    def pack(self, f, *values):
        self._buffer.extend(struct.pack(f, *values))
    def string(self, text: str):
        encoded = text.encode() + b'\x00'
        self.i4(len(encoded))
        self.s(encoded)
    def get_buffer(self) -> bytes: return bytes(self._buffer)
    def size(self) -> int: return len(self._buffer)
    def align_to(self, alignment: int):
        current_size = len(self._buffer)
        padding = (alignment - current_size % alignment) % alignment
        if padding > 0:
            self._buffer.extend(b'\x00' * padding)

# ============================================================
# PAK CLASSES - COMPLETE
# ============================================================

class PakInfo:
    def __init__(self, buffer, keystream: List[int]):
        def decrypt_index_encrypted(x: int) -> int:
            MASK_8 = 255
            return (x ^ keystream[3]) & MASK_8
        def decrypt_magic(x: int) -> int:
            return x ^ keystream[2]
        def decrypt_index_hash(x: bytes) -> bytes:
            key = struct.pack('<5I', *keystream[4:][:5])
            assert len(x) == len(key)
            return bytes((a ^ b for a, b in zip(x, key)))
        def decrypt_index_size(x: int) -> int:
            return x ^ (keystream[10] << 32 | keystream[11])
        def decrypt_index_offset(x: int) -> int:
            return x ^ (keystream[0] << 32 | keystream[1])
        reader = Reader(buffer[-PakInfo._mem_size((-1)):])
        self.index_encrypted = decrypt_index_encrypted(reader.u1()) == 1
        self.magic = decrypt_magic(reader.u4())
        self.version = reader.u4()
        self.index_hash = decrypt_index_hash(reader.s(20)) if self.version >= 6 else bytes()
        self.index_size = decrypt_index_size(reader.u8())
        self.index_offset = decrypt_index_offset(reader.u8())
        if self.version <= 3:
            self.index_encrypted = False
    @staticmethod
    def _mem_size(_: int) -> int:
        return 45

class TencentPakInfo(PakInfo):
    def __init__(self, buffer, keystream: List[int]):
        def decrypt_unk(x: bytes) -> bytes:
            key = struct.pack('<8I', *keystream[7:][:8])
            assert len(x) == len(key)
            return bytes((a ^ b for a, b in zip(x, key)))
        def decrypt_stem_hash(x: int) -> int:
            return x ^ keystream[8]
        def decrypt_unk_hash(x: int) -> int:
            return x ^ keystream[9]
        super().__init__(buffer, keystream)
        reader = Reader(buffer[-TencentPakInfo._mem_size(self.version):])
        self.unk1 = decrypt_unk(reader.s(32)) if self.version >= 7 else bytes()
        self.packed_key = reader.s(256) if self.version >= 8 else bytes()
        self.packed_iv = reader.s(256) if self.version >= 8 else bytes()
        self.packed_index_hash = reader.s(256) if self.version >= 8 else bytes()
        self.stem_hash = decrypt_stem_hash(reader.u4()) if self.version >= 9 else 0
        self.unk2 = decrypt_unk_hash(reader.u4()) if self.version >= 9 else 0
        self.content_org_hash = reader.s(20) if self.version >= 12 else bytes()
    @staticmethod
    def _mem_size(version: int) -> int:
        size_for_7 = 32 if version >= 7 else 0
        size_for_8 = 768 if version >= 8 else 0
        size_for_9 = 8 if version >= 9 else 0
        size_for_12 = 20 if version >= 12 else 0
        return PakInfo._mem_size(version) + size_for_7 + size_for_8 + size_for_9 + size_for_12

class PakCompressedBlock:
    def __init__(self, reader: Reader):
        self.start = reader.u8()
        self.end = reader.u8()

@dataclass
class TencentPakEntry:
    def __init__(self, reader: Reader, version: int):
        self.content_hash = reader.s(20)
        if version <= 1:
            _ = reader.u8()
        self.offset = reader.u8()
        self.uncompressed_size = reader.u8()
        self.compression_method = reader.u4() & CM_MASK
        self.size = reader.u8()
        self.unk1 = reader.u1() if version >= 5 else 0
        self.unk2 = reader.s(20) if version >= 5 else bytes()
        if self.compression_method != 0 and version >= 3:
            self.compressed_blocks = [PakCompressedBlock(reader) for _ in range(reader.u4())]
        else:
            self.compressed_blocks = []
        self.compression_block_size = reader.u4() if version >= 4 else 0
        self.encrypted = reader.u1() == 1 if version >= 4 else False
        self.encryption_method = reader.u4() if version >= 12 else 0
        self.index_new_sep = reader.u4() if version >= 12 else 0

class PakCrypto:
    class _LCG:
        def __init__(self, seed: int):
            self.state = seed
        def next(self) -> int:
            MASK_32 = 4294967295
            MSB_1 = 2147483648
            def wrap(x: int) -> int:
                x &= MASK_32
                if not x & MSB_1:
                    return x
                else:
                    return (x + MSB_1 & MASK_32) - MSB_1
            x1 = wrap(1103515245 * self.state)
            self.state = wrap(x1 + 12345)
            x2 = wrap(x1 + 77880) if self.state < 0 else self.state
            return (x2 >> 16 & MASK_32) % 32767
    @staticmethod
    def zuc_keystream() -> List[int]:
        zuc = gmalg.ZUC(ZUC_KEY, ZUC_IV)
        return [struct.unpack('>I', zuc.generate())[0] for _ in range(16)]
    @staticmethod
    def _xorxor(buffer, x) -> bytes:
        return bytes((buffer[i] ^ x[i % len(x)] for i in range(len(buffer))))
    @staticmethod
    def _hashhash(buffer, n: int) -> bytes:
        result = bytes()
        for i in range(math.ceil(n / SHA1.digest_size)):
            result += SHA1.new(buffer).digest()
        if len(result) >= n:
            result = result[:n]
            return result
        else:
            result += b'\x00' * (n - len(result))
            return result
    @staticmethod
    def _meowmeow(buffer) -> bytes:
        def unpad(x):
            skip = 1 + next((i for i in range(len(x)) if x[i]!= 0))
            return x[skip:]
        if len(buffer) < 43:
            return bytes()
        else:
            x1 = buffer[1:][:SHA1.digest_size]
            x2 = buffer[SHA1.digest_size + 1:]
            x1 = PakCrypto._xorxor(x1, PakCrypto._hashhash(x2, len(x1)))
            x2 = PakCrypto._xorxor(x2, PakCrypto._hashhash(x1, len(x2)))
            part1, m = (x2[:SHA1.digest_size], x2[SHA1.digest_size:])
            if part1!= SHA1.new(b'\x00' * SHA1.digest_size).digest():
                return bytes()
            else:
                return unpad(m)
    @staticmethod
    def rsa_extract(signature: bytes, modulus: bytes) -> bytes:
        c = int.from_bytes(signature, 'little')
        n = int.from_bytes(modulus, 'little')
        e = 65537
        m = pow(c, e, n).to_bytes(256, 'little').rstrip(b'\x00')
        return PakCrypto._meowmeow(Misc.pad_to_n(m, 4))
    @staticmethod
    def _decrypt_simple1(ciphertext) -> bytes:
        return bytes((x ^ SIMPLE1_DECRYPT_KEY for x in ciphertext))
    @staticmethod
    def _decrypt_simple2(ciphertext) -> bytes:
        class RollingKey:
            def __init__(self, initial_value: int):
                self._value = initial_value
            def update(self, x: int) -> int:
                self._value ^= x
                return self._value
        assert len(ciphertext) % SIMPLE2_BLOCK_SIZE == 0
        initial_key, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
        rolling_key = RollingKey(initial_key)
        plaintext = (struct.pack('<I', rolling_key.update(x)) for x in struct.unpack(f'<{len(ciphertext) // 4}I', ciphertext))
        return bytes(it.chain.from_iterable(plaintext))
    @staticmethod
    @lru_cache(maxsize=1)
    def _derive_sm4_key(file_path: PurePath, encryption_method: int) -> bytes:
        part1 = file_path.stem.lower()
        if encryption_method == EM_SM4_2:
            secret = SM4_SECRET_2
        else:
            if encryption_method == EM_SM4_4:
                secret = SM4_SECRET_4
            else:
                index = (encryption_method - EM_SM4_NEW_BASE) % len(SM4_SECRET_NEW)
                secret = f'{SM4_SECRET_NEW[index]}{encryption_method}'
        return SHA1.new(str(part1 + secret).encode()).digest()[:SM4.key_length()]
    @staticmethod
    @lru_cache(maxsize=1)
    def _sm4_context_for_key(key: bytes) -> SM4:
        return SM4(key)
    @staticmethod
    def _decrypt_sm4(ciphertext, file_path: PurePath, encryption_method: int) -> bytes:
        assert len(ciphertext) % SM4.block_length() == 0
        key = PakCrypto._derive_sm4_key(file_path, encryption_method)
        sm4 = PakCrypto._sm4_context_for_key(key)
        return bytes(it.chain.from_iterable((sm4.decrypt(x) for x in it.batched(ciphertext, SM4.block_length()))))
    @staticmethod
    def decrypt_index(ciphertext, pak_info: TencentPakInfo) -> bytes:
        if pak_info.version > 7:
            key = PakCrypto.rsa_extract(pak_info.packed_key, RSA_MOD_1)
            iv = PakCrypto.rsa_extract(pak_info.packed_iv, RSA_MOD_1)
            assert len(key) == 32 and len(iv) == 32
            aes = AES.new(key, MODE_CBC, iv[:16])
            return unpad(aes.decrypt(ciphertext), AES.block_size)
        else:
            return bytes(PakCrypto._decrypt_simple1(ciphertext))
    @staticmethod
    def _is_simple1_method(encryption_method: int) -> bool:
        return encryption_method == EM_SIMPLE1
    @staticmethod
    def _is_simple2_method(encryption_method: int) -> bool:
        return encryption_method == EM_SIMPLE2 or encryption_method == 17
    @staticmethod
    def _is_sm4_method(encryption_method: int) -> bool:
        return encryption_method == EM_SM4_2 or encryption_method == EM_SM4_4 or encryption_method & EM_SM4_NEW_MASK!= 0
    @staticmethod
    def align_encrypted_content_size(n: int, encryption_method: int) -> int:
        if PakCrypto._is_simple2_method(encryption_method):
            return Misc.align_up(n, SIMPLE2_BLOCK_SIZE)
        else:
            if PakCrypto._is_sm4_method(encryption_method):
                return Misc.align_up(n, SM4.block_length())
            else:
                return n
    @staticmethod
    def decrypt_block(ciphertext, file: PurePath, encryption_method: int) -> bytes:
        if PakCrypto._is_simple1_method(encryption_method):
            return PakCrypto._decrypt_simple1(ciphertext)
        else:
            if PakCrypto._is_simple2_method(encryption_method):
                return PakCrypto._decrypt_simple2(ciphertext)
            else:
                if PakCrypto._is_sm4_method(encryption_method):
                    return PakCrypto._decrypt_sm4(ciphertext, file, encryption_method)
                else:
                    raise ValueError(f'Unknown encryption method: {encryption_method}')
    @staticmethod
    @lru_cache(maxsize=33)
    def generate_block_indices(n: int, encryption_method: int) -> List[int]:
        if not PakCrypto._is_sm4_method(encryption_method):
            return list(range(n))
        else:
            permutation = []
            lcg = PakCrypto._LCG(n)
            while len(permutation)!= n:
                x = lcg.next() % n
                if x not in permutation:
                    permutation.append(x)
            inverse = [0] * len(permutation)
            for i, x in enumerate(permutation):
                inverse[x] = i
            return inverse

class PakCompression:
    @staticmethod
    @lru_cache(maxsize=33)
    def _zstd_decompressor(dict: ZstdCompressionDict) -> ZstdDecompressor:
        return ZstdDecompressor(dict)
    @staticmethod
    def zstd_dictionary(dict_data) -> ZstdCompressionDict:
        return ZstdCompressionDict(dict_data, DICT_TYPE_AUTO)
    @staticmethod
    def decompress_block(block, dict: Optional[ZstdCompressionDict], compression_method: int) -> bytes:
        if compression_method == CM_ZLIB:
            try:
                return zlib.decompress(block)
            except zlib.error:
                return block
        else:
            if compression_method == CM_ZSTD or compression_method == CM_ZSTD_DICT:
                if compression_method!= CM_ZSTD_DICT:
                    dict = None
                return PakCompression._zstd_decompressor(dict).decompress(block)
            else:
                raise ValueError(f'Unknown compression method: {compression_method}')

class TencentPakFile:
    def __init__(self, file_path: PurePath, is_od=False):
        self._file_path = file_path
        with open(file_path, 'rb') as file:
            self._file_content = memoryview(file.read())
        self._is_od = is_od
        self._mount_point = PurePath()
        self._is_zstd_with_dict = 'zsdic' in str(self._file_path)
        self._zstd_dict = None
        self._files = []
        self._index = {}
        self._pak_info = TencentPakInfo(self._file_content, PakCrypto.zuc_keystream())
        self._verify_stem_hash()
        self._tencent_load_index()
    
    def _get_method_str(self, method_int, is_encryption):
        if is_encryption:
            if PakCrypto._is_simple1_method(method_int): return "SIMPLE1"
            if PakCrypto._is_simple2_method(method_int): return "SIMPLE2"
            if PakCrypto._is_sm4_method(method_int): return f"SM4 (Type {method_int})"
            return "NONE" if method_int == 0 else "UNKNOWN"
        else:
            if method_int == CM_NONE: return "NONE"
            if method_int == CM_ZLIB: return "ZLIB"
            if method_int == CM_ZSTD: return "ZSTD"
            if method_int == CM_ZSTD_DICT: return "ZSTD_DICT"
            return "UNKNOWN"
    
    def _verify_stem_hash(self) -> None:
        if not self._is_od and self._pak_info.version >= 9:
                assert self._pak_info.stem_hash == zlib.crc32(self._file_path.stem.encode('utf-32le'))
    def _tencent_load_index(self) -> None:
        index_data = self._file_content[self._pak_info.index_offset:][:self._pak_info.index_size]
        if self._pak_info.index_encrypted:
            index_data = PakCrypto.decrypt_index(index_data, self._pak_info)
        else:
            index_data = index_data
        self._verify_index_hash(index_data)
        self._load_index(index_data)
    def _verify_index_hash(self, index_data) -> None:
        expected_hash = self._pak_info.index_hash
        if not self._is_od and self._pak_info.version >= 8:
                assert expected_hash == PakCrypto.rsa_extract(self._pak_info.packed_index_hash, RSA_MOD_2)
        assert expected_hash == SHA1.new(index_data).digest()
    @staticmethod
    def _construct_mount_point(mount_point: str) -> PurePath:
        result = PurePath()
        for part in PurePath(mount_point).parts:
            if part!= '..':
                result /= part
        return result
    def _peek_content(self, offset: int, size: int, encryption_method: int) -> memoryview:
        size = PakCrypto.align_encrypted_content_size(size, encryption_method)
        return self._file_content[offset:][:size]
    def _peek_block_content(self, block: PakCompressedBlock, encryption_method: int) -> memoryview:
        size = PakCrypto.align_encrypted_content_size(block.end - block.start, encryption_method)
        return self._file_content[block.start:][:size]
    def _construct_zstd_dict(self, dict_entry: TencentPakEntry) -> None:
        assert not self._zstd_dict
        assert not dict_entry.encrypted
        assert dict_entry.compression_method == CM_NONE
        reader = Reader(self._peek_content(dict_entry.offset, dict_entry.size, 0))
        dict_size = reader.u8()
        _ = reader.u4()
        assert dict_size == reader.u4()
        dict_data = reader.s(dict_size)
        self._zstd_dict = PakCompression.zstd_dictionary(dict_data)
    def _load_index(self, index_data) -> None:
        if self._pak_info.version <= 10:
            raise ValueError(f'Unsupported version: {self._pak_info.version}')
        else:
            reader = Reader(index_data)
            self._mount_point = self._construct_mount_point(reader.string())
            self._files = [TencentPakEntry(reader, self._pak_info.version) for _ in range(reader.u4())]
            for _ in range(reader.u8()):
                dir_path = PurePath(reader.string())
                e = {reader.string(): self._files[~reader.i4()] for _ in range(reader.u8())}
                if self._is_zstd_with_dict and dir_path.name == 'zstddic':
                    assert len(e) == 1
                    self._construct_zstd_dict(e[[*e.keys()][0]])
                else:
                    self._index.update({PurePath(dir_path): e})
    
    def _write_to_disk(self, file_path: Path, entry: TencentPakEntry) -> None:
        encryption_method = entry.encryption_method
        compression_method = entry.compression_method

        enc_str = self._get_method_str(encryption_method, True)
        comp_str = self._get_method_str(compression_method, False)
        console.print(f"[bold cyan]->[/] Unpack: [bold green]{file_path.name}[/] [[bold yellow]{comp_str}[/]/[bold magenta]{enc_str}[/]]")

        with open(file_path, 'wb') as file:
            if compression_method == CM_NONE:
                data = self._peek_content(entry.offset, entry.size, encryption_method)
                if entry.encrypted:
                    data = PakCrypto.decrypt_block(data, file_path, encryption_method)
                file.write(data)
                return
            else:
                for x in PakCrypto.generate_block_indices(len(entry.compressed_blocks), encryption_method):
                    data = self._peek_block_content(entry.compressed_blocks[x], encryption_method)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, file_path, encryption_method)
                    data = PakCompression.decompress_block(data, self._zstd_dict, compression_method)
                    file.write(data)
    
    def dump(self, out_path: Path) -> None:
        out_path = out_path / self._mount_point
        out_path.mkdir(parents=True, exist_ok=True)
        total_files = sum(len(d) for d in self._index.values())
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan][UNPACK][/] {task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Extracting files...", total=total_files)
            for dir_path, dir_content in self._index.items():
                current_out_path = out_path / dir_path
                current_out_path.mkdir(parents=True, exist_ok=True)
                for file_name, entry in dir_content.items():
                    self._write_to_disk(current_out_path / file_name, entry)
                    progress.update(task, advance=1)

def dump_unpacking_log(pak_file, output_log_path: Path):
    with open(output_log_path, 'w', encoding='utf-8') as log_file:
        log_file.write('================================================================================\n')
        log_file.write('PAK UNPACKING DEBUG LOG\n')
        log_file.write('================================================================================\n\n')
        log_file.write(f'PAK File: {pak_file._file_path}\n')
        log_file.write(f'PAK Info Version: {pak_file._pak_info.version}\n')
        log_file.write(f'Mount Point: {pak_file._mount_point}\n')
        log_file.write('--------------------------------------------------------------------------------\n\n')
        file_count = 0
        for dir_path, files in pak_file._index.items():
            for file_name, entry in files.items():
                file_count += 1
                full_path = str(PurePath(dir_path) / file_name).replace('\\', '/')
                log_file.write(f'\n[{file_count}] {full_path}\n')
                log_file.write(f'  Uncompressed Size: {entry.uncompressed_size:,} bytes\n')
                log_file.write(f'  Compressed Size: {entry.size:,} bytes\n')
                log_file.write(f'  Compression Method: {entry.compression_method}\n')
                log_file.write(f'  Encryption Method: {entry.encryption_method}\n')
                log_file.write(f'  Compressed Blocks: {len(entry.compressed_blocks)}\n')
                if entry.compressed_blocks:
                    for i, blk in enumerate(entry.compressed_blocks):
                        block_size = blk.end - blk.start
                        log_file.write(f'    Block {i}: Offset={blk.start:,} Size={block_size:,} bytes\n')
        log_file.write('\n================================================================================\n')
        log_file.write('END OF LOG\n')
        log_file.write('================================================================================\n')
    console.print(f'[bold #00FF88]✅ Debug log saved to: {output_log_path}[/bold #00FF88]')

# ============================================================
# SIMPLE BLOCK DISPLAY CLASS
# ============================================================

class SimpleBlockDisplay:
    """Simple display that shows each file and its blocks"""
    
    def __init__(self, total_files: int, pak_name: str):
        self.total_files = total_files
        self.pak_name = pak_name
        self.processed_files = 0
        self.current_file = ""
        self.current_file_idx = 0
        self.all_blocks = []
        self.total_fitted = 0
        self.total_skipped = 0
        
    def start_file(self, file_name: str, total_blocks: int):
        self.current_file_idx += 1
        self.current_file = file_name
        self.current_blocks = []
        self.current_total_blocks = total_blocks
        self.current_fitted = 0
        self.current_skipped = 0
        
        console.print()
        console.print(f"[bold cyan]┌─────────────────────────────────────────────────────────────[/bold cyan]")
        console.print(f"[bold cyan]│[/] [bold yellow][{self.current_file_idx}/{self.total_files}][/] [bold green]{file_name}[/bold green] [dim]({total_blocks} blocks)[/dim]")
        console.print(f"[bold cyan]├─────────────────────────────────────────────────────────────[/bold cyan]")
        
    def add_block(self, block_idx: int, block_size: int, fitted: bool, compression_ratio: float = None):
        size_mb = block_size / (1024 * 1024)
        if fitted:
            self.current_fitted += 1
            self.total_fitted += 1
            ratio_str = f" [{compression_ratio:.1%}]" if compression_ratio else ""
            status = f"[green]✓ FITTED{ratio_str}[/green]"
        else:
            self.current_skipped += 1
            self.total_skipped += 1
            status = f"[red]✗ SKIPPED[/red]"
        
        console.print(f"[bold cyan]│[/]    Block {block_idx:3d}: {size_mb:>7.2f} MB  →  {status}")
        self.current_blocks.append({'fitted': fitted})
        
    def finish_file(self):
        total_blocks = len(self.current_blocks)
        if total_blocks > 0:
            if self.current_fitted == total_blocks:
                status = "[green]✓ ALL FITTED[/green]"
            elif self.current_fitted > 0:
                status = f"[yellow]✓ {self.current_fitted}/{total_blocks} FITTED[/yellow]"
            else:
                status = "[red]✗ ALL SKIPPED[/red]"
        else:
            status = "[green]✓ DONE[/green]"
        
        console.print(f"[bold cyan]└─────────────────────────────────────────────────────────────[/bold cyan]")
        console.print(f"  [dim]Result: {status}[/dim]")
        
        self.processed_files += 1
        self.all_blocks.extend(self.current_blocks)
        
    def final_summary(self):
        total_blocks = len(self.all_blocks)
        console.print()
        console.print(f"[bold green]╔═════════════════════════════════════════════════════════════════╗[/bold green]")
        console.print(f"[bold green]║[/] [bold yellow]REPACK SUMMARY[/bold yellow]")
        console.print(f"[bold green]║[/]")
        console.print(f"[bold green]║[/]   Total Files:   [bold cyan]{self.processed_files}[/bold cyan]")
        console.print(f"[bold green]║[/]   Total Blocks:  [bold cyan]{total_blocks}[/bold cyan]")
        console.print(f"[bold green]║[/]   Fitted Blocks: [bold green]{self.total_fitted}[/bold green]")
        console.print(f"[bold green]║[/]   Skipped Blocks:[bold red]{self.total_skipped}[/bold red]")
        if total_blocks > 0:
            success_rate = (self.total_fitted / total_blocks) * 100
            console.print(f"[bold green]║[/]   Success Rate:  [bold yellow]{success_rate:.1f}%[/bold yellow]")
        console.print(f"[bold green]╚═════════════════════════════════════════════════════════════════╝[/bold green]")

# ============================================================
# REPACK FUNCTIONS - COMPLETE
# ============================================================

def _pw_string(s):
    if not s: return struct.pack('<i', 0)
    b = s.encode('utf-8') + b'\x00'
    return struct.pack('<i', len(b)) + b

def _pw_entry(e, v):
    w = bytearray(e.content_hash)
    w += struct.pack('<Q', e.offset)
    w += struct.pack('<Q', e.uncompressed_size)
    w += struct.pack('<I', e.compression_method)
    w += struct.pack('<Q', e.size)
    if v >= 5:
        w += bytes([e.unk1])
        w += e.unk2
    if e.compression_method != CM_NONE and v >= 3:
        w += struct.pack('<I', len(e.compressed_blocks))
        for b in e.compressed_blocks:
            w += struct.pack('<QQ', b.start, b.end)
    if v >= 4:
        w += struct.pack('<I', e.compression_block_size)
        w += bytes([1 if e.encrypted else 0])
    if v >= 12:
        w += struct.pack('<II', e.encryption_method, e.index_new_sep)
    return bytes(w)

def _get_all_dirs_and_mp(pak_file):
    raw = bytes(pak_file._file_content[
        pak_file._pak_info.index_offset:][:pak_file._pak_info.index_size])
    if pak_file._pak_info.index_encrypted:
        raw = PakCrypto.decrypt_index(raw, pak_file._pak_info)
    r = Reader(raw)
    mp = r.string()
    num_files = r.u4()
    for _ in range(num_files):
        TencentPakEntry(r, pak_file._pak_info.version)
    dirs = {}
    for _ in range(r.u8()):
        dp = r.string()
        cnt = r.u8()
        dirs[dp] = {r.string(): pak_file._files[~r.i4()] for _ in range(cnt)}
    return mp, dirs

def _best_compress(chunk, cm, zstd_dict=None):
    if cm == CM_ZLIB:
        return zlib.compress(chunk, 9)
    if cm in (CM_ZSTD, CM_ZSTD_DICT):
        zd = zstd_dict if cm == CM_ZSTD_DICT else None
        for lvl in [22, 19, 16, 13, 10, 7, 4, 1]:
            try:
                return ZstdCompressor(level=lvl, dict_data=zd, threads=1).compress(chunk)
            except Exception:
                continue
    return chunk

def _encrypt_plaintext(plaintext: bytes, pak_relative_path: PurePath, encryption_method: int) -> bytes:
    if PakCrypto._is_simple1_method(encryption_method):
        return bytes((b ^ SIMPLE1_DECRYPT_KEY for b in plaintext))
    else:
        if PakCrypto._is_simple2_method(encryption_method):
            pad = -len(plaintext) % SIMPLE2_BLOCK_SIZE
            plaintext += b'\x00' * pad
            key, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
            rolling = key
            out = []
            for x, in struct.iter_unpack('<I', plaintext):
                c = rolling ^ x
                out.append(c)
                rolling ^= c
            return struct.pack(f'<{len(out)}I', *out)
        else:
            if PakCrypto._is_sm4_method(encryption_method):
                key = PakCrypto._derive_sm4_key(pak_relative_path, encryption_method)
                sm4 = PakCrypto._sm4_context_for_key(key)
                pad_len = -len(plaintext) % 16
                if pad_len > 0:
                    plaintext = plaintext + b'\x00' * pad_len
                out = bytearray()
                for i in range(0, len(plaintext), 16):
                    block = plaintext[i:i + 16]
                    if len(block) < 16:
                        block = block.ljust(16, b'\x00')
                    out.extend(sm4.encrypt(block))
                return bytes(out)
            else:
                return plaintext

def _repack_uncompressed(outfh, pak_file, entry, pak_relative_path: PurePath, new_data: bytes):
    enc_method = entry.encryption_method
    target_size = entry.size
    enc_region = PakCrypto.align_encrypted_content_size(target_size, enc_method) if entry.encrypted else target_size
    plaintext = new_data[:enc_region]
    if entry.encrypted:
        a = PakCrypto.align_encrypted_content_size(len(plaintext), enc_method)
        plaintext += b'\x00' * (a - len(plaintext))
        cipher = _encrypt_plaintext(plaintext, pak_relative_path, enc_method)
        outfh.seek(entry.offset)
        outfh.write(cipher)
        with open(pak_file._file_path, 'rb') as src:
            src.seek(entry.offset + len(cipher))
            outfh.write(src.read(enc_region - len(cipher)))
    else:
        outfh.seek(entry.offset)
        outfh.write(plaintext)
        with open(pak_file._file_path, 'rb') as src:
            src.seek(entry.offset + len(plaintext))
            outfh.write(src.read(target_size - len(plaintext)))

def _repack_compressed_with_display(outfh, pak_file, entry, pak_relative_path, new_data, repack_dir, display):
    blocks = entry.compressed_blocks
    enc_method = entry.encryption_method
    comp_method = entry.compression_method
    order = PakCrypto.generate_block_indices(len(blocks), enc_method)
    
    if len(new_data) != entry.uncompressed_size:
        if len(new_data) < entry.uncompressed_size:
            new_data = new_data.ljust(entry.uncompressed_size, b'\x00')
        else:
            new_data = new_data[:entry.uncompressed_size]

    if len(blocks) > 1:
        if entry.compression_block_size > 0:
            chunk_size = entry.compression_block_size
        else:
            block_sizes = [blk.end - blk.start for blk in blocks]
            total_block_size = sum(block_sizes)
            avg_block_size = total_block_size / len(blocks)
            avg_compression_ratio = total_block_size / entry.uncompressed_size if entry.uncompressed_size > 0 else 1
            chunk_size = int(avg_block_size / avg_compression_ratio) if avg_compression_ratio > 0 else 65536
        
        ptr = 0
        for logical_i, phys_i in enumerate(order):
            blk = blocks[phys_i]
            target_size = blk.end - blk.start
            chunk_len = min(chunk_size, len(new_data) - ptr)
            if chunk_len <= 0: break
            chunk = new_data[ptr:ptr + chunk_len]
            ptr += chunk_len
            
            with open(pak_file._file_path, 'rb') as src:
                src.seek(blk.start)
                original_compressed = src.read(target_size)
            
            compressed_ok = False
            new_compressed = None
            zstd_dict = pak_file._zstd_dict if comp_method == CM_ZSTD_DICT else None
            
            if comp_method in (CM_ZSTD, CM_ZSTD_DICT):
                for level in [22, 19, 16, 13, 10, 7, 4, 1]:
                    c = ZstdCompressor(level=level, dict_data=zstd_dict, threads=1)
                    new_compressed = c.compress(chunk)
                    if len(new_compressed) <= target_size:
                        compressed_ok = True
                        break
            elif comp_method == CM_ZLIB:
                new_compressed = zlib.compress(chunk, zlib.Z_BEST_COMPRESSION)
                if len(new_compressed) <= target_size:
                    compressed_ok = True
            
            if not compressed_ok:
                outfh.seek(blk.start)
                outfh.write(original_compressed)
                display.add_block(logical_i, target_size, False)
                continue
            
            if entry.encrypted:
                if PakCrypto._is_sm4_method(enc_method):
                    pad_len = -len(new_compressed) % 16
                    if pad_len > 0: new_compressed += b'\x00' * pad_len
                new_compressed = _encrypt_plaintext(new_compressed, pak_relative_path, enc_method)
            
            if len(new_compressed) > target_size:
                outfh.seek(blk.start)
                outfh.write(original_compressed)
                display.add_block(logical_i, target_size, False)
            else:
                outfh.seek(blk.start)
                outfh.write(new_compressed)
                if len(new_compressed) < target_size:
                    outfh.write(b'\x00' * (target_size - len(new_compressed)))
                ratio = len(new_compressed) / len(chunk) if len(chunk) > 0 else 1
                display.add_block(logical_i, target_size, True, ratio)
    else:
        if not blocks: return
        blk = blocks[0]
        target_size = blk.end - blk.start
        
        with open(pak_file._file_path, 'rb') as src:
            src.seek(blk.start)
            original_compressed = src.read(target_size)
        
        compressed_ok = False
        new_compressed = None
        zstd_dict = pak_file._zstd_dict if comp_method == CM_ZSTD_DICT else None
        
        if comp_method in (CM_ZSTD, CM_ZSTD_DICT):
            for level in [22, 19, 16, 13, 10, 7, 4, 1]:
                c = ZstdCompressor(level=level, dict_data=zstd_dict, threads=1)
                new_compressed = c.compress(new_data)
                if len(new_compressed) <= target_size:
                    compressed_ok = True
                    break
        elif comp_method == CM_ZLIB:
            new_compressed = zlib.compress(new_data, zlib.Z_BEST_COMPRESSION)
            if len(new_compressed) <= target_size:
                compressed_ok = True
        
        if not compressed_ok:
            outfh.seek(blk.start)
            outfh.write(original_compressed)
            display.add_block(0, target_size, False)
            return
        
        if entry.encrypted:
            if PakCrypto._is_sm4_method(enc_method):
                pad_len = -len(new_compressed) % 16
                if pad_len > 0: new_compressed += b'\x00' * pad_len
            new_compressed = _encrypt_plaintext(new_compressed, pak_relative_path, enc_method)
        
        if len(new_compressed) > target_size:
            outfh.seek(blk.start)
            outfh.write(original_compressed)
            display.add_block(0, target_size, False)
        else:
            outfh.seek(blk.start)
            outfh.write(new_compressed)
            if len(new_compressed) < target_size:
                outfh.write(b'\x00' * (target_size - len(new_compressed)))
            ratio = len(new_compressed) / len(new_data) if len(new_data) > 0 else 1
            display.add_block(0, target_size, True, ratio)

def smart_resolve_by_fingerprint(filename: str, repack_file: Path, candidates: list):
    repack_size = repack_file.stat().st_size
    size_matches = [(path, entry) for path, entry in candidates if entry.uncompressed_size == repack_size]
    if len(size_matches) == 1:
        return size_matches[0]
    if not size_matches:
        return None
    def fingerprint(e):
        return (e.uncompressed_size, e.size, e.compression_method, len(e.compressed_blocks), e.compression_block_size)
    base_fp = fingerprint(size_matches[0][1])
    final_matches = [(path, entry) for path, entry in size_matches if fingerprint(entry) == base_fp]
    if len(final_matches) == 1:
        return final_matches[0]
    return None

def repack_pak_file_full(pak_file, edited_root, output_path, target_path=None, force_add=False):
    import copy as _cp

    console.print(f'[bold cyan]📦 Full PAK Rebuild mode[/bold cyan]')
    if target_path:
        console.print(f'[bold cyan]🎯 Target path: {target_path}[/bold cyan]')
    
    edit_files = []
    for p in Path(edited_root).rglob('*'):
        if p.is_file():
            edit_files.append(p)
    
    if not edit_files:
        console.print('[bold red]❌ No files found in EDIT folder![/bold red]')
        return 0
    
    console.print(f'[bold cyan]📁 Found {len(edit_files)} files in EDIT folder[/bold cyan]')

    version = pak_file._pak_info.version
    keystream = PakCrypto.zuc_keystream()
    orig_fc = pak_file._file_content

    mp_str, all_dirs = _get_all_dirs_and_mp(pak_file)

    if target_path and force_add:
        target_path = target_path.replace('\\', '/')
        matched_dir = None
        for existing_dir in all_dirs.keys():
            if existing_dir.strip('/').lower() == target_path.strip('/').lower():
                matched_dir = existing_dir
                break
        if matched_dir:
            target_path = matched_dir
        else:
            target_path = target_path.strip('/') + '/'
    
    pak_name_map = {}
    for dir_path, files in pak_file._index.items():
        for name, entry in files.items():
            full_path = str(PurePath(dir_path)/name).replace('\\', '/')
            pak_name_map.setdefault(name.lower(), []).append((full_path, entry))

    edited = {}
    
    for p in edit_files:
        fl = p.name.lower()
        found_match = False
        
        if fl in pak_name_map:
            cands = pak_name_map[fl]
            if target_path:
                target_candidates = [(fp, e) for fp, e in cands if target_path.strip('/') in fp]
                if target_candidates:
                    sz = p.stat().st_size
                    sm = [(fp, e) for fp, e in target_candidates if e.uncompressed_size == sz]
                    fp, ent = sm[0] if sm else target_candidates[0]
                    edited[fp] = (p, ent)
                    found_match = True
            
            if not found_match:
                sz = p.stat().st_size
                sm = [(fp, e) for fp, e in cands if e.uncompressed_size == sz]
                fp, ent = sm[0] if sm else cands[0]
                if target_path:
                    new_fp = f"{target_path.rstrip('/')}/{p.name}"
                    edited[new_fp] = (p, ent)
                else:
                    edited[fp] = (p, ent)
                found_match = True
        
        if not found_match:
            stem = p.stem.lower()
            ext = p.suffix.lower()
            for dir_path, files in pak_file._index.items():
                for name, entry in files.items():
                    if Path(name).stem.lower() == stem and Path(name).suffix.lower() == ext:
                        full_path = str(PurePath(dir_path)/name).replace('\\', '/')
                        if target_path:
                            new_fp = f"{target_path.rstrip('/')}/{p.name}"
                            edited[new_fp] = (p, entry)
                        else:
                            edited[full_path] = (p, entry)
                        found_match = True
                        break
                if found_match:
                    break
        
        if not found_match and force_add and target_path:
            template_entry = None
            for dir_path, files in pak_file._index.items():
                for name, entry in files.items():
                    if Path(name).suffix.lower() == p.suffix.lower():
                        template_entry = entry
                        break
                if template_entry: break
            
            if not template_entry:
                for dir_path, files in pak_file._index.items():
                    for name, entry in files.items():
                        template_entry = entry
                        break
                    if template_entry: break
            
            if template_entry:
                new_fp = f"{target_path.rstrip('/')}/{p.name}"
                edited[new_fp] = (p, template_entry)

    if not edited:
        console.print('[bold red]❌ No files to repack![/bold red]')
        return 0

    console.print(f'  [bold bright_cyan]📁 Files to repack: {len(edited)}[/bold bright_cyan]')

    new_files = []
    for e in pak_file._files:
        ne = _cp.copy(e)
        ne.compressed_blocks = [_cp.copy(b) for b in e.compressed_blocks]
        new_files.append(ne)

    old_to_new = {id(pak_file._files[i]): new_files[i] for i in range(len(pak_file._files))}
    edited_paths = {fp: p for fp, (p, _) in edited.items()}

    out_buf = bytearray()

    for dp_str, dir_files in list(all_dirs.items()):
        for name, old_entry in list(dir_files.items()):
            full_path = str(PurePath(dp_str)/name).replace('\\', '/')
            ne = old_to_new.get(id(old_entry), None)
            
            if ne is None:
                ne = _cp.copy(old_entry)
                ne.compressed_blocks = [_cp.copy(b) for b in old_entry.compressed_blocks]
                new_files.append(ne)
                old_to_new[id(old_entry)] = ne

            em = old_entry.encryption_method
            cm = old_entry.compression_method

            if full_path in edited_paths:
                p, template = edited[full_path]
                new_raw = p.read_bytes()
                pak_rel = PurePath(full_path)

                ne.content_hash = SHA1.new(new_raw).digest()
                ne.uncompressed_size = len(new_raw)
                ne.compression_method = template.compression_method if template else cm
                ne.encryption_method = template.encryption_method if template else em
                ne.encrypted = template.encrypted if template else old_entry.encrypted
                ne.unk1 = template.unk1 if template else old_entry.unk1
                
                if template and target_path:
                    full_path_str = mp_str + full_path
                    ne.unk2 = SHA1.new(full_path_str.lower().encode('utf-8')).digest()
                else:
                    ne.unk2 = template.unk2 if template else old_entry.unk2
                    
                ne.index_new_sep = template.index_new_sep if template else old_entry.index_new_sep

                if ne.compression_method == CM_NONE:
                    cipher = (_encrypt_plaintext(new_raw, pak_rel, ne.encryption_method)
                              if ne.encrypted else new_raw)
                    ne.offset = len(out_buf)
                    ne.size = len(new_raw)
                    ne.uncompressed_size = len(new_raw)
                    out_buf += cipher
                else:
                    cs = (template.compression_block_size if template and template.compression_block_size > 0 
                          else old_entry.compression_block_size if old_entry.compression_block_size > 0 
                          else 65536)
                    chunks = [new_raw[i:i+cs] for i in range(0, len(new_raw), cs)]
                    new_blks = []
                    for chunk in chunks:
                        compressed = _best_compress(chunk, ne.compression_method, pak_file._zstd_dict)
                        cipher = (_encrypt_plaintext(compressed, pak_rel, ne.encryption_method)
                                  if ne.encrypted else compressed)
                        blk = PakCompressedBlock.__new__(PakCompressedBlock)
                        blk.start = len(out_buf)
                        blk.end = blk.start + len(cipher)
                        out_buf += cipher
                        new_blks.append(blk)

                    ne.compressed_blocks = new_blks
                    ne.offset = new_blks[0].start if new_blks else len(out_buf)
                    ne.size = sum(b.end - b.start for b in new_blks)
                    ne.uncompressed_size = len(new_raw)

                console.print(f'[green]✓ Processed: {full_path}[/green]')

            else:
                if cm == CM_NONE:
                    read_sz = (PakCrypto.align_encrypted_content_size(old_entry.size, em)
                               if old_entry.encrypted else old_entry.size)
                    ne.offset = len(out_buf)
                    out_buf += bytes(orig_fc[old_entry.offset: old_entry.offset + read_sz])

                elif old_entry.compressed_blocks:
                    new_blks = []
                    for ob in old_entry.compressed_blocks:
                        unc = ob.end - ob.start
                        enc = (PakCrypto.align_encrypted_content_size(unc, em)
                               if old_entry.encrypted else unc)
                        nb = PakCompressedBlock.__new__(PakCompressedBlock)
                        nb.start = len(out_buf)
                        nb.end = nb.start + unc
                        out_buf += bytes(orig_fc[ob.start: ob.start + enc])
                        new_blks.append(nb)
                    ne.compressed_blocks = new_blks
                    ne.offset = new_blks[0].start

    if target_path and force_add:
        for fp, (p, template) in edited.items():
            already_processed = False
            for dp_str, dir_files in all_dirs.items():
                for name, entry in dir_files.items():
                    if str(PurePath(dp_str)/name).replace('\\', '/') == fp:
                        already_processed = True
                        break
                if already_processed:
                    break
            
            if not already_processed:
                ne = _cp.copy(template)
                new_raw = p.read_bytes()
                pak_rel = PurePath(fp)
                
                ne.content_hash = SHA1.new(new_raw).digest()
                ne.uncompressed_size = len(new_raw)
                ne.compression_method = template.compression_method
                ne.encryption_method = template.encryption_method
                ne.encrypted = template.encrypted
                ne.unk1 = template.unk1
                
                full_path_str = mp_str + fp
                ne.unk2 = SHA1.new(full_path_str.lower().encode('utf-8')).digest()
                
                ne.index_new_sep = template.index_new_sep

                if ne.compression_method == CM_NONE:
                    cipher = (_encrypt_plaintext(new_raw, pak_rel, ne.encryption_method)
                              if ne.encrypted else new_raw)
                    ne.offset = len(out_buf)
                    ne.size = len(new_raw)
                    ne.uncompressed_size = len(new_raw)
                    out_buf += cipher
                else:
                    cs = template.compression_block_size if template.compression_block_size > 0 else 65536
                    chunks = [new_raw[i:i+cs] for i in range(0, len(new_raw), cs)]
                    new_blks = []
                    for chunk in chunks:
                        compressed = _best_compress(chunk, ne.compression_method, pak_file._zstd_dict)
                        cipher = (_encrypt_plaintext(compressed, pak_rel, ne.encryption_method)
                                  if ne.encrypted else compressed)
                        blk = PakCompressedBlock.__new__(PakCompressedBlock)
                        blk.start = len(out_buf)
                        blk.end = blk.start + len(cipher)
                        out_buf += cipher
                        new_blks.append(blk)

                    ne.compressed_blocks = new_blks
                    ne.offset = new_blks[0].start if new_blks else len(out_buf)
                    ne.size = sum(b.end - b.start for b in new_blks)
                    ne.uncompressed_size = len(new_raw)

                new_files.append(ne)
                
                if target_path not in all_dirs:
                    all_dirs[target_path] = {}
                all_dirs[target_path][p.name] = ne
                console.print(f'[green]✓ Added new: {fp}[/green]')

    eidx = {id(new_files[i]): i for i in range(len(new_files))}

    idx = bytearray(_pw_string(mp_str))
    idx += struct.pack('<I', len(new_files))
    for ne in new_files:
        idx += _pw_entry(ne, version)
    idx += struct.pack('<Q', len(all_dirs))
    for dp_str, dir_files in all_dirs.items():
        idx += _pw_string(dp_str)
        idx += struct.pack('<Q', len(dir_files))
        for name, old_e in dir_files.items():
            idx += _pw_string(name)
            found_idx = None
            for i, e in enumerate(new_files):
                if id(e) == id(old_e):
                    found_idx = i
                    break
            if found_idx is None:
                for i, e in enumerate(new_files):
                    if e.offset == old_e.offset and e.size == old_e.size:
                        found_idx = i
                        break
            if found_idx is not None:
                idx += struct.pack('<i', ~found_idx)
            else:
                idx += struct.pack('<i', -1)

    index_plain = bytes(idx)
    new_sha1 = SHA1.new(index_plain).digest()

    if pak_file._pak_info.index_encrypted:
        key = PakCrypto.rsa_extract(pak_file._pak_info.packed_key, RSA_MOD_1)
        iv = PakCrypto.rsa_extract(pak_file._pak_info.packed_iv, RSA_MOD_1)
        aes = AES.new(key, MODE_CBC, iv[:16])
        pad = (-len(index_plain)) % AES.block_size or AES.block_size
        index_bytes = aes.encrypt(index_plain + bytes([pad] * pad))
    else:
        index_bytes = index_plain

    new_idx_offset = len(out_buf)
    new_idx_size = len(index_bytes)
    out_buf += index_bytes

    footer_sz = TencentPakInfo._mem_size(version)
    new_footer = bytearray(orig_fc[-footer_sz:])

    h_key = struct.pack('<5I', *keystream[4:9])
    new_footer[-36:-16] = bytes(a ^ b for a, b in zip(new_sha1, h_key))
    new_footer[-16:-8] = ((new_idx_size ^ (keystream[10] << 32 | keystream[11])).to_bytes(8, 'little'))
    new_footer[-8:] = ((new_idx_offset ^ (keystream[0] << 32 | keystream[1])).to_bytes(8, 'little'))

    out_buf += new_footer

    with open(output_path, 'wb') as f:
        f.write(out_buf)

    return len(edited)

def repack_pak_file_with_block_display(pak_file, edited_root: Path, output_path: Path):
    shutil.copy2(pak_file._file_path, output_path)
    
    pak_name_map = {}
    for dir_path, files in pak_file._index.items():
        for name, entry in files.items():
            full_path = str(PurePath(dir_path) / name).replace('\\', '/')
            key = name.lower()
            pak_name_map.setdefault(key, []).append((full_path, entry))
    
    edited = {}
    for p in edited_root.rglob('*'):
        if not p.is_file():
            continue
        fname_lower = p.name.lower()
        if fname_lower in pak_name_map:
            candidates = pak_name_map[fname_lower]
            if len(candidates) == 1:
                full_path, entry = candidates[0]
                edited[full_path] = (p, entry)
            else:
                resolved = smart_resolve_by_fingerprint(filename=p.name, repack_file=p, candidates=candidates)
                if resolved:
                    full_path, entry = resolved
                    edited[full_path] = (p, entry)
        else:
            stem = p.stem.lower()
            ext = p.suffix.lower()
            for dir_path, files in pak_file._index.items():
                for name, entry in files.items():
                    if Path(name).stem.lower() == stem and Path(name).suffix.lower() == ext:
                        full_path = str(PurePath(dir_path) / name).replace('\\', '/')
                        edited[full_path] = (p, entry)
                        break
    
    if not edited:
        console.print('[bold #FF0055]❌ No files to repack![/bold #FF0055]')
        return
    
    total_files = len(edited)
    display = SimpleBlockDisplay(total_files, pak_file._file_path.name)
    
    with open(output_path, 'r+b') as outfh:
        for full_path, (p, entry) in edited.items():
            file_name = p.name
            total_blocks = len(entry.compressed_blocks) if entry.compressed_blocks else 1
            
            display.start_file(file_name, total_blocks)
            new_data = p.read_bytes()
            pak_rel = PurePath(full_path)
            
            if entry.compression_method == CM_NONE:
                _repack_uncompressed(outfh, pak_file, entry, pak_rel, new_data)
                display.add_block(0, len(new_data), True)
            else:
                _repack_compressed_with_display(outfh, pak_file, entry, pak_rel, new_data, edited_root, display)
            
            display.finish_file()
    
    display.final_summary()

def detect_repack_mode(pak_path: Path) -> str:
    name = pak_path.name.lower()
    if name == 'mini_obb.pak':
        return 'MINI_OBB'
    if 'zsdic' in name:
        return 'OBBZSDIC'
    if 'game' in name or 'patch' in name:
        return 'GAMEPATCH'
    return 'OBBZSDIC'

def repack_mini_obb(pak, repack_dir, output_pak):
    console.print('[bold #00FFFF]🧩 Repack Mode: MINI_OBB[/bold #00FFFF]')
    pak._is_zstd_with_dict = False
    pak._zstd_dict = None
    repack_pak_file_with_block_display(pak_file=pak, edited_root=repack_dir, output_path=output_pak)

def repack_obbzsdic(pak, repack_dir, output_pak):
    console.print('[bold #00FFFF]🧩 Repack Mode: OBBZSDIC[/bold #00FFFF]')
    repack_pak_file_with_block_display(pak_file=pak, edited_root=repack_dir, output_path=output_pak)

def repack_gamepatch(pak, repack_dir, output_pak):
    console.print('[bold #00FFFF]🧩 Repack Mode: GAMEPATCH[/bold #00FFFF]')
    pak._is_zstd_with_dict = False
    pak._zstd_dict = None
    repack_pak_file_with_block_display(pak_file=pak, edited_root=repack_dir, output_path=output_pak)

# ============================================================
# PAK TYPE MENU FUNCTIONS
# ============================================================

def select_pak_file(folder_type: str, title: str) -> Path | None:
    input_dir = BASE_DIR / folder_type / 'INPUT'
    if not input_dir.exists():
        console.print(f'[red]❌ Folder not found: {input_dir}[/red]')
        return None
    pak_files = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() == '.pak']
    if not pak_files:
        console.print(f'[red]❌ No .pak files found in {input_dir}[/red]')
        return None
    table = Table(title=title, box=rich_box.SIMPLE, style='cyan')
    table.add_column('No.', style='cyan', justify='center')
    table.add_column('File Name', style='white')
    table.add_column('Size', style='yellow')
    for i, pak_file in enumerate(pak_files, 1):
        size = pak_file.stat().st_size
        size_str = f'{size / 1048576:.1f} MB' if size > 1048576 else f'{size / 1024:.1f} KB'
        table.add_row(str(i), pak_file.name, size_str)
    table.add_row(str(len(pak_files) + 1), 'Back to Menu', '')
    console.print(table)
    try:
        choice = int(Prompt.ask(f'[white]Select file (1-{len(pak_files) + 1})[/white]'))
        if choice == len(pak_files) + 1:
            return None
        if 1 <= choice <= len(pak_files):
            return pak_files[choice - 1]
        console.print('[red]❌ Invalid selection[/red]')
        return None
    except ValueError:
        console.print('[red]❌ Invalid input[/red]')
        return None

def handle_unpack(folder_type: str):
    pak_file = select_pak_file(folder_type, f'Unpack {folder_type}')
    if not pak_file:
        return
    
    console.print(Panel('[cyan]Select Unpack Mode[/cyan]', title='Unpack Mode', border_style='cyan'))
    table = Table(box=rich_box.SIMPLE)
    table.add_column('Option', justify='center')
    table.add_column('Mode')
    table.add_column('Description')
    table.add_row('1', '📁 Full Unpack', 'All files with folder structure')
    table.add_row('2', '📄 Only Files', 'Sirf files without folders')
    console.print(table)
    try:
        unpack_mode = Prompt.ask('[white]Select unpack mode (1-2)[/white]').strip()
    except KeyboardInterrupt:
        return
    if unpack_mode not in ['1', '2']:
        console.print('[red]❌ Invalid option[/red]')
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    
    output_folder = BASE_DIR / folder_type / 'UNPACKED' / pak_file.stem
    
    if unpack_mode == '1':
        console.print(f'[blue]📁 Full Unpacking: {pak_file.name}[/blue]')
        try:
            is_od_pack = folder_type == 'OD_PAK'
            pak = TencentPakFile(pak_file, is_od=is_od_pack)
            pak.dump(output_folder)
            log_path = output_folder / f'Debug_{pak_file.stem}.log'
            dump_unpacking_log(pak, log_path)
            console.print(Panel(f'[green]✅ Full Unpack complete![/green]\n[cyan]📁 Files extracted to: {output_folder}[/cyan]', title='Success', border_style='green'))
        except Exception as e:
            console.print(Panel(f'[red]❌ Unpack failed: {e}[/red]', title='Error', border_style='red'))
            traceback.print_exc()
    else:
        console.print(f'[blue]📄 Only Files Unpacking: {pak_file.name}[/blue]')
        try:
            is_od_pack = folder_type == 'OD_PAK'
            pak = TencentPakFile(pak_file, is_od=is_od_pack)
            temp_folder = output_folder / 'temp'
            pak.dump(temp_folder)
            console.print('[cyan]🔄 Moving files to single folder...[/cyan]')
            all_files = []
            for root, dirs, files in os.walk(temp_folder):
                for file in files:
                    all_files.append(Path(root) / file)
            moved_count = 0
            for file_path in all_files:
                try:
                    new_path = output_folder / file_path.name
                    counter = 1
                    while new_path.exists():
                        new_path = output_folder / f'{file_path.stem}_{counter}{file_path.suffix}'
                        counter += 1
                    shutil.move(str(file_path), str(new_path))
                    moved_count += 1
                except Exception as e:
                    console.print(f'[yellow]⚠ Could not move {file_path.name}: {e}[/yellow]')
            shutil.rmtree(temp_folder)
            console.print(Panel(f'[green]✅ Only Files Unpack complete![/green]\n[cyan]📄 Files successfully moved: {moved_count}[/cyan]\n[cyan]📁 All files in: {output_folder}[/cyan]', title='Success', border_style='green'))
        except Exception as e:
            console.print(Panel(f'[red]❌ Unpack failed: {e}[/red]', title='Error', border_style='red'))
            traceback.print_exc()
    Prompt.ask('[white]Press Enter to continue...[/white]', default='')

def handle_repack(folder_type: str):
    pak_file = select_pak_file(folder_type, f'Repack {folder_type}')
    if not pak_file:
        return
    
    console.print(Panel('[cyan]Select Repack Mode[/cyan]', title='Repack Mode', border_style='cyan'))
    table = Table(box=rich_box.SIMPLE)
    table.add_column('Option', justify='center')
    table.add_column('Mode')
    table.add_column('Description')
    table.add_row('1', '🔁 Normal Repack', 'Existing files only')
    table.add_row('2', '🧩 Chunk Repack', 'Block-wise repack')
    table.add_row('3', '💛 Full Rebuild', 'ANY SIZE - Recommended')
    table.add_row('4', '📁 Repack to PATH', 'Add files to specific path')
    console.print(table)
    
    choice = Prompt.ask('[bold yellow]Select option[/bold yellow] ', default='1')
    
    edited_folder = BASE_DIR / folder_type / 'EDITED'
    if not edited_folder.exists() or not any(edited_folder.rglob('*')):
        console.print(f'[red]❌ No files found in EDITED folder: {edited_folder}[/red]')
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    
    output_pak = BASE_DIR / folder_type / 'REPACKED' / f'{pak_file.stem}.pak'
    output_pak.parent.mkdir(exist_ok=True)
    
    try:
        pak = TencentPakFile(pak_file)
        
        if choice == '1':
            console.print('[bold #00FFFF]🔁 Normal Repack[/bold #00FFFF]')
            mode = detect_repack_mode(pak_file)
            if mode == 'MINI_OBB':
                repack_mini_obb(pak, edited_folder, output_pak)
            elif mode == 'GAMEPATCH':
                repack_gamepatch(pak, edited_folder, output_pak)
            else:
                repack_obbzsdic(pak, edited_folder, output_pak)
                
        elif choice == '2':
            console.print('[bold #00FFFF]🧩 Chunk Repack[/bold #00FFFF]')
            repack_pak_file_with_block_display(pak, edited_folder, output_pak)
            
        elif choice == '3':
            console.print('[bold #00FFFF]💛 Full Rebuild (ANY SIZE)[/bold #00FFFF]')
            count = repack_pak_file_full(pak, edited_folder, output_pak)
            if count > 0:
                console.print(f'[bold #00FF88]✅ Repacked {count} files successfully![/bold #00FF88]')
            else:
                console.print('[bold #FF0055]❌ No files repacked![/bold #FF0055]')
                
        elif choice == '4':
            console.print('[bold #00FFFF]📁 Repack to PATH[/bold #00FFFF]')
            console.print('[bold #FFFF00]📁 Enter the target path inside the PAK:[/bold #FFFF00]')
            console.print('[dim]Example: Content/Lua/GameLua/Mod/BRMod/Gameplay/Core[/dim]')
            target_path = Prompt.ask('[bold #00FFFF]Path: [/bold #00FFFF]').strip()
            if not target_path:
                console.print('[bold #FF0055]❌ No path provided![/bold #FF0055]')
                return
            target_path = target_path.replace('\\', '/').strip('/')
            if not target_path:
                console.print('[bold #FF0055]❌ Invalid target path![/bold #FF0055]')
                return
            count = repack_pak_file_full(pak, edited_folder, output_pak, target_path, force_add=True)
            if count > 0:
                console.print(f'[bold #00FF88]✅ Added {count} files to {target_path}![/bold #00FF88]')
            else:
                console.print('[bold #FF0055]❌ No files added![/bold #FF0055]')
        
        console.print(Panel(f'[green]✅ Repack complete![/green]\n[cyan]📁 Output: {output_pak}[/cyan]', title='Success', border_style='green'))
        
    except Exception as e:
        console.print(Panel(f'[red]❌ Repack failed: {e}[/red]', title='Error', border_style='red'))
        traceback.print_exc()
    
    Prompt.ask('[white]Press Enter to continue...[/white]', default='')

def repack_menu(folder_type: str):
    handle_repack(folder_type)

def show_type_menu(folder_type: str):
    while True:
        clear_screen()
        show_banner(_auth_data)
        console.print(Panel(f"""
[bold cyan]{folder_type} TOOL[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] UNPACK                 → Extract all files
[bold green][2][/bold green] REPACK                 → Build PAK (4 modes)
[bold green][3][/bold green] COMPARE & DUMP PAK     → Fast diff extract
[bold green][4][/bold green] SEARCH TEXT            → Find string in files
[bold green][5][/bold green] SEARCH FILE BY NAME    → Locate asset
[bold green][6][/bold green] CLEAR UNPACKED DATA    → Delete extracted files
[bold green][7][/bold green] UNPACK SINGLE BLOCK    → Extract by filename
[bold green][8][/bold green] CREATE FOLDER STRUCTURE→ For specific file
[bold red][0][/bold red] Back to Main Menu
""", border_style='cyan', padding=(1, 3)))
        choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '3', '4', '5', '6', '7', '8', '0'], default='0')
        
        if choice == '1':
            handle_unpack(folder_type)
        elif choice == '2':
            repack_menu(folder_type)
        elif choice == '3':
            fast_compare_and_extract_with_choice(folder_type)
        elif choice == '4':
            search_text_in_files(folder_type)
        elif choice == '5':
            search_files_by_name(folder_type)
        elif choice == '6':
            handle_clear_data(folder_type)
        elif choice == '7':
            unpack_file_blocks_using_filename(folder_type)
        elif choice == '8':
            create_folder_structure_with_filename(folder_type)
        elif choice == '0':
            break

# ============================================================
# SEARCH AND COMPARE FEATURES - COMPLETE
# ============================================================

def search_text_in_files(folder_type: str):
    unpacked_dir = BASE_DIR / folder_type / 'UNPACKED'
    if not unpacked_dir.exists() or not any(unpacked_dir.iterdir()):
        console.print(Panel(f'[red]❌ No unpacked data found for {folder_type}![/red]', title='Error', border_style='red'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    folders = [d for d in unpacked_dir.iterdir() if d.is_dir()]
    if not folders:
        console.print(Panel(f'[red]❌ No unpacked folders found for {folder_type}![/red]', title='Error', border_style='red'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    table = Table(title=f'Select Unpacked Folder - {folder_type}', box=rich_box.SIMPLE, style='cyan')
    table.add_column('No.', style='cyan', justify='center')
    table.add_column('Folder Name', style='white')
    table.add_column('Files Count', style='yellow')
    for i, folder in enumerate(folders, 1):
        file_count = len(list(folder.rglob('*'))) if folder.exists() else 0
        table.add_row(str(i), folder.name, str(file_count))
    console.print(table)
    try:
        choice = int(Prompt.ask(f'[white]Select folder to search in (1-{len(folders)})[/white]'))
        if not 1 <= choice <= len(folders):
            console.print('[red]❌ Invalid selection[/red]')
            return
        selected_folder = folders[choice - 1]
        search_text = Prompt.ask('[white]Enter text to search[/white]').strip()
        if not search_text:
            console.print('[red]❌ Search text cannot be empty[/red]')
            return
        console.print(Panel(f'[blue]🔍 Searching for: \'{search_text}\' in {selected_folder.name}[/blue]', border_style='blue'))
        search_results_dir = BASE_DIR / folder_type / 'SEARCH_RESULTS' / f'text_search_{search_text[:20]}'
        search_results_dir.mkdir(parents=True, exist_ok=True)
        found_files = []
        file_list = list(selected_folder.rglob('*'))
        file_list = [f for f in file_list if f.is_file()]
        total_files = len(file_list)
        with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TextColumn('[progress.percentage]{task.percentage:>3.0f}%'), TimeElapsedColumn(), console=console) as progress:
            task_id = progress.add_task('[cyan]Searching files...', total=total_files)
            for file_path in file_list:
                progress.update(task_id, description=f'[cyan]Searching: {file_path.name[:30]}...')
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_text.lower() in content.lower():
                            found_files.append(file_path)
                            relative_path = file_path.relative_to(selected_folder)
                            dest_path = search_results_dir / relative_path
                            dest_path.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(file_path, dest_path)
                except:
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            if search_text.encode('utf-8', errors='ignore') in content:
                                found_files.append(file_path)
                                relative_path = file_path.relative_to(selected_folder)
                                dest_path = search_results_dir / relative_path
                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                shutil.copy2(file_path, dest_path)
                    except:
                        pass
                progress.update(task_id, advance=1)
        console.print(Panel(f'[green]✅ Search complete![/green]\n[cyan]📁 Searched in: {selected_folder.name}[/cyan]\n[cyan]🔍 Search text: \'{search_text}\'[/cyan]\n[cyan]📄 Files searched: {total_files}[/cyan]\n[cyan]✅ Files found: {len(found_files)}[/cyan]\n[cyan]📂 Results saved to: {search_results_dir}[/cyan]', title='Search Results', border_style='green'))
        if found_files:
            table = Table(title='Found Files', box=rich_box.SIMPLE, style='green')
            table.add_column('No.', style='green', justify='center')
            table.add_column('File Name', style='white')
            table.add_column('Path', style='yellow')
            for i, file_path in enumerate(found_files[:20], 1):
                relative_path = file_path.relative_to(selected_folder)
                table.add_row(str(i), file_path.name, str(relative_path))
            if len(found_files) > 20:
                table.add_row('...', f'... and {len(found_files) - 20} more files', '...')
            console.print(table)
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
    except ValueError:
        console.print('[red]❌ Invalid input[/red]')

def search_files_by_name(folder_type: str):
    unpacked_dir = BASE_DIR / folder_type / 'UNPACKED'
    if not unpacked_dir.exists() or not any(unpacked_dir.iterdir()):
        console.print(Panel(f'[red]❌ No unpacked data found for {folder_type}![/red]', title='Error', border_style='red'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    folders = [d for d in unpacked_dir.iterdir() if d.is_dir()]
    if not folders:
        console.print(Panel(f'[red]❌ No unpacked folders found for {folder_type}![/red]', title='Error', border_style='red'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    table = Table(title=f'Select Unpacked Folder - {folder_type}', box=rich_box.SIMPLE, style='cyan')
    table.add_column('No.', style='cyan', justify='center')
    table.add_column('Folder Name', style='white')
    table.add_column('Files Count', style='yellow')
    for i, folder in enumerate(folders, 1):
        file_count = len(list(folder.rglob('*'))) if folder.exists() else 0
        table.add_row(str(i), folder.name, str(file_count))
    console.print(table)
    try:
        choice = int(Prompt.ask(f'[white]Select folder to search in (1-{len(folders)})[/white]'))
        if not 1 <= choice <= len(folders):
            console.print('[red]❌ Invalid selection[/red]')
            return
        selected_folder = folders[choice - 1]
        search_filename = Prompt.ask('[white]Enter filename to search (supports * wildcards)[/white]').strip()
        if not search_filename:
            console.print('[red]❌ Filename cannot be empty[/red]')
            return
        console.print(Panel(f'[blue]🔍 Searching for: \'{search_filename}\' in {selected_folder.name}[/blue]', border_style='blue'))
        search_results_dir = BASE_DIR / folder_type / 'SEARCH_RESULTS' / f'name_search_{search_filename[:20].replace("*", "wildcard")}'
        search_results_dir.mkdir(parents=True, exist_ok=True)
        found_files = []
        pattern = search_filename.replace('*', '.*')
        regex = re.compile(pattern, re.IGNORECASE)
        file_list = list(selected_folder.rglob('*'))
        file_list = [f for f in file_list if f.is_file()]
        total_files = len(file_list)
        with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TextColumn('[progress.percentage]{task.percentage:>3.0f}%'), TimeElapsedColumn(), console=console) as progress:
            task_id = progress.add_task('[cyan]Searching files...', total=total_files)
            for file_path in file_list:
                progress.update(task_id, description=f'[cyan]Searching: {file_path.name[:30]}...')
                if regex.search(file_path.name):
                    found_files.append(file_path)
                    relative_path = file_path.relative_to(selected_folder)
                    dest_path = search_results_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_path)
                progress.update(task_id, advance=1)
        console.print(Panel(f'[green]✅ Search complete![/green]\n[cyan]📁 Searched in: {selected_folder.name}[/cyan]\n[cyan]🔍 Search pattern: \'{search_filename}\'[/cyan]\n[cyan]📄 Files searched: {total_files}[/cyan]\n[cyan]✅ Files found: {len(found_files)}[/cyan]\n[cyan]📂 Results saved to: {search_results_dir}[/cyan]', title='Search Results', border_style='green'))
        if found_files:
            table = Table(title='Found Files', box=rich_box.SIMPLE, style='green')
            table.add_column('No.', style='green', justify='center')
            table.add_column('File Name', style='white')
            table.add_column('Path', style='yellow')
            table.add_column('Size', style='cyan')
            for i, file_path in enumerate(found_files[:20], 1):
                relative_path = file_path.relative_to(selected_folder)
                size = file_path.stat().st_size
                size_str = f'{size / 1024:.1f} KB' if size < 1048576 else f'{size / 1048576:.1f} MB'
                table.add_row(str(i), file_path.name, str(relative_path), size_str)
            if len(found_files) > 20:
                table.add_row('...', f'... and {len(found_files) - 20} more files', '...', '...')
            console.print(table)
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
    except ValueError:
        console.print('[red]❌ Invalid input[/red]')

def handle_clear_data(folder_type: str):
    unpacked_dir = BASE_DIR / folder_type / 'UNPACKED'
    if not unpacked_dir.exists() or not any(unpacked_dir.iterdir()):
        console.print(Panel(f'[yellow]⚠ No unpacked data found for {folder_type}[/yellow]', title='Info', border_style='yellow'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    folders = [d for d in unpacked_dir.iterdir() if d.is_dir()]
    if not folders:
        console.print(Panel(f'[yellow]⚠ No unpacked folders found for {folder_type}[/yellow]', title='Info', border_style='yellow'))
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
        return
    table = Table(title=f'Unpacked Data - {folder_type}', box=rich_box.SIMPLE, style='cyan')
    table.add_column('No.', style='cyan', justify='center')
    table.add_column('Folder Name', style='white')
    for i, folder in enumerate(folders, 1):
        table.add_row(str(i), folder.name)
    table.add_row(str(len(folders) + 1), 'Delete All')
    table.add_row(str(len(folders) + 2), 'Back to Menu')
    console.print(table)
    try:
        choice = int(Prompt.ask(f'[white]Select option (1-{len(folders) + 2})[/white]'))
        if choice == len(folders) + 2:
            return
        if choice == len(folders) + 1:
            confirm = Prompt.ask(f'[red]Delete ALL unpacked data for {folder_type}? (y/n)[/red]', choices=['y', 'n']).lower()
            if confirm == 'y':
                for folder in folders:
                    try:
                        shutil.rmtree(folder)
                        console.print(f'[green]✅ Deleted: {folder.name}[/green]')
                    except Exception as e:
                        console.print(f'[red]❌ Failed to delete {folder.name}: {e}[/red]')
        if 1 <= choice <= len(folders):
            folder = folders[choice - 1]
            confirm = Prompt.ask(f'[red]Delete {folder.name}? (y/n)[/red]', choices=['y', 'n']).lower()
            if confirm == 'y':
                try:
                    shutil.rmtree(folder)
                    console.print(f'[green]✅ Deleted: {folder.name}[/green]')
                except Exception as e:
                    console.print(f'[red]❌ Failed to delete {folder.name}: {e}[/red]')
        Prompt.ask('[white]Press Enter to continue...[/white]', default='')
    except ValueError:
        console.print('[red]❌ Invalid input[/red]')

def quick_block_fingerprint(pak_path: Path, entry):
    h = hashlib.md5()
    with open(pak_path, 'rb') as f:
        for real_idx in range(len(entry.compressed_blocks)):
            block = entry.compressed_blocks[real_idx]
            f.seek(block.start)
            data = f.read(min(1024, block.end - block.start))
            h.update(data)
    return h.digest()

def fast_compare_and_extract_with_choice(folder_type: str):
    console.print(Panel('[bold cyan]⚡ FAST PAK COMPARE & SMART EXTRACT[/bold cyan]\nMetadata + Fingerprint • Fully Decrypted Output', border_style='cyan'))
    compare_dir = BASE_DIR / folder_type / 'COMPARE_DAT'
    original_dir = compare_dir / 'Original_PAK'
    modded_dir = compare_dir / 'Modded_PAK'
    output_dir = compare_dir / 'Modified_Files'
    for d in [original_dir, modded_dir, output_dir]:
        d.mkdir(parents=True, exist_ok=True)
    original_paks = sorted(original_dir.glob('*.pak'))
    modded_paks = sorted(modded_dir.glob('*.pak'))
    if not original_paks or not modded_paks:
        console.print('[red]❌ Original / Modded PAK missing[/red]\n[cyan]Place original in COMPARE_DAT/Original_PAK/\nPlace modded in COMPARE_DAT/Modded_PAK/[/cyan]')
        Prompt.ask('Press Enter...', default='')
        return
    def choose_pak(paks, title):
        console.print(Panel(f'[cyan]{title}[/cyan]', border_style='cyan'))
        for i, p in enumerate(paks, 1):
            console.print(f'  [yellow]{i}[/yellow] ➜ {p.name}')
        try:
            return paks[int(Prompt.ask('Select number')) - 1]
        except:
            return None
    orig_pak = choose_pak(original_paks, 'Select ORIGINAL PAK')
    if not orig_pak:
        return
    mod_pak = choose_pak(modded_paks, 'Select MODDED PAK')
    if not mod_pak:
        return
    console.print(Panel('[cyan]Extraction Mode[/cyan]\n  [green]1️⃣  Full File Unpack (Decrypted)[/green]\n  [cyan]2️⃣  Chunk Unpack (Block-wise)[/cyan]', border_style='cyan'))
    mode = Prompt.ask('Choose mode', choices=['1', '2'], default='1')
    orig = TencentPakFile(orig_pak)
    mod = TencentPakFile(mod_pak)
    modified = []
    console.print('\n[yellow]⚡ Comparing files (fast + safe)...[/yellow]')
    for dir_path, orig_files in orig._index.items():
        mod_files = mod._index.get(dir_path)
        if not mod_files:
            continue
        for name, o_entry in orig_files.items():
            m_entry = mod_files.get(name)
            if not m_entry:
                continue
            same = (o_entry.uncompressed_size == m_entry.uncompressed_size and 
                    len(o_entry.compressed_blocks) == len(m_entry.compressed_blocks))
            if same:
                for ob, mb in zip(o_entry.compressed_blocks, m_entry.compressed_blocks):
                    if ob.end - ob.start != mb.end - mb.start:
                        same = False
                        break
            if same:
                if quick_block_fingerprint(orig_pak, o_entry) != quick_block_fingerprint(mod_pak, m_entry):
                    same = False
            if not same:
                modified.append((dir_path, name, m_entry))
    if not modified:
        console.print('[green]✅ No modified files found[/green]')
        Prompt.ask('Press Enter...', default='')
        return
    console.print(Panel(f'[bold green]✅ Modified Files Found:[/] {len(modified)}\n[cyan]Starting extraction...[/cyan]', border_style='green'))
    for dir_path, name, entry in modified:
        indices = PakCrypto.generate_block_indices(len(entry.compressed_blocks), entry.encryption_method)
        if mode == '1':
            full_data = b''
            with open(mod_pak, 'rb') as f:
                for real_idx in indices:
                    block = entry.compressed_blocks[real_idx]
                    f.seek(block.start)
                    raw_size = block.end - block.start
                    if entry.encrypted:
                        read_size = PakCrypto.align_encrypted_content_size(raw_size, entry.encryption_method)
                    else:
                        read_size = raw_size
                    raw = f.read(read_size)
                    if entry.encrypted:
                        raw = PakCrypto.decrypt_block(raw, Path(name), entry.encryption_method)
                    if entry.compression_method != CM_NONE:
                        try:
                            raw = PakCompression.decompress_block(raw, mod._zstd_dict, entry.compression_method)
                        except Exception:
                            pass
                    full_data += raw
            out_path = output_dir / dir_path / name
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(full_data)
            console.print(f'[green]✔ Extracted:[/] {name}')
        else:
            base = Path(name).stem
            ext = Path(name).suffix
            chunk_dir = output_dir / 'SINGLE_UNPACK' / base
            chunk_dir.mkdir(parents=True, exist_ok=True)
            with open(mod_pak, 'rb') as f:
                for i, real_idx in enumerate(indices):
                    block = entry.compressed_blocks[real_idx]
                    f.seek(block.start)
                    raw_size = block.end - block.start
                    if entry.encrypted:
                        read_size = PakCrypto.align_encrypted_content_size(raw_size, entry.encryption_method)
                    else:
                        read_size = raw_size
                    data = f.read(read_size)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, Path(name), entry.encryption_method)
                    if entry.compression_method != CM_NONE:
                        data = PakCompression.decompress_block(data, mod._zstd_dict, entry.compression_method)
                    (chunk_dir / f'{base}_{i}{ext}').write_bytes(data)
            console.print(f'[cyan]✔ Chunk Extracted:[/] {name}')
    console.print(Panel(f'[bold green]🎉 EXTRACTION COMPLETE[/bold green]\n[cyan]Files Extracted:[/] {len(modified)}', border_style='green'))
    Prompt.ask('[white]Press Enter to continue...[/white]', default='')

def unpack_file_blocks_using_filename(folder_type: str):
    console.print(f'[cyan]📦 Unpack File Using File Name[/cyan]\n[white]Module:[/] {folder_type}')
    pak_file = select_pak_file(folder_type, f'Select PAK File')
    if not pak_file:
        return
    pak_instance = TencentPakFile(pak_file)
    target_filename = Prompt.ask('Enter exact file name (with extension)').strip()
    if not target_filename:
        console.print('[red]❌ No filename entered[/red]')
        return
    console.print('\n[cyan]Extraction Mode[/cyan]')
    console.print('  1️⃣ Non Chunk Extract')
    console.print('  2️⃣ Chunk Extract')
    mode = Prompt.ask('Choose mode', choices=['1', '2'], default='2')
    output_root = BASE_DIR / folder_type / 'SINGLE_UNPACK'
    found = False
    for dir_path, files in pak_instance._index.items():
        entry = files.get(target_filename)
        if not entry:
            continue
        found = True
        file_base = Path(target_filename).stem
        file_ext = Path(target_filename).suffix
        indices = PakCrypto.generate_block_indices(len(entry.compressed_blocks), entry.encryption_method)
        if mode == '1':
            out_path = output_root / Path(target_filename) / dir_path / target_filename
            out_path.parent.mkdir(parents=True, exist_ok=True)
            full_data = bytearray()
            with open(pak_file, 'rb') as f_pak:
                for real_idx in indices:
                    block = entry.compressed_blocks[real_idx]
                    f_pak.seek(block.start)
                    raw_size = block.end - block.start
                    if entry.encrypted:
                        read_size = PakCrypto.align_encrypted_content_size(raw_size, entry.encryption_method)
                    else:
                        read_size = raw_size
                    data = f_pak.read(read_size)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, Path(target_filename), entry.encryption_method)
                    if entry.compression_method != CM_NONE:
                        data = PakCompression.decompress_block(data, pak_instance._zstd_dict, entry.compression_method)
                    full_data.extend(data)
            out_path.write_bytes(full_data)
            console.print(f'[bold green]✅ File Extracted:[/] {out_path}')
        else:
            out_dir = output_root / file_base
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(pak_file, 'rb') as f_pak:
                for i, real_idx in enumerate(indices):
                    block = entry.compressed_blocks[real_idx]
                    f_pak.seek(block.start)
                    raw_size = block.end - block.start
                    if entry.encrypted:
                        read_size = PakCrypto.align_encrypted_content_size(raw_size, entry.encryption_method)
                    else:
                        read_size = raw_size
                    data = f_pak.read(read_size)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, Path(target_filename), entry.encryption_method)
                    if entry.compression_method != CM_NONE:
                        data = PakCompression.decompress_block(data, pak_instance._zstd_dict, entry.compression_method)
                    out_file = out_dir / f'{file_base}_{i}{file_ext}'
                    out_file.write_bytes(data)
                    console.print(f'[green]✔ Extracted[/green] {out_file.name}')
            console.print(f'[bold green]✅ Total Blocks Extracted:[/] {len(indices)}\n[cyan]📁 Output:[/] {out_dir}')
        break
    if not found:
        console.print(f'[red]❌ File not found in PAK:[/] {target_filename}')
    Prompt.ask('[yellow]Press Enter to continue...[/yellow]', default='')

def create_folder_structure_with_filename(folder_type: str):
    base_dir = BASE_DIR / folder_type
    unpacked_root = base_dir / 'UNPACKED'
    edited_root = base_dir / 'EDITED'
    filename = Prompt.ask('[yellow]Enter exact file name (with extension)[/yellow]').strip()
    if not filename:
        console.print('[red]❌ No filename entered[/red]')
        return
    found = False
    for pak_folder in unpacked_root.iterdir():
        if pak_folder.is_dir():
            for file_path in pak_folder.rglob(filename):
                found = True
                relative_path = file_path.relative_to(pak_folder)
                target_path = edited_root / relative_path.parent
                target_path.mkdir(parents=True, exist_ok=True)
                console.print(Panel(f'[green]✅ Folder Structure Created[/green]\n\n[cyan]File Found:[/] {file_path}\n[cyan]EDITED Path:[/] {target_path}', title='Success', border_style='green'))
    if not found:
        console.print(Panel(f'[red]❌ File not found in UNPACKED[/red]\n{filename}', title='Not Found', border_style='red'))
    Prompt.ask('Press Enter...', default='')

# ============================================================
# AUTO CONFIGURATION FEATURES - COMPLETE
# ============================================================

TARGET_FILE_NAME = 'BP_PlayerPawn.uasset'
HEADSHOT_TARGETS = [
    b'EAvatarDamagePosition::BigBody',
    b'EAvatarDamagePosition::BigFoot',
    b'EAvatarDamagePosition::BigHand',
    b'EAvatarDamagePosition::BigLimbs'
]
HEADSHOT_REPLACE = b'EAvatarDamagePosition::BigHead'

def is_headshot_already_applied(data: bytes) -> bool:
    for t in HEADSHOT_TARGETS:
        if t in data:
            return False
    return HEADSHOT_REPLACE in data

def auto_headshot_playerpawn_smart():
    console.print(Panel('[bold cyan]🎯 AUTO HEADSHOT[/bold cyan]\nPatches BP_PlayerPawn.uasset for headshot detection', border_style='cyan'))
    unpacked_root = BASE_DIR / 'ZSDIC' / 'UNPACKED'
    edited_root = BASE_DIR / 'ZSDIC' / 'EDITED'
    edited_root.mkdir(parents=True, exist_ok=True)
    source_file = None
    source_root = None
    from_edited = False
    for f in edited_root.rglob(TARGET_FILE_NAME):
        source_file = f
        source_root = edited_root
        from_edited = True
        console.print('[yellow]ℹ Using EDITED File[/yellow]')
    if not source_file:
        for f in unpacked_root.rglob(TARGET_FILE_NAME):
            source_file = f
            source_root = unpacked_root
            console.print('[cyan]ℹ Using UNPACKED File[/cyan]')
    if not source_file:
        console.print('[red]❌ BP_PlayerPawn.uasset Not Found[/red]')
        Prompt.ask('Press Enter To Continue', default='')
        return
    data = bytearray(source_file.read_bytes())
    if from_edited and is_headshot_already_applied(data):
        console.print(Panel('[bold yellow]⚠ ALREADY HEADSHOT APPLIED[/bold yellow]', border_style='yellow'))
        Prompt.ask('Press Enter To Continue', default='')
        return
    modified = False
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), console=console) as progress:
        task = progress.add_task('[cyan]Applying Headshot Patch...', total=len(HEADSHOT_TARGETS))
        for target in HEADSHOT_TARGETS:
            start = 0
            while True:
                pos = data.find(target, start)
                if pos == -1:
                    break
                if target.endswith(b'BigLimbs'):
                    data[pos:pos + 30] = HEADSHOT_REPLACE
                    data[pos + 30] = 0
                else:
                    data[pos:pos + 30] = HEADSHOT_REPLACE
                start = pos + 30
                modified = True
            progress.advance(task)
    if not modified:
        console.print('[yellow]⚠ No Headshot Strings Found[/yellow]')
        Prompt.ask('Press Enter To Continue', default='')
        return
    if source_root == unpacked_root:
        rel = source_file.relative_to(unpacked_root)
        parts = rel.parts
        relative_path = Path(*parts[1:]) if len(parts) > 1 else Path(*parts)
    else:
        relative_path = source_file.relative_to(edited_root)
    out_path = edited_root / relative_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    console.print(Panel(f'[bold green]✅ HEADSHOT SUCCESS[/bold green]\n\nSaved to: {out_path}', border_style='green'))
    Prompt.ask('Press Enter to continue', default='')

MAX_SIZE = 1024

def auto_white_body_smart():
    console.print(Panel('[bold cyan]👤 AUTO WHITE BODY[/bold cyan]\nCreates white body DAT files', border_style='cyan'))
    unpacked_root = BASE_DIR / 'ZSDIC' / 'UNPACKED'
    edited_root = BASE_DIR / 'ZSDIC' / 'EDITED'
    edited_root.mkdir(parents=True, exist_ok=True)
    credit = Prompt.ask('[cyan]Enter Credit Text To Write Inside DATs[/cyan]')
    credit_bytes = credit.encode(errors='ignore')
    matched = 0
    dat_files = [f for f in unpacked_root.rglob('*') if f.is_file() and f.suffix.lower() == '.dat']
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), console=console) as progress:
        task = progress.add_task('[cyan]Scanning DAT Files For White Body...', total=len(dat_files))
        for file in dat_files:
            progress.advance(task)
            if file.stat().st_size > MAX_SIZE:
                continue
            try:
                data = file.read_bytes()
            except:
                continue
            rel = file.relative_to(unpacked_root)
            parts = rel.parts
            relative_path = Path(*parts[1:]) if len(parts) > 1 else Path(*parts)
            out_path = edited_root / relative_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00' + credit_bytes)
            matched += 1
    console.print(Panel(f'[bold green]✅ WHITE BODY COMPLETE[/bold green]\n\nDAT Files Processed: {matched}', border_style='green'))
    Prompt.ask('Press Enter to continue', default='')

GRASS_FILES = [
    'Baltic_GrassType02.uasset', 'Baltic_GrassType01.uasset',
    'Savage_GrassType02.uasset', 'Savage_GrassType01.uasset',
    'DihorOtok_GrassType03.uasset', 'DihorOtok_GrassType01.uasset',
    'Forest_GrassType01.uasset', 'Foliage_Grasstype_009.uasset'
]

def auto_grass_white_smart():
    console.print(Panel('[bold cyan]🌿 AUTO NO GRASS[/bold cyan]\nNulls grass texture files', border_style='cyan'))
    unpacked_root = BASE_DIR / 'ZSDIC' / 'UNPACKED'
    edited_root = BASE_DIR / 'ZSDIC' / 'EDITED'
    edited_root.mkdir(parents=True, exist_ok=True)
    credit = Prompt.ask('[cyan]Enter credit text[/cyan]')
    credit_bytes = credit.encode(errors='ignore')
    targets = []
    for name in GRASS_FILES:
        for f in edited_root.rglob(name):
            targets.append((f, edited_root))
    for name in GRASS_FILES:
        for f in unpacked_root.rglob(name):
            rel = f.relative_to(unpacked_root)
            parts = rel.parts
            rel_clean = Path(*parts[1:]) if len(parts) > 1 else Path(*parts)
            if not any(rel_clean == t[0].relative_to(edited_root) for t in targets if t[1] == edited_root):
                targets.append((f, unpacked_root))
    if not targets:
        console.print('[yellow]⚠ No Grass Files Found[/yellow]')
        Prompt.ask('Press Enter to continue', default='')
        return
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TextColumn('{task.completed}/{task.total}'), console=console) as progress:
        task = progress.add_task('[green]Processing grass files...', total=len(targets))
        for file, root in targets:
            progress.update(task, description=f'[cyan]{file.name}[/cyan]')
            if root == unpacked_root:
                rel = file.relative_to(unpacked_root)
                parts = rel.parts
                relative_path = Path(*parts[1:]) if len(parts) > 1 else Path(*parts)
            else:
                relative_path = file.relative_to(edited_root)
            out_path = edited_root / relative_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, 'wb') as f:
                f.write(b'\x00\x00\x00\x00\x00\x00\x00\x00' + credit_bytes)
            progress.advance(task)
    console.print(Panel(f'[bold green]✅ NO GRASS COMPLETE[/bold green]\n\nFiles processed: {len(targets)}', border_style='green'))
    Prompt.ask('Press Enter to continue', default='')

HEX_PATTERNS = {
    b'\xed\xff\xff\xff': b'\x00\x00\x00\x00',
    b'\xcd\xff\xff\xff': b'\x00\x00\x00\x00'
}

def auto_master_baltic_landscape_hex():
    console.print(Panel('[bold cyan]🧩 MASTER BALTIC LANDSCAPE PATCH[/bold cyan]\nHex replace EDFFFFFF / CDFFFFFF → 00000000', border_style='cyan'))
    unpacked_root = BASE_DIR / 'OD_PAK' / 'UNPACKED'
    edited_root = BASE_DIR / 'OD_PAK' / 'EDITED'
    edited_root.mkdir(parents=True, exist_ok=True)
    TARGET_FILE = 'Master_Baltic_Landscape.uexp'
    source_file = None
    source_root = None
    from_edited = False
    for f in edited_root.rglob(TARGET_FILE):
        source_file = f
        source_root = edited_root
        from_edited = True
        console.print('[yellow]ℹ Using EDITED file[/yellow]')
    if not source_file:
        for f in unpacked_root.rglob(TARGET_FILE):
            source_file = f
            source_root = unpacked_root
            console.print('[cyan]ℹ Using UNPACKED file[/cyan]')
    if not source_file:
        console.print('[red]❌ Master_Baltic_Landscape.uexp not found[/red]')
        Prompt.ask('[cyan]Press Enter To Continue[/cyan]', default='')
        return
    try:
        data = bytearray(source_file.read_bytes())
    except Exception as e:
        console.print(f'[red]❌ Read error:[/] {e}')
        Prompt.ask('[cyan]Press Enter To Continue[/cyan]', default='')
        return
    already_done = True
    for pat in HEX_PATTERNS:
        if pat in data:
            already_done = False
            break
    if from_edited and already_done:
        console.print(Panel('[bold yellow]⚠ ALREADY PATCHED[/bold yellow]\nHex Values Are Already NULL.', border_style='yellow'))
        Prompt.ask('[cyan]Press Enter To Continue[/cyan]', default='')
        return
    modified = False
    for pat, rep in HEX_PATTERNS.items():
        start = 0
        while True:
            idx = data.find(pat, start)
            if idx == -1:
                break
            data[idx:idx + 4] = rep
            start = idx + 4
            modified = True
    if not modified:
        console.print('[yellow]⚠ No Matching Hex Patterns Found[/yellow]')
        Prompt.ask('[cyan]Press Enter To Continue[/cyan]', default='')
        return
    if source_root == unpacked_root:
        rel = source_file.relative_to(unpacked_root)
        parts = rel.parts
        relative_path = Path(*parts[1:]) if len(parts) > 1 else Path(*parts)
    else:
        relative_path = source_file.relative_to(edited_root)
    out_path = edited_root / relative_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(data)
    console.print(Panel(f'[bold green]✅ PATCH SUCCESSFUL[/bold green]\n\nFile: {TARGET_FILE}\nHex: EDFFFFFF / CDFFFFFF → 00000000', border_style='green'))
    Prompt.ask('[cyan]Press Enter to continue[/cyan]', default='')

def auto_configuration_menu():
    while True:
        clear_screen()
        show_banner(_auth_data)
        console.print(Panel(f"""
[bold cyan]AUTO CONFIGURATION[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] Auto Headshot     → ZSDIC Headshot Mod
[bold green][2][/bold green] Auto White Body   → ZSDIC White Body
[bold green][3][/bold green] Auto No Grass     → ZSDIC No Grass
[bold green][4][/bold green] Auto Master Baltic → OD Pak Hex Patch
[bold red][0][/bold red] Back to Main Menu
""", border_style='cyan', padding=(1, 3)))
        choice = Prompt.ask('[bold yellow]Select option[/bold yellow] ', default='0')
        if choice == '1':
            auto_headshot_playerpawn_smart()
        elif choice == '2':
            auto_white_body_smart()
        elif choice == '3':
            auto_grass_white_smart()
        elif choice == '4':
            auto_master_baltic_landscape_hex()
        elif choice == '0':
            return

# ============================================================
# 120 FPS FEATURES - COMPLETE
# ============================================================

KNOWN_120FPS_MODELS = [
    'Infinix X6873', 'Infinix X6871', 'XT2507-2', 'CPH2613',
    'CPH2661', 'V2241HA', 'RMX5061', 'NX712J', 'XT2301-5',
    'M381Q', 'PGT-AN20', 'NX733J', '23046RP50C', 'PJJ110',
    '24069PC21G', 'NP03J', 'NX769J', 'V2332A', 'A024',
    'OPD2415', 'PGFM10', 'V2337A', 'V2359A', 'V2366GA',
    'V2217A', 'PJD110', 'PKC110', 'PJE110', '25010PN30G',
    '24129PN74G', 'A065', 'SM-S926B', 'A001', 'A059',
    'V2243A', 'RMX5032', 'ASUS_AI2205_C', 'MEIZU 20', 'V2232A',
    '25010PN30C', 'I2405', 'PKX110', 'PLM110', 'PLE110',
    '24069PC21I', 'SM-S721B', 'RMX5085', 'SM-S937B',
    'motorola edge 60 pro', 'RMX5030', 'RMX5210', 'RMX3851', 'PLG110'
]

FPS_TARGET_FILE = 'Client120FPSMapping.uexp'

def _fps_patch_model(data: bytearray, user_model: str) -> bool:
    new_bytes = user_model.encode('utf-8')
    for target in KNOWN_120FPS_MODELS:
        old_bytes = target.encode('utf-8')
        if len(new_bytes) > len(old_bytes):
            continue
        if old_bytes not in data:
            continue
        idx = 0
        while True:
            pos = data.find(old_bytes, idx)
            if pos == -1:
                break
            ahead = data[pos + len(old_bytes):pos + len(old_bytes) + 50]
            if b'120' in ahead and b'90' not in ahead:
                data[pos:pos + len(old_bytes)] = new_bytes + b'\x00' * (len(old_bytes) - len(new_bytes))
                return True
            idx = pos + 1
    for target in KNOWN_120FPS_MODELS:
        old_bytes = target.encode('utf-8')
        if len(new_bytes) <= len(old_bytes) and old_bytes in data:
            pos = data.find(old_bytes)
            data[pos:pos + len(old_bytes)] = new_bytes + b'\x00' * (len(old_bytes) - len(new_bytes))
            return True
    return False

def _fps_run(game_label: str, game_dir: Path, user_model: str):
    input_dir = game_dir / 'INPUT_PAK'
    output_dir = game_dir / 'OUTPUT_PAK'
    edited_dir = game_dir / 'EDITED_DAT'
    pak_files = sorted(input_dir.glob('*.pak'))
    if not pak_files:
        console.print(Panel(f'[red]❌ No .pak file found in INPUT_PAK folder![/red]\n[cyan]{input_dir}[/cyan]', border_style='red'))
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    pak_file = pak_files[0]
    console.print(f'[cyan]Processing: {pak_file.name}[/cyan]')
    console.print('[cyan]━━━ STEP 1/3 : UNPACKING ━━━[/cyan]')
    try:
        pak_inst = TencentPakFile(pak_file, is_od=False)
    except Exception as e:
        console.print(Panel(f'[red]❌ PAK load failed: {e}[/red]', border_style='red'))
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    found_entry = None
    found_dir = None
    for dir_path, files in pak_inst._index.items():
        if FPS_TARGET_FILE in files:
            found_entry = files[FPS_TARGET_FILE]
            found_dir = dir_path
            break
    if not found_entry:
        console.print(Panel(f'[red]❌ \'{FPS_TARGET_FILE}\' not found inside the PAK![/red]', border_style='red'))
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    mount_point = pak_inst._mount_point
    edited_file = edited_dir / mount_point / found_dir / FPS_TARGET_FILE
    edited_file.parent.mkdir(parents=True, exist_ok=True)
    pak_inst._write_to_disk(edited_file, found_entry)
    console.print(f'  [green]✔[/] Extracted → [dim]{Path(mount_point) / found_dir / FPS_TARGET_FILE}[/dim]')
    console.print('[cyan]━━━ STEP 2/3 : PATCHING ━━━[/cyan]')
    data = bytearray(edited_file.read_bytes())
    if not _fps_patch_model(data, user_model):
        console.print(Panel('[red]❌ Could not replace any known 120FPS model![/red]', border_style='red'))
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    edited_file.write_bytes(data)
    console.print(f'  [green]✔[/] Model patched → [bold white]{user_model}[/]')
    console.print('[cyan]━━━ STEP 3/3 : REPACKING ━━━[/cyan]')
    output_dir.mkdir(exist_ok=True)
    output_pak = output_dir / pak_file.name
    try:
        shutil.copy2(pak_file, output_pak)
        pak_inst.repack(edited_dir, output_pak)
        console.print(f'  [green]✔[/] Repacked → [dim]{output_pak.name}[/dim]')
    except Exception as e:
        console.print(Panel(f'[red]❌ Repack failed: {e}[/red]', border_style='red'))
        traceback.print_exc()
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    console.print(Panel(f'[bold green]🎉 {game_label} 120 FPS DONE![/bold green]\n[white]Model  :[/] [bold cyan]{user_model}[/]\n[white]Output :[/] [dim]{output_pak}[/dim]', border_style='green'))
    Prompt.ask('\n[white]Press Enter to continue...[/white]', default='')

def handle_auto_120fps():
    while True:
        clear_screen()
        show_banner(_auth_data)
        bgmi_input_ok = any((FPS_ROOT / 'BGMI' / 'INPUT_PAK').glob('*.pak'))
        pubg_input_ok = any((FPS_ROOT / 'PUBG' / 'INPUT_PAK').glob('*.pak'))
        def _tick(ok):
            return '[green]✔[/green]' if ok else '[red]✗[/red]'
        console.print(Panel(f"""
[bold cyan]AUTO 120 FPS[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] 🎮 BGMI
     Client120FPSMapping patch for BGMI
     INPUT_PAK: {_tick(bgmi_input_ok)}
[bold green][2][/bold green] 🎮 PUBG
     Client120FPSMapping patch for PUBG
     INPUT_PAK: {_tick(pubg_input_ok)}
[dim]Place your .pak file in the INPUT_PAK folder before running.[/dim]
[bold red][0][/bold red] Back
""", border_style='cyan', padding=(1, 3)))
        try:
            choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '0'], default='0')
        except KeyboardInterrupt:
            return
        if choice == '0':
            return
        game_label = 'BGMI' if choice == '1' else 'PUBG'
        game_dir = FPS_ROOT / ('BGMI' if choice == '1' else 'PUBG')
        console.print()
        user_model = Prompt.ask(f'[bold cyan]Enter {game_label} device model[/bold cyan]').strip()
        if not user_model:
            console.print('[red]❌ Model name empty[/red]')
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
        else:
            _fps_run(game_label, game_dir, user_model)

# ============================================================
# ANTIRESET FEATURES - COMPLETE
# ============================================================

ANTIRESET_JSON = ANTIRESET_DIR / 'antireset_info.json'

def _ar_fmt_size(n: int) -> str:
    if n >= 1073741824:
        return f'{n / 1073741824:.2f} GB'
    elif n >= 1048576:
        return f'{n / 1048576:.2f} MB'
    elif n >= 1024:
        return f'{n / 1024:.2f} KB'
    else:
        return f'{n} B'

def _ar_load_json() -> dict:
    if ANTIRESET_JSON.exists():
        try:
            return json.loads(ANTIRESET_JSON.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}

def _ar_save_json(data: dict):
    ANTIRESET_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

def _ar_pick_obb(directory: Path, label: str) -> Path | None:
    files = sorted(directory.glob('*.obb'))
    if not files:
        return None
    if len(files) == 1:
        return files[0]
    tbl = Table(box=rich_box.SIMPLE, show_header=True)
    tbl.add_column('No.', style='bold cyan', justify='center')
    tbl.add_column(f'{label} File', style='white')
    tbl.add_column('Size', style='yellow', justify='right')
    for i, f in enumerate(files, 1):
        sz = f.stat().st_size
        sz_str = _ar_fmt_size(sz)
        tbl.add_row(str(i), f.name, sz_str)
    console.print(tbl)
    try:
        idx = int(Prompt.ask(f'[cyan]Select {label} file[/cyan]', default='1')) - 1
        if 0 <= idx < len(files):
            return files[idx]
        return files[0]
    except Exception:
        return files[0]

def ar_unzip_obb():
    console.print(Panel('[bold cyan]📦 UNZIP OBB[/bold cyan]\nExtracts modded OBB files', border_style='cyan'))
    obb_file = _ar_pick_obb(MODDED_OBB_DIR, 'MODDED OBB')
    if not obb_file:
        org_obb = _ar_pick_obb(ORG_OBB_DIR, 'ORG OBB')
        if not org_obb:
            console.print(Panel(f'[red]❌ No OBB Found![/red]', border_style='red'))
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            return
        dest = MODDED_OBB_DIR / org_obb.name
        shutil.copy2(org_obb, dest)
        console.print(f'[cyan]📋 ORG OBB copied → MODDED_OBB ({org_obb.name})[/cyan]')
        obb_file = dest
    if not zipfile.is_zipfile(obb_file):
        console.print(Panel(f'[red]❌ \'{obb_file.name}\' Not Valid Zip![/red]', border_style='red'))
        Prompt.ask('\n[white]Press Enter...[/white]', default='')
        return
    extract_dir = MODDED_OBB_DIR / obb_file.stem
    extract_dir.mkdir(exist_ok=True)
    with zipfile.ZipFile(obb_file, 'r') as zf:
        members = zf.infolist()
        with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TaskProgressColumn(), TimeElapsedColumn(), console=console) as prog:
            task = prog.add_task('[cyan]Extracting...', total=len(members))
            for member in members:
                zf.extract(member, extract_dir)
                prog.advance(task)
    obb_file.unlink()
    info = _ar_load_json()
    info['obb_name'] = obb_file.name
    info['obb_stem'] = obb_file.stem
    info['extract_dir'] = str(extract_dir)
    info['unzipped'] = True
    _ar_save_json(info)
    console.print(Panel(f'[green]✔ Unzip done:[/] [cyan]{obb_file.name}[/] → [dim]{extract_dir.name}/[/dim]', border_style='green'))
    Prompt.ask('\n[white]Press Enter to continue...[/white]', default='')

def ar_make_antireset():
    console.print(Panel('[bold cyan]🛡 MAKE ANTIRESET OBB[/bold cyan]\nCreates padded OBB matching original size', border_style='cyan'))
    info = _ar_load_json()
    extract_dir = None
    obb_name = ''
    if info.get('unzipped'):
        if info.get('extract_dir'):
            if info.get('obb_name'):
                extract_dir = Path(info['extract_dir'])
                obb_name = info['obb_name']
                if not extract_dir.exists():
                    extract_dir = None
    if extract_dir is None:
        subdirs = [d for d in MODDED_OBB_DIR.iterdir() if d.is_dir()]
        if not subdirs:
            console.print(Panel('[red]❌ No Unzipped Folder Found![/red]\n[yellow]💡 First use Unzip OBB option.[/yellow]', border_style='red'))
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            return
        extract_dir = subdirs[0]
        obb_name = extract_dir.name + '.obb'
    console.print(Panel(f'[bold white]📂 Extract Dir :[/] [cyan]{extract_dir.name}[/]\n[bold white]📦 OBB Name    :[/] [cyan]{obb_name}[/]', border_style='cyan'))
    target_size = None
    size_source = ''
    org_obb = _ar_pick_obb(ORG_OBB_DIR, 'ORG OBB')
    if org_obb:
        target_size = org_obb.stat().st_size
        size_source = f'ORG OBB — {org_obb.name}'
        info['org_obb_name'] = org_obb.name
        info['target_size'] = target_size
        _ar_save_json(info)
        console.print(f'  [green]✔ ORG OBB found:[/] [white]{org_obb.name}[/] [dim]({_ar_fmt_size(target_size)})[/]')
    else:
        if info.get('target_size'):
            target_size = int(info['target_size'])
            size_source = f'JSON Cache — {info.get("org_obb_name", "unknown")}'
            console.print(f'  [cyan]ℹ Using cached target size from JSON:[/] [white]{_ar_fmt_size(target_size)}[/]')
        else:
            console.print(Panel(f'[red]❌ No OBB Found In ORG_OBB Folder & No Target json Found![/red]\n[yellow]💡 Put Your Original OBB In ORG_OBB Folder[/yellow]', border_style='red'))
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
            return
    console.print()
    console.print('[bold cyan]━━━ STEP 1/2 : ZIPPING (STORE) ━━━[/bold cyan]')
    out_obb = MODDED_OBB_DIR / obb_name
    all_files = [f for f in extract_dir.rglob('*') if f.is_file()]
    with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TaskProgressColumn(), TimeElapsedColumn(), console=console) as prog:
        task = prog.add_task('[yellow]Zipping (STORE)...', total=len(all_files))
        with zipfile.ZipFile(out_obb, 'w', compression=zipfile.ZIP_STORED) as zf:
            for f in all_files:
                arcname = f.relative_to(extract_dir)
                zf.write(f, arcname)
                prog.advance(task)
    zipped_size = out_obb.stat().st_size
    console.print(f'\n  [white]Zipped size  :[/] [cyan]{_ar_fmt_size(zipped_size)}[/]')
    console.print(f'  [white]Target size  :[/] [cyan]{_ar_fmt_size(target_size)}[/] [dim]({size_source})[/]')
    console.print('\n[bold cyan]━━━ STEP 2/2 : PADDING ━━━[/bold cyan]')
    if zipped_size > target_size:
        console.print(Panel(f'[yellow]⚠ Zipped OBB ({_ar_fmt_size(zipped_size)}) is already LARGER than ORG OBB ({_ar_fmt_size(target_size)})![/yellow]', border_style='yellow'))
    elif zipped_size == target_size:
        console.print('  [green]✔ Sizes already match — no padding needed[/green]')
    else:
        bytes_to_add = target_size - zipped_size
        console.print(f'  [white]Padding needed:[/] [yellow]{_ar_fmt_size(bytes_to_add)}[/]')
        with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), console=console) as prog:
            task = prog.add_task('[magenta]Adding padding...', total=bytes_to_add)
            with open(out_obb, 'ab') as f:
                chunk_sz = 1048576
                remaining = bytes_to_add
                while remaining > 0:
                    chunk = min(chunk_sz, remaining)
                    f.write(b'\x00' * chunk)
                    remaining -= chunk
                    prog.update(task, advance=chunk)
    final_size = out_obb.stat().st_size
    console.print(Panel(f'[bold green]🎉 ANTIRESET OBB READY![/bold green]\n\n[white]Output File  :[/] [cyan]{out_obb.name}[/]\n[white]Final Size   :[/] [yellow]{_ar_fmt_size(final_size)}[/]\n[white]Target Size  :[/] [dim]{_ar_fmt_size(target_size)}[/]\n[white]Location     :[/] [dim]{MODDED_OBB_DIR}[/]', title='[green]✅ Success[/green]', border_style='green'))
    Prompt.ask('\n[white]Press Enter to continue...[/white]', default='')

def handle_antireset_tool():
    while True:
        clear_screen()
        show_banner(_auth_data)
        info = _ar_load_json()
        unzipped = info.get('unzipped', False)
        obb_name = info.get('obb_name', '—')
        cached_sz = info.get('target_size')
        org_obb_present = bool(list(ORG_OBB_DIR.glob('*.obb')))
        def _tick(cond):
            return '[green]✔[/green]' if cond else '[red]✗[/red]'
        console.print(Panel(f"""
[bold cyan]ANTIRESET OBB TOOL[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] 📦 UNZIP OBB
     MODDED_OBB → Extract and delete .obb
[bold green][2][/bold green] 🛡 MAKE ANTIRESET
     ZIP (STORE) → Pad to match ORG OBB
[bold cyan]STATUS[/bold cyan]
  ORG OBB present   {_tick(org_obb_present)}
  OBB Unzipped      {_tick(unzipped)}
  Cached ORG Size   {_tick(bool(cached_sz))}
[bold red][0][/bold red] Back
""", border_style='cyan', padding=(1, 3)))
        try:
            choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '0'], default='0')
        except KeyboardInterrupt:
            return
        if choice == '1':
            ar_unzip_obb()
        elif choice == '2':
            ar_make_antireset()
        elif choice == '0':
            break

# ============================================================
# ENCRYPT/DECRYPT FEATURES - COMPLETE
# ============================================================

_MINI_BYTES = bytes.fromhex('a207970006046e500e000000486c42adac7abf083cb61f01f805e156acf00638733f82b80aeefb1fd6d98dedb47ad1a6')
_ZSDIC_BYTES = bytes.fromhex('76f6150006046e500e000000f4eeff5d2e38812ae810e2689c81eee55f3b20bc6337dcb80aeefb1fc15764d1b47ad1a6')
_TAIL_BYTES = bytes.fromhex('b47ad1a6')

def _ep_paks(folder: Path) -> list:
    if not folder.exists():
        return []
    return sorted([f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in ['.pak', '.obb']], key=lambda x: x.name.lower())

def _ep_sz(p: Path) -> str:
    try:
        b = os.path.getsize(p)
        if b >= 1073741824:
            return f'{b / 1073741824:.2f} GB'
        elif b >= 1048576:
            return f'{b / 1048576:.2f} MB'
        return f'{b / 1024:.1f} KB'
    except:
        return '?'

def _ep_rand_byte() -> int:
    return random.randint(0, 255)

def _ep_encrypt_normal(src: Path, dst: Path) -> bool:
    try:
        shutil.copy2(src, dst)
        with open(dst, 'r+b') as f:
            f.seek(0, 2)
            size = f.tell()
            if size < 45:
                return False
            f.seek(max(0, size - 45))
            f.write(b'\x00' * 45)
        return True
    except Exception as e:
        console.print(f'  [red]✖[/red]  {src.name}: {e}')
        return False

def _ep_build_v2_tail(enc_level: int, custom_key) -> bytes:
    remaining = 41 - enc_level
    tail = bytearray()
    if remaining > 0:
        tail.append(103)
    if remaining > 1:
        tail.append(109)
    kb = list(custom_key.encode('utf-8')[:20]) if custom_key else []
    for i in range(2, remaining):
        ki = i - 2
        tail.append(kb[ki] if ki < len(kb) else _ep_rand_byte())
    tail += _TAIL_BYTES
    return bytes(tail)

def _ep_encrypt_v2(src: Path, dst: Path, enc_level: int, custom_key) -> bool:
    try:
        with open(src, 'rb') as f:
            data = f.read()
        if len(data) < 45:
            return False
        with open(dst, 'wb') as f:
            f.write(data[:-45] + _ep_build_v2_tail(enc_level, custom_key))
        return True
    except Exception as e:
        console.print(f'  [red]✖[/red]  {src.name}: {e}')
        return False

def _ep_decrypt(src: Path, dst: Path, sig: bytes) -> bool:
    try:
        shutil.copy2(src, dst)
        with open(dst, 'r+b') as f:
            f.seek(0, 2)
            size = f.tell()
            if size < 48:
                return False
            f.seek(size - 48)
            f.write(sig)
        return True
    except Exception as e:
        console.print(f'  [red]✖[/red]  {src.name}: {e}')
        return False

def _ep_show_files(files: list, title: str):
    t = Table(box=rich_box.SIMPLE, expand=True)
    t.add_column('#', style=f'bold yellow', width=4, justify='right')
    t.add_column('FILE NAME', style='bold white')
    t.add_column('SIZE', justify='right', style='dim')
    for i, f in enumerate(files, 1):
        t.add_row(str(i), f.name, _ep_sz(f))
    console.print(Panel(t, title=f'[bold cyan]{title}[/]', border_style='cyan'))

def _ep_show_result(rows, title, ok, fail):
    t = Table(box=rich_box.SIMPLE, expand=True)
    t.add_column('', width=3, justify='center')
    t.add_column('FILE', style='white')
    t.add_column('STATUS', justify='center')
    for icon, name, markup in rows:
        c = 'green' if icon == '✔' else 'red'
        t.add_row(f'[bold {c}]{icon}[/]', name, markup)
    console.print(Panel(t, title=f'[bold cyan]{title}[/]', border_style='green' if not fail else 'yellow'))
    console.print(f'  [bold green]✔ {ok} success[/]' + (f'  [bold red]✖ {fail} failed[/]' if fail else ''))

def handle_encrypt_pak_tool():
    while True:
        clear_screen()
        show_banner(_auth_data)
        console.print(Panel(f"""
[bold cyan]ENCRYPT & DECRYPT OBB[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] NORMAL ENCRYPTION     → Standard Encryption
[bold green][2][/bold green] CUSTOM ENCRYPTION     → Custom Level + Custom Key
[bold green][3][/bold green] DECRYPT PAK           → Decrypt MINI OBB / ZSDIC
[bold red][0][/bold red] Back
""", border_style='cyan', padding=(1, 3)))
        choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '3', '0'], default='0')
        if choice == '0':
            return
        elif choice == '1':
            in_dir = BASE_DIR / 'ENC_DEC' / 'NORMAL_ENC' / 'INPUT'
            out_dir = BASE_DIR / 'ENC_DEC' / 'NORMAL_ENC' / 'OUTPUT'
            files = _ep_paks(in_dir)
            if not files:
                console.print(Panel(f'[red]⚠ No .pak / .obb files found![/red]', border_style='red'))
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            _ep_show_files(files, f'📥 INPUT — {len(files)} file(s)')
            console.print()
            yn = Prompt.ask(f'[bold yellow]Proceed? {len(files)} file(s) will be encrypted[/] [dim](y/n)[/dim]', default='y')
            if yn.strip().lower() != 'y':
                continue
            console.print()
            ok, fail, rows = 0, 0, []
            with Progress(SpinnerColumn(spinner_name='dots2'), TextColumn('[bold cyan]{task.description}'), BarColumn(), TaskProgressColumn(), TimeElapsedColumn(), console=console) as prog:
                task = prog.add_task('Encrypting (Normal)...', total=len(files))
                for f in files:
                    if _ep_encrypt_normal(f, out_dir / f.name):
                        ok += 1
                        rows.append(('✔', f.name, '[bold green]ENCRYPTED[/]'))
                    else:
                        fail += 1
                        rows.append(('✖', f.name, '[bold red]FAILED[/]'))
                    prog.advance(task)
            console.print()
            _ep_show_result(rows, '📊 NORMAL ENCRYPT RESULT', ok, fail)
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
        elif choice == '2':
            in_dir = BASE_DIR / 'ENC_DEC' / 'CUSTOM_ENC' / 'INPUT'
            out_dir = BASE_DIR / 'ENC_DEC' / 'CUSTOM_ENC' / 'OUTPUT'
            console.print(Panel('[bold yellow]⚠ Custom encrypted files CANNOT be decrypted back![/bold yellow]', border_style='yellow'))
            yn = Prompt.ask('[bold yellow]Continue?[/] [dim](y/n)[/dim]', default='n')
            if yn.strip().lower() != 'y':
                continue
            console.print()
            console.print('[bold cyan]━━━ SELECT ENCRYPTION LEVEL (1-10) ━━━[/bold cyan]')
            level_desc = {
                1: 'Lightest', 2: 'Very light', 3: 'Light',
                4: 'Moderate', 5: 'Medium', 6: 'Strong',
                7: 'Very strong', 8: 'Heavy', 9: 'Very heavy', 10: 'Maximum'
            }
            for n in range(1, 11):
                console.print(f'  [yellow]{n}[/yellow] → {level_desc[n]}')
            enc_level = None
            while enc_level is None:
                raw = Prompt.ask('[bold cyan]Enter level (1-10)[/bold cyan]').strip()
                if raw.isdigit() and 1 <= int(raw) <= 10:
                    enc_level = int(raw)
                else:
                    console.print('  [red]Invalid — enter a number between 1 and 10.[/red]')
            custom_key = None
            use_key = Prompt.ask('[bold cyan]Add a custom key?[/] [dim](y/n)[/dim]', default='n').strip().lower()
            if use_key == 'y':
                ki = Prompt.ask('[bold cyan]Enter key (max 20 characters)[/bold cyan]').strip()
                if ki and len(ki) <= 20:
                    custom_key = ki
            files = _ep_paks(in_dir)
            if not files:
                console.print(Panel(f'[red]⚠ No .pak / .obb files found![/red]', border_style='red'))
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            _ep_show_files(files, f'📥 INPUT — {len(files)} file(s)')
            console.print()
            yn = Prompt.ask(f'[bold yellow]Encrypt {len(files)} file(s) with level {enc_level}?[/] [dim](y/n)[/dim]', default='y')
            if yn.strip().lower() != 'y':
                continue
            console.print()
            ok, fail, rows = 0, 0, []
            with Progress(SpinnerColumn(spinner_name='dots2'), TextColumn('[bold cyan]{task.description}'), BarColumn(), TaskProgressColumn(), TimeElapsedColumn(), console=console) as prog:
                task = prog.add_task(f'Encrypting (level {enc_level})...', total=len(files))
                for f in files:
                    if _ep_encrypt_v2(f, out_dir / f.name, enc_level, custom_key):
                        ok += 1
                        rows.append(('✔', f.name, f'[bold green]ENCRYPTED[/] [dim](lvl {enc_level})[/dim]'))
                    else:
                        fail += 1
                        rows.append(('✖', f.name, '[bold red]FAILED[/]'))
                    prog.advance(task)
            console.print()
            _ep_show_result(rows, '📊 CUSTOM ENCRYPT RESULT', ok, fail)
            Prompt.ask('\n[white]Press Enter...[/white]', default='')
        elif choice == '3':
            in_dir = BASE_DIR / 'ENC_DEC' / 'DECRYPT' / 'INPUT'
            out_dir = BASE_DIR / 'ENC_DEC' / 'DECRYPT' / 'OUTPUT'
            console.print(Panel(f"""
[bold cyan]DECRYPT PAK[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] DECRYPT MINI OBB
[bold green][2][/bold green] DECRYPT ZSDIC
[bold red][0][/bold red] Back
""", border_style='cyan'))
            sub_choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '0'], default='0')
            if sub_choice == '0':
                continue
            sig = _MINI_BYTES if sub_choice == '1' else _ZSDIC_BYTES
            label = 'MINI OBB' if sub_choice == '1' else 'ZSDIC'
            files = _ep_paks(in_dir)
            if not files:
                console.print(Panel(f'[red]⚠ No .pak / .obb files found![/red]', border_style='red'))
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
                continue
            _ep_show_files(files, f'📥 INPUT — {len(files)} file(s)')
            console.print()
            yn = Prompt.ask(f'[bold yellow]Proceed? {len(files)} file(s) → {label} decrypt[/] [dim](y/n)[/dim]', default='y')
            if yn.strip().lower() != 'y':
                continue
            console.print()
            ok, fail, rows = 0, 0, []
            with Progress(SpinnerColumn(spinner_name='dots2'), TextColumn('[bold cyan]{task.description}'), BarColumn(), TaskProgressColumn(), TimeElapsedColumn(), console=console) as prog:
                task = prog.add_task(f'Decrypting ({label})...', total=len(files))
                for f in files:
                    if _ep_decrypt(f, out_dir / f.name, sig):
                        ok += 1
                        rows.append(('✔', f.name, f'[bold green]DECRYPTED [{label}][/]'))
                    else:
                        fail += 1
                        rows.append(('✖', f.name, '[bold red]FAILED[/]'))
                    prog.advance(task)
            console.print()
            _ep_show_result(rows, f'📊 DECRYPT RESULT — {label}', ok, fail)
            Prompt.ask('\n[white]Press Enter...[/white]', default='')

# ============================================================
# SPLIT/MERGE FEATURES - COMPLETE
# ============================================================

CHUNK_SIZE = 65536

def split_file_ui():
    console.print(Panel('[bold cyan]✂️ SPLIT FILE[/bold cyan]\nSplits into 64KB chunks', border_style='cyan'))
    files = [f for f in SPLIT_DIR.iterdir() if f.is_file()]
    if not files:
        console.print('[red]❌ No Files Found In SPLIT Folder[/red]')
        Prompt.ask('Press Enter...', default='')
        return
    for i, f in enumerate(files, 1):
        console.print(f'  [{i}] {f.name} ({_ep_sz(f)})')
    try:
        idx = int(Prompt.ask('Select Number')) - 1
        src_file = files[idx]
    except:
        console.print('[red]❌ Invalid Selection[/red]')
        return
    out_dir = SPLIT_DIR / src_file.stem
    out_dir.mkdir(exist_ok=True)
    console.print(f'\n[yellow]✂ Splitting:[/] {src_file.name}')
    part = 0
    with open(src_file, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            out_file = out_dir / f'{src_file.stem}_{part}{src_file.suffix}'
            out_file.write_bytes(chunk)
            part += 1
    console.print(Panel(f'[bold green]✅ Split Complete[/bold green]\n[white]Chunks:[/] {part}\n[cyan]Output:[/] {out_dir}', border_style='green'))
    Prompt.ask('[white]Press Enter to continue...[/white]', default='')

def merge_file_ui():
    console.print(Panel('[bold cyan]🧩 MERGE CHUNKS[/bold cyan]\nMerges chunks back to file', border_style='cyan'))
    folders = [d for d in MERGE_DIR.iterdir() if d.is_dir()]
    if not folders:
        console.print('[red]❌ No Chunk Folders In MERGE[/red]')
        Prompt.ask('Press Enter...', default='')
        return
    console.print('\n[cyan]Select Folder To Merge[/cyan]')
    for i, d in enumerate(folders, 1):
        console.print(f'  [{i}] {d.name}')
    try:
        idx = int(Prompt.ask('Select Number')) - 1
        src_dir = folders[idx]
    except:
        return
    chunks = sorted(src_dir.iterdir(), key=lambda f: int(f.stem.split('_')[-1]))
    if not chunks:
        console.print('[red]❌ No Chunks Found[/red]')
        return
    out_name = Prompt.ask('Enter Merged File Name (With Extension)')
    if not out_name:
        return
    out_file = MERGE_DIR / out_name
    with open(out_file, 'wb') as out:
        for c in chunks:
            out.write(c.read_bytes())
    console.print(Panel(f'[bold green]✅ Merge Completed[/bold green]\nChunks Merged: {len(chunks)}\nOutput: {out_file}', border_style='green'))
    Prompt.ask('Press Enter...', default='')

def search_text_in_splitted_files():
    console.print(Panel('[bold cyan]🔎 SEARCH IN SPLIT FILES[/bold cyan]', border_style='cyan'))
    folders = [d for d in SPLIT_DIR.iterdir() if d.is_dir()]
    if not folders:
        console.print('[red]❌ No Split Folders Found[/red]')
        Prompt.ask('Press Enter...', default='')
        return
    console.print('\n[cyan]Select Folder To Search[/cyan]')
    for i, d in enumerate(folders, 1):
        console.print(f'  [{i}] {d.name}')
    try:
        idx = int(Prompt.ask('Select Number')) - 1
        target_dir = folders[idx]
    except:
        console.print('[red]❌ Invalid Selection[/red]')
        return
    search_text = Prompt.ask('\n[yellow]Enter Text To Search[/yellow]').strip()
    if not search_text:
        console.print('[red]❌ Empty Text[/red]')
        return
    search_bytes = search_text.encode(errors='ignore')
    console.print(f'\n[yellow]🔎 Searching \'{search_text}\' in:[/] {target_dir.name}\n')
    found_files = []
    scanned = 0
    for f in sorted(target_dir.iterdir()):
        if not f.is_file():
            continue
        scanned += 1
        try:
            data = f.read_bytes()
            if search_bytes in data:
                found_files.append(f)
                console.print(f'[green]✔ FOUND:[/] {f.name}')
        except:
            continue
    if not found_files:
        console.print('\n[red]❌ Text not found in any chunk[/red]')
        Prompt.ask('\n[white]Press Enter to continue...[/white]', default='')
        return
    console.print(f'\n[bold green]✅ Found in {len(found_files)} file(s)[/bold green]')
    console.print(f'[cyan]📊 Scanned Files:[/] {scanned}')
    choice = Prompt.ask('\n[yellow]Copy edited files? (Y/N)[/yellow]', default='N').strip().lower()
    if choice == 'y':
        dest_root = target_dir / search_text
        dest_root.mkdir(parents=True, exist_ok=True)
        for f in found_files:
            try:
                shutil.copy(f, dest_root / f.name)
            except:
                pass
        console.print(f'[bold green]📁 Copied {len(found_files)} file(s) to:[/] {dest_root}')
    Prompt.ask('\n[white]Press Enter to continue...[/white]', default='')

def file_split_merge_menu():
    while True:
        clear_screen()
        show_banner(_auth_data)
        console.print(Panel(f"""
[bold cyan]SPLIT / MERGE FILES[/bold cyan]
[bold cyan]──────────────────────────────[/bold cyan]
[bold green][1][/bold green] ✂️ Split File (64 KB chunks)
[bold green][2][/bold green] 🧩 Merge Chunks
[bold green][3][/bold green] 🔎 Search Text In Split Files
[bold red][0][/bold red] Back
""", border_style='cyan', padding=(1, 3)))
        choice = Prompt.ask('[bold yellow]Select option[/bold yellow]', choices=['1', '2', '3', '0'], default='0')
        if choice == '1':
            split_file_ui()
        elif choice == '2':
            merge_file_ui()
        elif choice == '3':
            search_text_in_splitted_files()
        elif choice == '0':
            return

# ============================================================
# LUA TOOL CORE - COMPLETE
# ============================================================

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/DANGERMODVIP/wewe/main"
_K = bytes.fromhex("112136474657a78d9d8490d8ab008c35261af7e45805b8b31507d02c1e8ff6c8")

TEMP_DIR = os.path.join(tempfile.gettempdir(), "yukioh_okami_tools")
os.makedirs(TEMP_DIR, exist_ok=True)
JAVA_JAR = os.path.join(TEMP_DIR, "unluac_patched.jar")

def _download_tools():
    files = {
        JAVA_JAR: f"{GITHUB_RAW_BASE}/unluac_patched.jar",
    }
    for local_path, url in files.items():
        if os.path.exists(local_path):
            continue
        try:
            if not HAS_REQUESTS:
                continue
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
                console.print(f"[cyan]Downloaded {os.path.basename(local_path)}[/cyan]")
            else:
                console.print(f"[yellow]Failed to download {os.path.basename(local_path)} (HTTP {r.status_code})[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Error downloading {os.path.basename(local_path)}: {e}[/yellow]")

_download_tools()

def _cleanup_lua_tools():
    pass

atexit.register(_cleanup_lua_tools)

_STD_OPCODE_NAMES = [
    "MOVE","LOADK","LOADKX","LOADBOOL","LOADNIL",
    "GETUPVAL","GETTABUP","GETTABLE","SETTABUP","SETUPVAL",
    "SETTABLE","NEWTABLE","SELF","ADD","SUB",
    "MUL","MOD","POW","DIV","IDIV",
    "BAND","BOR","BXOR","SHL","SHR",
    "UNM","BNOT","NOT","LEN","CONCAT",
    "JMP","EQ","LT","LE","TEST",
    "TESTSET","CALL","TAILCALL","RETURN","FORLOOP",
    "FORPREP","TFORCALL","TFORLOOP","SETLIST","CLOSURE",
    "VARARG","EXTRAARG"
]

_T24_NAME_SHUFFLED = {
    0:"ADD", 1:"SUB", 2:"MUL", 5:"DIV", 7:"BAND", 10:"SHL",
    12:"UNM", 14:"NOT", 15:"LEN", 16:"CONCAT",
    17:"MOVE", 18:"LOADK", 20:"LOADBOOL", 21:"LOADNIL",
    22:"GETUPVAL", 23:"GETTABUP", 24:"GETTABLE",
    8:"SETTABUP", 9:"SETUPVAL", 27:"SETTABLE", 28:"NEWTABLE", 29:"SELF",
    30:"JMP", 31:"EQ", 32:"LT", 33:"LE", 34:"TEST", 35:"TESTSET",
    36:"CALL", 37:"TAILCALL", 38:"RETURN",
    39:"FORLOOP", 40:"FORPREP", 41:"TFORCALL", 42:"TFORLOOP",
    43:"SETLIST", 44:"CLOSURE", 45:"VARARG",
}
_T24_TO_STD = {t24: _STD_OPCODE_NAMES.index(nm) for t24, nm in _T24_NAME_SHUFFLED.items() if nm in _STD_OPCODE_NAMES}
_STD_TO_T24 = {std: t24 for t24, std in _T24_TO_STD.items()}

def _convert_t24_to_standard(src_path, dst_path):
    with open(src_path, 'rb') as f:
        d = bytearray(f.read())
    if d[:4] != b'\x1bLua' or d[4] != 0x53:
        return False, 'Not Lua 5.3 bytecode'
    out = bytearray()
    pos = [0]
    out.extend(d[:34])
    pos[0] = 34

    def rb():
        v = d[pos[0]]
        pos[0] += 1
        return v

    def ri32():
        v = struct.unpack_from('<i', d, pos[0])[0]
        pos[0] += 4
        return v

    def ri64():
        v = struct.unpack_from('<q', d, pos[0])[0]
        pos[0] += 8
        return v

    def rf64():
        v = struct.unpack_from('<d', d, pos[0])[0]
        pos[0] += 8
        return v

    def wb(v):
        out.append(v & 0xFF)

    def wi32(v):
        out.extend(struct.pack('<i', v))

    def wi64(v):
        out.extend(struct.pack('<q', v))

    def wf64(v):
        out.extend(struct.pack('<d', v))

    def _xdecwrite():
        sz = d[pos[0]]
        if sz == 0:
            pos[0] += 1
            out.append(0)
            return
        if sz == 0xFF:
            length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1
            ds = pos[0] + 9
            pos[0] = ds + length
            out.append(0xFF)
            out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1
            ds = pos[0] + 1
            pos[0] = ds + length
            out.append(sz)
        for i in range(length):
            out.append(d[ds + i] ^ _K[i % len(_K)])

    def _remap(ins):
        t24_op = ins & 0x3F
        std_op = _T24_TO_STD.get(t24_op, t24_op)
        return (ins & ~0x3F) | std_op

    def _rebuild():
        _xdecwrite()
        wi32(ri32())
        wi32(ri32())
        wb(rb())
        wb(rb())
        wb(rb())
        n = ri32()
        wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]
            pos[0] += 4
            out.extend(struct.pack('<I', _remap(ins)))
        n = ri32()
        wi32(n)
        for _ in range(n):
            t = rb()
            wb(t)
            if t == 0:
                pass
            elif t == 1:
                wb(rb())
            elif t == 3:
                wf64(rf64())
            elif t == 19:
                wi64(ri64())
            elif t in (4, 20):
                _xdecwrite()
            else:
                raise ValueError(f'Unknown const type {t}')
        n = ri32()
        wi32(n)
        for _ in range(n):
            wb(rb())
            wb(rb())
        n = ri32()
        wi32(n)
        for _ in range(n):
            _rebuild()
        n = ri32()
        t24_lines = list(d[pos[0]:pos[0] + n])
        pos[0] += n
        abs_n = ri32()
        pos[0] += abs_n * 8
        wi32(n)
        for ln in t24_lines:
            out.extend(struct.pack('<i', ln))
        n = ri32()
        wi32(n)
        for _ in range(n):
            _xdecwrite()
            wi32(ri32())
            wi32(ri32())
        n = ri32()
        wi32(n)
        for _ in range(n):
            _xdecwrite()

    try:
        _rebuild()
        with open(dst_path, 'wb') as f:
            f.write(out)
        return True, f'{len(d)}B -> {len(out)}B'
    except Exception as e:
        return False, str(e)

def _run_unluac(std_luac_path):
    if not os.path.isfile(JAVA_JAR):
        return None, f'unluac_patched.jar not found: {JAVA_JAR}'
    try:
        r = subprocess.run(['java', '-jar', JAVA_JAR, std_luac_path], capture_output=True, timeout=60)
        raw = r.stdout.decode('utf-8', errors='replace')
        _NOISE = [
            r'No pubg_map\.properties found\. Using standard map\.',
            r'Using standard map\.',
            r'No pubg_map\.properties found\.',
        ]
        for pattern in _NOISE:
            raw = re.sub(pattern, '', raw)
        lines = [l for l in raw.split('\n') if l.strip() != '' or l == '']
        clean = []
        i = 0
        while i < len(lines):
            stripped = lines[i].rstrip()
            if re.search(r'\s*local\s+\w+\s*=\s*$', stripped):
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                next_stripped = lines[j].strip() if j < len(lines) else ''
                if next_stripped.startswith('function'):
                    clean.append(stripped + ' ' + lines[j].lstrip())
                    i = j + 1
                    continue
                i += 1
                continue
            clean.append(lines[i])
            i += 1
        code = '\n'.join(clean)
        if not code.strip():
            return None, f'unluac empty output (exit={r.returncode})'

        credit_top = '--[[ Decompiled by Yukioh Ōkami TOOL v4.5 ]]--\n'
        credit_mid = '--[[ Fully developed by @Yukira_12 ]]--\n'
        code = credit_top + credit_mid + code

        return code, ''
    except FileNotFoundError:
        return None, 'java not found'
    except subprocess.TimeoutExpired:
        return None, 'unluac timeout (>60s)'
    except Exception as e:
        return None, str(e)

def decompile_file(in_path, out_path):
    jar_ok = os.path.isfile(JAVA_JAR)
    with tempfile.NamedTemporaryFile(suffix='.luac', delete=False) as tf:
        tmp_std = tf.name
    conv_ok = False
    conv_msg = ''
    try:
        conv_ok, conv_msg = _convert_t24_to_standard(in_path, tmp_std)
    except Exception as e:
        conv_ok = False
        conv_msg = str(e)

    if conv_ok and jar_ok:
        code, err = _run_unluac(tmp_std)
        if code:
            try:
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(code)
                if os.path.exists(tmp_std):
                    os.unlink(tmp_std)
                return True, '', 'unluac_patched', len(code.splitlines()), 0
            except Exception:
                pass

    if os.path.exists(tmp_std):
        os.unlink(tmp_std)
    return False, conv_msg or 'Decompile failed', 'none', 0, 0

def _extract_source_name_t24(t24_path):
    try:
        with open(t24_path, 'rb') as f:
            d = f.read()
        if len(d) < 36 or d[:4] != b'\x1bLua' or d[4] != 0x53:
            return None
        pos = 34
        sz = d[pos]
        if sz == 0:
            return ''
        elif sz == 0xFF:
            if len(d) < pos + 9:
                return None
            length = struct.unpack_from('<Q', d, pos + 1)[0] - 1
            if len(d) < pos + 9 + length:
                return None
            name_bytes = bytes(d[pos + 9 + i] ^ _K[i % len(_K)] for i in range(length))
        else:
            length = sz - 1
            if len(d) < pos + 1 + length:
                return None
            name_bytes = bytes(d[pos + 1 + i] ^ _K[i % len(_K)] for i in range(length))
        return name_bytes.decode('utf-8', errors='replace')
    except Exception:
        return None

def _patch_source_name_std(std_bytes, new_source_name):
    d = bytearray(std_bytes)
    pos = 34
    input_size_t = d[13]
    sz = d[pos]
    if sz == 0:
        old_total = 1
    elif sz == 0xFF:
        if input_size_t == 8:
            old_len = struct.unpack_from('<Q', d, pos + 1)[0] - 1
            old_total = 1 + 8 + old_len
        else:
            old_len = struct.unpack_from('<I', d, pos + 1)[0] - 1
            old_total = 1 + 4 + old_len
    else:
        old_len = sz - 1
        old_total = 1 + old_len
    new_name_bytes = new_source_name.encode('utf-8') if new_source_name else b''
    new_len = len(new_name_bytes)
    if new_len == 0:
        new_str_bytes = bytes([0])
    elif new_len + 1 < 0xFF:
        new_str_bytes = bytes([new_len + 1]) + new_name_bytes
    else:
        if input_size_t == 8:
            new_str_bytes = bytes([0xFF]) + struct.pack('<Q', new_len + 1) + new_name_bytes
        else:
            new_str_bytes = bytes([0xFF]) + struct.pack('<I', new_len + 1) + new_name_bytes
    return bytes(d[:pos]) + new_str_bytes + bytes(d[pos + old_total:])

def _rebuild_std_to_t24(std_bytecode):
    d = bytearray(std_bytecode)
    out = bytearray()
    pos = [34]
    out.extend(d[:34])
    input_size_t = d[13]
    out[13] = 4

    def rb():
        v = d[pos[0]]
        pos[0] += 1
        return v

    def ri32():
        v = struct.unpack_from('<i', d, pos[0])[0]
        pos[0] += 4
        return v

    def ri64():
        v = struct.unpack_from('<q', d, pos[0])[0]
        pos[0] += 8
        return v

    def rf64():
        v = struct.unpack_from('<d', d, pos[0])[0]
        pos[0] += 8
        return v

    def wi32(v):
        out.extend(struct.pack('<i', v))

    def wu32(v):
        out.extend(struct.pack('<I', v))

    def wi64(v):
        out.extend(struct.pack('<q', v))

    def wf64(v):
        out.extend(struct.pack('<d', v))

    def _enc():
        sz = d[pos[0]]
        if sz == 0:
            pos[0] += 1
            out.append(0)
            return
        if sz == 0xFF:
            if input_size_t == 8:
                length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1
                ds = pos[0] + 9
                pos[0] = ds + length
            else:
                length = struct.unpack_from('<I', d, pos[0]+1)[0] - 1
                ds = pos[0] + 5
                pos[0] = ds + length
            out.append(0xFF)
            out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1
            ds = pos[0] + 1
            pos[0] = ds + length
            out.append(sz)
        for i in range(length):
            out.append(d[ds + i] ^ _K[i % len(_K)])

    def rebuild():
        _enc()
        wi32(ri32())
        wi32(ri32())
        out.append(rb())
        out.append(rb())
        out.append(rb())
        n = ri32()
        wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]
            pos[0] += 4
            std_op = ins & 0x3F
            t24_op = _STD_TO_T24.get(std_op, std_op)
            wu32((ins & ~0x3F) | t24_op)
        n = ri32()
        wi32(n)
        for _ in range(n):
            t = rb()
            out.append(t)
            if t == 0:
                pass
            elif t == 1:
                out.append(rb())
            elif t == 3:
                wf64(rf64())
            elif t == 19:
                wi64(ri64())
            elif t in (4, 20):
                _enc()
            else:
                raise ValueError(f'Unknown const type {t}')
        n = ri32()
        wi32(n)
        for _ in range(n):
            out.append(rb())
            out.append(rb())
        n = ri32()
        wi32(n)
        for _ in range(n):
            rebuild()
        n = ri32()
        lines_i32 = []
        for _ in range(n):
            lines_i32.append(struct.unpack_from('<i', d, pos[0])[0])
            pos[0] += 4
        wi32(n)
        for ln in lines_i32:
            out.append(ln & 0xFF)
        _ABSLINE_INTERVAL = 128
        if n >= _ABSLINE_INTERVAL:
            _abs_entries = [(pc, lines_i32[pc]) for pc in range(_ABSLINE_INTERVAL, n, _ABSLINE_INTERVAL)]
            wi32(len(_abs_entries))
            for _pc, _ln in _abs_entries:
                wi32(_pc)
                wi32(_ln)
        else:
            wi32(0)
        n = ri32()
        wi32(n)
        for _ in range(n):
            _enc()
            wi32(ri32())
            wi32(ri32())
        n = ri32()
        wi32(n)
        for _ in range(n):
            _enc()

    try:
        rebuild()
        return bytes(out)
    except Exception:
        return None

def _detect_env():
    if (os.environ.get("TERMUX_VERSION") or os.path.isdir("/data/data/com.termux") or
            os.path.isfile("/data/data/com.termux/files/usr/bin/pkg")):
        return "termux"
    if os.path.isfile("/usr/bin/apt-get") or os.path.isfile("/usr/bin/apt"):
        return "debian"
    if os.path.isfile("/usr/bin/pacman"):
        return "arch"
    return "unknown"

def _find_compiler():
    system_paths = ['luac5.3', 'luac', '/usr/bin/luac5.3', '/usr/local/bin/luac5.3',
                    '/data/data/com.termux/files/usr/bin/luac5.3',
                    '/data/data/com.termux/files/usr/bin/luac']
    for c in system_paths:
        try:
            r = subprocess.run([c, '-v'], capture_output=True, timeout=3)
            if b'5.3' in r.stdout + r.stderr:
                return 'luac', c
        except Exception:
            pass
    return None, None

def compile_file(src_path, out_path, orig_source_name=None):
    try:
        with open(src_path, 'rb') as _f:
            _magic = _f.read(4)
        if _magic == b'\x1bLua':
            return False, "File is already compiled bytecode.", ''
    except OSError as e:
        return False, f'File read error: {e}', ''

    ctype, cpath = _find_compiler()
    if ctype is None:
        env = _detect_env()
        if env == 'termux':
            hint = 'pkg install lua53'
        elif env == 'debian':
            hint = 'sudo apt install lua5.3'
        elif env == 'arch':
            hint = 'sudo pacman -S lua53'
        else:
            hint = 'install Lua 5.3 compiler (luac5.3)'
        return False, f'Lua 5.3 compiler not found. Install: {hint}', ''

    with tempfile.NamedTemporaryFile(suffix='.luac', delete=False) as tf:
        tmp_out = tf.name
    try:
        result = subprocess.run([cpath, '-s', '-o', tmp_out, src_path], capture_output=True, timeout=30)
        if result.returncode != 0:
            err = result.stderr.decode('utf-8', errors='replace')
            return False, f'luac error: {err.strip()[:200]}', cpath

        with open(tmp_out, 'rb') as f:
            std_bytes = f.read()
        if std_bytes[:4] != b'\x1bLua' or std_bytes[4] != 0x53:
            return False, 'luac did not produce valid Lua 5.3 bytecode', cpath
        if orig_source_name:
            std_bytes = _patch_source_name_std(std_bytes, orig_source_name)
        t24_bytes = _rebuild_std_to_t24(std_bytes)
        if not t24_bytes:
            return False, 'T24 rebuild failed', cpath
        with open(out_path, 'wb') as f:
            f.write(t24_bytes)
        return True, '', cpath
    finally:
        if os.path.exists(tmp_out):
            os.unlink(tmp_out)

def safe_optimize_lua(src):
    try:
        src = re.sub(r'--\[\[.*?\]\]', '', src, flags=re.S)
        src = re.sub(r'--[^\n]*', '', src)
        src = re.sub(r'[ \t]+$', '', src, flags=re.M)
        src = re.sub(r'\n\s*\n+', '\n', src)
        return src.strip()
    except Exception:
        return src

def _compile_with_optimizer(in_path, out_path, orig_sname=None):
    try:
        with open(in_path, 'r', encoding='utf-8') as f:
            original_src = f.read()
        optimized_src = safe_optimize_lua(original_src)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.lua', mode='w', encoding='utf-8')
        tmp.write(optimized_src)
        tmp.close()
        ok, err, tool = compile_file(tmp.name, out_path, orig_source_name=orig_sname)
        try:
            os.unlink(tmp.name)
        except:
            pass
        return ok, err, tool
    except Exception as e:
        return False, str(e), "optimizer"

# ============================================================
# LUA MENU - COMPLETE
# ============================================================

def lua_xor_decrypt(data: bytes, key: bytes) -> bytes:
    if not data:
        return data
    out = bytearray(len(data))
    key_len = len(key)
    for i, b in enumerate(data):
        out[i] = b ^ key[i % key_len]
    return bytes(out)

def lua_try_all_keys(data: bytes) -> tuple:
    best_key = None
    best_key_name = ""
    best_score = 0
    for name, key in ALL_LUA_KEYS.items():
        decrypted = lua_xor_decrypt(data, key)
        printable = sum(1 for b in decrypted[:256] if 32 <= b < 127 or b in (9, 10, 13))
        score = printable / min(len(decrypted), 256)
        if score > best_score:
            best_score = score
            best_key = key
            best_key_name = name
    return best_key, best_key_name, best_score

def is_lua_bytecode(data: bytes) -> bool:
    return len(data) >= 4 and data[:4] == b'\x1bLua'

def is_plain_lua(data: bytes) -> bool:
    if is_lua_bytecode(data):
        return False
    if len(data) < 10:
        return False
    try:
        text = data[:500].decode('utf-8', errors='ignore')
        lua_keywords = ['function', 'local', 'return', 'if', 'then', 'end', 'for', 'while', 'do', 'else', 'elseif']
        keyword_count = sum(1 for kw in lua_keywords if kw in text.lower())
        if keyword_count >= 2:
            return True
    except:
        pass
    printable = sum(1 for b in data[:500] if 32 <= b < 127 or b in (9, 10, 13))
    ratio = printable / min(len(data), 500)
    return ratio > 0.7

def decompile_lua_with_unluac(data: bytes, output_file: str, key: bytes = None) -> tuple:
    jar = get_unluac_jar()
    if not jar:
        return False, "unluac.jar not found"
    
    java = shutil.which("java")
    if not java:
        return False, "Java not found"
    
    if key:
        data = lua_xor_decrypt(data, key)
    
    if len(data) > 5 and data[5] == 0x01:
        patched = bytearray(data)
        patched[5] = 0x00
        if len(patched) > 8 and patched[8] == 0x04:
            patched[8] = 0x08
        data = bytes(patched)
    
    with tempfile.NamedTemporaryFile(suffix=".luac", delete=False) as tmp:
        tmp_path = tmp.name
        tmp.write(data)
    
    try:
        cmd = [java, "-jar", jar, tmp_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            return True, "Decompiled successfully"
        else:
            error = result.stderr or "Unknown error"
            return False, f"unluac error: {error}"
    except Exception as e:
        return False, f"Error: {e}"
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def get_unluac_jar() -> Optional[str]:
    locations = [
        "./unluac.jar",
        "./tools/unluac.jar",
        "./unluac/unluac.jar",
        os.path.expanduser("~/unluac.jar"),
        os.path.expanduser("~/tools/unluac.jar"),
        os.path.join(TEMP_DIR, "unluac_patched.jar"),
    ]
    for loc in locations:
        if os.path.isfile(loc):
            return loc
    return None

def decompile_lua_file(filepath: str, output_file: str = None) -> dict:
    result = {'success': False, 'message': '', 'output_file': output_file, 'strings': []}
    console.print(f"\n[bold cyan]📁 Processing Lua: {filepath}[/bold cyan]")
    
    if not os.path.isfile(filepath):
        result['message'] = f"File not found: {filepath}"
        console.print(f"[bold red]❌ {result['message']}[/bold red]")
        return result
    
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        console.print(f"[bold green]✅ Size: {len(data):,} bytes[/bold green]")
    except Exception as e:
        result['message'] = f"Failed to read: {e}"
        console.print(f"[bold red]❌ {result['message']}[/bold red]")
        return result
    
    if is_plain_lua(data):
        console.print(f"[bold yellow]ℹ️ This is a plain Lua source file[/bold yellow]")
        if not output_file:
            output_file = filepath + ".copy"
        try:
            text = data.decode('utf-8', errors='replace')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            result['success'] = True
            result['message'] = f"Copied plain Lua source to {output_file}"
            console.print(f"[bold green]✅ {result['message']}[/bold green]")
            return result
        except:
            result['message'] = "Could not read as plain text"
            console.print(f"[bold red]❌ {result['message']}[/bold red]")
            return result
    
    key, key_name, score = lua_try_all_keys(data)
    console.print(f"[bold green]✅ Using key: {key_name} (score: {score:.2f})[/bold green]")
    
    if not output_file:
        stem = os.path.splitext(filepath)[0]
        output_file = f"{stem}_decompiled.lua"
    
    result['output_file'] = output_file
    
    console.print(f"[bold cyan]🔧 Decompiling with unluac...[/bold cyan]")
    success, msg = decompile_lua_with_unluac(data, output_file, key)
    
    if success:
        result['success'] = True
        result['message'] = f"Decompiled successfully to {output_file}"
        console.print(f"[bold green]✅ {result['message']}[/bold green]")
        return result
    
    console.print(f"[bold yellow]⚠️ unluac failed: {msg}[/bold yellow]")
    console.print(f"[bold cyan]🔧 Extracting strings...[/bold cyan]")
    
    strings = extract_lua_strings(data, key)
    result['strings'] = strings
    
    if strings:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"-- Decompiled from: {filepath}\n")
            f.write(f"-- Key used: {key_name}\n")
            f.write(f"-- Total strings: {len(strings)}\n\n")
            for i, s in enumerate(strings, 1):
                f.write(f"-- [{s['type']}] {s['text']}\n")
        
        result['success'] = True
        result['message'] = f"Extracted {len(strings)} strings to {output_file}"
        console.print(f"[bold green]✅ {result['message']}[/bold green]")
    else:
        result['message'] = "No strings could be extracted"
        console.print(f"[bold red]❌ {result['message']}[/bold red]")
    
    return result

def extract_lua_strings(data: bytes, key: bytes = None) -> List[Dict]:
    strings = []
    
    if key is None:
        key, key_name, score = lua_try_all_keys(data)
    else:
        key_name = "User Provided"
        score = 1.0
    
    if not is_lua_bytecode(data):
        decrypted = lua_xor_decrypt(data, key)
    else:
        decrypted = data
    
    i = 0
    n = len(decrypted)
    while i < n:
        b = decrypted[i]
        if b in (0x04, 0x14):
            if i + 1 < n:
                size = decrypted[i + 1]
                payload_len = size - 1
                if payload_len > 0 and (i + 2 + payload_len) <= n:
                    encrypted = decrypted[i + 2: i + 2 + payload_len]
                    decrypted_str = lua_xor_decrypt(encrypted, key)
                    try:
                        text = decrypted_str.decode('utf-8', errors='replace')
                        clean = ''.join(c if 32 <= ord(c) < 127 or c in '\n\t\r' else '?' for c in text)
                        if len(clean.strip()) > 1:
                            strings.append({
                                'offset': i,
                                'type': 'LSTRING' if b == 0x14 else 'STRING',
                                'size': size,
                                'text': clean,
                                'hex': decrypted_str.hex()
                            })
                    except:
                        pass
                    i += 2 + payload_len
                    continue
        i += 1
    
    return strings

def compile_lua_to_gfp(lua_file: str, output_file: str = None, key: bytes = None) -> tuple:
    if not key:
        key = DEFAULT_LUA_KEY
    
    if not output_file:
        output_file = os.path.splitext(lua_file)[0] + "_compiled.luac"
    
    luac = shutil.which("luac5.3") or shutil.which("luac")
    if not luac:
        return False, "luac5.3 not found. Install: pkg install lua53"
    
    try:
        with tempfile.NamedTemporaryFile(suffix=".luac", delete=False) as tmp:
            tmp_path = tmp.name
        
        cmd = [luac, "-o", tmp_path, lua_file]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return False, f"Compilation error: {result.stderr}"
        
        with open(tmp_path, 'rb') as f:
            bytecode = f.read()
        
        os.unlink(tmp_path)
        
        patched = bytearray(bytecode)
        if len(patched) > 5 and patched[5] == 0x00:
            patched[5] = 0x01
        if len(patched) > 8 and patched[8] == 0x08:
            patched[8] = 0x04
        
        with open(output_file, 'wb') as f:
            f.write(bytes(patched))
        
        return True, f"Compiled successfully to {output_file}"
        
    except Exception as e:
        return False, f"Error: {e}"

def batch_decompile_lua(directory: str, output_dir: str = None) -> Dict:
    result = {'success': 0, 'failed': 0, 'total': 0, 'output_dir': output_dir}
    
    input_dir = Path(directory)
    if not input_dir.exists():
        console.print(f"[bold red]❌ Directory not found: {directory}[/bold red]")
        return result
    
    if not output_dir:
        output_dir = input_dir / "decompiled_output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(input_dir.glob("*.luac")) + list(input_dir.glob("*.lua"))
    
    if not files:
        console.print(f"[bold yellow]⚠️ No .luac or .lua files found[/bold yellow]")
        return result
    
    result['total'] = len(files)
    console.print(f"[bold green]📁 Found {len(files)} files[/bold green]")
    
    for i, filepath in enumerate(files, 1):
        console.print(f"\n[bold cyan][{i}/{len(files)}][/bold cyan]")
        output_file = output_dir / f"{filepath.stem}_decompiled.lua"
        decompile_result = decompile_lua_file(str(filepath), str(output_file))
        if decompile_result['success']:
            result['success'] += 1
        else:
            result['failed'] += 1
    
    console.print(f"\n[bold green]✅ Processed {result['success']}/{result['total']} files successfully[/bold green]")
    return result

def batch_compile_lua(directory: str, output_dir: str = None) -> Dict:
    result = {'success': 0, 'failed': 0, 'total': 0, 'output_dir': output_dir}
    
    input_dir = Path(directory)
    if not input_dir.exists():
        console.print(f"[bold red]❌ Directory not found: {directory}[/bold red]")
        return result
    
    if not output_dir:
        output_dir = input_dir / "compiled_output"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(input_dir.glob("*.lua"))
    
    if not files:
        console.print(f"[bold yellow]⚠️ No .lua files found[/bold yellow]")
        return result
    
    result['total'] = len(files)
    console.print(f"[bold green]📁 Found {len(files)} files[/bold green]")
    
    for i, filepath in enumerate(files, 1):
        console.print(f"\n[bold cyan][{i}/{len(files)}][/bold cyan]")
        output_file = output_dir / f"{filepath.stem}_compiled.luac"
        success, msg = compile_lua_to_gfp(str(filepath), str(output_file))
        if success:
            result['success'] += 1
            console.print(f"[bold green]✅ {msg}[/bold green]")
        else:
            result['failed'] += 1
            console.print(f"[bold red]❌ {msg}[/bold red]")
    
    console.print(f"\n[bold green]✅ Processed {result['success']}/{result['total']} files successfully[/bold green]")
    return result

def lua_menu():
    while True:
        clear_screen()
        if _auth_data:
            show_banner(_auth_data)
        else:
            show_banner(None)
        console.print(f"""
[bold cyan]╔══════════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║[/bold cyan]  [bold magenta]🔥 LUA DECOMPILER & COMPILER[/bold magenta]                 [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold yellow]For Game for Peace / PUBG / BGMI[/bold yellow]                [bold cyan]║[/bold cyan]
[bold cyan]║[/bold cyan]  [bold green]⚔️ Yukioh Ōkami & @Yukira_12[/bold green]                     [bold cyan]║[/bold cyan]
[bold cyan]╚══════════════════════════════════════════════════════════╝[/bold cyan]

[bold cyan]1.[/bold cyan] Decompile Lua File
[bold cyan]2.[/bold cyan] Compile Lua to GFP
[bold cyan]3.[/bold cyan] Batch Decompile (.luac files)
[bold cyan]4.[/bold cyan] Batch Compile (.lua files)
[bold cyan]5.[/bold cyan] Show XOR Keys
[bold cyan]0.[/bold cyan] Back to Main Menu
""")
        choice = safe_input('[bold yellow]Enter choice: [/bold yellow]').strip()
        if choice == '0':
            break
        elif choice == '1':
            filepath = safe_input('[bold cyan]📁 Enter .luac file path: [/bold cyan]').strip()
            if not filepath or not os.path.isfile(filepath):
                console.print('[bold red]❌ File not found[/bold red]')
                continue
            output = safe_input('[bold cyan]📁 Output file (Enter for auto): [/bold cyan]').strip()
            decompile_lua_file(filepath, output or None)
            safe_input('\nPress Enter to continue...')
        elif choice == '2':
            filepath = safe_input('[bold cyan]📁 Enter .lua file path: [/bold cyan]').strip()
            if not filepath or not os.path.isfile(filepath):
                console.print('[bold red]❌ File not found[/bold red]')
                continue
            output = safe_input('[bold cyan]📁 Output file (Enter for auto): [/bold cyan]').strip()
            success, msg = compile_lua_to_gfp(filepath, output or None)
            if success:
                console.print(f'[bold green]✅ {msg}[/bold green]')
            else:
                console.print(f'[bold red]❌ {msg}[/bold red]')
            safe_input('\nPress Enter to continue...')
        elif choice == '3':
            directory = safe_input('[bold cyan]📁 Enter directory with .luac files: [/bold cyan]').strip()
            if not directory or not os.path.isdir(directory):
                console.print('[bold red]❌ Directory not found[/bold red]')
                continue
            output = safe_input('[bold cyan]📁 Output directory (Enter for auto): [/bold cyan]').strip()
            batch_decompile_lua(directory, output or None)
            safe_input('\nPress Enter to continue...')
        elif choice == '4':
            directory = safe_input('[bold cyan]📁 Enter directory with .lua files: [/bold cyan]').strip()
            if not directory or not os.path.isdir(directory):
                console.print('[bold red]❌ Directory not found[/bold red]')
                continue
            output = safe_input('[bold cyan]📁 Output directory (Enter for auto): [/bold cyan]').strip()
            batch_compile_lua(directory, output or None)
            safe_input('\nPress Enter to continue...')
        elif choice == '5':
            console.print(f"""
[bold green]🔑 64-bit Key (Recommended):[/bold green]
  {GFP_XOR_KEY_64BIT.hex().upper()}

[bold yellow]🔑 32-bit Key:[/bold yellow]
  {GFP_XOR_KEY_32BIT.hex().upper()}

[bold red]🔑 Old Key (PATCHED):[/bold red]
  {OLD_XOR_KEY.hex().upper()}
""")
            safe_input('Press Enter to continue...')
        else:
            console.print('[bold red]❌ Invalid choice[/bold red]')
            time.sleep(1)

def safe_input(prompt: str = '') -> str:
    try:
        return input(prompt)
    except (EOFError, RuntimeError):
        try:
            if sys.platform != 'win32':
                with open('/dev/tty', 'r') as tty:
                    sys.stderr.write(prompt)
                    sys.stderr.flush()
                    return tty.readline().rstrip('\n')
            else:
                with open('CON', 'r') as con:
                    sys.stderr.write(prompt)
                    sys.stderr.flush()
                    return con.readline().rstrip('\r\n')
        except Exception:
            return ''
    except Exception:
        return ''

# ============================================================
# UI HELPERS - COMPLETE
# ============================================================

def progress_animation(message, duration=0.8):
    steps = 20
    with Progress(SpinnerColumn(), TextColumn(f"[{ACCENT}]{message}"), BarColumn(bar_width=40), transient=True) as progress:
        task = progress.add_task("", total=steps)
        for i in range(steps):
            time.sleep(duration / steps)
            progress.update(task, advance=1)

def section_header(title: str):
    console.print()
    console.print(Rule(f"[bold {GOLD}] // {title} // [/]", style=f"bold {ACCENT}"))
    console.print()

def success(msg): console.print(f"[bold {TEAL}]  ✔  {msg}[/]")
def warn(msg): console.print(f"[bold {GOLD}]  ⚠  {msg}[/]")
def error(msg): console.print(f"[bold {RED}]  ✘  {msg}[/]")
def info(msg): console.print(f"[bold {ACCENT}]  ➤  {msg}[/]")

def fmt_size(n: int) -> str:
    if n < 1024: return f"{n}B"
    elif n < 1024**2: return f"{n/1024:.1f}KB"
    elif n < 1024**3: return f"{n/1024**2:.1f}MB"
    else: return f"{n/1024**3:.2f}GB"

def show_how_to_use():
    clear_screen()
    if _auth_data:
        show_banner(_auth_data)
    else:
        show_banner(None)
    section_header("HOW TO USE")
    guide = f"""
[bold yellow]📁 FOLDER STRUCTURE[/bold yellow]
[bold cyan]Yukioh_Ōkami_v4.5/[/bold cyan]
├── 📁 [cyan]ZSDIC[/cyan]/              → For ZSDIC PAK files
│   ├── 📁 [green]INPUT[/green]/          → [white]Place .pak files here[/white]
│   ├── 📁 [yellow]UNPACKED[/yellow]/       → [white]Extracted files go here[/white]
│   ├── 📁 [yellow]EDITED[/yellow]/         → [white]Place modified files here[/white]
│   ├── 📁 [red]REPACKED[/red]/           → [white]Repacked .pak output[/white]
│   └── 📁 [magenta]COMPARE_DAT[/magenta]/    → [white]Compare & extract[/white]
├── 📁 [cyan]MINI_OBB[/cyan]/            → Same structure as ZSDIC
├── 📁 [cyan]OD_PAK[/cyan]/              → Same structure as ZSDIC
├── 📁 [cyan]GAMEPATCH[/cyan]/           → Same structure as ZSDIC
├── 📁 [cyan]ANTIRESET[/cyan]/           → AntiReset OBB Tool
├── 📁 [cyan]120_FPS[/cyan]/             → 120 FPS Unlock Tool
├── 📁 [cyan]ENC_DEC[/cyan]/             → Encrypt/Decrypt OBB
├── 📁 [cyan]SPLIT_MERGE[/cyan]/         → Split/Merge Files
└── 📁 [cyan]AUTO_CONFIG[/cyan]/         → Auto Configuration Presets

[bold yellow]1. UNPACK PAK[/bold yellow]
   - Place .pak in [cyan]ZSDIC/INPUT/[/cyan]
   - Select option 1 → Choose PAK → Unpack

[bold yellow]2. REPACK PAK[/bold yellow]
   - Place modified files in [cyan]ZSDIC/EDITED/[/cyan]
   - Select option 2 → Choose PAK → 4 repack modes

[bold yellow]3. AUTO CONFIGURATION[/bold yellow]
   - Headshot, White Body, No Grass, Master Baltic

[bold yellow]4. 120 FPS UNLOCK[/bold yellow]
   - Place PAK in [cyan]120_FPS/BGMI/INPUT_PAK/[/cyan]

[bold yellow]5. ANTIRESET OBB[/bold yellow]
   - Place original OBB in [cyan]ANTIRESET/ORG_OBB/[/cyan]
   - Place modded OBB in [cyan]ANTIRESET/MODDED_OBB/[/cyan]
"""
    console.print(Panel(guide, border_style=ACCENT, title="[bold]DOCUMENTATION[/bold]"))
    console.print(f"\n[dim]Press Enter to return...[/dim]")
    input()

# ============================================================
# MAIN MENU - v4.5 KEPT
# ============================================================

def _draw_menu():
    W = 50
    title = "Yukioh Ōkami  //  MAIN MENU  v4.5"
    tp = (W - len(title)) // 2
    console.print(Align.center(f"[bold {ACCENT}]╔{'═'*W}╗[/]"))
    console.print(Align.center(f"[bold {ACCENT}]║[/] {' ' * tp}[bold {GOLD}]{title}[/bold {GOLD}]{' ' * (W - tp - len(title))}[bold {ACCENT}]║[/]"))
    console.print(Align.center(f"[bold {ACCENT}]╠{'─'*W}╣[/]"))
    items = [
        ("1", "ZSDIC Tool", ACCENT),
        ("2", "MINI_OBB Tool", ACCENT),
        ("3", "OD_PAK Tool", ACCENT),
        ("4", "GAMEPATCH Tool", ACCENT),
        ("5", "Auto 120 FPS", ACCENT),
        ("6", "AntiReset OBB Tool", ACCENT),
        ("7", "Auto Configuration", ACCENT),
        ("8", "Split/Merge Files", ACCENT),
        ("9", "Encrypt/Decrypt OBB", ACCENT),
        ("0", "LUA Decompiler/Compiler", ACCENT),
    ]
    
    if _auth_data and _auth_data.get('type') == 'admin':
        items.append(("A", "🔐 Admin HWID Manager", PINK))
        items.append(("R", "📊 Rate Limiter Status", GOLD))
    
    for num, label, lcolor in items:
        console.print(Align.center(f"[bold {ACCENT}]║[/]  [bold {GOLD}][{num}][/bold {GOLD}]  [bold {lcolor}]>>[/bold {lcolor}]  [white]{label}[/white]{' ' * max(W - len(f'  [{num}]  >>  {label}'), 1)}[bold {ACCENT}]║[/]"))
    console.print(Align.center(f"[bold {ACCENT}]╠{'─'*W}╣[/]"))
    console.print(Align.center(f"[bold {ACCENT}]║[/]  [bold red][X][/bold red]  [bold red]<<[/bold red]  [white]Logout & Exit[/white]{' ' * (W - len('  [X]  <<  Logout & Exit'))}[bold {ACCENT}]║[/]"))
    console.print(Align.center(f"[bold {ACCENT}]╚{'═'*W}╝[/]"))

def startup_animation():
    clear_screen()
    art_lines = _DEFAULT_BANNER_ART
    steps = [
        ("Initializing Yukioh Ōkami Engine v4.5", 0.5),
        ("Loading PAK Modules", 0.4),
        ("Connecting to GitHub Key System", 0.6),
        ("Verifying License with HWID", 0.5),
    ]
    console.print()
    for line in art_lines:
        console.print(Align.center(f"[bold {ACCENT}]{line}[/]"))
    console.print(Align.center(f"[bold {GOLD}]  ━━━  P A K  +  L U A  T O O L  v4.5  ━━━[/]"))
    console.print(Align.center(f"[dim]          Secure HWID Key System  ·  Built by @Yukira_12[/dim]"))
    console.print()
    for msg, dur in steps:
        with Progress(SpinnerColumn(spinner_name="dots", style=f"bold {ACCENT}"), TextColumn(f"[bold {ACCENT}]{msg}[/]"), BarColumn(bar_width=30, style=ACCENT, complete_style=GOLD), TimeElapsedColumn(), transient=True, console=console) as prog:
            task = prog.add_task("", total=20)
            for _ in range(20):
                time.sleep(dur / 20)
                prog.update(task, advance=1)
        console.print(Align.center(f"[bold {TEAL}]  [OK]  {msg}[/]"))
    time.sleep(0.3)
    clear_screen()

# ============================================================
# MAIN FUNCTION - WITH SECURITY CHECKS
# ============================================================

def main():
    # ============================================================
    # 🔐 SECURITY CHECKS AT STARTUP
    # ============================================================
    
    # 1. Anti-debug check
    if anti_debug_check():
        console.print("[red]❌ Security check failed! Exiting...[/red]")
        time.sleep(2)
        sys.exit(1)
    
    # 2. Integrity check (warning only, don't block)
    if not check_code_integrity():
        console.print("[yellow]⚠️ Code integrity warning[/yellow]")
    
    _ensure_base_dirs()
    startup_animation()

    try:
        auth_data = check_auth()
    except KeyboardInterrupt:
        console.print("\n[yellow]Authentication cancelled by user.[/yellow]")
        sys.exit(0)
    if auth_data is None:
        error("Authentication failed. Exiting.")
        sys.exit(1)

    global _auth_data
    _auth_data = auth_data

    if db_client:
        db_client.start_tool_session(tool_name="Yukioh_Ōkami_v4.5", hwid=get_hwid(), authenticated=True)

    if not HAS_PAK_DEPS:
        show_banner(_auth_data, show_menu=False)
        warn(f"PAK dependencies missing: {_PAK_IMPORT_ERROR}")
        warn("PAK tools disabled. Install: pip install pycryptodome zstandard gmalg requests")
        try:
            Prompt.ask(f"\n[dim]Press Enter to continue...[/dim]", default="")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)

    while True:
        show_banner(_auth_data, show_menu=True)
        try:
            choice = Prompt.ask(f"[bold {GOLD}]Select option[/bold {GOLD}]").strip().upper()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == '1':
            show_type_menu('ZSDIC')
        elif choice == '2':
            show_type_menu('MINI_OBB')
        elif choice == '3':
            show_type_menu('OD_PAK')
        elif choice == '4':
            show_type_menu('GAMEPATCH')
        elif choice == '5':
            handle_auto_120fps()
        elif choice == '6':
            handle_antireset_tool()
        elif choice == '7':
            auto_configuration_menu()
        elif choice == '8':
            file_split_merge_menu()
        elif choice == '9':
            handle_encrypt_pak_tool()
        elif choice == '0':
            lua_menu()
        elif choice == 'A':
            if _auth_data and _auth_data.get('type') == 'admin':
                admin_hwid_manager()
            else:
                console.print('[red]❌ Admin access required![/red]')
                console.print(f'[yellow]Contact {SUPPORT_CONTACT} for admin access.[/yellow]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
        elif choice == 'R':
            if _auth_data and _auth_data.get('type') == 'admin':
                show_rate_limiter_status()
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
            else:
                console.print('[red]❌ Admin access required![/red]')
                Prompt.ask('\n[white]Press Enter...[/white]', default='')
        elif choice == 'X':
            clear_screen()
            console.print()
            for line in _get_banner_art(_auth_data):
                console.print(Align.center(f"[bold {ACCENT}]{line}[/]"))
            console.print()
            console.print(Align.center(f"[bold green]  [OK]  Logout successful. Goodbye![/bold green]"))
            console.print(Align.center(f"[dim]  Developed by @Yukira_12[/dim]"))
            console.print()
            with Progress(transient=True) as progress:
                task = progress.add_task("[cyan]Exiting...", total=100)
                for i in range(101):
                    time.sleep(0.008)
                    progress.update(task, advance=1)
            clear_screen()
            sys.exit(0)
        else:
            warn("Invalid option. Enter 1-9, 0 for LUA, A for Admin, or X to exit.")

        try:
            Prompt.ask(f"\n[dim]Press Enter to continue...[/dim]", default="")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print('\n[bold #FFFF00]⚠ Interrupted. Exiting...[/bold #FFFF00]')
        sys.exit(0)
    except Exception as e:
        console.print(f'[bold #FF0055]💥 ERROR:[/bold #FF0055] {escape(str(e))}')
        import traceback
        traceback.print_exc()
        safe_input('\nPress Enter to exit...')
        sys.exit(1)