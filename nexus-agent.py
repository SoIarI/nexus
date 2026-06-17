#!/usr/bin/env python3
"""NEXUS PC Agent — Telegram task listener for Windows."""

import json
import os
import sys
import time
import threading
import requests
import pyperclip
from windows_toasts import Toast, WindowsToaster

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nexus-config.json")


def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] nexus-config.json not found at {CONFIG_FILE}")
        print("Copy nexus-config.json, fill in your values, and try again.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in nexus-config.json: {e}")
        sys.exit(1)


def tg_send(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        res = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
        data = res.json()
        if not data.get("ok"):
            print(f"  [WARN] Telegram error: {data.get('description')}")
            return False
        return True
    except Exception as e:
        print(f"  [WARN] Send failed: {e}")
        return False


def tg_get_updates(bot_token, offset):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        res = requests.get(
            url,
            params={"offset": offset, "timeout": 5, "allowed_updates": ["message"]},
            timeout=15,
        )
        data = res.json()
        if not data.get("ok"):
            return [], offset
        updates = data.get("result", [])
        new_offset = updates[-1]["update_id"] + 1 if updates else offset
        return updates, new_offset
    except Exception as e:
        print(f"  [WARN] Poll error: {e}")
        return [], offset


def show_toast(title, body):
    try:
        toaster = WindowsToaster("NEXUS")
        t = Toast()
        t.text_fields = [title, (body or "")[:120]]
        toaster.show_toast(t)
    except Exception as e:
        print(f"  [WARN] Toast failed: {e}")


def extract_title(text):
    for line in text.strip().splitlines():
        if line.startswith("📋"):
            return line.replace("📋", "").strip()
    return (text.splitlines()[0] if text else "New task")[:60]


def print_banner(pc_chat_id):
    print("╔══════════════════════════════════════╗")
    print("║           NEXUS PC AGENT             ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  Listening on chat: {str(pc_chat_id)[:18]:<18} ║")
    print("╠══════════════════════════════════════╣")
    print("║  done <snippet>  — mark complete     ║")
    print("║  wip  <snippet>  — mark in progress  ║")
    print("║  q / quit        — exit              ║")
    print("╚══════════════════════════════════════╝")
    print()


def main():
    config = load_config()
    bot_token = config.get("bot_token", "").strip()
    phone_chat_id = str(config.get("phone_chat_id", "")).strip()
    pc_chat_id = str(config.get("pc_chat_id", "")).strip()

    if not bot_token or bot_token == "YOUR_BOT_TOKEN_HERE":
        print("[ERROR] bot_token not set in nexus-config.json")
        sys.exit(1)
    if not pc_chat_id or pc_chat_id == "YOUR_PC_CHAT_ID_HERE":
        print("[ERROR] pc_chat_id not set in nexus-config.json")
        sys.exit(1)

    print_banner(pc_chat_id)

    offset = 0
    running = True

    def poll_loop():
        nonlocal offset
        while running:
            try:
                updates, offset = tg_get_updates(bot_token, offset)
                for update in updates:
                    msg = update.get("message", {})
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    text = msg.get("text", "")

                    if chat_id != pc_chat_id or not text:
                        continue

                    title = extract_title(text)
                    ts = time.strftime("%H:%M:%S")
                    print(f"[{ts}] ─── TASK RECEIVED ───────────────────")
                    print(text[:300] + ("…" if len(text) > 300 else ""))
                    print()

                    show_toast(title, text)

                    try:
                        pyperclip.copy(text)
                        print(f"  ✓ Copied to clipboard\n")
                    except Exception as e:
                        print(f"  ! Clipboard unavailable: {e}\n")

                time.sleep(5)
            except Exception as e:
                print(f"[WARN] Poll loop error: {e}")
                time.sleep(10)

    thread = threading.Thread(target=poll_loop, daemon=True)
    thread.start()

    while running:
        try:
            line = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\nShutting down.")
            break

        if not line:
            continue
        if line.lower() in ("q", "quit", "exit"):
            print("NEXUS agent stopped.")
            running = False
            break

        parts = line.split(" ", 1)
        cmd = parts[0].lower()
        snippet = parts[1].strip() if len(parts) > 1 else "task"

        if cmd == "done":
            reply = f"✅ Done: {snippet}"
        elif cmd == "wip":
            reply = f"🔄 In Progress: {snippet}"
        else:
            print("  Commands: done <snippet> | wip <snippet> | q")
            continue

        if phone_chat_id and phone_chat_id != "YOUR_PHONE_CHAT_ID_HERE":
            ok = tg_send(bot_token, phone_chat_id, reply)
            print(f"  {'✓ Sent to phone' if ok else '✗ Send failed'}: {reply}")
        else:
            print(f"  (no phone_chat_id set — not sent): {reply}")


if __name__ == "__main__":
    main()
