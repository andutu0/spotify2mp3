#!/usr/bin/env python3
"""
Exporta titlurile pieselor + artistii dintr-un playlist Spotify intr-un fisier .txt.
- Suporta playlisturi publice (client credentials).
- Optional: --user-auth pentru playlisturi private/colaborative (OAuth in browser).
"""

import argparse
import os
import re
import sys
from typing import Iterable, Tuple

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotipy.exceptions import SpotifyException


PLAYLIST_REGEX = re.compile(
    r"(?:https?://open\.spotify\.com/playlist/|spotify:playlist:)([A-Za-z0-9]+)"
)

SCOPES = ["playlist-read-private"]  # necesar doar pentru --user-auth


def extract_playlist_id(url_or_uri: str) -> str:
    m = PLAYLIST_REGEX.search(url_or_uri)
    if not m:
        raise ValueError("Nu pare a fi un link/uri valid de playlist Spotify.")
    return m.group(1)


def get_spotify_client(user_auth: bool) -> spotipy.Spotify:
    if user_auth:
        # Autentificare utilizator (browser) – pentru playlisturi private/collab
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                scope=SCOPES,
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8080"),
                cache_path=os.getenv("SPOTIPY_CACHE", ".cache-spotify"),
                show_dialog=False,
            )
        )
    else:
        # Doar pentru playlisturi publice
        cid = os.getenv("SPOTIFY_CLIENT_ID")
        cs = os.getenv("SPOTIFY_CLIENT_SECRET")
        if not cid or not cs:
            raise EnvironmentError(
                "Lipseste SPOTIFY_CLIENT_ID sau SPOTIFY_CLIENT_SECRET din variabilele de mediu.\n"
                "Seteaza-le sau ruleaza cu --user-auth."
            )
        sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=cid, client_secret=cs
            )
        )
    return sp


def paginate_tracks(sp: spotipy.Spotify, playlist_id: str) -> Iterable[dict]:
    """Itereaza prin toate track-urile din playlist (paginare automata)."""
    limit = 100
    offset = 0
    while True:
        page = sp.playlist_items(
            playlist_id,
            fields="items(track(name,artists(name),is_local,type)),next",
            additional_types=("track",),  # ignora episoade/podcasturi
            limit=limit,
            offset=offset,
        )
        items = page.get("items") or []
        for it in items:
            yield it
        next_url = page.get("next")
        if not next_url or len(items) == 0:
            break
        offset += limit


def format_track_line(item: dict) -> Tuple[bool, str]:
    """
    Returneaza (ok, line). ok=False daca nu e track valid (ex: podcast/episod sau local fara nume).
    """
    track = item.get("track")
    if not track:
        return False, ""
    if track.get("type") != "track":
        return False, ""  # sare peste episoade/podcasturi
    name = (track.get("name") or "").strip()
    artists = track.get("artists") or []
    artist_names = ", ".join([a.get("name", "").strip() for a in artists if a.get("name")])
    if not name or not artist_names:
        return False, ""
    return True, f"{name} — {artist_names}"


def main():
    parser = argparse.ArgumentParser(
        description="Exporta piesele + artistii dintr-un playlist Spotify intr-un .txt"
    )
    parser.add_argument("playlist", help="Link sau URI de playlist Spotify")
    parser.add_argument(
        "-o", "--output", default="playlist.txt", help="Fisierul de iesire (default: playlist.txt)"
    )
    parser.add_argument(
        "--user-auth",
        action="store_true",
        help="Foloseste autentificare de utilizator (necesar pentru playlisturi private/colaborative).",
    )
    args = parser.parse_args()

    try:
        playlist_id = extract_playlist_id(args.playlist)
    except ValueError as e:
        print(f"Eroare: {e}", file=sys.stderr)
        sys.exit(2)

    try:
        sp = get_spotify_client(args.user_auth)
    except Exception as e:
        print(f"Eroare la autentificare: {e}", file=sys.stderr)
        sys.exit(2)

    lines = []
    skipped = 0

    try:
        for item in paginate_tracks(sp, playlist_id):
            ok, line = format_track_line(item)
            if ok:
                lines.append(line)
            else:
                skipped += 1
    except SpotifyException as e:
        print(f"Spotify API error: {e}", file=sys.stderr)
        sys.exit(1)

    # Scrie fisierul
    with open(args.output, "w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln + "\n")

    print(f"Am salvat {len(lines)} piese in '{args.output}'.", flush=True)
    if skipped:
        print(f"Sarite (non-track/invalid): {skipped}")


if __name__ == "__main__":
    main()
