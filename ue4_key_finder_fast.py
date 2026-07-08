#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════╗
║              ANDROID UE4 AES/XOR KEY FINDER v2.0                ║
║         Find Lua XOR Key & AES Keys in libUE4.so               ║
║              🇨🇳 Game for Peace / PUBG / BGMI                  ║
║                         ⚡ FAST VERSION ⚡                      ║
║                      (< 1 minute scan)                         ║
║                                                                 ║
║  ⚔️ HIMESHxSlayr | Created by Himesh Shah                      ║
║  🔥 Designed by HIMESHxSlayr                                   ║
║  👑 HIMESHxSlayr Studios                                       ║
║  © HIMESHxSlayr | All Rights Reserved                         ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ============================================================
# CREDITS
# ============================================================

__author__ = "HIMESHxSlayr (Himesh Shah)"
__copyright__ = "© HIMESHxSlayr"
__version__ = "2.0"
__tool_name__ = "UE4 AES/XOR Key Finder"

CREDITS = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              ⚔️ HIMESHxSlayr presents...                         ║
║              🚀 UE4 Key Finder Tool                             ║
║                                                                   ║
║           Created & Developed by Himesh Shah                     ║
║              🔥 HIMESHxSlayr 🔥                                 ║
║                                                                   ║
║           © HIMESHxSlayr | All Rights Reserved                  ║
║           👑 HIMESHxSlayr Studios                               ║
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
# KNOWN XOR KEYS (Quick lookup)
# ============================================================

KNOWN_KEYS = {
    "Game for Peace (GFP)": bytes([
        0xEF, 0xC1, 0x71, 0x3E, 0xE3, 0x34, 0x7D, 0x24,
        0x58, 0xE1, 0x9A, 0x38, 0x4F, 0xA4, 0x6D, 0x08,
        0x64, 0x70, 0xAC, 0xF2, 0xBC, 0xE6, 0x2E, 0x41,
        0x4F, 0x00, 0x83, 0xE7, 0xE7, 0x0B, 0x20, 0x07,
    ]),
    "BGMI 3.8+": bytes([
        0x34, 0x66, 0x25, 0x74, 0x89, 0x78, 0xE4, 0xA9,
        0x5A, 0x41, 0xBC, 0x7A, 0xD6, 0x16, 0x21, 0x23,
        0x4D, 0x61, 0xDA, 0x94, 0x9B, 0xDF, 0x13, 0x3C,
        0x69, 0x3A, 0x31, 0x0A, 0x5F, 0xD7, 0x99, 0x95,
    ]),
    "PUBG Global 4.1": bytes([
        0xE5, 0xB4, 0xED, 0x1D, 0x82, 0x43, 0x7C, 0x5A,
        0x9F, 0x33, 0xA6, 0x8B, 0xD2, 0x4E, 0x71, 0x90,
        0x23, 0x65, 0xAA, 0x0F, 0x8C, 0x47, 0x3B, 0x6A,
        0x4F, 0x00, 0x83, 0xE7, 0xE7, 0x0B, 0x20, 0x07,
    ]),
}

# ============================================================
# OPTIMIZED KEY FINDER
# ============================================================

@dataclass
class FoundKey:
    offset: int
    key: bytes
    key_type: str
    confidence: float
    description: str

class FastKeyFinder:
    def __init__(self, data: bytes):
        self.data = data
        self.size = len(data)
        self.results: List[FoundKey] = []
    
    def search_known_keys(self) -> List[FoundKey]:
        """Quick search for known keys - uses optimized find()"""
        results = []
        for name, key in KNOWN_KEYS.items():
            pos = self.data.find(key)
            if pos != -1:
                results.append(FoundKey(
                    offset=pos,
                    key=key,
                    key_type="Known Key",
                    confidence=1.0,
                    description=f"{name} - Found at 0x{pos:X}"
                ))
        return results
    
    def search_pattern_fast(self, pattern: bytes, description: str = "") -> List[FoundKey]:
        """Fast pattern search using memoryview"""
        results = []
        pos = self.data.find(pattern)
        if pos != -1:
            results.append(FoundKey(
                offset=pos,
                key=b'\x00' * 32,
                key_type="Pattern",
                confidence=0.5,
                description=f"{description} at 0x{pos:X}"
            ))
        return results
    
    def search_lua_headers(self) -> List[FoundKey]:
        """Search for Lua-related patterns (very fast)"""
        results = []
        patterns = [
            (b'\x1bLua', "Lua Magic"),
            (b'\x19\x93\x0d\x0a\x1a\x0a', "LUAC_DATA"),
            (b'LuaXOREncryptor', "Encryptor Class"),
            (b'XOR_KEY', "XOR Key Ref"),
        ]
        for pattern, desc in patterns:
            results.extend(self.search_pattern_fast(pattern, desc))
        return results
    
    def search_common_offsets(self) -> List[FoundKey]:
        """Search common offset ranges where keys are found"""
        results = []
        # Common offset ranges for keys
        ranges = [
            (0x1A00000, 0x1A50000),  # GFP typical
            (0x18D0000, 0x1900000),  # Global typical
            (0x1B00000, 0x1B50000),  # BGMI typical
            (0x1900000, 0x1940000),  # Alternative
        ]
        
        for start, end in ranges:
            if start < self.size and end < self.size:
                chunk = self.data[start:end]
                # Look for 32-byte patterns with good entropy
                for i in range(0, len(chunk) - 31, 4):
                    key = chunk[i:i+32]
                    if self._is_good_key(key):
                        results.append(FoundKey(
                            offset=start + i,
                            key=key,
                            key_type="Offset Range",
                            confidence=0.8,
                            description=f"Potential key in range 0x{start:X}-0x{end:X}"
                        ))
        return results
    
    def _is_good_key(self, data: bytes) -> bool:
        """Quick check if bytes look like a valid key"""
        if len(data) != 32:
            return False
        # Check for reasonable entropy (quick check)
        unique = len(set(data))
        if unique < 8:  # Too few unique bytes
            return False
        # Check not all zeros/ones
        if all(b == 0 for b in data) or all(b == 0xFF for b in data):
            return False
        return True
    
    def search_all_optimized(self) -> List[FoundKey]:
        """Run all searches in optimized order"""
        results = []
        
        # 1. Known keys - fastest
        print(f"{c(Colors.DIM, '   ⚡ Searching known keys...')}")
        results.extend(self.search_known_keys())
        if results:
            print(f"{c(Colors.GREEN, f'   ✅ Found {len(results)} known keys!')}")
        
        # 2. Lua headers
        print(f"{c(Colors.DIM, '   ⚡ Searching Lua headers...')}")
        results.extend(self.search_lua_headers())
        
        # 3. Common offset ranges
        print(f"{c(Colors.DIM, '   ⚡ Searching common offsets...')}")
        results.extend(self.search_common_offsets())
        
        return results

# ============================================================
# MAIN FUNCTIONS
# ============================================================

def print_banner():
    print(f"""
{c(Colors.CYAN, '╔' + '═'*60 + '╗')}
{c(Colors.CYAN, '║')}  {c(Colors.BOLD + Colors.MAGENTA, '🔑 ANDROID UE4 AES/XOR KEY FINDER v2.0')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.GREEN, '⚡ FAST VERSION - < 1 minute scan')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.YELLOW, '🇨🇳 Game for Peace / PUBG / BGMI')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.BOLD + Colors.WHITE, '⚔️ HIMESHxSlayr | Created by Himesh Shah')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '║')}  {c(Colors.DIM, '© HIMESHxSlayr | All Rights Reserved')}  {c(Colors.CYAN, '║')}
{c(Colors.CYAN, '╚' + '═'*60 + '╝')}
    """)

def scan_file_optimized(filepath: str, output: str = None):
    """Optimized file scan"""
    print(f"{c(Colors.CYAN, f'📁 Scanning: {filepath}')}")
    
    if not os.path.isfile(filepath):
        print(f"{c(Colors.RED, f'❌ File not found: {filepath}')}")
        return
    
    try:
        print(f"{c(Colors.DIM, '   Reading file...')}")
        start_time = time.time()
        
        with open(filepath, 'rb') as f:
            data = f.read()
        
        size_mb = len(data) / (1024 * 1024)
        elapsed = time.time() - start_time
        print(f"{c(Colors.GREEN, f'✅ Size: {size_mb:.2f} MB ({len(data):,} bytes) - Read in {elapsed:.1f}s')}")
    except Exception as e:
        print(f"{c(Colors.RED, f'❌ Error reading file: {e}')}")
        return
    
    # Create finder
    finder = FastKeyFinder(data)
    
    # Search for keys
    print(f"\n{c(Colors.YELLOW, '🔍 Searching for keys...')}")
    start_time = time.time()
    results = finder.search_all_optimized()
    elapsed = time.time() - start_time
    
    print(f"{c(Colors.DIM, f'   Scan completed in {elapsed:.1f}s')}")
    
    # Display results
    if not results:
        print(f"{c(Colors.RED, '❌ No keys found!')}")
        print(f"{c(Colors.YELLOW, '💡 Try using IDA Pro to find the key manually.')}")
        print(f"{c(Colors.YELLOW, '   Search for: EF C1 71 3E E3 34 7D 24')}")
        return
    
    print(f"\n{c(Colors.GREEN, f'✅ Found {len(results)} potential keys:')}\n")
    
    for i, r in enumerate(results, 1):
        key_hex = r.key[:32].hex().upper() if len(r.key) >= 32 else r.key.hex().upper()
        print(f"  {i:2d}. {c(Colors.GREEN, f'0x{r.offset:08X}')} {c(Colors.YELLOW, key_hex)}")
        print(f"       {c(Colors.CYAN, f'[{r.key_type}]')} {c(Colors.DIM, r.description)}")
        print()
    
    # Show the best match
    best = max(results, key=lambda x: x.confidence)
    print(f"{c(Colors.BOLD + Colors.GREEN, f'🏆 Best match:')}")
    print(f"  {c(Colors.CYAN, 'Offset:')} 0x{best.offset:08X}")
    print(f"  {c(Colors.CYAN, 'Key:')} {best.key.hex().upper()}")
    print(f"  {c(Colors.CYAN, 'Type:')} {best.key_type}")
    
    # Save results
    if output:
        with open(output, 'w') as f:
            f.write("# UE4 AES/XOR Keys Found\n\n")
            f.write(f"Best Key:\n")
            f.write(f"Offset: 0x{best.offset:08X}\n")
            f.write(f"Key: {best.key.hex().upper()}\n")
            f.write(f"Type: {best.key_type}\n\n")
            f.write("All Results:\n")
            f.write("-" * 40 + "\n")
            for r in results:
                f.write(f"Offset: 0x{r.offset:08X}\n")
                f.write(f"Key: {r.key.hex().upper()}\n")
                f.write(f"Type: {r.key_type}\n")
                f.write(f"Description: {r.description}\n")
                f.write("-" * 30 + "\n")
        print(f"\n{c(Colors.GREEN, f'✅ Results saved to: {output}')}")
    
    # Show known keys for comparison
    print(f"\n{c(Colors.YELLOW, '📋 Known keys for reference:')}")
    for name, key in KNOWN_KEYS.items():
        print(f"  {c(Colors.CYAN, name)}: {c(Colors.DIM, key.hex().upper())}")

def main():
    print_banner()
    
    print(f"{c(Colors.CYAN, '📋 Interactive Mode')}")
    print(f"  {c(Colors.YELLOW, '1.')} Scan local file (FAST)")
    print(f"  {c(Colors.YELLOW, '2.')} Exit")
    
    choice = input(f"\n{c(Colors.CYAN, 'Select option (1-2): ')}").strip()
    
    if choice == '1':
        filepath = input(f"{c(Colors.CYAN, 'Enter file path: ')}").strip()
        if not filepath:
            filepath = "libUE4.so"
            print(f"{c(Colors.DIM, f'   Using default: {filepath}')}")
        scan_file_optimized(filepath, "ue4_keys.txt")
    
    elif choice == '2':
        print(f"{c(Colors.GREEN, '👋 Goodbye!')}")
    
    else:
        print(f"{c(Colors.RED, '❌ Invalid choice')}")

if __name__ == "__main__":
    print(f"\n{c(Colors.DIM, '🔥 Powered by HIMESHxSlayr')}")
    main()