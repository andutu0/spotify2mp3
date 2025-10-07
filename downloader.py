#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Smart audio downloader:
    - Optiunea 1: primeste un titlu (text) si descarca prima potrivire de pe YouTube ca MP3.
    - Optiunea 2: primeste un fisier .txt cu titluri (un titlu pe rand), creeaza un director
        cu numele fisierului si descarca toate melodiile in acel director.

Dependente: yt-dlp, ffmpeg
"""

import os
import sys
import re
import pathlib
from typing import List, Optional

try:
        from yt_dlp import YoutubeDL
except ImportError:
        print("Lipseste pachetul yt-dlp. Instaleaza cu: pip install yt-dlp", file=sys.stderr)
        sys.exit(1)

# --------- Utils ----------

def sanitize_dir_name(name: str) -> str:
        # scoate caractere care pot incurca un nume de folder
        name = name.strip()
        name = re.sub(r'[\\/:*?"<>|]+', "_", name)
        name = name.replace("\0", "")
        return name or "downloads"

def ensure_dir(path: pathlib.Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

def read_lines_from_txt(txt_path: pathlib.Path) -> List[str]:
        with txt_path.open("r", encoding="utf-8") as f:
                lines = [ln.strip() for ln in f.readlines()]
        # elimina linii goale si comentarii
        return [ln for ln in lines if ln and not ln.lstrip().startswith("#")]

def make_ydl(out_dir: pathlib.Path, audio_codec: str = "mp3", audio_quality: str = "192") -> YoutubeDL:
        ydl_opts = {
                "quiet": False,
                "ignoreerrors": True,
                "restrictfilenames": False,
                "noplaylist": True,
                "continuedl": True,
                "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
                "format": "bestaudio/best",
                "postprocessors": [
                        {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": audio_codec,
                                "preferredquality": audio_quality,
                        }
                ],
                # retea / stabilitate
                "retries": 10,
                "fragment_retries": 10,
                "nocheckcertificate": True,
        }
        return YoutubeDL(ydl_opts)

def search_and_download(query: str, out_dir: pathlib.Path) -> Optional[str]:
        """
        Cauta prima potrivire pe YouTube si o descarca ca MP3.
        Returneaza titlul media descarcata sau None daca a esuat.
        """
        ensure_dir(out_dir)
        ydl = make_ydl(out_dir)
        search_expr = f"ytsearch1:{query}"
        try:
                info = ydl.extract_info(search_expr, download=True)
                # ytsearch1 returneaza un dict cu 'entries'
                if info and "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                        title = entry.get("title") or query
                        return title
                return None
        except Exception as e:
                print(f"[E] Eroare la descarcare pentru: {query}\n    {e}", file=sys.stderr)
                return None

# --------- Main flow ----------

def menu() -> int:
        print("Alege modul:")
        print("  1) Introduc un TITLU de melodie si o descarca")
        print("  2) Dau un FISIER .txt cu multe titluri (cate unul pe rand)")
        while True:
                choice = input("Alegerea ta [1/2]: ").strip()
                if choice in ("1", "2"):
                        return int(choice)
                print("Te rog alege 1 sau 2.")

def mode_single():
        title = input("Titlul melodiei (ex: 'Daft Punk - Get Lucky'): ").strip()
        if not title:
                print("Titlu gol. Iesire.")
                return
        out_dir = pathlib.Path.cwd() / "downloads_single"
        print(f"[i] Salvez in: {out_dir}")
        ok_title = search_and_download(title, out_dir)
        if ok_title:
                print(f"Descacat: {ok_title}")
        else:
                print("Nu am reusit sa descarc aceasta melodie.")

def mode_batch():
        path_str = input("Cale catre fisierul .txt: ").strip().strip('"').strip("'")
        txt_path = pathlib.Path(path_str)
        if not txt_path.exists() or not txt_path.is_file():
                print("Fisierul nu exista sau nu este un fisier valid.")
                return
        titles = read_lines_from_txt(txt_path)
        if not titles:
                print("Fisierul nu contine titluri valide.")
                return

        out_dir_name = sanitize_dir_name(txt_path.stem)
        out_dir = txt_path.parent / out_dir_name
        print(f"[i] Creez/folosesc director: {out_dir}")
        ensure_dir(out_dir)

        ok, fail = 0, 0
        for i, q in enumerate(titles, 1):
                print(f"\n[{i}/{len(titles)}] {q}")
                if search_and_download(q, out_dir):
                        ok += 1
                else:
                        fail += 1

        print("\n===== Rezumat =====")
        print(f"  Reusite: {ok}")
        print(f"  Esecuri: {fail}")
        print(f"  Director: {out_dir.resolve()}")

def main():
        # daca vrei si mod non-interactiv, poti adauga argparse aici ulterior
        choice = menu()
        if choice == 1:
                mode_single()

        else:
                mode_batch()

if __name__ == "__main__":
        # Declaratie responsabila: utilizeaza scriptul in acord cu legile drepturilor de autor
        # si cu termenii platformelor (YouTube/Spotify/etc.). Tu esti responsabil pentru
        # continutul pe care il descarci.
        main()
