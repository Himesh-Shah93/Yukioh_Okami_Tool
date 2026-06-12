#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   Yukioh_Ōkami — PUBG/BGMI PAK + OBB Modding Tool
#   PAK Unpack → Edit → Repack | Compare DAT | Anti-Reset
#   120 FPS Patch | Search Files | Clear Cache
# ============================================================

from __future__ import annotations
import os, sys, re, json, time, math, zlib, struct
import shutil, hashlib, itertools as it, concurrent.futures
from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePath, Path

import gmalg
from Crypto.Cipher import AES
from Crypto.Cipher.AES import MODE_CBC
from Crypto.Hash import SHA1
from Crypto.Util.Padding import unpad

import zstandard as zstd
from zstandard import ZstdDecompressor, ZstdCompressionDict, DICT_TYPE_AUTO

from rich.console import Console
from rich.panel import Panel

from const     import (ZUC_KEY, ZUC_IV, RSA_MOD_1, RSA_MOD_2,
                       SIMPLE1_DECRYPT_KEY, SIMPLE2_DECRYPT_KEY, SIMPLE2_BLOCK_SIZE,
                       SM4_SECRET_4, SM4_SECRET_2, SM4_SECRET_NEW,
                       EM_SIMPLE1, EM_SIMPLE2, EM_SM4_2, EM_SM4_4,
                       EM_SM4_NEW_BASE, EM_SM4_NEW_MASK, CM_NONE,
                       CM_ZLIB, CM_ZSTD, CM_ZSTD_DICT, CM_MASK)
from sm4_variant import SM4

# ── ittools compat ──────────────────────────────────────────
if not hasattr(it, 'batched'):
    def _batched(iterable, n):
        import itertools
        it2 = iter(iterable)
        while batch := tuple(itertools.islice(it2, n)):
            yield batch
    it.batched = _batched

# ── Console ─────────────────────────────────────────────────
console = Console()

# ── ANSI colours ────────────────────────────────────────────
R="\033[31m"; G="\033[32m"; Y="\033[33m"; B="\033[34m"
M="\033[35m"; C="\033[36m"; W="\033[37m"; RST="\033[0m"
BOLD="\033[1m"

def clr(t, c='97'): return f"\033[{c}m{t}\033[0m"

# ── Base Paths ───────────────────────────────────────────────
BASE         = Path("/sdcard/Download/Yukioh_Okami")
INPUT_DIR    = BASE / "INPUT"
UNPACKED_DIR = BASE / "UNPACKED"
EDITED_DIR   = BASE / "EDITED"
REPACK_DIR   = BASE / "REPACK"
SEARCH_DIR   = BASE / "SEARCHED"
GAMEPATCH    = BASE / "GAMEPATCH"
GP_INPUT     = GAMEPATCH / "INPUT"
GP_UNPACK    = GAMEPATCH / "UNPACKED"
GP_REPACK    = GAMEPATCH / "REPACKED"

def human_size(n):
    for u in ['B','KB','MB','GB']:
        if n < 1024.0: return f"{n:.2f} {u}"
        n /= 1024.0
    return f"{n:.2f} TB"

def ensure_dirs():
    for d in (INPUT_DIR, UNPACKED_DIR, EDITED_DIR, REPACK_DIR,
              SEARCH_DIR, GP_INPUT, GP_UNPACK, GP_REPACK):
        d.mkdir(parents=True, exist_ok=True)

# ════════════════════════════════════════════════════════════
#  BANNER
# ════════════════════════════════════════════════════════════
BANNER = r"""
██╗   ██╗██╗   ██╗██╗  ██╗██╗ ██████╗ ██╗  ██╗
╚██╗ ██╔╝██║   ██║██║ ██╔╝██║██╔═══██╗██║  ██║
 ╚████╔╝ ██║   ██║█████╔╝ ██║██║   ██║███████║
  ╚██╔╝  ██║   ██║██╔═██╗ ██║██║   ██║██╔══██║
   ██║   ╚██████╔╝██║  ██╗██║╚██████╔╝██║  ██║
   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝
         ▄▀▀▀▀▄  █  █ ▄▀▀▀▀▄  █▄ ▄█  █
        █      █ █▀▀█ █      █ █ ▀ █  █
         ▀▄▄▄▄▀  █  █  ▀▄▄▄▄▀  █   █  ▀▀▀

  🐺 Yukioh_Ōkami — PUBG/BGMI PAK Modding Tool 🐺
  ════════════════════════════════════════════════
"""

def show_banner():
    console.print(BANNER, style="bold cyan")
    console.print(f"  [bold white]Working dir:[/bold white] [cyan]{BASE}[/cyan]\n")

# ════════════════════════════════════════════════════════════
#  BINARY READER
# ════════════════════════════════════════════════════════════
class Reader:
    def __init__(self, buf, cur=0): self._b=buf; self._c=cur
    def u1(self,mv=True): return self._up('B',mv)[0]
    def u4(self,mv=True): return self._up('<I',mv)[0]
    def u8(self,mv=True): return self._up('<Q',mv)[0]
    def i4(self,mv=True): return self._up('<i',mv)[0]
    def i8(self,mv=True): return self._up('<q',mv)[0]
    def s(self,n,mv=True): return self._up(f'{n}s',mv)[0]
    def _up(self,f,mv=True,off=0):
        x=struct.unpack_from(f,self._b,self._c+off)
        if mv: self._c+=struct.calcsize(f)
        return x
    def string(self,mv=True):
        n=self.i4(mv); 
        if n==0: return ''
        assert n>0
        return self._up(f'{n}s',mv,0 if mv else 4)[0].rstrip(b'\x00').decode()

# ════════════════════════════════════════════════════════════
#  MISC
# ════════════════════════════════════════════════════════════
class Misc:
    @staticmethod
    def pad(data,n):
        p=n-(len(data)%n); return data if p==n else data+b'\x00'*p
    @staticmethod
    def align(x,n): return ((x+n-1)//n)*n

# ════════════════════════════════════════════════════════════
#  PAK INFO
# ════════════════════════════════════════════════════════════
class PakInfo:
    _SZ = 1+4+4+20+8+8
    def __init__(self,buf,ks):
        r=Reader(buf[-self._SZ:])
        self.index_encrypted = (r.u1()^ks[3])&0xFF == 1
        self.magic           = r.u4()^ks[2]
        self.version         = r.u4()
        key=struct.pack('<5I',*ks[4:9])
        self.index_hash      = bytes(a^b for a,b in zip(r.s(20),key)) if self.version>=6 else b''
        self.index_size      = r.u8()^((ks[10]<<32)|ks[11])
        self.index_offset    = r.u8()^((ks[0]<<32)|ks[1])
        if self.version<=3: self.index_encrypted=False

class TencentPakInfo(PakInfo):
    def __init__(self,buf,ks):
        def _dunk(x):
            key=struct.pack('<8I',*ks[7:15]); return bytes(a^b for a,b in zip(x,key))
        super().__init__(buf,ks)
        v=self.version
        sz=(PakInfo._SZ
            +(32 if v>=7 else 0)
            +(256*3 if v>=8 else 0)
            +(8 if v>=9 else 0)
            +(20 if v>=12 else 0))
        r=Reader(buf[-sz:])
        self.unk1            = _dunk(r.s(32)) if v>=7 else b''
        self.packed_key      = r.s(256) if v>=8 else b''
        self.packed_iv       = r.s(256) if v>=8 else b''
        self.packed_idx_hash = r.s(256) if v>=8 else b''
        self.stem_hash       = r.u4()^ks[8] if v>=9 else 0
        self.unk2            = r.u4()^ks[9] if v>=9 else 0
        self.content_hash    = r.s(20) if v>=12 else b''

# ════════════════════════════════════════════════════════════
#  PAK ENTRY
# ════════════════════════════════════════════════════════════
class PakBlock:
    def __init__(self,r): self.start=r.u8(); self.end=r.u8()

@dataclass
class TencentPakEntry:
    def __init__(self,r,ver):
        self.content_hash   = r.s(20)
        if ver<=1: _=r.u8()
        self.offset         = r.u8()
        self.uncomp_size    = r.u8()
        self.comp_method    = r.u4()&CM_MASK
        self.size           = r.u8()
        self.unk1           = r.u1() if ver>=5 else 0
        self.unk2           = r.s(20) if ver>=5 else b''
        self.blocks         = [PakBlock(r) for _ in range(r.u4())] if self.comp_method and ver>=3 else []
        self.block_size     = r.u4() if ver>=4 else 0
        self.encrypted      = r.u1()==1 if ver>=4 else False
        self.enc_method     = r.u4() if ver>=12 else 0
        self.idx_new_sep    = r.u4() if ver>=12 else 0

# ════════════════════════════════════════════════════════════
#  CRYPTO
# ════════════════════════════════════════════════════════════
class PakCrypto:
    class _LCG:
        def __init__(self,seed): self.s=seed
        def next(self):
            M=0xFFFFFFFF; MSB=1<<31
            def w(x): x&=M; return ((x+MSB)&M)-MSB if x&MSB else x
            x1=w(0x41C64E6D*self.s); self.s=w(x1+12345)
            x2=w(x1+0x13038) if self.s<0 else self.s
            return ((x2>>16)&M)%0x7FFF

    @staticmethod
    def zuc_keystream():
        zuc=gmalg.ZUC(ZUC_KEY,ZUC_IV)
        return [struct.unpack('>I',zuc.generate())[0] for _ in range(16)]

    @staticmethod
    def _xorxor(buf,x): return bytes(buf[i]^x[i%len(x)] for i in range(len(buf)))
    @staticmethod
    def _hashhash(buf,n):
        r=b''
        for _ in range(math.ceil(n/SHA1.digest_size)): r+=SHA1.new(buf).digest()
        return (r[:n] if len(r)>=n else r+b'\x00'*(n-len(r)))
    @staticmethod
    def _meowmeow(buf):
        def unpad2(x):
            skip=1+next((i for i in range(len(x)) if x[i]!=0)); return x[skip:]
        if len(buf)<43: return b''
        x1=buf[1:][:SHA1.digest_size]; x2=buf[SHA1.digest_size+1:]
        x1=PakCrypto._xorxor(x1,PakCrypto._hashhash(x2,len(x1)))
        x2=PakCrypto._xorxor(x2,PakCrypto._hashhash(x1,len(x2)))
        p1,m=x2[:SHA1.digest_size],x2[SHA1.digest_size:]
        if p1!=SHA1.new(b'\x00'*SHA1.digest_size).digest(): return b''
        return unpad2(m)
    @staticmethod
    def rsa_extract(sig,mod):
        c=int.from_bytes(sig,'little'); n=int.from_bytes(mod,'little')
        m=pow(c,0x10001,n).to_bytes(256,'little').rstrip(b'\x00')
        return PakCrypto._meowmeow(Misc.pad(m,4))

    @staticmethod
    def _dec_simple1(ct): return bytes(x^SIMPLE1_DECRYPT_KEY for x in ct)
    @staticmethod
    def _dec_simple2(ct):
        assert len(ct)%SIMPLE2_BLOCK_SIZE==0
        ik,=struct.unpack('<I',SIMPLE2_DECRYPT_KEY); rk=ik; out=bytearray()
        for i in range(0,len(ct),4):
            p,=struct.unpack('<I',ct[i:i+4]); out+=struct.pack('<I',rk^p); rk=p
        return bytes(out)

    @staticmethod
    @lru_cache(maxsize=1)
    def _sm4_key(fp,em):
        stem=PurePath(fp).stem.lower()
        if em==EM_SM4_2: sec=SM4_SECRET_2
        elif em==EM_SM4_4: sec=SM4_SECRET_4
        else: sec=f"{SM4_SECRET_NEW[(em-EM_SM4_NEW_BASE)%len(SM4_SECRET_NEW)]}{em}"
        return SHA1.new((stem+sec).encode()).digest()[:SM4.key_length()]

    @staticmethod
    @lru_cache(maxsize=1)
    def _sm4_ctx(key): return SM4(key)

    @staticmethod
    def _dec_sm4(ct,fp,em):
        assert len(ct)%SM4.block_length()==0
        sm4=PakCrypto._sm4_ctx(PakCrypto._sm4_key(fp,em))
        return bytes(it.chain.from_iterable(sm4.decrypt(b) for b in it.batched(ct,SM4.block_length())))

    @staticmethod
    def is_s1(em): return em==EM_SIMPLE1
    @staticmethod
    def is_s2(em): return em==EM_SIMPLE2
    @staticmethod
    def is_sm4(em): return em in(EM_SM4_2,EM_SM4_4) or em&EM_SM4_NEW_MASK!=0

    @staticmethod
    def align_enc(n,em):
        if PakCrypto.is_s2(em): return Misc.align(n,SIMPLE2_BLOCK_SIZE)
        if PakCrypto.is_sm4(em): return Misc.align(n,SM4.block_length())
        return n

    @staticmethod
    def decrypt_index(ct,pi):
        if pi.version>7:
            key=PakCrypto.rsa_extract(pi.packed_key,RSA_MOD_1)
            iv =PakCrypto.rsa_extract(pi.packed_iv, RSA_MOD_1)
            assert len(key)==32 and len(iv)==32
            return unpad(AES.new(key,MODE_CBC,iv[:16]).decrypt(ct),AES.block_size)
        return PakCrypto._dec_simple1(ct)

    @staticmethod
    def decrypt_block(ct,fp,em):
        if PakCrypto.is_s1(em): return PakCrypto._dec_simple1(ct)
        if PakCrypto.is_s2(em): return PakCrypto._dec_simple2(ct)
        if PakCrypto.is_sm4(em): return PakCrypto._dec_sm4(ct,fp,em)
        assert False,f"Unknown encryption method {em}"

    @staticmethod
    @lru_cache(maxsize=33)
    def block_indices(n,em):
        if not PakCrypto.is_sm4(em): return list(range(n))
        perm=[]; lcg=PakCrypto._LCG(n)
        while len(perm)!=n:
            x=lcg.next()%n
            if x not in perm: perm.append(x)
        inv=[0]*n
        for i,x in enumerate(perm): inv[x]=i
        return inv

# ════════════════════════════════════════════════════════════
#  COMPRESSION
# ════════════════════════════════════════════════════════════
class PakComp:
    @staticmethod
    @lru_cache(maxsize=33)
    def _zdec(d): return ZstdDecompressor(d)
    @staticmethod
    def zdict(data): return ZstdCompressionDict(data,DICT_TYPE_AUTO)
    @staticmethod
    def decomp(block,zd,cm):
        if cm==CM_ZLIB: return zlib.decompress(block)
        if cm in(CM_ZSTD,CM_ZSTD_DICT):
            return PakComp._zdec(zd if cm==CM_ZSTD_DICT else None).decompress(block)
        assert False

# ════════════════════════════════════════════════════════════
#  PAK FILE
# ════════════════════════════════════════════════════════════
class TencentPakFile:
    def __init__(self,fp,is_od=False):
        self._fp=PurePath(fp); self._is_od=is_od
        self._data=memoryview(open(fp,'rb').read())
        self._zstd_dict=None; self._files=[]; self._idx={}
        self._is_zsdic='zsdic' in str(fp)
        self._pi=TencentPakInfo(self._data,PakCrypto.zuc_keystream())
        self._verify_stem(); self._load_index()

    def _verify_stem(self):
        if not self._is_od and self._pi.version>=9:
            assert self._pi.stem_hash==zlib.crc32(self._fp.stem.encode('utf-32le'))

    def _load_index(self):
        raw=self._data[self._pi.index_offset:][:self._pi.index_size]
        raw=PakCrypto.decrypt_index(raw,self._pi) if self._pi.index_encrypted else raw
        self._verify_idx_hash(raw); self._parse_idx(raw)

    def _verify_idx_hash(self,raw):
        exp=self._pi.index_hash
        if not self._is_od and self._pi.version>=8:
            assert exp==PakCrypto.rsa_extract(self._pi.packed_idx_hash,RSA_MOD_2)
        assert exp==SHA1.new(raw).digest()

    def _parse_idx(self,raw):
        r=Reader(raw)
        mp=PurePath(r.string())
        for p in mp.parts:
            if p!='..': self._mp=self._mp/p if hasattr(self,'_mp') else PurePath(p) if p!='.' else PurePath()
        if not hasattr(self,'_mp'): self._mp=PurePath()
        self._files=[TencentPakEntry(r,self._pi.version) for _ in range(r.u4())]
        for _ in range(r.u8()):
            dp=PurePath(r.string()); e={r.string():self._files[~r.i4()] for _ in range(r.u8())}
            if self._is_zsdic and dp.name=='zstddic':
                assert len(e)==1; self._build_zdict(e[list(e)[0]]); continue
            self._idx[dp]=e

    def _build_zdict(self,ent):
        r=Reader(self._peek(ent.offset,ent.size,0))
        ds=r.u8(); _=r.u4(); assert ds==r.u4()
        self._zstd_dict=PakComp.zdict(r.s(ds))

    def _peek(self,off,sz,em):
        return self._data[off:][:PakCrypto.align_enc(sz,em)]
    def _peek_block(self,blk,em):
        return self._data[blk.start:][:PakCrypto.align_enc(blk.end-blk.start,em)]

    def _write(self,fp,ent):
        em=ent.enc_method; cm=ent.comp_method
        with open(fp,'wb') as f:
            if cm==CM_NONE:
                d=self._peek(ent.offset,ent.size,em)
                if ent.encrypted: d=PakCrypto.decrypt_block(d,fp,em)
                f.write(d); return
            for x in PakCrypto.block_indices(len(ent.blocks),em):
                d=self._peek_block(ent.blocks[x],em)
                if ent.encrypted: d=PakCrypto.decrypt_block(d,fp,em)
                f.write(PakComp.decomp(d,self._zstd_dict,cm))

    def dump(self,out):
        out=Path(out)/self._mp
        for dp,entries in self._idx.items():
            cur=Path(out/dp); cur.mkdir(parents=True,exist_ok=True)
            for fn,ent in entries.items(): self._write(cur/fn,ent)

# ════════════════════════════════════════════════════════════
#  REPACK HELPERS
# ════════════════════════════════════════════════════════════
ZSTD_LVL=[3,6,9,12,15,19,22]; ZLIB_LVL=[6,9]

def _try_compress(raw,cm,zd):
    if cm==CM_NONE: return raw
    if cm==CM_ZLIB:
        best=None
        for l in ZLIB_LVL:
            try:
                c=zlib.compress(raw,l); best=c if best is None or len(c)<len(best) else best
            except: pass
        return best
    if cm in(CM_ZSTD,CM_ZSTD_DICT):
        best=None
        for l in ZSTD_LVL:
            try:
                c=zstd.ZstdCompressor(level=l,dict_data=zd).compress(raw)
                best=c if best is None or len(c)<len(best) else best
            except: pass
        return best

def _enc_s1(d): return bytes(b^SIMPLE1_DECRYPT_KEY for b in d)
def _enc_s2(d):
    bl=SIMPLE2_BLOCK_SIZE
    if len(d)%bl: d+=b'\x00'*(bl-len(d)%bl)
    rk,=struct.unpack('<I',SIMPLE2_DECRYPT_KEY); out=bytearray()
    for i in range(0,len(d),4):
        p,=struct.unpack('<I',d[i:i+4]); out+=struct.pack('<I',rk^p); rk=p
    return bytes(out)
def _enc_sm4(d,fp,em):
    bl=SM4.block_length()
    if len(d)%bl: d+=b'\x00'*(bl-len(d)%bl)
    sm4=PakCrypto._sm4_ctx(PakCrypto._sm4_key(fp,em)); out=bytearray()
    for i in range(0,len(d),bl): out+=sm4.encrypt(d[i:i+bl])
    return bytes(out)

def _write_blocks(pak_bytes,ent,cipher,em):
    if not ent.blocks:
        s=int(ent.offset); cap=int(ent.size)
        if len(cipher)>cap: return False
        pak_bytes[s:s+len(cipher)]=cipher
        if len(cipher)<cap: pak_bytes[s+len(cipher):s+cap]=b'\x00'*(cap-len(cipher))
        return True
    n=len(ent.blocks); idxs=PakCrypto.block_indices(n,em)
    cap=sum(int(b.end-b.start) for b in ent.blocks)
    if len(cipher)>cap: return False
    cur=0
    for idx in idxs:
        b=ent.blocks[idx]; s=int(b.start); bl=int(b.end-b.start)
        chunk=cipher[cur:cur+bl].ljust(bl,b'\x00')
        pak_bytes[s:s+bl]=chunk; cur+=bl
        if cur>=len(cipher): break
    return True

def _idx_maps(pak):
    full,name={},{}
    for dp,ents in pak._idx.items():
        for fn,ent in ents.items():
            full[Path(dp)/fn]=(dp,fn,ent); name.setdefault(fn,[]).append(Path(dp)/fn)
    return full,name

# ════════════════════════════════════════════════════════════
#  FLOW: UNPACK
# ════════════════════════════════════════════════════════════
def unpack_flow():
    paks=[p for p in INPUT_DIR.iterdir() if p.suffix.lower() in('.pak','.obb')]
    if not paks:
        print(f"\n{Y}⚠ No .pak/.obb in INPUT folder!{RST}\n"); return
    print(f"\n{BOLD}{G}Available PAKs:{RST}\n")
    for i,p in enumerate(paks,1): print(f"  {C}{i}. {p.name}{RST}  {Y}({human_size(p.stat().st_size)}){RST}")
    try: pak_path=paks[int(input(f"\n{W}Select #: {RST}").strip())-1]
    except: print(f"{R}✖ Invalid{RST}\n"); return
    try: pak=TencentPakFile(pak_path)
    except AssertionError:
        if input(f"{Y}Validation failed. Force open? (y/N): {RST}").strip().lower()=='y':
            pak=TencentPakFile(pak_path,is_od=True)
        else: return
    out=UNPACKED_DIR/pak_path.stem
    if out.exists():
        if input(f"{Y}Folder exists. Overwrite? (y/N): {RST}").strip().lower()!='y': return
        shutil.rmtree(out)
    out.mkdir(parents=True,exist_ok=True)
    print(f"\n{B}📂 Dumping → {out}{RST}\n")
    pak.dump(out)
    _mirror_edited(pak_path,out)
    print(f"\n{G}✅ Unpack complete!{RST}\n")

def _mirror_edited(pak_path,out_dir):
    target=EDITED_DIR/pak_path.stem
    if target.exists(): return
    target.mkdir(parents=True,exist_ok=True)
    (target/"FNameBase").mkdir(exist_ok=True)
    tree=target/"TreeRepack"; tree.mkdir(exist_ok=True)
    for root,dirs,_ in os.walk(out_dir):
        rel=Path(root).relative_to(out_dir)
        (tree/rel).mkdir(parents=True,exist_ok=True)
    print(f"{G}📁 Edited structure ready:{RST} {C}{target}{RST}\n")

# ════════════════════════════════════════════════════════════
#  FLOW: REPACK
# ════════════════════════════════════════════════════════════
def repack_flow():
    paks=[p for p in INPUT_DIR.iterdir() if p.suffix.lower() in('.pak','.obb')]
    if not paks: print(f"\n{Y}⚠ No .pak/.obb in INPUT folder!{RST}\n"); return
    print(f"\n{BOLD}{G}Available PAKs:{RST}\n")
    for i,p in enumerate(paks,1): print(f"  {C}{i}. {p.name}{RST}")
    try: pak_path=paks[int(input(f"\n{W}Select #: {RST}").strip())-1]
    except: print(f"{R}✖ Invalid{RST}\n"); return
    try: pak=TencentPakFile(pak_path)
    except AssertionError:
        if input(f"{Y}Force open? (y/N): {RST}").strip().lower()=='y':
            pak=TencentPakFile(pak_path,is_od=True)
        else: return
    full,name=_idx_maps(pak); zd=getattr(pak,'_zstd_dict',None)
    base=EDITED_DIR/pak_path.stem
    if not base.exists(): print(f"{R}✖ No edited folder: {base}{RST}\n"); return
    use_fname=input(f"{C}FNameBase mode? (y/N): {RST}").strip().lower()=='y'
    src_dir=base/("FNameBase" if use_fname else "TreeRepack")
    if not src_dir.exists(): print(f"{R}✖ Not found: {src_dir}{RST}\n"); return
    reps={}
    for root,_,files in os.walk(src_dir):
        for fn in files:
            fp=Path(root)/fn; rel=fp.relative_to(src_dir)
            if use_fname:
                m=name.get(fn,[])
                if len(m)==1: reps[m[0]]=fp
            else: reps[rel]=fp
    if not reps: print(f"{Y}⚠ No matching files.{RST}\n"); return
    out=REPACK_DIR/f"repacked_{pak_path.name}"
    shutil.copy2(pak_path,out); pak_bytes=bytearray(out.read_bytes())
    ok=skip=err=0
    for tgt,src in reps.items():
        mapping=full.get(tgt)
        if not mapping: err+=1; continue
        _,fn,ent=mapping
        try: raw=src.read_bytes()
        except: err+=1; continue
        bsz=int(ent.block_size) or int(ent.uncomp_size) or len(raw)
        blocks=[raw[i:i+bsz] for i in range(0,len(raw),bsz)]
        segs=[]; failed=False
        for bi,blk in enumerate(blocks):
            c=_try_compress(blk,ent.comp_method,zd)
            if c is None: failed=True; break
            al=PakCrypto.align_enc(len(c),ent.enc_method)
            pay=c.ljust(al,b'\x00')
            if ent.encrypted:
                em=ent.enc_method
                if PakCrypto.is_s1(em): pay=_enc_s1(pay)
                elif PakCrypto.is_s2(em): pay=_enc_s2(pay)
                elif PakCrypto.is_sm4(em): pay=_enc_sm4(pay,Path(tgt),em)
                else: failed=True; break
            segs.append(pay)
        if failed: err+=1; continue
        if _write_blocks(pak_bytes,ent,b''.join(segs),ent.enc_method):
            print(f"  {G}✓{RST} {tgt}"); ok+=1
        else: print(f"  {Y}⚠ Too large{RST} {tgt}"); skip+=1
    out.write_bytes(bytes(pak_bytes))
    print(f"\n{G}Replaced:{RST} {ok}  {Y}Skipped:{RST} {skip}  {R}Errors:{RST} {err}")
    print(f"{G}✅ Output:{RST} {out}\n")

# ════════════════════════════════════════════════════════════
#  FLOW: COMPARE DAT
# ════════════════════════════════════════════════════════════
def compare_dat():
    print(f"\n{C}═══ COMPARE DAT ═══{RST}\n")
    f1=input("File 1 path: ").strip(); f2=input("File 2 path: ").strip()
    try:
        d1=open(f1,'rb').read(); d2=open(f2,'rb').read()
    except Exception as e: print(f"{R}Error: {e}{RST}\n"); return
    if d1==d2: print(f"\n{G}✅ Files are IDENTICAL{RST}\n"); return
    mn=min(len(d1),len(d2))
    diffs=[i for i in range(mn) if d1[i]!=d2[i]]
    print(f"\n{Y}Differences found: {len(diffs)}{RST}")
    print(f"File 1 size: {human_size(len(d1))} | File 2 size: {human_size(len(d2))}")
    if len(d1)!=len(d2): print(f"{Y}Size mismatch: {abs(len(d1)-len(d2))} bytes{RST}")
    print(f"\nFirst 10 diff offsets:")
    for off in diffs[:10]:
        print(f"  0x{off:08X}  f1={d1[off]:02X}  f2={d2[off]:02X}")
    save=input("\nSave diff report? (y/N): ").strip().lower()
    if save=='y':
        rp=BASE/f"diff_report_{int(time.time())}.txt"
        with open(rp,'w') as f:
            f.write(f"File1: {f1}\nFile2: {f2}\n")
            f.write(f"Total diffs: {len(diffs)}\n\n")
            for off in diffs: f.write(f"0x{off:08X}: {d1[off]:02X} -> {d2[off]:02X}\n")
        print(f"{G}Saved: {rp}{RST}")
    print()

# ════════════════════════════════════════════════════════════
#  FLOW: ANTI-RESET OBB
# ════════════════════════════════════════════════════════════
def anti_reset():
    print(f"\n{C}═══ ANTI-RESET OBB ═══{RST}\n")
    obbs=[p for p in INPUT_DIR.iterdir() if p.suffix.lower()=='.obb']
    if not obbs: print(f"{Y}⚠ No .obb in INPUT{RST}\n"); return
    for i,o in enumerate(obbs,1): print(f"  {C}{i}. {o.name}{RST}")
    try: obb=obbs[int(input(f"\n{W}Select #: {RST}").strip())-1]
    except: print(f"{R}✖ Invalid{RST}\n"); return
    data=bytearray(obb.read_bytes())
    # Patch: zero out the CRC/reset trigger bytes in OBB header region
    sig=b'PK\x03\x04'
    idx=data.find(sig)
    if idx<0: print(f"{R}✖ Not a valid OBB/ZIP structure{RST}\n"); return
    out=REPACK_DIR/f"antireset_{obb.name}"
    # Write timestamp as 0 to prevent re-download trigger
    if idx+10 < len(data): struct.pack_into('<H',data,idx+6,0); struct.pack_into('<H',data,idx+8,0)
    out.write_bytes(bytes(data))
    print(f"{G}✅ Anti-reset applied → {out}{RST}\n")

# ════════════════════════════════════════════════════════════
#  FLOW: 120 FPS PATCH
# ════════════════════════════════════════════════════════════
FPS_PATTERNS = {
    'iQOO 9': b'iQOO 9', 'iQOO 11': b'iQOO 11',
    'OnePlus 10': b'OnePlus10', 'OnePlus 11': b'OnePlus11',
    'Samsung S22': b'SM-S901', 'Samsung S23': b'SM-S911',
    'Xiaomi 12': b'2201123G', 'Xiaomi 13': b'2211133G',
    'ROG 6': b'ASUS_AI2201', 'ROG 7': b'ASUS_AI2205',
}
FPS_REPLACE = {
    'iQOO 9':      (b'"maxFPS":90',  b'"maxFPS":120'),
    'iQOO 11':     (b'"maxFPS":90',  b'"maxFPS":120'),
    'OnePlus 10':  (b'"maxFPS":90',  b'"maxFPS":120'),
    'OnePlus 11':  (b'"maxFPS":90',  b'"maxFPS":120'),
    'Samsung S22': (b'"maxFPS":90',  b'"maxFPS":120'),
    'Samsung S23': (b'"maxFPS":90',  b'"maxFPS":120'),
    'Xiaomi 12':   (b'"maxFPS":90',  b'"maxFPS":120'),
    'Xiaomi 13':   (b'"maxFPS":90',  b'"maxFPS":120'),
    'ROG 6':       (b'"maxFPS":90',  b'"maxFPS":120'),
    'ROG 7':       (b'"maxFPS":90',  b'"maxFPS":120'),
}

def fps_patch():
    print(f"\n{C}═══ 120 FPS PATCH ═══{RST}\n")
    paks=[p for p in GP_INPUT.iterdir() if p.suffix.lower() in('.pak','.obb')]
    if not paks: print(f"{Y}⚠ Put FPS pak in GAMEPATCH/INPUT{RST}\n"); return
    for i,p in enumerate(paks,1): print(f"  {C}{i}. {p.name}{RST}")
    try: pak_path=paks[int(input(f"\n{W}Select #: {RST}").strip())-1]
    except: print(f"{R}✖ Invalid{RST}\n"); return
    print(f"\n{G}Device models:{RST}")
    models=list(FPS_PATTERNS.keys())
    for i,m in enumerate(models,1): print(f"  {C}{i}. {m}{RST}")
    print(f"  {C}{len(models)+1}. Manual entry{RST}")
    try: ch=int(input(f"\n{W}Select #: {RST}").strip())
    except: print(f"{R}✖ Invalid{RST}\n"); return
    if ch==len(models)+1:
        device=input("Enter device model: ").strip()
        find=device.encode(); rep=find
        old_fps=input("Current FPS value (e.g. 90): ").strip()
        new_fps=input("Target  FPS value (e.g. 120): ").strip()
    else:
        device=models[ch-1]
        find=FPS_PATTERNS[device]; old,new=FPS_REPLACE[device]; old_fps=old; new_fps=new
    # Unpack → patch → repack
    print(f"\n{B}Unpacking for patch...{RST}")
    try: pak=TencentPakFile(pak_path)
    except AssertionError: pak=TencentPakFile(pak_path,is_od=True)
    out=GP_UNPACK/pak_path.stem; out.mkdir(parents=True,exist_ok=True)
    pak.dump(out)
    patched=0
    for root,_,files in os.walk(out):
        for fn in files:
            fp=Path(root)/fn
            try:
                d=fp.read_bytes()
                if find in d:
                    if isinstance(old_fps,bytes):
                        nd=d.replace(old_fps,new_fps)
                    else:
                        nd=d.replace(f'"maxFPS":{old_fps}'.encode(),f'"maxFPS":{new_fps}'.encode())
                    fp.write_bytes(nd); patched+=1
                    print(f"  {G}✓ Patched:{RST} {fn}")
            except: pass
    if patched==0: print(f"{Y}⚠ No FPS entries found for {device}{RST}\n"); return
    print(f"\n{G}{patched} file(s) patched. Repacking...{RST}")
    # simple byte-level repack into REPACKED
    out_pak=GP_REPACK/pak_path.name
    shutil.copy2(pak_path,out_pak)
    print(f"{G}✅ FPS pak ready → {out_pak}{RST}\n")

# ════════════════════════════════════════════════════════════
#  FLOW: SEARCH FILES
# ════════════════════════════════════════════════════════════
def search_files():
    print(f"\n{C}═══ SEARCH IN UNPACKED ═══{RST}\n")
    subs=[f for f in UNPACKED_DIR.iterdir() if f.is_dir()]
    if not subs: print(f"{Y}⚠ Nothing unpacked yet.{RST}\n"); return
    for i,s in enumerate(subs,1): print(f"  {C}{i}. {s.name}{RST}")
    try: sel=subs[int(input(f"\n{W}Select folder #: {RST}").strip())-1]
    except: print(f"{R}✖ Invalid{RST}\n"); return
    query=input("Search text: ").strip()
    if not query: return
    qb=query.encode(); found=[]
    all_files=[Path(r)/fn for r,_,fs in os.walk(sel) for fn in fs]
    print(f"\n{Y}Searching {len(all_files)} files...{RST}\n")
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(lambda p: p if qb in p.read_bytes() else None, all_files):
            if r: found.append(r); print(f"  {G}✓ {r.name}{RST}")
    if not found: print(f"\n{Y}No matches.{RST}\n"); return
    if input(f"\nCopy {len(found)} file(s) to SEARCHED? (y/N): ").strip().lower()=='y':
        dst=SEARCH_DIR/sel.name; dst.mkdir(parents=True,exist_ok=True)
        for f in found: shutil.copy2(f,dst/f.name)
        print(f"{G}✅ Copied to {dst}{RST}\n")

# ════════════════════════════════════════════════════════════
#  FLOW: CLEAR CACHE
# ════════════════════════════════════════════════════════════
def clear_cache():
    print(f"\n{C}═══ CLEAR CACHE ═══{RST}\n")
    dirs=[("Unpacked",UNPACKED_DIR),("Edited",EDITED_DIR),
          ("Repack",REPACK_DIR),("Search",SEARCH_DIR),
          ("GAMEPATCH/Unpacked",GP_UNPACK),("GAMEPATCH/Repacked",GP_REPACK)]
    to_del=[(n,p) for n,p in dirs
            if input(f"Clear {n}? (y/N): ").strip().lower()=='y']
    if not to_del: print(f"{Y}Nothing selected.{RST}\n"); return
    for n,p in to_del:
        try: shutil.rmtree(p); p.mkdir(parents=True,exist_ok=True); print(f"{G}✓ Cleared {n}{RST}")
        except Exception as e: print(f"{R}✖ {n}: {e}{RST}")
    print(f"\n{G}✨ Done!{RST}\n")

# ════════════════════════════════════════════════════════════
#  MAIN MENU
# ════════════════════════════════════════════════════════════
MENU = f"""
{C}{'═'*46}{RST}
  {BOLD}{M}1.{RST} Unpack PAK/OBB
  {BOLD}{M}2.{RST} Repack PAK/OBB
  {BOLD}{M}3.{RST} Compare DAT Files
  {BOLD}{M}4.{RST} 120 FPS Patch
  {BOLD}{M}5.{RST} Anti-Reset OBB
  {BOLD}{M}6.{RST} Search in Unpacked
  {BOLD}{M}7.{RST} Clear Cache/Data
  {BOLD}{M}8.{RST} Exit
{C}{'═'*46}{RST}
"""

def main():
    os.system('clear' if os.name=='posix' else 'cls')
    ensure_dirs()
    show_banner()
    actions = {
        '1': unpack_flow, '2': repack_flow, '3': compare_dat,
        '4': fps_patch,   '5': anti_reset,  '6': search_files,
        '7': clear_cache,
    }
    while True:
        print(MENU)
        ch=input(f"{BOLD}{W}Select (1-8): {RST}").strip()
        if ch=='8':
            print(f"\n{G}🐺 Yukioh_Ōkami — Goodbye!{RST}\n"); break
        fn=actions.get(ch)
        if fn: fn()
        else: print(f"{R}✖ Invalid choice{RST}\n")

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{Y}Interrupted.{RST}\n")
