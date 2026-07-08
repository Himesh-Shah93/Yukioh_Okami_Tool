

# SM4 KEYS PUBG FINDER
# @YUKIRA12

import os
import subprocess
import sys
from colorama import Fore, Style, init

init(autoreset=True)

LIBRARY = "libUE4.so"
DATABASE = "YUKIRA12_sm4_keys.txt"
LENGTH = 20

class ByteSequenceAnalyzer:
    def __init__(self, path):
        self.path = path

    def collect_wide_strings(self):
        cmd = ["strings", "-el", self.path]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return [s.strip() for s in proc.stdout.splitlines() if s.strip()]

    def collect_embedded_keys(self):
        try:
            with open(self.path, 'rb') as f:
                blob = f.read()

            results = set()
            cursor = 0
            while cursor < len(blob) - 44:
                if blob[cursor] == 0 and blob[cursor + 1] == 0:
                    segment = b''
                    valid = True
                    ptr = cursor + 2

                    for _ in range(LENGTH):
                        if ptr + 1 >= len(blob):
                            valid = False
                            break
                        char_val = blob[ptr]
                        null_val = blob[ptr + 1]
                        symbol = chr(char_val) if 32 <= char_val < 127 else None
                        if symbol is None or null_val != 0:
                            valid = False
                            break
                        if not (symbol.isalnum() or symbol in '$*'):
                            valid = False
                            break
                        segment += bytes([char_val])
                        ptr += 2

                    if valid and ptr + 1 < len(blob) and blob[ptr] == 0 and blob[ptr + 1] == 0:
                        try:
                            results.add(segment.decode('ascii'))
                        except:
                            pass
                    cursor += 1
                else:
                    cursor += 1
            return list(results)
        except Exception:
            return []

class SequenceEvaluator:
    def __init__(self, wide_strings, embedded_keys=None):
        self.wide_strings = wide_strings
        self.embedded_keys = embedded_keys if embedded_keys else []
        self.collected = set()

    def longest_alpha_streak(self, seq):
        best = cur = 0
        for ch in seq:
            if ch.isalpha():
                cur += 1
                best = max(best, cur)
            else:
                cur = 0
        return best

    def unique_fraction(self, seq):
        return len(set(seq)) / len(seq)

    def is_plausible(self, seq):
        if len(seq) != LENGTH:
            return False
        if any(not (c.isalnum() or c in "$*") for c in seq):
            return False
        if seq.isalpha():
            return False
        if not any(c.isdigit() or c in "$*" for c in seq):
            return False
        if self.longest_alpha_streak(seq) > 9:
            return False
        if self.unique_fraction(seq) < 0.6:
            return False
        return True

    def process(self):
        for s in self.wide_strings:
            s = s.strip()
            if self.is_plausible(s):
                self.collected.add(s)
        for k in self.embedded_keys:
            if self.is_plausible(k):
                self.collected.add(k)
        return sorted(self.collected)

    def persist(self, output, found):
        existing = set()
        if os.path.isfile(output):
            with open(output, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("===="):
                        continue
                    existing.add(line.split("  = ")[0].strip())

        lib_count = len(found)
        prior = len(existing)
        new = [k for k in found if k not in existing]

        print(Fore.YELLOW + f"[*] Keys extracted: {lib_count}")
        if not lib_count:
            print(Fore.RED + "[!] No valid keys.")
            return
    
        print(Fore.CYAN + "\n[+] SM4_KEY_FOUND:")
        for k in found:
            print(f"    {k}")

        if not new:
            print(Fore.GREEN + f"[*] Database total: {prior}")
            return

        with open(output, "a", encoding="utf-8") as f:
            if os.path.getsize(output) == 0:
                f.write("==== YUKIRA12 SM4 TOOL FINDER====\n")
            for k in new:
                f.write(k + "\n")

        print(Fore.CYAN + "\n[+] SM4_KEY_FOUND:")
        for k in new:
            print(f"    {k}")

def main():
    print(Fore.MAGENTA + Style.BRIGHT + ":: YUKIRA12 SM4 KEY FINDER TOOL ::")

    if not os.path.isfile(LIBRARY):
        print(Fore.RED + f"[ERROR] Missing {LIBRARY}")
        sys.exit(1)

    print(Fore.GREEN + f"[+] Target: {LIBRARY}")

    analyzer = ByteSequenceAnalyzer(LIBRARY)
    wide = analyzer.collect_wide_strings()
    embedded = analyzer.collect_embedded_keys()

    evaluator = SequenceEvaluator(wide, embedded)
    results = evaluator.process()
    evaluator.persist(DATABASE, results)

if __name__ == "__main__":
    main()