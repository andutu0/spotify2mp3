#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import pathlib

ID_BRACKET_RE = re.compile(r"\s*\[[A-Za-z0-9_-]+\]\s*$")  # ex: " ... [abc123]" la finalul numelui

def unique_path(path: pathlib.Path) -> pathlib.Path:
    """Evita suprascrierea: adauga (1), (2), ... daca fisierul tinta exista."""
    if not path.exists():
        return path
    stem, suffix = path.stem, path.suffix
    i = 1
    while True:
        cand = path.with_name(f"{stem} ({i}){suffix}")
        if not cand.exists():
            return cand
        i += 1

def clean_filenames(out_dir: pathlib.Path) -> None:
    """
    Redenumeste fisierele MP3 din out_dir, scotand sufixul [videoID] dintre paranteze patrate.
    Exemplu: 'Song — Artist [dQw4w9WgXcQ].mp3' -> 'Song — Artist.mp3'
    """
    if not out_dir.exists() or not out_dir.is_dir():
        print(f"X Director invalid: {out_dir}")
        return

    count_ok = 0
    count_skip = 0

    for f in out_dir.glob("*.mp3"):
        # lucram pe numele fara extensie
        new_stem = ID_BRACKET_RE.sub("", f.stem).rstrip()
        if not new_stem or new_stem == f.stem:
            count_skip += 1
            continue

        target = f.with_name(new_stem + f.suffix)
        target = unique_path(target)  # evita suprascrierea
        try:
            f.rename(target)
            print(f"V {f.name}  ->  {target.name}")
            count_ok += 1
        except Exception as e:
            print(f"X Nu am putut redenumi {f.name}: {e}")

    print(f"\nRezumat: redenumite {count_ok}, fara schimbari {count_skip}")

def main():
    if len(sys.argv) >= 2:
        dir_str = sys.argv[1]
    else:
        dir_str = input("Introdu calea directorului cu fisiere MP3: ").strip()

    out_dir = pathlib.Path(dir_str).expanduser().resolve()
    print(f"[i] Director: {out_dir}")
    clean_filenames(out_dir)

if __name__ == "__main__":
    main()
