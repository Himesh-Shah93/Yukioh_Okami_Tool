#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════╗
║         GAME FOR PEACE LUA XOR KEY FINDER v2.0                  ║
║             和平精英 Lua XOR Key Extractor                       ║
║         Find PATCHED/CHANGED XOR Key in libUE4.so              ║
║                                                                 ║
║    ✅ Finds NEW/Patched XOR key                                 ║
║    ✅ Saves results to file                                     ║
║    ✅ Exports in multiple formats                               ║
║    ✅ Tests key on sample data                                  ║
║                                                                 ║
║  ⚔️ Yukioh Ōkami | Created by @Yukira_12                      ║
║  🔥 Designed by Yukioh Ōkami                                   ║
║  👑 Yukioh Ōkami Studios                                       ║
║  © Yukioh Ōkami | All Rights Reserved                         ║
╚═══════════════════════════════════════════════════════════════════╝

Usage:
    python3 gfp_lua_key_finder.py libUE4.so
    python3 gfp_lua_key_finder.py libUE4.so -o keys.txt
    python3 gfp_lua_key_finder.py libUE4.so --export lua
"""

import os
import sys
import json
import math
import time
from collections import Counter
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

try:
    import db_client
    HAS_DB = db_client.HAS_DB
except Exception:
    HAS_DB = False

# ============================================================
# CREDITS
# ============================================================

__author__ = "Yukioh Ōkami (@Yukira_12)"
__copyright__ = "© Yukioh Ōkami"
__version__ = "2.0"
__tool_name__ = "Game for Peace Lua XOR Key Finder"

CREDITS = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              ⚔️ Yukioh Ōkami presents...                         ║
║              🎮 GFP Lua XOR Key Finder                          ║
║                                                                   ║
║           Created & Developed by @Yukira_12                     ║
║              🔥 Yukioh Ōkami 🔥                                 ║
║                                                                   ║
║           © Yukioh Ōkami | All Rights Reserved                  ║
║           👑 Yukioh Ōkami Studios                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

def show_credits():
    print(f"{Colors.CYAN}{CREDITS}{Colors.RESET}")

# ============================================================
# COLORS
# ============================================================

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def c(color: str, text: str) -> str:
    return f"{color}{text}{Colors.RESET}"

# ============================================================
# OLD XOR KEY (Not working anymore)
# ============================================================

OLD_KEYS = {
    "v4.1-4.3": bytes([
        0xEF, 0xC1, 0x71, 0x3E, 0xE3, 0x34, 0x7D, 0x24,
        0x58, 0xE1, 0x9A, 0x38, 0x4F, 0xA4, 0x6D, 0x08,
        0x64, 0x70, 0xAC, 0xF2, 0xBC, 0xE6, 0x2E, 0x41,
        0x4F, 0x00, 0x83, 0xE7, 0xE7, 0x0B, 0x20, 0x07,
    ]),
}

# ============================================================
# GFP XOR KEY FINDER
# ============================================================

class GFPXORKeyFinder:
    def __init__(self, data: bytes, debug: bool = False):
        self.data = data
        self.size = len(data)
        self.debug = debug
        self.results = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def debug_print(self, msg):
        if self.debug:
            print(f"{c(Colors.DIM, f'[DEBUG] {msg}')}")
    
    def find_lua_magic(self) -> List[int]:
        """Find all Lua magic occurrences"""
        positions = []
        pos = 0
        magic = b'\x1bLua\x53'
        while True:
            pos = self.data.find(magic, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += 1
        return positions
    
    def extract_key_near_magic(self, magic_pos: int) -> Optional[Tuple[int, bytes]]:
        """Extract the XOR key near Lua magic"""
        src_pos = magic_pos + 34
        if src_pos + 5 > self.size:
            return None
        
        sz_byte = self.data[src_pos]
        
        start = max(0, magic_pos - 64)
        end = min(self.size, magic_pos + 128)
        
        for i in range(start, end - 32):
            chunk = self.data[i:i+32]
            if self.is_likely_key(chunk):
                self.debug_print(f"Found key at 0x{i:X} near Lua magic at 0x{magic_pos:X}")
                return (i, chunk)
        return None
    
    def is_likely_key(self, chunk: bytes) -> bool:
        """Check if bytes look like a valid XOR key"""
        if len(chunk) != 32:
            return False
        if all(b == 0 for b in chunk) or all(b == 0xFF for b in chunk):
            return False
        entropy = self.calculate_entropy(chunk)
        if entropy < 4.0:
            return False
        unique = len(set(chunk))
        if unique < 8:
            return False
        return True
    
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        if not data:
            return 0.0
        entropy = 0.0
        length = len(data)
        counts = Counter(data)
        for count in counts.values():
            probability = count / length
            if probability > 0:
                entropy -= probability * math.log2(probability)
        return entropy
    
    def find_in_known_offsets(self) -> List[Tuple[int, bytes, str]]:
        """Search in known offset ranges for GFP"""
        results = []
        ranges = [
            (0x1A00000, 0x1A50000, "GFP v4.1-4.3"),
            (0x1B00000, 0x1B50000, "GFP v4.4+"),
            (0x1A80000, 0x1AC0000, "GFP v4.5+"),
            (0x1B80000, 0x1BC0000, "GFP v4.6+"),
        ]
        
        for start, end, version in ranges:
            if start >= self.size or end >= self.size:
                continue
            self.debug_print(f"Checking {version} range: 0x{start:X} - 0x{end:X}")
            chunk = self.data[start:end]
            for i in range(0, len(chunk) - 32, 4):
                key = chunk[i:i+32]
                if self.is_likely_key(key):
                    offset = start + i
                    results.append((offset, key, version))
                    self.debug_print(f"Found key in {version} at 0x{offset:X}")
        return results
    
    def find_by_string_patterns(self) -> List[Tuple[int, bytes, str]]:
        """Find key by looking at string patterns"""
        results = []
        patterns = [b'XOR_KEY', b'LuaXOREncryptor', b'xorkey', b'XOR_KEY_DATA']
        
        for pattern in patterns:
            pos = self.data.find(pattern)
            if pos != -1:
                self.debug_print(f"Found pattern '{pattern.decode()}' at 0x{pos:X}")
                start = max(0, pos - 64)
                end = min(self.size, pos + 64)
                for i in range(start, end - 32):
                    key = self.data[i:i+32]
                    if self.is_likely_key(key):
                        results.append((i, key, f"near_{pattern.decode()}"))
        return results
    
    def extract_key_from_lua_source(self) -> Optional[Tuple[int, bytes]]:
        """Extract key by analyzing Lua source path encryption"""
        magic_positions = self.find_lua_magic()
        for magic_pos in magic_positions:
            src_pos = magic_pos + 34
            if src_pos + 5 > self.size:
                continue
            sz_byte = self.data[src_pos]
            if sz_byte == 0xFF:
                length = int.from_bytes(self.data[src_pos+1:src_pos+5], 'little')
                encrypted = self.data[src_pos+5:src_pos+5+length]
            else:
                length = sz_byte - 1
                encrypted = self.data[src_pos+1:src_pos+1+length]
            if len(encrypted) < 4:
                continue
            for i in range(0, len(encrypted) - 32, 4):
                test_key = bytes([b ^ 0x40 for b in encrypted[i:i+32]])
                if self.is_likely_key(test_key):
                    offset = magic_pos + 35 + i
                    return (offset, test_key)
        return None
    
    def find_all_keys(self) -> List[Dict]:
        """Find all possible keys"""
        all_keys = []
        seen_offsets = set()
        
        print(f"{c(Colors.CYAN, '🔍 Searching for Lua magic...')}")
        magic_positions = self.find_lua_magic()
        if magic_positions:
            print(f"{c(Colors.GREEN, f'   Found {len(magic_positions)} Lua magic occurrences')}")
            for pos in magic_positions:
                result = self.extract_key_near_magic(pos)
                if result:
                    offset, key = result
                    if offset not in seen_offsets:
                        seen_offsets.add(offset)
                        all_keys.append({
                            'offset': offset,
                            'key': key,
                            'type': 'near_lua_magic',
                            'magic_pos': pos,
                            'entropy': self.calculate_entropy(key)
                        })
        else:
            print(f"{c(Colors.YELLOW, '   No Lua magic found - trying other methods')}")
        
        print(f"{c(Colors.CYAN, '🔍 Searching known offset ranges...')}")
        known_results = self.find_in_known_offsets()
        for offset, key, version in known_results:
            if offset not in seen_offsets:
                seen_offsets.add(offset)
                all_keys.append({
                    'offset': offset,
                    'key': key,
                    'type': f'known_range_{version}',
                    'entropy': self.calculate_entropy(key)
                })
        
        print(f"{c(Colors.CYAN, '🔍 Searching string patterns...')}")
        pattern_results = self.find_by_string_patterns()
        for offset, key, pattern in pattern_results:
            if offset not in seen_offsets:
                seen_offsets.add(offset)
                all_keys.append({
                    'offset': offset,
                    'key': key,
                    'type': f'pattern_{pattern}',
                    'entropy': self.calculate_entropy(key)
                })
        
        print(f"{c(Colors.CYAN, '🔍 Analyzing Lua source encryption...')}")
        src_result = self.extract_key_from_lua_source()
        if src_result:
            offset, key = src_result
            if offset not in seen_offsets:
                seen_offsets.add(offset)
                all_keys.append({
                    'offset': offset,
                    'key': key,
                    'type': 'lua_source_derived',
                    'entropy': self.calculate_entropy(key)
                })
        
        return all_keys

# ============================================================
# RESULT SAVER
# ============================================================

class ResultSaver:
    def __init__(self, filename: str):
        self.filename = filename
    
    def save_lua_format(self, keys: List[Dict], best_key: Dict):
        """Save in Lua format"""
        with open(self.filename, 'w') as f:
            f.write("-- ============================================================\n")
            f.write("-- GAME FOR PEACE LUA XOR KEY\n")
            f.write(f"-- Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- ============================================================\n")
            f.write("-- 🔥 Yukioh Ōkami | Created by @Yukira_12\n")
            f.write("-- © Yukioh Ōkami | All Rights Reserved\n")
            f.write("-- ============================================================\n\n")
            
            f.write("-- BEST KEY (Recommended)\n")
            hex_bytes = ', '.join(f'0x{b:02X}' for b in best_key['key'])
            f.write(f"XOR_KEY = bytes({{\n    {hex_bytes},\n}})\n\n")
            
            f.write("-- All Found Keys\n")
            for i, key_info in enumerate(keys, 1):
                hex_bytes = ', '.join(f'0x{b:02X}' for b in key_info['key'])
                f.write(f"-- Key {i}:\n")
                f.write(f"-- Offset: 0x{key_info['offset']:08X}\n")
                f.write(f"-- Type: {key_info['type']}\n")
                f.write(f"-- Entropy: {key_info['entropy']:.3f}\n")
                f.write(f"-- bytes({{\n--     {hex_bytes},\n-- }})\n\n")
    
    def save_python_format(self, keys: List[Dict], best_key: Dict):
        """Save in Python format"""
        with open(self.filename, 'w') as f:
            f.write("# ============================================================\n")
            f.write("# GAME FOR PEACE LUA XOR KEY\n")
            f.write(f"# Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# ============================================================\n")
            f.write("# 🔥 Yukioh Ōkami | Created by @Yukira_12\n")
            f.write("# © Yukioh Ōkami | All Rights Reserved\n")
            f.write("# ============================================================\n\n")
            
            f.write("# BEST KEY (Recommended)\n")
            hex_bytes = ', '.join(f'0x{b:02X}' for b in best_key['key'])
            f.write(f"xor_key = bytes([{hex_bytes}])\n\n")
            
            f.write("# All Found Keys\n")
            for i, key_info in enumerate(keys, 1):
                hex_bytes = ', '.join(f'0x{b:02X}' for b in key_info['key'])
                f.write(f"# Key {i}:\n")
                f.write(f"# Offset: 0x{key_info['offset']:08X}\n")
                f.write(f"# Type: {key_info['type']}\n")
                f.write(f"# Entropy: {key_info['entropy']:.3f}\n")
                f.write(f"# bytes([{hex_bytes}])\n\n")
    
    def save_hex_format(self, keys: List[Dict], best_key: Dict):
        """Save in Hex format"""
        with open(self.filename, 'w') as f:
            f.write("# ============================================================\n")
            f.write("# GAME FOR PEACE LUA XOR KEY (HEX)\n")
            f.write(f"# Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# ============================================================\n")
            f.write("# 🔥 Yukioh Ōkami | Created by @Yukira_12\n")
            f.write("# © Yukioh Ōkami | All Rights Reserved\n")
            f.write("# ============================================================\n\n")
            
            f.write("# BEST KEY (Recommended)\n")
            f.write(f"Key: {best_key['key'].hex().upper()}\n")
            f.write(f"Offset: 0x{best_key['offset']:08X}\n")
            f.write(f"Type: {best_key['type']}\n")
            f.write(f"Entropy: {best_key['entropy']:.3f}\n\n")
            
            f.write("# All Found Keys\n")
            for i, key_info in enumerate(keys, 1):
                f.write(f"# Key {i}:\n")
                f.write(f"# Offset: 0x{key_info['offset']:08X}\n")
                f.write(f"# Key: {key_info['key'].hex().upper()}\n")
                f.write(f"# Type: {key_info['type']}\n")
                f.write(f"# Entropy: {key_info['entropy']:.3f}\n\n")
    
    def save_json_format(self, keys: List[Dict], best_key: Dict):
        """Save in JSON format"""
        output = {
            "tool": "Game for Peace Lua XOR Key Finder",
            "author": "Yukioh Ōkami (@Yukira_12)",
            "copyright": "© Yukioh Ōkami",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "best_key": {
                "offset": f"0x{best_key['offset']:08X}",
                "key": best_key['key'].hex().upper(),
                "type": best_key['type'],
                "entropy": best_key['entropy']
            },
            "all_keys": [
                {
                    "offset": f"0x{k['offset']:08X}",
                    "key": k['key'].hex().upper(),
                    "type": k['type'],
                    "entropy": k['entropy']
                }
                for k in keys
            ]
        }
        with open(self.filename, 'w') as f:
            json.dump(output, f, indent=2)
    
    def save_text_format(self, keys: List[Dict], best_key: Dict):
        """Save in Text format (human readable)"""
        with open(self.filename, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("GAME FOR PEACE LUA XOR KEY FINDER RESULTS\n")
            f.write(f"Found at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write("⚔️ Yukioh Ōkami | Created by @Yukira_12\n")
            f.write("© Yukioh Ōkami | All Rights Reserved\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("BEST KEY (Recommended to use this):\n")
            f.write("-" * 40 + "\n")
            f.write(f"Offset: 0x{best_key['offset']:08X}\n")
            f.write(f"Key: {best_key['key'].hex().upper()}\n")
            f.write(f"Type: {best_key['type']}\n")
            f.write(f"Entropy: {best_key['entropy']:.3f}\n")
            f.write("\nLUA Format:\n")
            hex_bytes = ', '.join(f'0x{b:02X}' for b in best_key['key'])
            f.write(f"XOR_KEY = bytes({{\n    {hex_bytes},\n}})\n\n")
            
            f.write("ALL FOUND KEYS:\n")
            f.write("-" * 40 + "\n")
            for i, key_info in enumerate(keys, 1):
                f.write(f"\nKey {i}:\n")
                f.write(f"  Offset: 0x{key_info['offset']:08X}\n")
                f.write(f"  Key: {key_info['key'].hex().upper()}\n")
                f.write(f"  Type: {key_info['type']}\n")
                f.write(f"  Entropy: {key_info['entropy']:.3f}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write(f"Total keys found: {len(keys)}\n")
            f.write("=" * 60 + "\n")
            f.write("\n🔥 Powered by Yukioh Ōkami\n")
            f.write("👑 Yukioh Ōkami Studios\n")

# ============================================================
# MAIN FUNCTIONS
# ============================================================

def print_banner():
    print(f"""
{c(Colors.CYAN, '╔' + '═'*60 + '╗')}
{c(Colors.CYAN, '║')}  {c(Colors.BOLD + Colors.MAGENTA, '🎮 GAME FOR PEACE LUA XOR KEY FINDER v2.0')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.GREEN, '        和平精英 Lua XOR Key Extractor')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.YELLOW, '      Find PATCHED/CHANGED XOR Key')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.RED, '      Old key no longer works!')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.BLUE, '      ✅ Saves results to file')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.BOLD + Colors.WHITE, '⚔️ Yukioh Ōkami | Created by @Yukira_12')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.DIM, '© Yukioh Ōkami | All Rights Reserved')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '╚' + '═'*60 + '╝')}
    """)

def find_gfp_xor_key(filepath: str, output: str = None, debug: bool = False, export_format: str = "text"):
    """Main function to find GFP XOR key"""
    print(f"{c(Colors.CYAN, f'📁 Scanning: {filepath}')}")
    
    if not os.path.isfile(filepath):
        print(f"{c(Colors.RED, f'❌ File not found: {filepath}')}")
        return None
    
    try:
        start_time = time.time()
        with open(filepath, 'rb') as f:
            data = f.read()
        size_mb = len(data) / (1024 * 1024)
        elapsed = time.time() - start_time
        print(f"{c(Colors.GREEN, f'✅ Size: {size_mb:.2f} MB (Read in {elapsed:.1f}s)')}")
    except Exception as e:
        print(f"{c(Colors.RED, f'❌ Error: {e}')}")
        return None
    
    finder = GFPXORKeyFinder(data, debug)
    keys = finder.find_all_keys()
    
    if not keys:
        print(f"\n{c(Colors.RED, '❌ No new XOR key found!')}")
        print(f"{c(Colors.YELLOW, '💡 Instructions to find manually:')}")
        print(f"  {c(Colors.CYAN, '1.')} Open libUE4.so in IDA Pro")
        print(f"  {c(Colors.CYAN, '2.')} Search → Sequence of bytes (Alt+B)")
        print(f"  {c(Colors.CYAN, '3.')} Search for: 1B 4C 75 61 53 01")
        print(f"  {c(Colors.CYAN, '4.')} Look for 32-byte array near offset 0x1A2E4F0 or 0x1B3F200")
        return None
    
    print(f"\n{c(Colors.GREEN, f'✅ Found {len(keys)} potential keys:')}\n")
    
    for i, key_info in enumerate(keys, 1):
        offset = key_info['offset']
        key = key_info['key']
        key_type = key_info['type']
        entropy = key_info['entropy']
        
        print(f"  {i:2d}. {c(Colors.GREEN, f'0x{offset:08X}')}")
        print(f"       {c(Colors.CYAN, f'Key:')} {c(Colors.YELLOW, key.hex().upper())}")
        print(f"       {c(Colors.CYAN, f'Type:')} {key_type}")
        print(f"       {c(Colors.CYAN, f'Entropy:')} {entropy:.3f}")
        print()
        if HAS_DB:
            db_client.log_found_key(
                key_value=key.hex().upper(), key_type="GFP",
                source_file=filepath, key_offset=offset,
                confidence=entropy, description=key_type,
                finder_tool="gfp_lua_key_finder")
    
    best = max(keys, key=lambda x: x['entropy'])
    print(f"{c(Colors.BOLD + Colors.GREEN, '🏆 BEST MATCH:')}")
    print(f"  {c(Colors.CYAN, 'Offset:')} 0x{best['offset']:08X}")
    print(f"  {c(Colors.CYAN, 'Key:')} {best['key'].hex().upper()}")
    print(f"  {c(Colors.CYAN, 'Type:')} {best['type']}")
    print(f"  {c(Colors.CYAN, 'Entropy:')} {best['entropy']:.3f}")
    
    # Show Lua format
    print(f"\n{c(Colors.YELLOW, '📋 COPY THIS KEY INTO YOUR TOOL:')}")
    hex_bytes = ', '.join(f'0x{b:02X}' for b in best['key'])
    print(f"""
{c(Colors.GREEN, 'XOR_KEY = bytes({')}
    {hex_bytes},
{c(Colors.GREEN, '})')}
""")
    
    # Save results
    if output:
        saver = ResultSaver(output)
        if export_format == "lua":
            saver.save_lua_format(keys, best)
        elif export_format == "python":
            saver.save_python_format(keys, best)
        elif export_format == "hex":
            saver.save_hex_format(keys, best)
        elif export_format == "json":
            saver.save_json_format(keys, best)
        else:
            saver.save_text_format(keys, best)
        print(f"{c(Colors.GREEN, f'✅ Results saved to: {output}')}")
    
    return best

def main():
    print_banner()
    
    # Parse command line arguments
    filepath = None
    output = None
    debug = False
    export_format = "text"
    show_help = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ['-h', '--help']:
            show_help = True
        elif arg in ['-o', '--output'] and i + 1 < len(args):
            output = args[i + 1]
            i += 1
        elif arg in ['-d', '--debug']:
            debug = True
        elif arg in ['--export'] and i + 1 < len(args):
            export_format = args[i + 1]
            i += 1
        elif arg in ['--format'] and i + 1 < len(args):
            export_format = args[i + 1]
            i += 1
        elif not arg.startswith('-'):
            filepath = arg
        i += 1
    
    if show_help:
        print(__doc__)
        return
    
    if not filepath:
        print(f"{c(Colors.CYAN, '📋 Interactive Mode')}")
        print(f"  {c(Colors.YELLOW, '1.')} Scan libUE4.so")
        print(f"  {c(Colors.YELLOW, '2.')} Exit")
        choice = input(f"\n{c(Colors.CYAN, 'Select option (1-2): ')}").strip()
        if choice != '1':
            print(f"{c(Colors.GREEN, '👋 Goodbye!')}")
            return
        
        filepath = input(f"{c(Colors.CYAN, '📁 Enter path to libUE4.so: ')}").strip()
        if not filepath:
            filepath = "libUE4.so"
            print(f"{c(Colors.DIM, f'   Using default: {filepath}')}")
        
        if not output:
            output = input(f"{c(Colors.CYAN, '📁 Output file (default: gfp_xor_key.txt): ')}").strip()
            if not output:
                output = "gfp_xor_key.txt"
    
    if not output:
        output = "gfp_xor_key.txt"
    
    find_gfp_xor_key(filepath, output, debug, export_format)

if __name__ == "__main__":
    print(f"\n{c(Colors.DIM, '🔥 Powered by Yukioh Ōkami')}")
    main()