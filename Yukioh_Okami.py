#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# Yukioh Ōkami TOOL PAK + LUA Edition (Online Tool ENABLED)
# PAK Unpack -> LUA Decrypt -> Edit -> LUA Compile -> PAK Repack
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
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePath, Path
from datetime import datetime
from threading import Thread
from queue import Queue

# ============================================================
# INTERNAL CONSTANTS (formerly const.py)
# ============================================================

ZUC_KEY = bytes.fromhex('01010101010101010101010101010101')
ZUC_IV = bytes.fromhex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

RSA_MOD_1 = bytes.fromhex(
    'CBE8B9F2504050EF9831B719E9A6249A6D238505ADE909BDE78C180DED6072A0C3347B8AF4780E1F212D952D82D4BF7F233C1ECA499E1F9D9A85B4FAD759F54BABC1666C5DE411EA9E4B2374425DD6C6F54333BBC8F2610FE6063E4D0D6C21A671A8F7C3740555E5DC06D4E1691C456DB4116C0C012BF7B206E8311AAAEC689952BF804EF638F09D5822B4117B114208F14DEB459E80CB770E5B0D7978E21F5E6CED4999D3583108221A7AB28B960277ADB5690A332784019D9C195BE4EA9EA0A09459010F236465DE0D59C3EF7324E954E1118D93EE19F299760C2CDB963CE87973EA5ECC9BBE81C27D4C7C8572AC07E9BCEAC9BD72AB7A56A3C0AD736ABCE4')
RSA_MOD_2 = bytes.fromhex(
    '7F58E8A39A4DA4E87357DDD650EAA16D3B5CE95B213D1030A662566444796A78A84AE9AC3DBFFDE7F41094896696835DAF13B89E6EC2B84963B1B1BAF7151DA245C3FBFAE2A6AE18B2684D03F9229DE2C91440F2A3A3BCDE1E5680C16722A88039C73560D5D43F4B6562C2EEA5B1D926D86B51108A2643C70FB74D6442CE3A08339B8FD8F660AE88129B7AB8C46F2FA58124485CCCB1E987B05A6DA65A01858ED3F89905449AE42BB07290FCB9994BF22E26610BCABB9804783A3B9587917F3D97316EDDA15C5E13F79066407B55A93B291B68A4AC42A98D6E35FED84B14A792D154E62028DDAD20FC301951E5924BE9AD62FB719DD94CC30CAB871BEC4377A8')

SIMPLE1_DECRYPT_KEY = 0x79

SIMPLE2_DECRYPT_KEY = bytes.fromhex('E55B4ED1')
SIMPLE2_BLOCK_SIZE = 16

SM4_SECRET_4 = '09ea7a1d9e6528b72b48'
SM4_SECRET_2 = '%*.059;@DFLNPVXZ`bdj'

SM4_SECRET_NEW = [
     'aT0cL1yN4pT3sZ7eM2vY',
     'dB6lB3vE0eZ8wM8rI0aC',
     'gD4jQ2aL3bS3lC3xT0iW',
     'hM1pH9iY8wM9hT4lN5uJ',
     'iQ0eM0mJ7uT0kV6kL5zY',
     'iT2vS0cS6yT6cZ1sE1lO',
     'jU5bH7lQ0fM9hK2kI0oF',
     'kG6bC8jK0fL0dE4sH4mL',
     'qC4jS5bZ6fL5xE6nD4zA',
     'rT6aQ6oZ1yM0gO5tO1aN',
     'tP7sP7nI9rA2vQ4cV5yQ',
     'uQ3cO2dX7xY4xU7gH7iS',
     'uV6fU8fC9zN3mP5dH8mN',
     'xT1cJ6dL5wC0kK1rB4dK',
     'xU1yQ8wE9zY3gZ3bT5aE',
     'xG2qW5lP7lV2iN5fN5pG',
     'gW1fR0jK6wQ4oN0oK1kZ',
     'aJ4pV7iZ7pU4wP2aC2cZ',
     'cX6jT3cM2oT3vK0kJ1qN',
     'Q0hVTKey$as*1ZFlQCiA',
     'eb691efea914241317a8',
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

# ============================================================
# INTERNAL SM4 IMPLEMENTATION (formerly sm4.py)
# ============================================================

from typing import List
from gmalg.base import BlockCipher
from gmalg.errors import *
from gmalg.utils import ROL32

# tencent is using custom S-BOX, FK and CK

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

_FK = [
    0x46970E9C, 0x4BC0685E, 0x59056186, 0xBCA2491E
]

_CK = [
    0x000EB92B, 0x3A0AE783, 0x9E3B5C67, 0xADDBDABF, 0x7B7484CB, 0x49156C63, 0xC79AB5E7, 0x79EC9CFF,
    0x1725BEAB, 0x2FB89CA3, 0x24808AD7, 0xDDD28B1F, 0x4740DA4B, 0xBBC3EA73, 0x247B30E7, 0x91BE385F,
    0x0401248B, 0x45FCD3A3, 0x530B4CE7, 0xC68DD35F, 0xE3D16C2B, 0x4F698C13, 0x6B92C747, 0x769EFB1F,
    0x4C73BE9B, 0xC942B193, 0xAD80D827, 0x372FB33F, 0x13CB6AAB, 0x2BDC0AA3, 0x17A4A247, 0xD5E96CAF
]


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


def _key_expand(key: bytes, rkey: List[int]):
    """Key expansion."""

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


class SM4(BlockCipher):
    """SM4 Algorithm."""

    @classmethod
    def key_length(self) -> int:
        """Get key length in bytes."""
        return 16

    @classmethod
    def block_length(self) -> int:
        """Get block length in bytes."""
        return 16

    def __init__(self, key: bytes) -> None:
        """SM4 Algorithm.

        Args:
            key: 16 bytes key.

        Raises:
            IncorrectLengthError: Incorrect key length.
        """
        if len(key) != self.key_length():
            raise IncorrectLengthError("Key", f"{self.key_length()} bytes", f"{len(key)} bytes")

        self._key: bytes = key
        self._rkey: List[int] = [0] * 32
        _key_expand(self._key, self._rkey)
        self._block_buffer = bytearray()

    def encrypt(self, block: bytes) -> bytes:
        """Encrypt.

        Args:
            block: Plain block to encrypt, must be 16 bytes.

        Returns:
            bytes: 16 bytes cipher block.

        Raises:
            IncorrectLengthError: Incorrect block length.
        """
        if len(block) != self.block_length():
            raise IncorrectLengthError("Block", f"{self.block_length()} bytes", f"{len(block)} bytes")

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
        """Decrypt.

        Args:
            block: cipher block to decrypt, must be 16 bytes.

        Returns:
            bytes: 16 bytes plain block.

        Raises:
            IncorrectLengthError: Incorrect block length.
        """
        if len(block) != self.block_length():
            raise IncorrectLengthError("Block", f"{self.block_length()} bytes", f"{len(block)} bytes")

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
# UTILITIES (keep as fallback)
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
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, MofNCompleteColumn
    from rich import box as rich_box
    from rich.text import Text
    from rich.columns import Columns
    from rich.rule import Rule
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.align import Align
    from rich.layout import Layout
    console = Console()
except ImportError:
    # Fallback if rich not installed
    console = Console() if 'Console' in dir() else None
    class DummyConsole:
        def print(self, *args, **kwargs): print(*args)
        def input(self, *args, **kwargs): return input(*args)
    if console is None:
        console = DummyConsole()

# ============================================================
# PAK DEPENDENCIES CHECK
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

# ============================================================
# Online Tool SYSTEM
# ============================================================

import sys
try:
    ANA_DIZIN = Path(__file__).resolve().parent
except NameError:
    ANA_DIZIN = Path(sys.argv[0]).resolve().parent if sys.argv[0] else Path.cwd()
PAKS_DIR       = ANA_DIZIN / 'PAKS'
UNPACKED_DIR   = ANA_DIZIN / 'unpacked'
REPACKED_DIR   = ANA_DIZIN / 'repacked'
MANIFEST_DIR   = ANA_DIZIN / 'Manifest'

LUA_ORIGINAL_DIR   = ANA_DIZIN / 'LUA_ORIGINAL'
LUA_DECOMPILED_DIR = ANA_DIZIN / 'DECOMPILED'
LUA_EDIT_DIR       = ANA_DIZIN / 'EDIT_LUA'
LUA_COMPILED_DIR   = ANA_DIZIN / 'COMPILED'

AUTH_CONFIG_FILE = ANA_DIZIN / "config.json"
PANEL_URL = "https://codes-bgmi.rf.gd/op/kuro-panel/connect"
GAME_NAME = "BGMI — Battlegrounds Mobile India"

_auth_data = None

def _ensure_base_dirs():
    for d in [ANA_DIZIN, PAKS_DIR, UNPACKED_DIR, REPACKED_DIR, MANIFEST_DIR,
              LUA_ORIGINAL_DIR, LUA_DECOMPILED_DIR, LUA_EDIT_DIR,
              LUA_COMPILED_DIR]:
        d.mkdir(parents=True, exist_ok=True)

def get_hwid() -> str:
    try:
        mac = uuid.getnode()
        if mac != 0xffffffffffff:
            return f"MAC_{mac:012x}"
    except:
        pass
    hwid_file = ANA_DIZIN / ".hwid"
    if hwid_file.exists():
        return hwid_file.read_text().strip()
    else:
        new_hwid = f"RAND_{uuid.uuid4().hex[:16]}"
        hwid_file.write_text(new_hwid)
        return new_hwid

def load_saved_auth() -> dict:
    if AUTH_CONFIG_FILE.exists():
        try:
            with open(AUTH_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_auth(key: str, modname: str, credit: str, expiry: str, token: str):
    data = {
        'key': key,
        'modname': modname,
        'credit': credit,
        'expiry': expiry,
        'token': token,
        'saved_at': datetime.now().isoformat()
    }
    with open(AUTH_CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def clear_saved_auth():
    if AUTH_CONFIG_FILE.exists():
        AUTH_CONFIG_FILE.unlink()

def verify_key_with_panel(user_key: str, serial: str = None) -> dict:
    if not HAS_REQUESTS:
        return {'status': False, 'reason': 'requests module not installed (pip install requests)'}
    if serial is None:
        serial = get_hwid()
    payload = {
        'game': GAME_NAME,
        'user_key': user_key,
        'serial': serial
    }
    try:
        response = requests.post(PANEL_URL, data=payload, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {'status': False, 'reason': f'HTTP {response.status_code}'}
    except requests.exceptions.Timeout:
        return {'status': False, 'reason': 'Connection timeout'}
    except requests.exceptions.ConnectionError:
        return {'status': False, 'reason': 'Cannot reach panel'}
    except Exception as e:
        return {'status': False, 'reason': str(e)}

# ============================================================
# FANCY UI BANNER
# ============================================================

ACCENT = "bright_cyan"
GOLD   = "bright_yellow"
TEAL   = "bright_green"
DIM    = "bright_black"
RED    = "bright_red"

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
                                                                                

                🐺 Yukioh_Ōkami — PUBG/BGMI PAK Modding Tool 🐺
                ═══════════════════════════════════════════════
"""
]

def _get_banner_art(auth_data) -> list:
    if auth_data:
        raw = auth_data.get('banner_art', '')
        if raw:
            lines = raw.split('\n') if isinstance(raw, str) else raw
            if isinstance(lines, list) and len(lines) >= 3:
                return lines
    return _DEFAULT_BANNER_ART

def show_banner(auth_data=None, show_menu=False):
    clear_screen()

    if auth_data is None:
        modname      = "Yukioh Ōkami TOOL"
        credit       = "0"
        expiry       = "N/A"
        status       = "NOT LOGGED IN"
        status_color = "red"
    else:
        modname = auth_data.get('modname', 'Yukioh Ōkami TOOL')
        credit  = auth_data.get('credit', '0')
        expiry  = auth_data.get('expiry', 'N/A')
        status  = "ACTIVE"
        status_color = "green"
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

    console.print(Align.center(f"[bold {GOLD}]  ━━━  P A K  +  L U A  T O O L  ━━━[/]"))
    console.print(Align.center(f"[dim]          Online Tool  ·  Built by @Yukira_12[/dim]"))
    console.print()

    W = 52

    def _pad(label, value):
        plain_len = 2 + len(label) + 1 + len(value)
        return max(W - plain_len - 1, 1)

    def row(label, value, val_color):
        p = _pad(label, value)
        return (
            f"[bold {ACCENT}]║[/]"
            f"  [bold white]{label}[/bold white] "
            f"[bold {val_color}]{value}[/bold {val_color}]"
            f"{' ' * p}"
            f"[bold {ACCENT}]║[/]"
        )

    def row_center(text, color=DIM):
        p_total = W - len(text)
        pl = p_total // 2
        pr = p_total - pl
        return (
            f"[bold {ACCENT}]║[/]"
            f"{' ' * pl}[{color}]{text}[/{color}]{' ' * pr}"
            f"[bold {ACCENT}]║[/]"
        )

    console.print(Align.center(f"[bold {ACCENT}]╔{'═'*W}╗[/]"))
    console.print(Align.center(f"[bold {ACCENT}]╠{'═'*W}╣[/]"))
    console.print(Align.center(row("  [*] STATUS :", status,  status_color))) 
    console.print(Align.center(row("  [-] SERVER :", modname, GOLD))) 
    console.print(Align.center(row("  [-] CREDIT :", credit,  "bright_green"))) 
    console.print(Align.center(row("  [-] EXPIRY :", expiry,  ACCENT))) 
    console.print(Align.center(f"[bold {ACCENT}]╠{'═'*W}╣[/]"))
    console.print(Align.center(row_center("UNPACK  ·  REPACK  ·  COMPILE  ·   DECOMPILE")))
    console.print(Align.center(f"[bold {ACCENT}]╚{'═'*W}╝[/]"))
    console.print()

    if show_menu:
        _draw_menu()

def show_login_screen():
    clear_screen()

    console.print()
    for line in _DEFAULT_BANNER_ART:
        console.print(Align.center(f"[bold {GOLD}]{line}[/]"))
    console.print(Align.center(f"[bold {ACCENT}]  ━━━  P A K  +  L U A  TOOL  ━━━[/]"))
    console.print(Align.center(f"[dim]          Online Tool  ·  Built by @Yukira_12[/dim]"))
    console.print()

    W = 52
    console.print(Align.center(f"[bold {GOLD}]╔{'═'*W}╗[/]"))
    console.print(Align.center(f"[bold {GOLD}]╠{'═'*W}╣[/]"))
    title_pad = (W - len("[ LICENSE KEY REQUIRED ]")) // 2
    console.print(Align.center(
        f"[bold {GOLD}]║[/]"
        f"{' ' * title_pad}[bold red][ LICENSE KEY REQUIRED ][/bold red]"
        f"{' ' * (W - title_pad - len('[ LICENSE KEY REQUIRED ]'))}"
        f"[bold {GOLD}]║[/]"
    ))
    console.print(Align.center(f"[bold {GOLD}]╠{'═'*W}╣[/]"))
    instr = "Enter your key below to continue"
    ip = (W - len(instr)) // 2
    console.print(Align.center(
        f"[bold {GOLD}]║[/]"
        f"{' ' * ip}[cyan]{instr}[/cyan]"
        f"{' ' * (W - ip - len(instr))}"
        f"[bold {GOLD}]║[/]"
    ))
    console.print(Align.center(f"[bold {GOLD}]╚{'═'*W}╝[/]"))
    console.print()

def check_auth() -> dict:
    global _auth_data
    
    if _auth_data is not None:
        return _auth_data
    
    saved = load_saved_auth()
    saved_key = saved.get('key')
    
    if saved_key:
        console.print("[dim]Checking saved key...[/dim]")
        result = verify_key_with_panel(saved_key)
        
        if result.get('status') == True:
            data = result.get('data', {})
            expiry_str = data.get('EXP', '')
            if expiry_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_str.replace(' ', 'T'))
                    if expiry_date < datetime.now():
                        console.print("[yellow]Saved key expired![/yellow]")
                        clear_saved_auth()
                        saved_key = None
                except:
                    pass
            
            if saved_key:
                mod_status = data.get('mod_status', 'on')
                if mod_status == 'off':
                    console.print("[red]Tool disabled by admin![/red]")
                    sys.exit(1)
                
                _auth_data = {
                    'key': saved_key,
                    'modname': data.get('modname', 'Yukioh Ōkami TOOL'),
                    'credit': data.get('credit', '0'),
                    'expiry': expiry_str,
                    'token': data.get('token', ''),
                    'slot': data.get('SLOT', ''),
                    'rng': data.get('rng', ''),
                    'banner_art': data.get('banner_art', ''),
                    'banner_color': data.get('banner_color', ''),
                }
                return _auth_data
        else:
            console.print("[yellow]Saved key invalid[/yellow]")
            clear_saved_auth()
    
    show_login_screen()
    
    while True:
        user_key = Prompt.ask("[bold cyan]Enter your key[/bold cyan]").strip()
        if not user_key:
            console.print("[red]Key cannot be empty![/red]")
            continue
        
        with Progress(SpinnerColumn(), TextColumn("[cyan]Verifying...[/cyan]"), transient=True) as prog:
            prog.add_task("", total=None)
            result = verify_key_with_panel(user_key)
        
        if result.get('status') == True:
            data = result.get('data', {})
            
            mod_status = data.get('mod_status', 'on')
            if mod_status == 'off':
                console.print("[red]Tool disabled by admin![/red]")
                sys.exit(1)
            
            expiry_str = data.get('EXP', '')
            if expiry_str:
                try:
                    expiry_date = datetime.fromisoformat(expiry_str.replace(' ', 'T'))
                    if expiry_date < datetime.now():
                        console.print("[red]Key expired![/red]")
                        continue
                except:
                    pass
            
            modname = data.get('modname', 'Yukioh Ōkami TOOL')
            credit = data.get('credit', '0')
            token = data.get('token', '')
            
            save_auth(user_key, modname, credit, expiry_str, token)
            
            _auth_data = {
                'key': user_key,
                'modname': modname,
                'credit': credit,
                'expiry': expiry_str,
                'token': token,
                'slot': data.get('SLOT', ''),
                'rng': data.get('rng', ''),
                'banner_art': data.get('banner_art', ''),
                'banner_color': data.get('banner_color', ''),
            }
            
            console.print(f"[bold {TEAL}]  [OK]  Login successful![/bold {TEAL}]")
            time.sleep(0.8)
            return _auth_data
        else:
            reason = result.get('reason', 'KEY GALAT H!!')
            console.print(f"[red]Login failed: {reason}[/red]")

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

    def u1(self, move_cursor=True): return self.unpack('B',   move_cursor=move_cursor)[0]
    def u4(self, move_cursor=True): return self.unpack('<I',  move_cursor=move_cursor)[0]
    def u8(self, move_cursor=True): return self.unpack('<Q',  move_cursor=move_cursor)[0]
    def i1(self, move_cursor=True): return self.unpack('b',   move_cursor=move_cursor)[0]
    def i4(self, move_cursor=True): return self.unpack('<i',  move_cursor=move_cursor)[0]
    def i8(self, move_cursor=True): return self.unpack('<q',  move_cursor=move_cursor)[0]
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

    def u1(self, v): self.pack('B',  v)
    def u4(self, v): self.pack('<I', v)
    def u8(self, v): self.pack('<Q', v)
    def i1(self, v): self.pack('b',  v)
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
# PAK CLASSES (Core logic)
# ============================================================

if HAS_PAK_DEPS:
    class BlockLogger:
        def __init__(self, filename):
            self.filename = filename
            self.blocks = []
            self.original_total_size = 0
            self.compressed_total_size = 0

        def add_block(self, block_index, original_size, compressed_size,
                      compression_method, level, success_flag, block_offset, block_end):
            self.blocks.append({
                'index': block_index, 'original_size': original_size,
                'compressed_size': compressed_size, 'compression_method': compression_method,
                'level': level, 'success': success_flag,
                'block_offset': block_offset, 'block_end': block_end,
                'slot_size': block_end - block_offset,
            })

        def print_summary(self):
            t = Table(title=f"Blocks: {Path(self.filename).name}", show_header=True,
                      header_style=f"bold {ACCENT}", box=rich_box.SIMPLE)
            t.add_column("Block", style="cyan", width=6)
            t.add_column("Original", justify="right", width=12)
            t.add_column("Compressed", justify="right", width=12)
            t.add_column("Slot", justify="right", width=12)
            t.add_column("Free", justify="right", width=10)
            t.add_column("Method", width=14)
            t.add_column("OK", width=4)
            for b in self.blocks:
                free = b['slot_size'] - b['compressed_size']
                free_str = (f"[green]+{free:,}[/green]" if free >= 100
                            else f"[yellow]+{free:,}[/yellow]" if free >= 0
                            else f"[red]{free:,}[/red]")
                t.add_row(str(b['index']), f"{b['original_size']:,}",
                          f"{b['compressed_size']:,}", f"{b['slot_size']:,}",
                          free_str, b['compression_method'][:13],
                          "YES" if b['success'] else "NO")
            console.print(t)

    class RepackLogger:
        def __init__(self):
            self.successes = []
            self.failures  = []

        def log_success(self, file_name, compressed_size, slot_size):
            self.successes.append({'file': file_name, 'compressed': compressed_size, 'slot': slot_size})

        def log_failure(self, file_name, reason, details):
            self.failures.append({'file': file_name, 'reason': reason, 'details': details})

        def print_summary(self):
            if self.successes:
                t = Table(title="Successful Repacks", show_header=True,
                          header_style="bold green", box=rich_box.SIMPLE)
                t.add_column("File", style="cyan")
                t.add_column("Compressed", justify="right")
                t.add_column("Slot", justify="right")
                for s in self.successes:
                    t.add_row(Path(s['file']).name, f"{s['compressed']:,}", f"{s['slot']:,}")
                console.print(t)
            if self.failures:
                t = Table(title="Failed Repacks", show_header=True,
                          header_style="bold red", box=rich_box.SIMPLE)
                t.add_column("File", style="cyan")
                t.add_column("Reason")
                t.add_column("Details", style="dim")
                for f in self.failures:
                    dstr = ", ".join(f"{k}:{v}" for k, v in f['details'].items())
                    t.add_row(Path(f['file']).name, f['reason'], dstr or "-")
                console.print(t)
            total = len(self.successes) + len(self.failures)
            rate = (len(self.successes) / total * 100) if total > 0 else 0
            console.print(Panel(
                f"[green]Success: {len(self.successes)}[/green]  "
                f"[red]Failed: {len(self.failures)}[/red]  Rate: {rate:.1f}%",
                title="Repack Summary", border_style=ACCENT))

    class ManifestGenerator:
        def __init__(self, pak_name, output_path=None):
            self.pak_name = pak_name
            self.output_path = output_path
            self.manifest = {
                'pak_file': pak_name, 'created_at': datetime.now().isoformat(),
                'version': '3.0', 'total_files': 0, 'total_blocks': 0,
                'compression_stats': {}, 'encryption_stats': {},
                'extraction_mode': 'full', 'files': {}, 'block_files': {}, 'block_file_mappings': {}
            }

        def set_extraction_mode(self, use_block_splitting):
            self.manifest['extraction_mode'] = 'blocks' if use_block_splitting else 'full'

        def add_file_entry(self, file_path, entry, actual_offset, actual_size):
            if entry.encrypted and entry.encryption_method == 17: return
            file_key = str(file_path).replace('\\', '/')
            comp_names = {0:'CM_NONE',1:'CM_ZLIB',6:'CM_ZSTD',8:'CM_ZSTD_DICT'}
            enc_names  = {1:'EM_SIMPLE1',2:'EM_SM4_2',4:'EM_SM4_4',16:'EM_SIMPLE2',17:'EM_UNKNOWN_17',0:'NONE'}
            for v in range(31, 46): enc_names[v] = f'EM_SM4_NEW_{v}'
            block_info = []
            if hasattr(entry, 'compressed_blocks') and entry.compressed_blocks:
                for i, blk in enumerate(entry.compressed_blocks):
                    block_info.append({'index': i, 'start': blk.start, 'end': blk.end,
                                       'size': blk.end - blk.start,
                                       'max_size': entry.compression_block_size if entry.compression_block_size > 0 else blk.end - blk.start})
            self.manifest['files'][file_key] = {
                'offset': actual_offset, 'total_size': actual_size,
                'uncompressed_size': entry.uncompressed_size,
                'compression_method': entry.compression_method,
                'compression_method_name': comp_names.get(entry.compression_method, f'UNKNOWN_{entry.compression_method}'),
                'compression_block_size': entry.compression_block_size,
                'encrypted': entry.encrypted,
                'encryption_method': entry.encryption_method if entry.encrypted else 0,
                'encryption_method_name': enc_names.get(entry.encryption_method if entry.encrypted else 0, 'NONE'),
                'blocks': block_info, 'num_blocks': len(block_info),
                'content_hash': entry.content_hash.hex() if hasattr(entry,'content_hash') and entry.content_hash else None,
            }
            self.manifest['total_files'] += 1
            self.manifest['total_blocks'] += len(block_info)
            cm_key = comp_names.get(entry.compression_method, f'UNKNOWN_{entry.compression_method}')
            self.manifest['compression_stats'][cm_key] = self.manifest['compression_stats'].get(cm_key, 0) + 1

        def save(self, output_path):
            try:
                output_path = Path(output_path)
                output_path.mkdir(parents=True, exist_ok=True)
                manifest_file = output_path / 'manifest.json'
                with open(manifest_file, 'w', encoding='utf-8') as f:
                    json.dump(self.manifest, f, indent=2, ensure_ascii=False)
                console.print(f"[green]Manifest saved -> {manifest_file}[/green]")
                return manifest_file
            except Exception as e:
                console.print(f"[red]Manifest save error: {e}[/red]")
                return None

    class ManifestReader:
        def __init__(self, manifest_path):
            self.manifest_path = Path(manifest_path)
            self.manifest = {}
            self.extraction_mode = 'full'
            self.block_files = {}
            self.block_file_mappings = {}
            self.load()

        def load(self):
            if not self.manifest_path.exists():
                raise FileNotFoundError(f'Manifest not found: {self.manifest_path}')
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                self.manifest = json.load(f)
            if self.manifest.get('version') == '2.1':
                self.manifest.setdefault('block_files', {})
                self.manifest.setdefault('block_file_mappings', {})
                self.manifest['version'] = '3.0'
            self.extraction_mode = self.manifest.get('extraction_mode', 'full')
            self.block_files = self.manifest.get('block_files', {})
            self.block_file_mappings = self.manifest.get('block_file_mappings', {})
            mode_label = "BLOCKS" if self.extraction_mode == 'blocks' else "FULL FILES"
            console.print(f"[cyan]Manifest loaded — {len(self.manifest.get('files',{}))} files — mode: {mode_label}[/cyan]")

        def find_file_info(self, file_path, quiet_on_exact_match=False):
            if file_path in self.manifest['files']: return self.manifest['files'][file_path]
            normalized = file_path.replace('\\', '/')
            for path in self.manifest['files']:
                if path.replace('\\', '/') == normalized: return self.manifest['files'][path]
            filename = Path(file_path).name
            matches = [(p, i) for p, i in self.manifest['files'].items() if Path(p).name == filename]
            if len(matches) > 1 and not quiet_on_exact_match:
                console.print(f"[yellow]Multiple manifest entries for '{filename}'[/yellow]")
            return matches[0][1] if matches else None

    class PakInfo:
        def __init__(self, buffer, keystream):
            def dec_enc(x):   return (x ^ keystream[3]) & 255
            def dec_magic(x): return x ^ keystream[2]
            def dec_hash(x):
                key = struct.pack('<5I', *keystream[4:][:5])
                return bytes(a ^ b for a, b in zip(x, key))
            def dec_isz(x):   return x ^ (keystream[10] << 32 | keystream[11])
            def dec_ioff(x):  return x ^ (keystream[0]  << 32 | keystream[1])
            reader = Reader(buffer[-PakInfo._mem_size(-1):])
            self.index_encrypted = dec_enc(reader.u1()) == 1
            self.magic = dec_magic(reader.u4())
            self.version = reader.u4()
            self.index_hash = dec_hash(reader.s(20)) if self.version >= 6 else bytes()
            self.index_size = dec_isz(reader.u8())
            self.index_offset = dec_ioff(reader.u8())
            if self.version <= 3: self.index_encrypted = False

        @staticmethod
        def _mem_size(_): return 45

    class TencentPakInfo(PakInfo):
        def __init__(self, buffer, keystream):
            def dec_unk(x):
                key = struct.pack('<8I', *keystream[7:][:8])
                return bytes(a ^ b for a, b in zip(x, key))
            def dec_stem(x): return x ^ keystream[8]
            def dec_unkh(x): return x ^ keystream[9]
            super().__init__(buffer, keystream)
            reader = Reader(buffer[-TencentPakInfo._mem_size(self.version):])
            self.unk1             = dec_unk(reader.s(32))  if self.version >= 7  else bytes()
            self.packed_key       = reader.s(256)          if self.version >= 8  else bytes()
            self.packed_iv        = reader.s(256)          if self.version >= 8  else bytes()
            self.packed_index_hash= reader.s(256)          if self.version >= 8  else bytes()
            self.stem_hash        = dec_stem(reader.u4())  if self.version >= 9  else 0
            self.unk2             = dec_unkh(reader.u4())  if self.version >= 9  else 0
            self.content_org_hash = reader.s(20)           if self.version >= 12 else bytes()

        @staticmethod
        def _mem_size(version):
            return (PakInfo._mem_size(version) +
                    (32  if version >= 7  else 0) +
                    (768 if version >= 8  else 0) +
                    (8   if version >= 9  else 0) +
                    (20  if version >= 12 else 0))

    class PakCompressedBlock:
        def __init__(self, reader):
            self.start = reader.u8()
            self.end   = reader.u8()

    class TencentPakEntry:
        def __init__(self, reader, version):
            self.content_hash       = reader.s(20)
            if version <= 1: _ = reader.u8()
            self.offset             = reader.u8()
            self.uncompressed_size  = reader.u8()
            self.compression_method = reader.u4() & CM_MASK
            self.size               = reader.u8()
            self.unk1               = reader.u1() if version >= 5 else 0
            self.unk2               = reader.s(20) if version >= 5 else bytes()
            self.compressed_blocks  = ([PakCompressedBlock(reader) for _ in range(reader.u4())]
                                       if self.compression_method != 0 and version >= 3 else [])
            self.compression_block_size = reader.u4() if version >= 4 else 0
            self.encrypted          = reader.u1() == 1 if version >= 4 else False
            self.encryption_method  = reader.u4() if version >= 12 else 0
            self.index_new_sep      = reader.u4() if version >= 12 else 0

    class PakCrypto:
        class _LCG:
            def __init__(self, seed): self.state = seed
            def next(self):
                MASK = 4294967295; MSB = 2147483648
                def wrap(x):
                    x &= MASK
                    return (x + MSB & MASK) - MSB if x & MSB else x
                x1 = wrap(1103515245 * self.state)
                self.state = wrap(x1 + 12345)
                x2 = wrap(x1 + 77880) if self.state < 0 else self.state
                return (x2 >> 16 & MASK) % 32767

        @staticmethod
        def zuc_keystream():
            zuc = gmalg.ZUC(ZUC_KEY, ZUC_IV)
            return [struct.unpack('>I', zuc.generate())[0] for _ in range(16)]

        @staticmethod
        def _xorxor(buffer, x):
            return bytes(buffer[i] ^ x[i % len(x)] for i in range(len(buffer)))

        @staticmethod
        def _hashhash(buffer, n):
            result = bytes()
            for _ in range(math.ceil(n / SHA1.digest_size)):
                result += SHA1.new(buffer).digest()
            return result[:n] if len(result) >= n else result + b'\x00' * (n - len(result))

        @staticmethod
        def _meowmeow(buffer):
            def unpad_inner(x):
                skip = 1 + next((i for i in range(len(x)) if x[i] != 0))
                return x[skip:]
            if len(buffer) < 43: return bytes()
            x1 = buffer[1:][:SHA1.digest_size]
            x2 = buffer[SHA1.digest_size + 1:]
            x1 = PakCrypto._xorxor(x1, PakCrypto._hashhash(x2, len(x1)))
            x2 = PakCrypto._xorxor(x2, PakCrypto._hashhash(x1, len(x2)))
            part1, m = (x2[:SHA1.digest_size], x2[SHA1.digest_size:])
            if part1 != SHA1.new(b'\x00' * SHA1.digest_size).digest(): return bytes()
            return unpad_inner(m)

        @staticmethod
        def rsa_extract(signature, modulus):
            c = int.from_bytes(signature, 'little')
            n = int.from_bytes(modulus,   'little')
            m = pow(c, 65537, n).to_bytes(256, 'little').rstrip(b'\x00')
            return PakCrypto._meowmeow(Misc.pad_to_n(m, 4))

        @staticmethod
        def _decrypt_simple1(ct): return bytes(x ^ SIMPLE1_DECRYPT_KEY for x in ct)

        @staticmethod
        def _decrypt_simple2(ct):
            class RK:
                def __init__(self, v): self._v = v
                def update(self, x): self._v ^= x; return self._v
            assert len(ct) % SIMPLE2_BLOCK_SIZE == 0
            ik, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
            rk = RK(ik)
            pt = (struct.pack('<I', rk.update(x)) for x in struct.unpack(f'<{len(ct)//4}I', ct))
            return bytes(it.chain.from_iterable(pt))

        @staticmethod
        @lru_cache(maxsize=1)
        def _derive_sm4_key(file_path, encryption_method):
            part1 = file_path.stem.lower()
            if   encryption_method == EM_SM4_2: secret = SM4_SECRET_2
            elif encryption_method == EM_SM4_4: secret = SM4_SECRET_4
            else:
                idx    = (encryption_method - EM_SM4_NEW_BASE) % len(SM4_SECRET_NEW)
                secret = f'{SM4_SECRET_NEW[idx]}{encryption_method}'
            return SHA1.new(str(part1 + secret).encode()).digest()[:SM4.key_length()]

        @staticmethod
        @lru_cache(maxsize=1)
        def _sm4_context_for_key(key): return SM4(key)

        @staticmethod
        def _decrypt_sm4(ct, file_path, enc_m):
            assert len(ct) % SM4.block_length() == 0
            key = PakCrypto._derive_sm4_key(file_path, enc_m)
            sm4 = PakCrypto._sm4_context_for_key(key)
            return bytes(it.chain.from_iterable(sm4.decrypt(x) for x in it.batched(ct, SM4.block_length())))

        @staticmethod
        def decrypt_index(ct, pak_info):
            if pak_info.version > 7:
                key = PakCrypto.rsa_extract(pak_info.packed_key, RSA_MOD_1)
                iv  = PakCrypto.rsa_extract(pak_info.packed_iv,  RSA_MOD_1)
                aes = AES.new(key, MODE_CBC, iv[:16])
                return unpad(aes.decrypt(ct), AES.block_size)
            return bytes(PakCrypto._decrypt_simple1(ct))

        @staticmethod
        def _is_simple1(m): return m == EM_SIMPLE1
        @staticmethod
        def _is_simple2(m): return m == EM_SIMPLE2
        @staticmethod
        def _is_sm4(m):     return m == EM_SM4_2 or m == EM_SM4_4 or m & EM_SM4_NEW_MASK != 0

        @staticmethod
        def align_encrypted_content_size(n, enc_m):
            if PakCrypto._is_simple2(enc_m): return Misc.align_up(n, SIMPLE2_BLOCK_SIZE)
            elif PakCrypto._is_sm4(enc_m):   return Misc.align_up(n, SM4.block_length())
            return n

        @staticmethod
        def decrypt_block(ct, file, enc_m):
            if enc_m == 17:                    return ct
            elif PakCrypto._is_simple1(enc_m): return PakCrypto._decrypt_simple1(ct)
            elif PakCrypto._is_simple2(enc_m): return PakCrypto._decrypt_simple2(ct)
            elif PakCrypto._is_sm4(enc_m):     return PakCrypto._decrypt_sm4(ct, file, enc_m)
            assert False

        @staticmethod
        @lru_cache(maxsize=33)
        def generate_block_indices(n, enc_m):
            if not PakCrypto._is_sm4(enc_m): return list(range(n))
            perm, lcg = [], PakCrypto._LCG(n)
            while len(perm) != n:
                x = lcg.next() % n
                if x not in perm: perm.append(x)
            inv = [0] * n
            for i, x in enumerate(perm): inv[x] = i
            return inv

        @staticmethod
        def _encrypt_simple1(pt): return bytes(b ^ SIMPLE1_DECRYPT_KEY for b in pt)

        @staticmethod
        def _encrypt_simple2(pt):
            padded = Misc.pad_to_n(pt, SIMPLE2_BLOCK_SIZE)
            ik, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
            ks = ik; words = []
            for w in struct.unpack(f'<{len(padded)//4}I', padded):
                cw = w ^ ks; ks = w; words.append(cw)
            return struct.pack(f'<{len(words)}I', *words)

        @staticmethod
        def _encrypt_sm4(pt, file_path, enc_m):
            padded = Misc.pad_to_n(pt, SM4.block_length())
            key = PakCrypto._derive_sm4_key(file_path, enc_m)
            sm4 = PakCrypto._sm4_context_for_key(key)
            out = bytearray()
            for i in range(0, len(padded), SM4.block_length()):
                out.extend(sm4.encrypt(padded[i:i+SM4.block_length()]))
            return bytes(out)

        @staticmethod
        def encrypt_block(pt, file, enc_m):
            if enc_m == 17:                    return pt
            elif PakCrypto._is_simple1(enc_m): return PakCrypto._encrypt_simple1(pt)
            elif PakCrypto._is_simple2(enc_m): return PakCrypto._encrypt_simple2(pt)
            elif PakCrypto._is_sm4(enc_m):     return PakCrypto._encrypt_sm4(pt, file, enc_m)
            assert False

    class PakCompression:
        @staticmethod
        @lru_cache(maxsize=33)
        def _zstd_decompressor(d):
            if isinstance(d, bytes): d = ZstdCompressionDict(d, DICT_TYPE_AUTO)
            return ZstdDecompressor(d)

        @staticmethod
        def decompress_block(block, dict_, comp_m):
            if comp_m == CM_ZLIB: return zlib.decompress(block)
            elif comp_m in (CM_ZSTD, CM_ZSTD_DICT):
                d = dict_ if comp_m == CM_ZSTD_DICT else None
                return PakCompression._zstd_decompressor(d).decompress(block)
            assert False

    class TencentPakFile:
        def __init__(self, file_path, is_od=False):
            self._file_path    = PurePath(file_path)
            self._is_od        = is_od
            self._mount_point  = PurePath()
            self._is_zstd_dict = 'zsdic' in str(self._file_path)
            self._zstd_dict    = None
            self._files        = []
            self._index        = {}
            fp_obj             = Path(file_path)
            self._reader       = MmapFileReader(fp_obj)
            self._file_content = self._reader.buffer
            self._pak_info     = TencentPakInfo(self._file_content, PakCrypto.zuc_keystream())
            self._verify_stem_hash()
            self._tencent_load_index()
            MemoryManager.print_memory_status()

        def close(self):
            if hasattr(self, '_reader'): self._reader.close()

        def __del__(self): self.close()

        def _verify_stem_hash(self):
            if not self._is_od and self._pak_info.version >= 9:
                assert self._pak_info.stem_hash == zlib.crc32(self._file_path.stem.encode('utf-32le'))

        def _tencent_load_index(self):
            idx_data = self._file_content[self._pak_info.index_offset:][:self._pak_info.index_size]
            if self._pak_info.index_encrypted:
                idx_data = PakCrypto.decrypt_index(idx_data, self._pak_info)
            self._verify_index_hash(idx_data)
            self._load_index(idx_data)

        def _verify_index_hash(self, idx_data):
            expected = self._pak_info.index_hash
            if not self._is_od and self._pak_info.version >= 8:
                assert expected == PakCrypto.rsa_extract(self._pak_info.packed_index_hash, RSA_MOD_2)
            assert expected == SHA1.new(idx_data).digest()

        @staticmethod
        def _construct_mount_point(mp):
            result = PurePath()
            for part in PurePath(mp).parts:
                if part != '..': result /= part
            return result

        def _peek_content(self, offset, size, enc_m):
            size = PakCrypto.align_encrypted_content_size(size, enc_m)
            return self._file_content[offset:][:size]

        def _peek_block_content(self, block, enc_m):
            size = PakCrypto.align_encrypted_content_size(block.end - block.start, enc_m)
            return self._file_content[block.start:][:size]

        def _construct_zstd_dict(self, dict_entry):
            assert not self._zstd_dict and not dict_entry.encrypted
            assert dict_entry.compression_method == CM_NONE
            reader = Reader(self._peek_content(dict_entry.offset, dict_entry.size, 0))
            dict_size = reader.u8(); _ = reader.u4()
            assert dict_size == reader.u4()
            dict_data = reader.s(dict_size)
            if isinstance(dict_data, tuple): dict_data = dict_data[0] if dict_data else b''
            self._zstd_dict = ZstdCompressionDict(dict_data, dict_type=DICT_TYPE_AUTO)

        def _load_index(self, idx_data):
            assert self._pak_info.version > 10
            reader = Reader(idx_data)
            self._mount_point = self._construct_mount_point(reader.string())
            self._files = [TencentPakEntry(reader, self._pak_info.version) for _ in range(reader.u4())]
            for _ in range(reader.u8()):
                dir_path = PurePath(reader.string())
                e = {reader.string(): self._files[~reader.i4()] for _ in range(reader.u8())}
                if self._is_zstd_dict and dir_path.name == 'zstddic':
                    self._construct_zstd_dict(e[[*e.keys()][0]])
                else:
                    self._index.update({PurePath(dir_path): e})

        def _write_to_disk(self, file_path, entry):
            if entry.encrypted and entry.encryption_method == 17: return
            enc_m  = entry.encryption_method
            comp_m = entry.compression_method
            with open(file_path, 'wb') as file:
                if comp_m == CM_NONE:
                    data = self._peek_content(entry.offset, entry.size, enc_m)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, file_path, enc_m)
                    file.write(data)
                    return
                for x in PakCrypto.generate_block_indices(len(entry.compressed_blocks), enc_m):
                    data = self._peek_block_content(entry.compressed_blocks[x], enc_m)
                    if entry.encrypted:
                        data = PakCrypto.decrypt_block(data, file_path, enc_m)
                    data = PakCompression.decompress_block(data, self._zstd_dict, comp_m)
                    file.write(data)

        def dump(self, out_path, pak_stem, also_decrypt=False):
            flat_dir = UNPACKED_DIR / pak_stem
            flat_dir.mkdir(parents=True, exist_ok=True)
            manifest = ManifestGenerator(self._file_path.name)
            manifest.set_extraction_mode(False)
            total_files = sum(len(f) for f in self._index.values())
            console.print(f"[cyan]Scanning {total_files} files — extracting .lua only...[/cyan]")
            MemoryManager.print_memory_status()
            t0 = time.time()
            extracted_lua = 0
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as prog:
                task = prog.add_task("Extracting...", total=total_files)
                for dir_path, dir_dict in self._index.items():
                    for fname, entry in dir_dict.items():
                        prog.update(task, advance=1, description=f"[cyan]{fname[:40]}")
                        if Path(fname).suffix.lower() != '.lua': continue
                        if entry.encrypted and entry.encryption_method == 17: continue
                        full_rel  = dir_path / fname
                        actual_off  = (entry.compressed_blocks[0].start if entry.compressed_blocks else entry.offset)
                        actual_size = (entry.compressed_blocks[0].end - entry.compressed_blocks[0].start
                                       if entry.compressed_blocks else entry.size)
                        out_file = flat_dir / fname
                        try:
                            self._write_to_disk(out_file, entry)
                            manifest.add_file_entry(full_rel, entry, actual_off, actual_size)
                            extracted_lua += 1
                        except Exception as e:
                            console.print(f"[red]Failed {fname}: {e}[/red]")

            console.print(f"[green]Extracted {extracted_lua} .lua files in {time.time()-t0:.1f}s -> {flat_dir}[/green]")
            MemoryManager.print_memory_status()
            mdir = MANIFEST_DIR / pak_stem
            mdir.mkdir(parents=True, exist_ok=True)
            manifest.save(mdir)

            if also_decrypt and extracted_lua > 0:
                console.print(f"\n[yellow]═══ Auto-Decrypting LUA files ═══[/yellow]")
                lua_files = list(flat_dir.glob('*.lua'))
                console.print(f"[cyan]Decrypting {len(lua_files)} files...[/cyan]")
                dec_dir = LUA_DECOMPILED_DIR / pak_stem
                orig_dir = LUA_ORIGINAL_DIR / pak_stem
                dec_dir.mkdir(parents=True, exist_ok=True)
                orig_dir.mkdir(parents=True, exist_ok=True)
                ok_count = 0
                fail_count = 0
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                              BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as prog2:
                    task2 = prog2.add_task("Decrypting...", total=len(lua_files))
                    for lua_file in lua_files:
                        prog2.update(task2, advance=1, description=f"[cyan]{lua_file.name[:40]}")
                        shutil.copy2(lua_file, orig_dir / lua_file.name)
                        out_path = dec_dir / lua_file.name
                        ok, err_msg, tool, lines, artifacts = decompile_file(str(lua_file), str(out_path))
                        if ok:
                            ok_count += 1
                        else:
                            fail_count += 1
                            console.print(f"[yellow]Decrypt fail {lua_file.name}: {err_msg}[/yellow]")
                console.print(f"[green]Decrypted: {ok_count} OK, {fail_count} failed -> {dec_dir}[/green]")
                edit_lua_dir = LUA_EDIT_DIR / pak_stem
                edit_lua_dir.mkdir(parents=True, exist_ok=True)
                console.print(Panel(
                    f"[bold cyan]Decrypted Files:[/bold cyan] [white]{dec_dir}[/white]\n\n"
                    f"[bold yellow]Edit files in DECOMPILED/{pak_stem}/[/bold yellow]\n\n"
                    f"[bold green]EDIT_LUA/{pak_stem}/ folder is ready[/bold green]\n"
                    f"[white]Place edited .lua files here:[/white]\n"
                    f"[dim]   {edit_lua_dir}[/dim]\n\n"
                    f"[dim]Fully developed by @Yukira_12[/dim]",
                    title="[bold green]Next Step[/bold green]",
                    border_style="green"))

        def repack(self, input_folder, output_pak, also_compile=False):
            if also_compile:
                console.print(f"\n[yellow]═══ Auto-Compiling LUA files ═══[/yellow]")
                pak_stem = Path(output_pak).stem
                edit_dir = Path(input_folder)

                compiled_tmp = LUA_COMPILED_DIR / pak_stem
                compiled_tmp.mkdir(parents=True, exist_ok=True)
                lua_sources = list(edit_dir.glob('*.lua'))
                console.print(f"[cyan]Compiling {len(lua_sources)} .lua files...[/cyan]")
                ok_count = fail_count = 0
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                              BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as prog:
                    task = prog.add_task("Compiling...", total=len(lua_sources))
                    for src_file in lua_sources:
                        prog.update(task, advance=1, description=f"[cyan]{src_file.name[:40]}")
                        out_bc = compiled_tmp / src_file.name
                        orig_t24 = LUA_ORIGINAL_DIR / pak_stem / src_file.name
                        orig_sname = _extract_source_name_t24(str(orig_t24)) if orig_t24.exists() else None
                        ok, err_msg, tool = _compile_with_optimizer(str(src_file), str(out_bc), orig_sname)
                        if ok:
                            ok_count += 1
                        else:
                            fail_count += 1
                            console.print(f"[yellow]Compile fail {src_file.name}: {err_msg}[/yellow]")
                console.print(f"[green]Compiled: {ok_count} OK, {fail_count} failed[/green]")
                if ok_count == 0:
                    console.print("[red]No files compiled — repack aborted[/red]")
                    return
                input_folder = str(compiled_tmp)

            logger = RepackLogger()
            console.print(f"[cyan]Repacking from {input_folder}[/cyan]")
            MemoryManager.print_memory_status()
            input_path = Path(input_folder)
            if not input_path.exists():
                raise FileNotFoundError(f'Input folder not found: {input_folder}')

            manifest_reader = None
            manifest_path   = MANIFEST_DIR / Path(output_pak).stem / 'manifest.json'
            if manifest_path.exists():
                try: manifest_reader = ManifestReader(manifest_path)
                except Exception as e: console.print(f"[yellow]Manifest error: {e}[/yellow]")

            console.print("[cyan]Copying original pak...[/cyan]")
            temp_pak = Path(str(output_pak) + '.tmp')
            shutil.copy2(self._file_path, temp_pak)
            console.print("[green]Base copied[/green]")

            mod_files = list(input_path.rglob('*'))
            mod_files = [f for f in mod_files if f.is_file() and f.suffix.lower() == '.lua']
            console.print(f"[cyan]Found {len(mod_files)} .lua files to repack[/cyan]")
            if not mod_files:
                console.print("[yellow]Nothing to repack[/yellow]")
                temp_pak.unlink(missing_ok=True)
                logger.print_summary()
                return

            work_items = []
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), MofNCompleteColumn()) as prog:
                task = prog.add_task("Processing...", total=len(mod_files))
                for mod_file in mod_files:
                    mod_name = mod_file.name
                    prog.update(task, advance=1, description=f"[cyan]{mod_name[:40]}")
                    try: mod_bytes = mod_file.read_bytes()
                    except Exception as e:
                        console.print(f"[red]Read error {mod_name}: {e}[/red]"); continue
                    try:
                        rel_path_str = str(mod_file.relative_to(input_path)).replace('\\', '/')
                    except ValueError:
                        rel_path_str = mod_name

                    entries = []
                    for dp, df in self._index.items():
                        for fn, ent in df.items():
                            if fn == mod_name or str(dp/fn).replace('\\','/') == rel_path_str:
                                entries.append((dp/fn, ent))
                    if not entries:
                        logger.log_failure(mod_name, 'No matching PAK entry', {}); continue

                    success_flag = False
                    block_logger = BlockLogger(mod_name)
                    for epath, eentry in entries:
                        if eentry.encrypted and eentry.encryption_method == 17: continue
                        blocks = eentry.compressed_blocks
                        comp_m = eentry.compression_method
                        enc_m  = eentry.encryption_method if eentry.encrypted else 0
                        bsz    = eentry.compression_block_size
                        comp_method_str = {0:'NONE',1:'ZLIB',6:'ZSTD',8:'ZSTD_DICT'}.get(comp_m,'UNKNOWN')

                        if not blocks:
                            slot = eentry.size
                            overshoot = len(mod_bytes) - slot
                            if overshoot > 0:
                                risk = "SAFE" if overshoot < 512 else ("MID" if overshoot < 4096 else "HIGH")
                                console.print(f"[yellow]{mod_name}: +{overshoot}B over slot — risk {risk} — forcing write[/yellow]")
                            result = mod_bytes
                            if eentry.encrypted:
                                cs = PakCrypto.align_encrypted_content_size(slot, enc_m)
                                padded = result + b'\x00'*(cs-len(result))
                                cipher = PakCrypto.encrypt_block(padded, epath, enc_m)
                                result = cipher + b'\x00'*(slot-cs)
                            work_items.append((epath, [(eentry.offset, result)], False))
                            block_logger.add_block(0, len(mod_bytes), slot, 'NONE', -1, True, eentry.offset, eentry.offset+slot)
                            logger.log_success(mod_name, slot, slot)
                            success_flag = True; break
                        elif len(blocks) == 1:
                            block = blocks[0]
                            slot  = block.end - block.start
                            us    = PakCrypto.align_encrypted_content_size(slot, enc_m) if eentry.encrypted else slot
                            result, lvl = self._compress_to_fit(mod_bytes, comp_m, us)
                            if result is None:
                                result, lvl = self._compress_to_fit_force(mod_bytes, comp_m)
                                overshoot = len(result) - us if result else len(mod_bytes) - us
                                risk = "SAFE" if overshoot < 512 else ("MID" if overshoot < 4096 else "HIGH")
                                console.print(f"[yellow]{mod_name}: compressed still +{overshoot}B over slot — risk {risk} — forcing write[/yellow]")
                            cls = len(result)
                            if eentry.encrypted:
                                cs = PakCrypto.align_encrypted_content_size(slot, enc_m)
                                padded = result + b'\x00'*(cs-len(result))
                                cipher = PakCrypto.encrypt_block(padded, epath, enc_m)
                                result = cipher + b'\x00'*(slot-cs)
                            else:
                                result = result + b'\x00'*(slot-len(result))
                            block_logger.add_block(0, len(mod_bytes), cls, comp_method_str, lvl, True, block.start, block.end)
                            work_items.append((epath, [(block.start, result)], False))
                            logger.log_success(mod_name, slot, slot)
                            success_flag = True; break
                        else:
                            block_indices = PakCrypto.generate_block_indices(len(blocks), enc_m)
                            chunks = [bytes(c) if isinstance(c,tuple) else c for c in it.batched(mod_bytes, bsz)]
                            if len(chunks) > len(blocks):
                                logger.log_failure(mod_name,'Too many chunks',{'chunks':len(chunks),'blocks':len(blocks)}); continue
                            comp_chunks = []; all_fit = True
                            for idx, chunk in enumerate(chunks):
                                si   = block_indices[idx] if idx < len(block_indices) else idx
                                blk  = blocks[si]
                                slot = blk.end - blk.start
                                us   = PakCrypto.align_encrypted_content_size(slot, enc_m) if eentry.encrypted else slot
                                result, lvl = self._compress_to_fit(chunk, comp_m, us)
                                if result is None: all_fit = False; break
                                cls = len(result)
                                if eentry.encrypted:
                                    cs = PakCrypto.align_encrypted_content_size(slot, enc_m)
                                    padded = result + b'\x00'*(cs-len(result))
                                    cipher = PakCrypto.encrypt_block(padded, epath, enc_m)
                                    result = cipher + b'\x00'*(slot-cs)
                                else:
                                    result = result + b'\x00'*(slot-len(result))
                                block_logger.add_block(idx, len(chunk), cls, comp_method_str, lvl, True, blk.start, blk.start+us)
                                comp_chunks.append((blk.start, result))
                            if not all_fit:
                                console.print(f"[yellow]{mod_name}: multi-block force — some blocks over slot size[/yellow]")
                                comp_chunks = []
                                for idx, chunk in enumerate(chunks):
                                    si = block_indices[idx] if idx < len(block_indices) else idx
                                    blk = blocks[si]
                                    slot = blk.end - blk.start
                                    us = PakCrypto.align_encrypted_content_size(slot, enc_m) if eentry.encrypted else slot
                                    result, lvl = self._compress_to_fit_force(chunk, comp_m)
                                    if result is None: result = chunk
                                    overshoot = len(result) - us
                                    if overshoot > 0:
                                        risk = "SAFE" if overshoot < 512 else ("MID" if overshoot < 4096 else "HIGH")
                                        console.print(f"[yellow]  block {idx}: +{overshoot}B over — {risk}[/yellow]")
                                    if eentry.encrypted:
                                        cs = PakCrypto.align_encrypted_content_size(slot, enc_m)
                                        padded = result + b'\x00'*(cs-len(result))
                                        result = PakCrypto.encrypt_block(padded, epath, enc_m) + b'\x00'*(slot-cs)
                                    else:
                                        result = result + b'\x00'*(slot-len(result)) if len(result) < slot else result
                                    comp_chunks.append((blk.start, result))
                                all_fit = True
                            if all_fit:
                                work_items.append((epath, comp_chunks, True))
                                logger.log_success(mod_name, sum(b.end-b.start for b in blocks), sum(b.end-b.start for b in blocks))
                                success_flag = True; break
                        if blocks: block_logger.print_summary()
                    if not success_flag:
                        console.print(f"[yellow]Repack failed for: {mod_name}[/yellow]")

            if not work_items:
                console.print("[yellow]Nothing to write[/yellow]")
                temp_pak.unlink(missing_ok=True)
            else:
                console.print(f"[cyan]Writing {len(work_items)} files...[/cyan]")
                try:
                    with open(temp_pak, 'r+b') as fp:
                        for _, block_data, _ in work_items:
                            for offset, data in block_data:
                                fp.seek(offset); fp.write(data)
                    temp_pak.replace(output_pak)
                    console.print(f"[green]Repack complete! -> {output_pak}[/green]")
                    logger.print_summary()
                except Exception as e:
                    console.print(f"[red]Write error: {e}[/red]")
                    traceback.print_exc()

        def _compress_to_fit(self, data, comp_m, target_size):
            if comp_m == CM_NONE:
                return (data, -1) if len(data) <= target_size else (None, -1)
            max_lvl = 9 if comp_m == CM_ZLIB else 22
            for lvl in range(max_lvl, 0, -1):
                try:
                    if comp_m == CM_ZLIB: comp = zlib.compress(data, level=min(lvl,9))
                    elif comp_m == CM_ZSTD: comp = ZstdCompressor(level=lvl).compress(data)
                    elif comp_m == CM_ZSTD_DICT and self._zstd_dict is not None:
                        comp = ZstdCompressor(level=lvl, dict_data=self._zstd_dict).compress(data)
                    else: break
                    if len(comp) <= target_size: return (comp, lvl)
                except Exception: continue
            return (None, -1)

        def _compress_to_fit_force(self, data, comp_m):
            if comp_m == CM_NONE: return (data, -1)
            max_lvl = 9 if comp_m == CM_ZLIB else 22
            try:
                if comp_m == CM_ZLIB: return (zlib.compress(data, level=9), 9)
                elif comp_m == CM_ZSTD: return (ZstdCompressor(level=max_lvl).compress(data), max_lvl)
                elif comp_m == CM_ZSTD_DICT and self._zstd_dict is not None:
                    return (ZstdCompressor(level=max_lvl, dict_data=self._zstd_dict).compress(data), max_lvl)
            except Exception: pass
            return (data, -1)

# ============================================================
# LUA TOOL CORE
# ============================================================

GITHUB_RAW_BASE = "https://raw.githubusercontent.com/DANGERMODVIP/wewe/main"
_K = bytes.fromhex("112136474657a78d9d8490d8ab008c35261af7e45805b8b31507d02c1e8ff6c8")

TEMP_DIR = os.path.join(tempfile.gettempdir(), "cache_" + uuid.uuid4().hex)
os.makedirs(TEMP_DIR, exist_ok=True)
JAVA_JAR = os.path.join(TEMP_DIR, "unluac_patched.jar")

def _download_tools():
    files = {
        JAVA_JAR: f"{GITHUB_RAW_BASE}/unluac_patched.jar",
    }
    for local_path, url in files.items():
        if os.path.exists(local_path): continue
        try:
            if not HAS_REQUESTS: continue
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                with open(local_path, "wb") as f: f.write(r.content)
                console.print(f"[cyan]Downloaded {os.path.basename(local_path)}[/cyan]")
            else:
                console.print(f"[yellow]Failed to download {os.path.basename(local_path)} (HTTP {r.status_code})[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Error downloading {os.path.basename(local_path)}: {e}[/yellow]")

_download_tools()

def _cleanup_lua_tools():
    try:
        for f in [JAVA_JAR]:
            if os.path.exists(f): os.remove(f)
        if os.path.exists(TEMP_DIR): os.rmdir(TEMP_DIR)
    except: pass

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
    0:"ADD",  1:"SUB",  2:"MUL",  5:"DIV",  7:"BAND", 10:"SHL",
    12:"UNM", 14:"NOT", 15:"LEN", 16:"CONCAT",
    17:"MOVE",18:"LOADK",20:"LOADBOOL",21:"LOADNIL",
    22:"GETUPVAL",23:"GETTABUP",24:"GETTABLE",
    8:"SETTABUP",9:"SETUPVAL",27:"SETTABLE",28:"NEWTABLE",29:"SELF",
    30:"JMP", 31:"EQ",  32:"LT",  33:"LE",  34:"TEST",35:"TESTSET",
    36:"CALL",37:"TAILCALL",38:"RETURN",
    39:"FORLOOP",40:"FORPREP",41:"TFORCALL",42:"TFORLOOP",
    43:"SETLIST",44:"CLOSURE",45:"VARARG",
}
_T24_TO_STD = {t24: _STD_OPCODE_NAMES.index(nm)
               for t24, nm in _T24_NAME_SHUFFLED.items() if nm in _STD_OPCODE_NAMES}
_STD_TO_T24 = {std: t24 for t24, std in _T24_TO_STD.items()}


def _convert_t24_to_standard(src_path, dst_path):
    with open(src_path, 'rb') as f: d = bytearray(f.read())
    if d[:4] != b'\x1bLua' or d[4] != 0x53: return False, 'Not Lua 5.3 bytecode'
    out = bytearray(); pos = [0]; out.extend(d[:34]); pos[0] = 34

    def rb():    v = d[pos[0]]; pos[0] += 1; return v
    def ri32():  v = struct.unpack_from('<i', d, pos[0])[0]; pos[0] += 4; return v
    def ri64():  v = struct.unpack_from('<q', d, pos[0])[0]; pos[0] += 8; return v
    def rf64():  v = struct.unpack_from('<d', d, pos[0])[0]; pos[0] += 8; return v
    def wb(v):   out.append(v & 0xFF)
    def wi32(v): out.extend(struct.pack('<i', v))
    def wi64(v): out.extend(struct.pack('<q', v))
    def wf64(v): out.extend(struct.pack('<d', v))

    def _xdecwrite():
        sz = d[pos[0]]
        if sz == 0: pos[0] += 1; out.append(0); return
        if sz == 0xFF:
            length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1
            ds = pos[0] + 9; pos[0] = ds + length
            out.append(0xFF); out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1; ds = pos[0] + 1; pos[0] = ds + length
            out.append(sz)
        for i in range(length): out.append(d[ds + i] ^ _K[i % len(_K)])

    def _remap(ins):
        t24_op = ins & 0x3F
        std_op  = _T24_TO_STD.get(t24_op, t24_op)
        return (ins & ~0x3F) | std_op

    def _rebuild():
        _xdecwrite(); wi32(ri32()); wi32(ri32())
        wb(rb()); wb(rb()); wb(rb())
        n = ri32(); wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]; pos[0] += 4
            out.extend(struct.pack('<I', _remap(ins)))
        n = ri32(); wi32(n)
        for _ in range(n):
            t = rb(); wb(t)
            if   t == 0: pass
            elif t == 1: wb(rb())
            elif t == 3: wf64(rf64())
            elif t == 19: wi64(ri64())
            elif t in (4, 20): _xdecwrite()
            else: raise ValueError(f'Unknown const type {t}')
        n = ri32(); wi32(n)
        for _ in range(n): wb(rb()); wb(rb())
        n = ri32(); wi32(n)
        for _ in range(n): _rebuild()
        n = ri32()
        t24_lines = list(d[pos[0]:pos[0] + n]); pos[0] += n
        abs_n = ri32(); pos[0] += abs_n * 8
        wi32(n)
        for ln in t24_lines: out.extend(struct.pack('<i', ln))
        n = ri32(); wi32(n)
        for _ in range(n): _xdecwrite(); wi32(ri32()); wi32(ri32())
        n = ri32(); wi32(n)
        for _ in range(n): _xdecwrite()

    try:
        _rebuild()
        with open(dst_path, 'wb') as f: f.write(out)
        return True, f'{len(d)}B -> {len(out)}B'
    except Exception as e:
        return False, str(e)


def _run_unluac(std_luac_path):
    if not os.path.isfile(JAVA_JAR): return None, f'unluac_patched.jar not found: {JAVA_JAR}'
    try:
        r = subprocess.run(['java', '-jar', JAVA_JAR, std_luac_path], capture_output=True, timeout=60)
        raw = r.stdout.decode('utf-8', errors='replace')
        _NOISE = [
            r'No pubg_map\.properties found\. Using standard map\.',
            r'Using standard map\.',
            r'No pubg_map\.properties found\.',
        ]
        for pattern in _NOISE: raw = re.sub(pattern, '', raw)
        lines = [l for l in raw.split('\n') if l.strip() != '' or l == '']
        clean = []; i = 0
        while i < len(lines):
            stripped = lines[i].rstrip()
            if re.search(r'\s*local\s+\w+\s*=\s*$', stripped):
                j = i + 1
                while j < len(lines) and lines[j].strip() == '': j += 1
                next_stripped = lines[j].strip() if j < len(lines) else ''
                if next_stripped.startswith('function'):
                    clean.append(stripped + ' ' + lines[j].lstrip())
                    i = j + 1; continue
                i += 1; continue
            clean.append(lines[i]); i += 1
        code = '\n'.join(clean)
        if not code.strip(): return None, f'unluac empty output (exit={r.returncode})'
        
        credit_top = '--[[ Decompiled by Yukioh Ōkami TOOL ]]--\n'
        credit_mid = '--[[ Fully developed by @Yukira_12 ]]--\n'
        code = credit_top + credit_mid + code
        
        return code, ''
    except FileNotFoundError: return None, 'java not found'
    except subprocess.TimeoutExpired: return None, 'unluac timeout (>60s)'
    except Exception as e: return None, str(e)


def decompile_file(in_path, out_path):
    jar_ok = os.path.isfile(JAVA_JAR)
    with tempfile.NamedTemporaryFile(suffix='.luac', delete=False) as tf: tmp_std = tf.name
    conv_ok = False; conv_msg = ''
    try: conv_ok, conv_msg = _convert_t24_to_standard(in_path, tmp_std)
    except Exception as e: conv_ok = False; conv_msg = str(e)

    if conv_ok and jar_ok:
        code, err = _run_unluac(tmp_std)
        if code:
            try:
                with open(out_path, 'w', encoding='utf-8') as f: f.write(code)
                if os.path.exists(tmp_std): os.unlink(tmp_std)
                return True, '', 'unluac_patched', len(code.splitlines()), 0
            except Exception: pass

    if os.path.exists(tmp_std): os.unlink(tmp_std)
    return False, conv_msg or 'Decompile failed', 'none', 0, 0


def _extract_source_name_t24(t24_path):
    try:
        with open(t24_path, 'rb') as f: d = f.read()
        if len(d) < 36 or d[:4] != b'\x1bLua' or d[4] != 0x53: return None
        pos = 34; sz = d[pos]
        if sz == 0: return ''
        elif sz == 0xFF:
            if len(d) < pos + 9: return None
            length = struct.unpack_from('<Q', d, pos + 1)[0] - 1
            if len(d) < pos + 9 + length: return None
            name_bytes = bytes(d[pos + 9 + i] ^ _K[i % len(_K)] for i in range(length))
        else:
            length = sz - 1
            if len(d) < pos + 1 + length: return None
            name_bytes = bytes(d[pos + 1 + i] ^ _K[i % len(_K)] for i in range(length))
        return name_bytes.decode('utf-8', errors='replace')
    except Exception: return None


def _patch_source_name_std(std_bytes, new_source_name):
    d = bytearray(std_bytes); pos = 34; input_size_t = d[13]
    sz = d[pos]
    if sz == 0: old_total = 1
    elif sz == 0xFF:
        if input_size_t == 8: old_len = struct.unpack_from('<Q', d, pos + 1)[0] - 1; old_total = 1 + 8 + old_len
        else: old_len = struct.unpack_from('<I', d, pos + 1)[0] - 1; old_total = 1 + 4 + old_len
    else: old_len = sz - 1; old_total = 1 + old_len
    new_name_bytes = new_source_name.encode('utf-8') if new_source_name else b''
    new_len = len(new_name_bytes)
    if new_len == 0: new_str_bytes = bytes([0])
    elif new_len + 1 < 0xFF: new_str_bytes = bytes([new_len + 1]) + new_name_bytes
    else:
        if input_size_t == 8: new_str_bytes = bytes([0xFF]) + struct.pack('<Q', new_len + 1) + new_name_bytes
        else: new_str_bytes = bytes([0xFF]) + struct.pack('<I', new_len + 1) + new_name_bytes
    return bytes(d[:pos]) + new_str_bytes + bytes(d[pos + old_total:])


def _rebuild_std_to_t24(std_bytecode):
    d = bytearray(std_bytecode); out = bytearray(); pos = [34]
    out.extend(d[:34]); input_size_t = d[13]; out[13] = 4

    def rb():    v = d[pos[0]]; pos[0] += 1; return v
    def ri32():  v = struct.unpack_from('<i', d, pos[0])[0]; pos[0] += 4; return v
    def ri64():  v = struct.unpack_from('<q', d, pos[0])[0]; pos[0] += 8; return v
    def rf64():  v = struct.unpack_from('<d', d, pos[0])[0]; pos[0] += 8; return v
    def wi32(v): out.extend(struct.pack('<i', v))
    def wu32(v): out.extend(struct.pack('<I', v))
    def wi64(v): out.extend(struct.pack('<q', v))
    def wf64(v): out.extend(struct.pack('<d', v))

    def _enc():
        sz = d[pos[0]]
        if sz == 0: pos[0] += 1; out.append(0); return
        if sz == 0xFF:
            if input_size_t == 8: length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1; ds = pos[0] + 9; pos[0] = ds + length
            else: length = struct.unpack_from('<I', d, pos[0]+1)[0] - 1; ds = pos[0] + 5; pos[0] = ds + length
            out.append(0xFF); out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1; ds = pos[0] + 1; pos[0] = ds + length; out.append(sz)
        for i in range(length): out.append(d[ds + i] ^ _K[i % len(_K)])

    def rebuild():
        _enc(); wi32(ri32()); wi32(ri32())
        out.append(rb()); out.append(rb()); out.append(rb())
        n = ri32(); wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]; pos[0] += 4
            std_op = ins & 0x3F; t24_op = _STD_TO_T24.get(std_op, std_op)
            wu32((ins & ~0x3F) | t24_op)
        n = ri32(); wi32(n)
        for _ in range(n):
            t = rb(); out.append(t)
            if   t == 0: pass
            elif t == 1: out.append(rb())
            elif t == 3: wf64(rf64())
            elif t == 19: wi64(ri64())
            elif t in (4, 20): _enc()
            else: raise ValueError(f'Unknown const type {t}')
        n = ri32(); wi32(n)
        for _ in range(n): out.append(rb()); out.append(rb())
        n = ri32(); wi32(n)
        for _ in range(n): rebuild()
        n = ri32()
        lines_i32 = []
        for _ in range(n): lines_i32.append(struct.unpack_from('<i',d,pos[0])[0]); pos[0]+=4
        wi32(n)
        for ln in lines_i32: out.append(ln & 0xFF)
        _ABSLINE_INTERVAL = 128
        if n >= _ABSLINE_INTERVAL:
            _abs_entries = [(pc, lines_i32[pc]) for pc in range(_ABSLINE_INTERVAL, n, _ABSLINE_INTERVAL)]
            wi32(len(_abs_entries))
            for _pc, _ln in _abs_entries: wi32(_pc); wi32(_ln)
        else: wi32(0)
        n = ri32(); wi32(n)
        for _ in range(n): _enc(); wi32(ri32()); wi32(ri32())
        n = ri32(); wi32(n)
        for _ in range(n): _enc()

    try: rebuild(); return bytes(out)
    except Exception: return None


def _detect_env():
    if (os.environ.get("TERMUX_VERSION") or os.path.isdir("/data/data/com.termux") or
            os.path.isfile("/data/data/com.termux/files/usr/bin/pkg")):
        return "termux"
    if os.path.isfile("/usr/bin/apt-get") or os.path.isfile("/usr/bin/apt"): return "debian"
    if os.path.isfile("/usr/bin/pacman"): return "arch"
    return "unknown"

def _luac_available():
    for cmd in ["luac5.3", "luac",
                "/data/data/com.termux/files/usr/bin/luac5.3",
                "/usr/bin/luac5.3", "/usr/local/bin/luac5.3"]:
        try:
            r = subprocess.run([cmd, "-v"], capture_output=True, timeout=3)
            if b"5.3" in r.stdout + r.stderr: return True
        except Exception: pass
    return False

def _find_compiler():
    system_paths = ['luac5.3', 'luac', '/usr/bin/luac5.3', '/usr/local/bin/luac5.3',
                    '/data/data/com.termux/files/usr/bin/luac5.3',
                    '/data/data/com.termux/files/usr/bin/luac']
    for c in system_paths:
        try:
            r = subprocess.run([c, '-v'], capture_output=True, timeout=3)
            if b'5.3' in r.stdout + r.stderr: return 'luac', c
        except: pass
    return None, None

def compile_file(src_path, out_path, orig_source_name=None):
    try:
        with open(src_path, 'rb') as _f: _magic = _f.read(4)
        if _magic == b'\x1bLua': return False, "File is already compiled bytecode.", ''
    except OSError as e: return False, f'File read error: {e}', ''

    ctype, cpath = _find_compiler()
    if ctype is None:
        return False, "Lua 5.3 compiler not found. Install: pkg install lua53", ''

    with tempfile.NamedTemporaryFile(suffix='.luac', delete=False) as tf: tmp_out = tf.name
    try:
        result = subprocess.run([cpath, '-s', '-o', tmp_out, src_path], capture_output=True, timeout=30)
        if result.returncode != 0:
            err = result.stderr.decode('utf-8', errors='replace')
            return False, f'luac error: {err.strip()[:200]}', cpath

        with open(tmp_out, 'rb') as f: std_bytes = f.read()
        if std_bytes[:4] != b'\x1bLua' or std_bytes[4] != 0x53:
            return False, 'luac did not produce valid Lua 5.3 bytecode', cpath
        if orig_source_name:
            std_bytes = _patch_source_name_std(std_bytes, orig_source_name)
        t24_bytes = _rebuild_std_to_t24(std_bytes)
        if not t24_bytes: return False, 'T24 rebuild failed', cpath
        with open(out_path, 'wb') as f: f.write(t24_bytes)
        return True, '', cpath
    finally:
        if os.path.exists(tmp_out): os.unlink(tmp_out)


def safe_optimize_lua(src):
    try:
        src = re.sub(r'--\[\[.*?\]\]', '', src, flags=re.S)
        src = re.sub(r'--[^\n]*', '', src)
        src = re.sub(r'[ \t]+$', '', src, flags=re.M)
        src = re.sub(r'\n\s*\n+', '\n', src)
        return src.strip()
    except Exception: return src


def _compile_with_optimizer(in_path, out_path, orig_sname=None):
    try:
        with open(in_path, 'r', encoding='utf-8') as f: original_src = f.read()
        optimized_src = safe_optimize_lua(original_src)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.lua', mode='w', encoding='utf-8')
        tmp.write(optimized_src); tmp.close()
        ok, err, tool = compile_file(tmp.name, out_path, orig_source_name=orig_sname)
        try: os.unlink(tmp.name)
        except: pass
        return ok, err, tool
    except Exception as e: return False, str(e), "optimizer"

def progress_animation(message, duration=0.8):
    steps = 20
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[{ACCENT}]{message}"),
        BarColumn(bar_width=40),
        transient=True,
    ) as progress:
        task = progress.add_task("", total=steps)
        for i in range(steps):
            time.sleep(duration / steps)
            progress.update(task, advance=1)

def section_header(title: str):
    console.print()
    console.print(Rule(f"[bold {GOLD}] // {title} // [/]", style=f"bold {ACCENT}"))
    console.print()

def success(msg):
    console.print(f"[bold {TEAL}]  ✔  {msg}[/]")
def warn(msg):
    console.print(f"[bold {GOLD}]  ⚠  {msg}[/]")
def error(msg):
    console.print(f"[bold {RED}]  ✘  {msg}[/]")
def info(msg):
    console.print(f"[bold {ACCENT}]  ➤  {msg}[/]")

def fmt_size(n: int) -> str:
    if n < 1024:         return f"{n}B"
    elif n < 1024**2:    return f"{n/1024:.1f}KB"
    elif n < 1024**3:    return f"{n/1024**2:.1f}MB"
    else:                return f"{n/1024**3:.2f}GB"

def show_how_to_use():
    clear_screen()
    if _auth_data:
        show_banner(_auth_data)
    else:
        show_banner(None)
    section_header("HOW TO USE")
    guide = """
    [bold yellow]1. UNPACK PAK[/bold yellow]
       - Place your .pak file in [cyan]PAKS/[/cyan] folder
       - Select option 1 from main menu
       - Choose your pak file
       - Confirm if you want to decrypt LUA files
    
    [bold yellow]2. DECRYPT (DECOMPILE) LUA FILES[/bold yellow]
       - After unpacking, decrypted files go to [cyan]DECOMPILED/[/cyan]
       - Original Files goes to [cyan]LUA_ORIGINAL/[/cyan]
       - Edit the [cyan]DECOMPILED/[/cyan] .lua files
    
    [bold yellow]3. COMPILE MODIFIED LUA[/bold yellow]
       - Place edited .lua files in [cyan]EDIT_LUA/<pak_name>/[/cyan]
       - Select option 4 to compile to Files
       - Compiled files go to [cyan]COMPILED/[/cyan]
    
    [bold yellow]4. REPACK PAK[/bold yellow]
       - Select option 2
       - Choose your unpacked folder
       - Confirm compile option
       - Repacked pak saved to [cyan]repacked/[/cyan]
    
    [bold yellow]REQUIREMENTS[/bold yellow]
       - Python 3.8+
       - Java Runtime (for unluac)
       - lua5.3 (for compilation)
    
    [dim]Install on Termux:[/dim]
       [cyan]pkg install python openjdk-17 lua53[/cyan]
       [cyan]pip install rich pycryptodome zstandard gmalg requests psutil[/cyan]
    """
    console.print(Panel(guide, border_style=ACCENT, title="[bold]DOCUMENTATION[/bold]"))
    console.print(f"\n[dim]Press Enter to return...[/dim]")
    input()

# ============================================================
# MAIN MENU
# ============================================================

def _draw_menu():
    W = 50
    title = "Yukioh Ōkami  //  MAIN MENU"
    tp = (W - len(title)) // 2
    console.print(Align.center(f"[bold {ACCENT}]╔{'═'*W}╗[/]"))
    console.print(Align.center(
        f"[bold {ACCENT}]║[/]"
        f"{' ' * tp}[bold {GOLD}]{title}[/bold {GOLD}]"
        f"{' ' * (W - tp - len(title))}"
        f"[bold {ACCENT}]║[/]"
    ))
    console.print(Align.center(f"[bold {ACCENT}]╠{'─'*W}╣[/]"))
    items = [
        ("1", "Unpack PAK File",   ACCENT),
        ("2", "Repack PAK File",   ACCENT),
        ("3", "Decrypt LUA Files", ACCENT),
        ("4", "Compile LUA Files", ACCENT),
        ("5", "How To Use",        DIM),
    ]
    for num, label, lcolor in items:
        content = f"  [{num}]  >>  {label}"
        pad = W - len(content)
        console.print(Align.center(
            f"[bold {ACCENT}]║[/]"
            f"  [bold {GOLD}][{num}][/bold {GOLD}]"
            f"  [bold {lcolor}]>>[/bold {lcolor}]"
            f"  [white]{label}[/white]"
            f"{' ' * max(pad, 1)}"
            f"[bold {ACCENT}]║[/]"
        ))
    console.print(Align.center(f"[bold {ACCENT}]╠{'─'*W}╣[/]"))
    exit_content = f"  [0]  <<  Logout & Exit"
    exit_pad = W - len(exit_content)
    console.print(Align.center(
        f"[bold {ACCENT}]║[/]"
        f"  [bold red][0][/bold red]"
        f"  [bold red]<<[/bold red]"
        f"  [white]Logout & Exit[/white]"
        f"{' ' * max(exit_pad, 1)}"
        f"[bold {ACCENT}]║[/]"
    ))
    console.print(Align.center(f"[bold {ACCENT}]╚{'═'*W}╝[/]"))
    console.print()

def print_main_menu():
    _draw_menu()


def startup_animation():
    clear_screen()
    art_lines = _DEFAULT_BANNER_ART
    steps = [
        ("Initializing Yukioh Ōkami Engine",   0.5),
        ("Loading PAK Modules",          0.4),
        ("Connecting to Auth Panel",      0.6),
        ("Verifying License",             0.5),
    ]
    console.print()
    for line in art_lines:
        console.print(Align.center(f"[bold {ACCENT}]{line}[/]"))
    console.print(Align.center(f"[bold {GOLD}]  ━━━  P A K  +  L U A  T O O L  ━━━[/]"))
    console.print(Align.center(f"[dim]          Online Tool  ·  Built by @Yukira_12[/dim]"))
    console.print()
    for msg, dur in steps:
        with Progress(
            SpinnerColumn(spinner_name="dots", style=f"bold {ACCENT}"),
            TextColumn(f"[bold {ACCENT}]{msg}[/]"),
            BarColumn(bar_width=30, style=ACCENT, complete_style=GOLD),
            TimeElapsedColumn(),
            transient=True,
            console=console,
        ) as prog:
            task = prog.add_task("", total=20)
            for _ in range(20):
                time.sleep(dur / 20)
                prog.update(task, advance=1)
        console.print(Align.center(f"[bold {TEAL}]  [OK]  {msg}[/]"))
    time.sleep(0.3)
    clear_screen()


def _select_pak():
    paks = sorted(PAKS_DIR.glob('*.pak'))
    if not paks:
        warn("No .pak files in PAKS/"); return None
    for i, p in enumerate(paks, 1):
        console.print(f"  [cyan]{i}[/cyan]. {p.name}  ({fmt_size(p.stat().st_size)})")
    try:
        ii = int(Prompt.ask(f"[cyan]  Select PAK[/cyan]")) - 1
        if not (0 <= ii < len(paks)): error("Invalid"); return None
        return paks[ii]
    except ValueError: error("Invalid"); return None


def main():
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
            choice = Prompt.ask(f"[bold {GOLD}]Select option[/bold {GOLD}]").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == '1':
            if not HAS_PAK_DEPS: error("PAK deps missing"); continue
            section_header("UNPACK PAK FILE")
            pak_file = _select_pak()
            if not pak_file: continue

            also_decrypt = Confirm.ask(
                f"\n  [bold cyan]Decrypt LUA files after extraction?[/bold cyan]",
                default=True
            )

            try:
                info(f"Processing: {pak_file.name}")
                progress_animation("Loading PAK structure", 0.8)
                MemoryManager.print_memory_status()
                pak = TencentPakFile(pak_file)
                pak.dump(UNPACKED_DIR, pak_file.stem, also_decrypt=also_decrypt)
                pak.close(); MemoryManager.force_gc()
            except Exception as e:
                error(f"Failed: {e}"); traceback.print_exc()

        elif choice == '2':
            if not HAS_PAK_DEPS: error("PAK deps missing"); continue
            section_header("REPACK PAK FILE")

            valid = [f for f in sorted(UNPACKED_DIR.iterdir())
                     if f.is_dir() and (MANIFEST_DIR / f.name / 'manifest.json').exists()
                     and (PAKS_DIR / f"{f.name}.pak").exists()]
            if not valid: warn("No valid unpacked folders found"); continue
            for i, f in enumerate(valid, 1):
                console.print(f"  [cyan]{i}[/cyan]. {f.name}")
            try:
                ii = int(Prompt.ask("  Select folder")) - 1
                if not (0 <= ii < len(valid)): error("Invalid"); continue
            except ValueError: error("Invalid"); continue

            folder = valid[ii]

            also_compile = Confirm.ask(
                f"\n  [bold cyan]Compile LUA files before repacking?[/bold cyan]",
                default=True
            )

            if also_compile:
                edit_dir = LUA_EDIT_DIR / folder.name
                if not edit_dir.exists() or not list(edit_dir.glob('*.lua')):
                    warn(f"No .lua files found in EDIT_LUA/{folder.name}/")
                    warn(f"Please place edited files here: {edit_dir}")
                    if not Confirm.ask("  Continue without compile?", default=False):
                        continue
                    also_compile = False
                    edit_dir = folder / 'edited'
            else:
                edit_dir = folder / 'edited'

            if not also_compile and not edit_dir.exists():
                warn(f"No 'edited' subfolder in {folder}"); continue

            output_pak = REPACKED_DIR / f'{folder.name}.pak'
            console.print(f"  [cyan]Source:[/cyan] {edit_dir}")
            console.print(f"  [cyan]Output:[/cyan] {output_pak}")
            MemoryManager.print_memory_status()

            if Confirm.ask("[yellow]  Proceed?[/yellow]", default=True):
                try:
                    progress_animation("Preparing repack", 0.5)
                    pak = TencentPakFile(PAKS_DIR / f"{folder.name}.pak")
                    pak.repack(str(edit_dir), output_pak, also_compile=also_compile)
                    pak.close(); MemoryManager.force_gc()
                except Exception as e:
                    error(f"Repack failed: {e}"); traceback.print_exc()

        elif choice == '3':
            section_header("DECRYPT LUA FILES")
            unpacked_folders = [f for f in sorted(UNPACKED_DIR.iterdir()) if f.is_dir()]
            if not unpacked_folders: warn("No unpacked folders found"); continue
            for i, f in enumerate(unpacked_folders, 1):
                lua_count = len(list(f.glob('*.lua')))
                console.print(f"  [cyan]{i}[/cyan]. {f.name}  ({lua_count} lua files)")
            try:
                ii = int(Prompt.ask("  Select folder")) - 1
                if not (0 <= ii < len(unpacked_folders)): error("Invalid"); continue
            except ValueError: error("Invalid"); continue
            folder = unpacked_folders[ii]
            lua_files = list(folder.glob('*.lua'))
            if not lua_files: warn("No .lua files found"); continue
            dec_dir = LUA_DECOMPILED_DIR / folder.name
            orig_dir = LUA_ORIGINAL_DIR / folder.name
            dec_dir.mkdir(parents=True, exist_ok=True)
            orig_dir.mkdir(parents=True, exist_ok=True)
            ok_count = fail_count = 0
            info(f"Decrypting {len(lua_files)} files...")
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as prog:
                task = prog.add_task("Decrypting...", total=len(lua_files))
                for lua_file in lua_files:
                    prog.update(task, advance=1, description=f"[cyan]{lua_file.name[:40]}")
                    shutil.copy2(lua_file, orig_dir / lua_file.name)
                    out_path = dec_dir / lua_file.name
                    ok, err_msg, tool, lines, artifacts = decompile_file(str(lua_file), str(out_path))
                    if ok: ok_count += 1
                    else: fail_count += 1; warn(f"Fail {lua_file.name}: {err_msg}")
            success(f"Decrypted: {ok_count} OK, {fail_count} failed -> {dec_dir}")
            edit_lua_dir = LUA_EDIT_DIR / folder.name
            edit_lua_dir.mkdir(parents=True, exist_ok=True)
            info(f"EDIT_LUA/{folder.name}/ folder ready -> {edit_lua_dir}")

        elif choice == '4':
            section_header("COMPILE LUA FILES")
            edit_folders = [f for f in sorted(LUA_EDIT_DIR.iterdir()) if f.is_dir()] if LUA_EDIT_DIR.exists() else []
            root_lua = list(LUA_EDIT_DIR.glob('*.lua')) if LUA_EDIT_DIR.exists() else []
            if not edit_folders and not root_lua:
                warn(f"No files in EDIT_LUA/ folder: {LUA_EDIT_DIR}"); continue

            if edit_folders:
                for i, f in enumerate(edit_folders, 1):
                    lua_count = len(list(f.glob('*.lua')))
                    console.print(f"  [cyan]{i}[/cyan]. {f.name}  ({lua_count} lua files)")
                console.print(f"  [cyan]{len(edit_folders)+1}[/cyan]. Root EDIT_LUA/  ({len(root_lua)} files)")
                try:
                    ii = int(Prompt.ask("  Select")) - 1
                    if ii == len(edit_folders): src_dir = LUA_EDIT_DIR; stem = "compiled"
                    elif 0 <= ii < len(edit_folders): src_dir = edit_folders[ii]; stem = edit_folders[ii].name
                    else: error("Invalid"); continue
                except ValueError: error("Invalid"); continue
            else:
                src_dir = LUA_EDIT_DIR; stem = "compiled"

            out_dir = LUA_COMPILED_DIR / stem
            out_dir.mkdir(parents=True, exist_ok=True)
            lua_sources = list(src_dir.glob('*.lua'))
            if not lua_sources: warn("No .lua files found"); continue
            info(f"Compiling {len(lua_sources)} files -> {out_dir}")
            ok_count = fail_count = 0
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                          BarColumn(), MofNCompleteColumn(), TimeElapsedColumn()) as prog:
                task = prog.add_task("Compiling...", total=len(lua_sources))
                for src_file in lua_sources:
                    prog.update(task, advance=1, description=f"[cyan]{src_file.name[:40]}")
                    out_bc = out_dir / src_file.name
                    orig_t24 = LUA_ORIGINAL_DIR / stem / src_file.name
                    orig_sname = _extract_source_name_t24(str(orig_t24)) if orig_t24.exists() else None
                    ok, err_msg, tool = _compile_with_optimizer(str(src_file), str(out_bc), orig_sname)
                    if ok: ok_count += 1
                    else: fail_count += 1; warn(f"Fail {src_file.name}: {err_msg}")
            success(f"Compiled: {ok_count} OK, {fail_count} failed -> {out_dir}")

        elif choice == '5':
            show_how_to_use()

        elif choice == '0':
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
            warn("Invalid option. Enter 1, 2, 3, 4, 5, or 0.")

        try:
            Prompt.ask(f"\n[dim]  Press Enter to continue...[/dim]", default="")
        except (KeyboardInterrupt, EOFError):
            break


if __name__ == '__main__':
    main()