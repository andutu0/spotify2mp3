# 🎵 Spotify2MP3

Convert a Spotify playlist into a folder full of MP3 files — step by step, using your own scripts.


## 🧩 Overview

This mini-pipeline transforms a Spotify playlist into MP3 files using three independent Python scripts:

1. **`get_playlist.py`** – extracts song titles + artists from a Spotify playlist into a `.txt` file  
2. **`downloader.py`** – reads that `.txt` and downloads MP3s from YouTube (`yt-dlp` + `ffmpeg`)  
3. **`clean_names.py`** – cleans the filenames by removing unwanted suffixes like `[videoID]`  

> ⚠️ This tool is for **educational purposes only**. Please respect copyright laws and platform terms.

---

## ⚙️ Requirements

- **Python** ≥ 3.9  
- **Libraries:**
  ```bash
  pip install spotipy yt-dlp
  ```
- **`ffmpeg`** must be installed and available in your system PATH.

Check installation:
```bash
ffmpeg -version
```

---

## 🚀 Quick Start

Clone or copy the repository, make sure all `.py` files are in the same folder, then follow these steps:

### 1️⃣ Export playlist to text – `get_playlist.py`

Extract all songs from a Spotify playlist into a `.txt` file.

#### Usage

```bash
python get_playlist.py <playlist_link_or_uri> [-o output.txt] [--user-auth]
```

#### Parameters

| Option | Description |
|:-------|:-------------|
| `playlist` | Spotify playlist link or URI |
| `-o`, `--output` | Output file (default: `playlist.txt`) |
| `--user-auth` | Use user authentication (needed for private playlists) |

#### Example

```bash
# Public playlist (requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in environment)
python get_playlist.py https://open.spotify.com/playlist/XXXX -o playlist.txt

# Private playlist (opens OAuth browser login)
python get_playlist.py spotify:playlist:XXXX --user-auth -o my_playlist.txt
```

#### Output
A text file like:
```
Daft Punk — Get Lucky
Coldplay — Yellow
Tame Impala — The Less I Know The Better
```

#### Authentication

- **Public playlists:** use Spotify API client credentials:
  ```bash
  export SPOTIFY_CLIENT_ID="..." 
  export SPOTIFY_CLIENT_SECRET="..."
  ```
- **Private playlists:** add `--user-auth` (a browser window will open once for authorization).

---

### 2️⃣ Download songs as MP3 – `downloader.py`

Reads each line from a `.txt` file and downloads the first YouTube result as an MP3 file using `yt-dlp` and `ffmpeg`.

#### Usage

Simply run:
```bash
python downloader.py
```

Choose from the interactive menu:
```
Alege modul:
  1) Titlu unic → descarcă
  2) Fișier .txt cu mai multe titluri
Alegerea ta [1/2]:
```

#### Example

If you already have `playlist.txt`:
```
python downloader.py
# Choose option 2
# Path to playlist.txt
```

It will create a new folder (based on the `.txt` filename) and download all songs there.

#### Notes

- Downloads are retried automatically if interrupted.
- You can stop/resume safely.
- The conversion to MP3 (192 kbps) happens automatically.

Example output:
```
[i] Director ieșire: playlist
✔ Daft Punk — Get Lucky
✔ Coldplay — Yellow
✔ Tame Impala — The Less I Know The Better
===== Rezumat =====
  Reușite: 3
  Eșecuri: 0
```

---

### 3️⃣ Clean up filenames – `clean_names.py`

Removes YouTube video IDs from filenames (e.g. `[dQw4w9WgXcQ]`) and ensures no overwriting occurs.

#### Usage

```bash
python clean_names.py path/to/mp3_folder
```

#### Example Output

```
✔ Daft Punk — Get Lucky [dQw4w9WgXcQ].mp3  →  Daft Punk — Get Lucky.mp3
✔ Coldplay — Yellow [e-ORhEE9VVg].mp3  →  Coldplay — Yellow.mp3

Rezumat: redenumite 2, fără schimbări 1
```

---


## 🧩 Folder Structure

```
Spotify2MP3/
│
├── get_playlist.py
├── downloader.py
├── clean_names.py
├── main.py                # optional, orchestrator
├── playlist.txt           # generated titles
└── downloads/             # generated MP3s
```

---

## 🧾 License

This project is provided **as-is**, for educational and personal use only.  
Do not use it for piracy or commercial redistribution.

---

Enjoy your clean MP3 collection 🎧
