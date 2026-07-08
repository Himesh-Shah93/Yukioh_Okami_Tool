# 🐺 Yukioh_Ōkami — PUBG/BGMI PAK Modding Tool

**Complete PAK + LUA workflow: Unpack → Decrypt → Edit → Compile → Repack**

---

## 📌 Features

- ✅ **Unpack** PAK / OBB files (PUBG Mobile / BGMI)
- ✅ **Repack** modified files back to working PAK
- ✅ **LUA decompilation** – convert bytecode to readable source
- ✅ **LUA compilation** – turn edited source back to bytecode
- ✅ **Auto-decrypt** LUA files during unpack (optional)
- ✅ **Auto-compile** before repacking (optional)
- ✅ **Memory‑efficient** – uses mmap for large files
- ✅ **Online license system** – secure activation
- ✅ **Telegram integration** for debugging (optional)
- ✅ **120 FPS patch** support (via GAMEPATCH folder structure)

---

## 📁 Folder Structure (auto-created)

```

~/Yukioh_Okami_Tool/
├── PAKS/              ← place .pak files here
├── unpacked/          ← extracted files go here
├── repacked/          ← final repacked .pak output
├── Manifest/          ← manifest files (mapping)
├── LUA_ORIGINAL/      ← original .lua bytecode (backup)
├── DECOMPILED/        ← decompiled .lua source
├── EDIT_LUA/          ← place your edited .lua files here
├── COMPILED/          ← compiled bytecode ready for repack
└── config.json        ← saved license key (auto-generated)

```

---

## 🚀 Installation (Termux)

### Quick install (recommended)

```bash
bash <(curl -s https://raw.githubusercontent.com/Himesh-Shah93/Yukioh_Okami_Tool/main/install.sh)
```

Manual install

```bash
git clone https://github.com/Himesh-Shah93/Yukioh_Okami_Tool
cd Yukioh_Okami_Tool
bash install.sh
```

After installation, you can run the tool with:

```bash
Yukioh_Okami_Tool
```

or

```bash
cd ~/Yukioh_Okami_Tool && python Yukioh_Okami.py
```

---

🧭 Usage (Main Menu)

Option Description
1. Unpack PAK File Select a .pak from PAKS/. Optionally decrypt LUA files automatically.
2. Repack PAK File Choose an unpacked folder. Optionally compile LUA before repacking.
3. Decrypt LUA Files Decrypt already‑extracted .lua files from any folder.
4. Compile LUA Files Compile edited .lua source from EDIT_LUA/ into bytecode.
5. How To Use In‑app documentation.
0. Logout & Exit Clear session and exit.

Typical Workflow

1. Place your .pak in PAKS/.
2. Unpack (option 1) – files go to unpacked/<pak_name>/.
3. Decrypt (option 3) – decompiled source appears in DECOMPILED/<pak_name>/.
4. Edit the .lua files (use any text editor).
5. Compile (option 4) – edited files from EDIT_LUA/<pak_name>/ go to COMPILED/<pak_name>/.
6. Repack (option 2) – choose the unpacked folder, enable auto‑compile, and get a new .pak in repacked/.

---

🔧 Requirements

· Python 3.8+ (installed automatically)
· Java Runtime (for unluac decompiler)
· Lua 5.3 (for compiling bytecode)

The installer handles all of these for Termux.

---

🛠 Troubleshooting

NameError: name 'Align' is not defined

· Cause: Missing rich library.
· Fix:
  ```bash
  pip install rich
  ```

ModuleNotFoundError: No module named 'Crypto'

· Cause: Missing pycryptodome.
· Fix:
  ```bash
  pip install pycryptodome
  ```

gmalg installation fails

· Cause: PyPI version may have issues on some architectures.
· Fix:
  ```bash
  pip install git+https://github.com/myzhan/gmalg
  ```

Java or Lua not found

· Fix:
  ```bash
  pkg install openjdk-17 lua53
  ```

“No .pak files in PAKS/”

· Make sure you placed your .pak file inside the PAKS/ folder.

“Invalid key” / “Connection timeout”

· Check your internet connection. The tool requires online license verification.

---

🔐 License System

This tool uses an online activation panel. You will be prompted to enter a valid license key on first run. The key is saved locally in config.json for future sessions.

---

👨‍💻 Developer

Yukioh_Ōkami – Fully developed by @Yukira_12

---

⚠️ Disclaimer

This tool is for educational purposes only. Use it at your own risk. The developer is not responsible for any misuse or damage caused by this software.

---

📜 License

This project is proprietary and not open‑source. Redistribution or modification without explicit permission is prohibited.

---

Enjoy modding! 🎮


## Developer

Created by **Yukioh_Ōkami**
