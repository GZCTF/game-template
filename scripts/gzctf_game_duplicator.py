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

    The script preserves flags, metadata, and attachments.
    All duplicated challenges are disabled by default.

Usage:
    Clone a game:
        python3 gzctf_game_duplicator.py --url https://ctf.example.com --username admin --password pass

    Create new game from selected challenges:
        python3 gzctf_game_duplicator.py --url https://ctf.example.com --username admin --password pass --newgame

    With custom invite code:
        python3 gzctf_game_duplicator.py --url https://ctf.example.com --username admin --password pass --invite-code MYCODE123
"""

import requests
import time
import argparse
import secrets

def generate_invite_code(length=24):
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def login(base_url, username, password):
    session = requests.Session()
    resp = session.post(f"{base_url}/api/account/login", json={
        "userName": username,
        "password": password,
        "challenge": None
    })
    if "GZCTF_Token" not in session.cookies:
        raise Exception("Login failed")
    return session

def fetch_games(session, base_url):
    resp = session.get(f"{base_url}/api/game?count=50&skip=0")
    resp.raise_for_status()
    return resp.json()["data"]

def fetch_challenges(session, base_url, game_id):
    resp = session.get(f"{base_url}/api/game/{game_id}/details")
    resp.raise_for_status()
    data = resp.json()
    flat = []
    for category in data.get("challenges", {}):
        for ch in data["challenges"][category]:
            ch["game_id"] = game_id
            flat.append(ch)
    return flat

def fetch_challenge_config(session, base_url, game_id, challenge_id):
    url = f"{base_url}/api/edit/games/{game_id}/challenges/{challenge_id}"
    resp = session.get(url)
    resp.raise_for_status()
    return resp.json()

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
    resp = session.post(f"{base_url}/api/edit/games", json=data)
    resp.raise_for_status()
    return resp.json()

def create_challenge_minimal(session, base_url, game_id, ch_full, ch_meta):
    score = ch_meta.get("originalScore", ch_meta.get("score", 100))
    data = {
        "title": ch_full.get("title", ch_meta["title"]),
        "category": ch_full.get("category", ch_meta.get("category", "Misc")),
        "type": ch_full.get("type", "StaticAttachment"),
        "isEnabled": False,  # Always disable by default
        "score": score,
        "minScore": score,
        "originalScore": score
    }
    resp = session.post(f"{base_url}/api/edit/games/{game_id}/challenges", json=data)
    resp.raise_for_status()
    return resp.json()

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
    resp = session.put(f"{base_url}/api/edit/games/{game_id}/challenges/{challenge_id}", json=patch_fields)
    resp.raise_for_status()

def duplicate_flags(session, base_url, new_game_id, new_challenge_id, flags):
    flag_data = [{"flag": f["flag"]} for f in flags]
    url = f"{base_url}/api/edit/games/{new_game_id}/challenges/{new_challenge_id}/flags"
    resp = session.post(url, json=flag_data)
    resp.raise_for_status()

def duplicate_attachment(session, base_url, full_url_base, new_game_id, new_challenge_id, attachment):
    if not attachment:
        return
    att_type = attachment.get("type")
    if att_type == "Remote":
        remote_url = f"{full_url_base}{attachment['url']}"
    elif att_type == "Local":
        remote_url = f"{full_url_base}{attachment['url']}"
    else:
        return
    data = {
        "attachmentType": "Remote",
        "remoteUrl": remote_url
    }
    url = f"{base_url}/api/edit/games/{new_game_id}/challenges/{new_challenge_id}/attachment"
    resp = session.post(url, json=data)
    resp.raise_for_status()

def duplicate_selected_challenges(session, base_url, full_url_base, all_challenges, new_game_id):
    for ch_meta in all_challenges:
        full = fetch_challenge_config(session, base_url, ch_meta["game_id"], ch_meta["id"])
        created = create_challenge_minimal(session, base_url, new_game_id, full, ch_meta)
        update_challenge(session, base_url, new_game_id, created["id"], full)
        if full.get("flags"):
            duplicate_flags(session, base_url, new_game_id, created["id"], full["flags"])
        duplicate_attachment(session, base_url, full_url_base, new_game_id, created["id"], full.get("attachment"))
        print(f" → Duplicated: {created['title']}")

def main():
    parser = argparse.ArgumentParser(description="GZCTF Game and Challenge Cloner")
    parser.add_argument("--url", required=True, help="Base URL of the GZCTF instance")
    parser.add_argument("--username", required=True, help="Username")
    parser.add_argument("--password", required=True, help="Password")
    parser.add_argument("--invite-code", help="Optional invite code")
    parser.add_argument("--newgame", action="store_true", help="Create a new game from selected challenges")
    args = parser.parse_args()

    base_url = args.url.rstrip('/')
    session = login(base_url, args.username, args.password)
    games = fetch_games(session, base_url)

    if args.newgame:
        print("\n📦 Available Games:")
        all_challenges = []
        for g in games:
            chs = fetch_challenges(session, base_url, g["id"])
            for ch in chs:
                ch["game_title"] = g["title"]
                all_challenges.append(ch)

        all_challenges.sort(key=lambda ch: ch["id"])

        print("\n🧩 Challenges Across All Games:")
        for ch in all_challenges:
            print(f"{ch['id']:>3} | {ch['game_title']:<20} | [{ch.get('category', '-')}] {ch['title']} ({ch.get('originalScore', ch.get('score', 0))} pts)")

        ids = input("\nEnter comma-separated challenge IDs to clone: ").split(",")
        selected = [ch for ch in all_challenges if str(ch["id"]) in [i.strip() for i in ids]]

        if not selected:
            print("❌ No valid challenges selected.")
            return

        title = input("\n🎮 Enter a name for the new game: ").strip()
        new_game = create_game(session, base_url, title, args.invite_code)
        print(f"\n✅ Created new game: {new_game['title']} (ID: {new_game['id']})")
        print(f"🔐 Invite Code: {new_game['inviteCode']}")
        duplicate_selected_challenges(session, base_url, args.url.rstrip('/'), selected, new_game["id"])

    else:
        print("\nAvailable Games:")
        games.sort(key=lambda g: g["id"])
        for g in games:
            print(f"{g['id']}: {g['title']}")

        game_id = input("\nEnter game ID to duplicate: ").strip()
        original = next((g for g in games if str(g["id"]) == game_id), None)
        if not original:
            print("❌ Invalid game ID")
            return

        challenges_meta = fetch_challenges(session, base_url, game_id)
        print(f"\nFound {len(challenges_meta)} challenges.")

        dup_all = input("Duplicate all challenges? (y/n): ").strip().lower()
        if dup_all != 'y':
            print("\nAvailable Challenges:")
            challenges_meta.sort(key=lambda ch: ch["id"])
            for ch in challenges_meta:
                print(f"{ch['id']:>3}: [{ch.get('category', '-')}] {ch['title']} ({ch.get('originalScore', ch.get('score', 0))} pts)")
            ids = input("Enter comma-separated challenge IDs to copy: ").split(",")
            ids = [i.strip() for i in ids]
            challenges_meta = [ch for ch in challenges_meta if str(ch["id"]) in ids]

        new_title = original["title"] + " (Copy)"
        new_game = create_game(session, base_url, new_title, args.invite_code)
        print(f"\n✅ Created new hidden game: {new_game['title']} (ID: {new_game['id']})")
        print(f"🔐 Invite Code: {new_game['inviteCode']}")
        duplicate_selected_challenges(session, base_url, args.url.rstrip('/'), challenges_meta, new_game["id"])

    print("\n🎉 Duplication complete.")

if __name__ == "__main__":
    main()
