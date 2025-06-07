#!/usr/bin/env python3
"""
GZCTF Game and Challenge Cloner

Author: l4rm4nd (https://github.com/l4rm4nd)
License: MIT

Description:
    This script allows duplicating existing games and challenges on a GZCTF instance.
    It supports two modes:
      - Clone an existing game and all/some of its challenges.
      - Create a new empty game and populate it with challenges selected from any game.

    Supports cross-instance duplication if --dst-url and --dst-token are supplied.
    The script preserves flags, hints, metadata, and attachments.
    All duplicated challenges are disabled by default.

Usage:
    Clone a game on the same instance:
        python3 gzctf_cloner.py --url https://ctf.source.com --token '<GZCTF_Token>'

    Create a new game from selected challenges:
        python3 gzctf_cloner.py --url https://ctf.source.com --token '<GZCTF_Token>' --newgame

    Cross-instance duplication:
        python3 gzctf_cloner.py --url https://ctf.source.com --token '<GZCTF_Token>' \
            --dst-url https://ctf.dest.com --dst-token '<GZCTF_Token>'

    Custom invite code:
        python3 gzctf_cloner.py --url https://ctf.example.com --token '<GZCTF_Token>' --invite-code MYCODE123
"""

import requests
import argparse
import time
import secrets
import sys

def generate_invite_code(length=24):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def session_with_token(base_url, token):
    session = requests.Session()
    domain = base_url.split("//")[-1].split("/")[0]
    session.cookies.set("GZCTF_Token", token, domain=domain)
    return session

def fetch_games(session, base_url):
    try:
        r = session.get(f"{base_url}/api/game?count=50&skip=0")
        r.raise_for_status()
        return r.json()["data"]
    except Exception as e:
        print(f"❌ Failed to fetch games: {e}")
        sys.exit(1)

def fetch_challenges(session, base_url, game_id):
    try:
        r = session.get(f"{base_url}/api/game/{game_id}/details")
        r.raise_for_status()
        flat = []
        for category in r.json().get("challenges", {}):
            for ch in r.json()["challenges"][category]:
                ch["game_id"] = game_id
                flat.append(ch)
        return flat
    except Exception as e:
        print(f"❌ Failed to fetch challenges for game {game_id}: {e}")
        return []

def fetch_challenge_config(session, base_url, game_id, challenge_id):
    r = session.get(f"{base_url}/api/edit/games/{game_id}/challenges/{challenge_id}")
    r.raise_for_status()
    return r.json()

def create_game(session, base_url, title, invite_code=None):
    now = int(time.time()) + 600
    data = {
        "title": title,
        "summary": f"Cloned: {title}",
        "hidden": True,
        "acceptWithoutReview": False,
        "writeupRequired": False,
        "inviteCodeRequired": True,
        "inviteCode": invite_code or generate_invite_code(),
        "practiceMode": True,
        "start": now * 1000,
        "end": (now + 3600) * 1000
    }
    r = session.post(f"{base_url}/api/edit/games", json=data)
    r.raise_for_status()
    return r.json()

def create_challenge_minimal(session, base_url, game_id, ch_full, ch_meta):
    score = ch_meta.get("originalScore", ch_meta.get("score", 100))
    data = {
        "title": ch_full.get("title", ch_meta["title"]),
        "category": ch_full.get("category", ch_meta.get("category", "Misc")),
        "type": ch_full.get("type", "StaticAttachment"),
        "isEnabled": False,
        "score": score,
        "minScore": score,
        "originalScore": score
    }
    r = session.post(f"{base_url}/api/edit/games/{game_id}/challenges", json=data)
    r.raise_for_status()
    return r.json()

def update_challenge(session, base_url, game_id, challenge_id, ch):
    patch_fields = {
        "title": ch.get("title"),
        "content": ch.get("content"),
        "flagTemplate": ch.get("flagTemplate"),
        "category": ch.get("category"),
        "hints": ch.get("hints", []),
        "fileName": ch.get("fileName"),
        "containerImage": ch.get("containerImage"),
        "memoryLimit": ch.get("memoryLimit"),
        "cpuCount": ch.get("cpuCount"),
        "storageLimit": ch.get("storageLimit"),
        "containerExposePort": ch.get("containerExposePort"),
        "enableTrafficCapture": ch.get("enableTrafficCapture"),
        "disableBloodBonus": ch.get("disableBloodBonus"),
        "originalScore": ch.get("originalScore"),
        "minScoreRate": ch.get("minScoreRate"),
        "difficulty": ch.get("difficulty")
    }
    patch_fields = {k: v for k, v in patch_fields.items() if v is not None}
    r = session.put(f"{base_url}/api/edit/games/{game_id}/challenges/{challenge_id}", json=patch_fields)
    r.raise_for_status()

def duplicate_flags(session, base_url, game_id, cid, flags):
    flag_data = [{"flag": f["flag"]} for f in flags]
    r = session.post(f"{base_url}/api/edit/games/{game_id}/challenges/{cid}/flags", json=flag_data)
    r.raise_for_status()

def duplicate_attachment(session, base_url, full_url_base, game_id, cid, attachment):
    if not attachment or not attachment.get("url"): return
    remote_url = full_url_base + attachment["url"]
    data = {"attachmentType": "Remote", "remoteUrl": remote_url}
    r = session.post(f"{base_url}/api/edit/games/{game_id}/challenges/{cid}/attachment", json=data)
    r.raise_for_status()

def duplicate_selected_challenges(src_sess, dst_sess, src_base, dst_base, full_url_base, challenges, new_game_id):
    for ch in challenges:
        try:
            full = fetch_challenge_config(src_sess, src_base, ch["game_id"], ch["id"])
            created = create_challenge_minimal(dst_sess, dst_base, new_game_id, full, ch)
            update_challenge(dst_sess, dst_base, new_game_id, created["id"], full)
            if full.get("flags"):
                duplicate_flags(dst_sess, dst_base, new_game_id, created["id"], full["flags"])
            if full.get("attachment"):
                duplicate_attachment(dst_sess, dst_base, full_url_base, new_game_id, created["id"], full["attachment"])
            print(f"✅ Cloned: {created['title']}")
        except Exception as e:
            print(f"❌ Failed to clone challenge {ch['id']}: {e}")

def main():
    parser = argparse.ArgumentParser(description="GZCTF Cloner via Token")
    parser.add_argument("--url", required=True, help="Source base URL")
    parser.add_argument("--token", required=True, help="GZCTF_Token cookie value for source session")
    parser.add_argument("--invite-code", help="Custom invite code")
    parser.add_argument("--newgame", action="store_true", help="New game from selected challenges")
    parser.add_argument("--dst-url", help="Destination base URL")
    parser.add_argument("--dst-token", help="Destination GZCTF_Token cookie value")

    args = parser.parse_args()

    src_url = args.url.rstrip("/")
    src_sess = session_with_token(src_url, args.token)

    dst_url = args.dst_url.rstrip("/") if args.dst_url else src_url
    dst_token = args.dst_token if args.dst_token else args.token
    dst_sess = session_with_token(dst_url, dst_token)

    games = fetch_games(src_sess, src_url)

    if args.newgame:
        all_challenges = []
        for g in games:
            chs = fetch_challenges(src_sess, src_url, g["id"])
            for ch in chs:
                ch["game_title"] = g["title"]
                try:
                    full = fetch_challenge_config(src_sess, src_url, g["id"], ch["id"])
                    ch["originalScore"] = full.get("originalScore", ch.get("score", 0))
                except:
                    ch["originalScore"] = ch.get("score", 0)
                all_challenges.append(ch)

        if not all_challenges:
            print("❌ No challenges available in any games.")
            return

        all_challenges.sort(key=lambda ch: ch["id"])
        print("\n📦 Available Challenges:")
        for ch in all_challenges:
            pts = ch.get("originalScore", ch.get("score", 0))
            print(f"{ch['id']:>3} | {ch['game_title']:<20} | [{ch.get('category','-')}] {ch['title']} ({pts} pts)")

        print()
        ids = input("🔢 Enter challenge IDs to clone (comma-separated): ").split(",")
        selected = [ch for ch in all_challenges if str(ch["id"]) in map(str.strip, ids)]
        if not selected:
            print("❌ No valid challenges selected.")
            return

        title = input("🎮 New game title: ").strip()
        new_game = create_game(dst_sess, dst_url, title, args.invite_code)
        print(f"\n✅ Created game: {new_game['title']} (ID: {new_game['id']})")
        duplicate_selected_challenges(src_sess, dst_sess, src_url, dst_url, src_url, selected, new_game["id"])

    elif len(games) > 0:
        print("\n📚 Available Games:")
        games.sort(key=lambda g: g["id"])
        for g in games:
            print(f"{g['id']}: {g['title']}")

        gid = input("🎯 Enter game ID to duplicate: ").strip()
        original = next((g for g in games if str(g["id"]) == gid), None)
        if not original:
            print("❌ Invalid game ID")
            return

        chs = fetch_challenges(src_sess, src_url, original["id"])
        if not chs:
            print("⚠️ No challenges found in selected game.")
            return

        print(f"\n🧩 Found {len(chs)} challenges.")
        if input("💭 Duplicate all? (y/n): ").strip().lower() != "y":
            for ch in chs:
                pts = ch.get("score", 0)
                print(f"{ch['id']:>3}: [{ch.get('category','-')}] {ch['title']} ({pts} pts)")
            ids = input("🔢 IDs to copy: ").split(",")
            chs = [c for c in chs if str(c["id"]) in map(str.strip, ids)]

        new_game = create_game(dst_sess, dst_url, original["title"] + " (Copy)", args.invite_code)
        print(f"\n✅ Created new hidden game: {new_game['title']} (ID: {new_game['id']})")
        duplicate_selected_challenges(src_sess, dst_sess, src_url, dst_url, src_url, chs, new_game["id"])

    else:
        print("❌ No games available.")

    print("\n🎉 Duplication complete.")

if __name__ == "__main__":
    main()
