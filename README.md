# 🐺 Yukioh_Ōkami — PUBG/BGMI PAK Modding Tool

Simple Unpacker • Repacker • Compare DAT • Anti-Reset • 120 FPS

---

## Features

- ✅ Fast PAK / OBB Unpack & Repack
- ✅ Supports PUBG Mobile / BGMI
- ✅ Auto folder structure after unpack
- ✅ Compare DAT files (find differences)
- ✅ Anti-Reset OBB system
- ✅ 120 FPS Patch tool
- ✅ Search files inside unpacked folders
- ✅ Clear cache / data

---

## Folder Structure

```
/sdcard/Download/Yukioh_Okami/
├── INPUT/          ← Put your .pak / .obb here
├── UNPACKED/       ← Extracted files appear here
├── EDITED/         ← Put your modified files here
├── REPACK/         ← Repacked output goes here
├── SEARCHED/       ← Search results copied here
└── GAMEPATCH/
    ├── INPUT/      ← FPS pak goes here
    ├── UNPACKED/
    └── REPACKED/   ← FPS patched pak goes here
```

---

## Usage

### Unpack
1. Put `.pak` / `.obb` in `INPUT/`
2. Run tool → Select **1. Unpack**
3. Files appear in `UNPACKED/`

### Repack
1. Put edited files in `EDITED/<pakname>/FNameBase/` or `TreeRepack/`
2. Run tool → Select **2. Repack**
3. Output in `REPACK/`

### 120 FPS
1. Put FPS pak in `GAMEPATCH/INPUT/`
2. Run tool → Select **4. 120 FPS Patch**
3. Select device model
4. Output in `GAMEPATCH/REPACKED/`

### Compare DAT
- Select **3. Compare DAT**
- Enter path to both files
- See byte-level differences

---

## Install (Termux)

```bash
bash install.sh
```

Then run:
```bash
python Yukioh_Okami.py
```

---

## Developer

Created by **Yukioh_Ōkami**
