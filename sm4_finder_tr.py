import sys
import os
import time
from pathlib import Path
from collections import defaultdict

# --- Renk Kodları (Hatalar Giderildi) ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'  # Eksik olan renk eklendi
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def draw_progress_bar(current, total, filename, length=25):
    """Ekranda dinamik ilerleme çubuğu ve info gösterir"""
    percent = ("{0:.1f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    # \r ile satırı başa sarıp güncelliyoruz
    sys.stdout.write(f'\r{Colors.CYAN}[BİLGİ]{Colors.ENDC} {filename[:15]} |{bar}| {percent}% ')
    sys.stdout.flush()

# --- SM4 Analiz Fonksiyonları ---
def is_sm4_new_candidate(s):
    if len(s) != 20: return False
    for i in range(20):
        pos = i % 3
        if pos == 0 and not s[i].islower(): return False
        elif pos == 1 and not s[i].isupper(): return False
        elif pos == 2 and not s[i].isdigit(): return False
    return True

def is_sm4_4_candidate(s):
    if len(s) != 20: return False
    u = sum(1 for c in s if c.isupper())
    l = sum(1 for c in s if c.islower())
    d = sum(1 for c in s if c.isdigit())
    return d >= 10 and l >= 5 and u == 0 and all(c.isalnum() for c in s)

def is_sm4_2_candidate(s):
    if len(s) != 20: return False
    u = sum(1 for c in s if c.isupper())
    l = sum(1 for c in s if c.islower())
    d = sum(1 for c in s if c.isdigit())
    s_char = sum(1 for c in s if c in '$*')
    return s_char >= 1 and u >= 5 and l >= 3 and d >= 1

def scan_file_with_bar(filepath):
    """Dosyayı parçalar halinde okuyarak barı günceller"""
    results = {'SM4_SECRET_4': [], 'SM4_SECRET_2': [], 'SM4_SECRET_NEW': []}
    try:
        content = filepath.read_bytes()
        total_len = len(content)
        target_len = 20
        
        # UTF-16LE araması
        for i in range(0, total_len - (target_len * 2), 2):
            # Her 500.000 byte'da bir barı güncelle (Performans için)
            if i % 500000 == 0:
                draw_progress_bar(i, total_len, filepath.name)
            
            chunk = content[i:i + target_len * 2]
            if all(b == 0 for b in chunk[1::2]) and all(32 <= b < 127 for b in chunk[0::2]):
                s = bytes(chunk[0::2]).decode('ascii', errors='ignore')
                if ' ' not in s:
                    if is_sm4_4_candidate(s): results['SM4_SECRET_4'].append(s)
                    elif is_sm4_2_candidate(s): results['SM4_SECRET_2'].append(s)
                    elif is_sm4_new_candidate(s): results['SM4_SECRET_NEW'].append(s)
        
        draw_progress_bar(total_len, total_len, filepath.name)
        print(f" {Colors.GREEN}TAMAMLANDI!{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}Hata: {e}{Colors.ENDC}")
    return results

def scan_folder_process():
    input_path = input(f"\n{Colors.GREEN}Klasör Yolu > {Colors.ENDC}").strip()
    folder = Path(input_path) if input_path else Path(".")
    
    if not folder.exists():
        print(f"{Colors.FAIL}Hata: Yol bulunamadı!{Colors.ENDC}")
        return

    so_files = list(folder.glob("**/*.so"))
    if not so_files:
        print(f"{Colors.FAIL}Hata: Hiç .so dosyası yok!{Colors.ENDC}")
        return

    print(f"\n{Colors.BOLD}{Colors.CYAN}Toplam {len(so_files)} dosya işleniyor...{Colors.ENDC}")
    
    all_secrets = defaultdict(set)
    for idx, so_file in enumerate(so_files, 1):
        print(f"{Colors.YELLOW}[{idx}/{len(so_files)}]{Colors.ENDC}", end=" ")
        file_results = scan_file_with_bar(so_file)
        
        for k, v in file_results.items():
            for secret in v:
                all_secrets[k].add(secret)

    # --- Sonuç Raporu ---
    print(f"\n{Colors.BOLD}{'='*50}\n         TARAMA SONUÇLARI\n{'='*50}{Colors.ENDC}")
    
    if not any(all_secrets.values()):
        print(f"{Colors.FAIL}Hiçbir anahtar bulunamadı.{Colors.ENDC}")
    else:
        for key_type in ['SM4_SECRET_4', 'SM4_SECRET_2', 'SM4_SECRET_NEW']:
            secrets = sorted(all_secrets[key_type])
            if secrets:
                print(f"\n{Colors.YELLOW}{key_type}:{Colors.ENDC}")
                for s in secrets:
                    print(f"  {Colors.GREEN}»{Colors.ENDC} '{s}'")

    input(f"\n{Colors.BLUE}Menüye dönmek için Enter'a bas...{Colors.ENDC}")

def main():
    while True:
        os.system('clear')
        print(f"{Colors.CYAN}{Colors.BOLD}==================================================")
        print("      SM4 ANAHTAR ARAMA TOOL PUBG MOBİLE RPAD")
        print(f"=================================================={Colors.ENDC}")
        print("1. Klasör Tara (.so dosyaları)")
        print("2. Çıkış")
        
        choice = input(f"\n{Colors.GREEN}Seçiminiz > {Colors.ENDC}")
        if choice == '1':
            scan_folder_process()
        elif choice == '2':
            break

if __name__ == "__main__":
    main()
