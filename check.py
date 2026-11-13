import json
import os
import urllib.request

API_KEY = os.environ["HYPIXEL_API_KEY"]
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
PLAYER = os.environ["PLAYER_NAME"]
STATE_FILE = "state.txt"


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "hypixel-watch", **(headers or {})})
    with urllib.request.urlopen(req) as r:
        return json.load(r)


uuid = get_json(f"https://api.mojang.com/users/profiles/minecraft/{PLAYER}")["id"]
data = get_json(f"https://api.hypixel.net/v2/status?uuid={uuid}", {"API-Key": API_KEY})
if not data["success"]:
    raise RuntimeError(f"Hypixel API error: {data}")

session = data["session"]
online = session["online"]
was_online = open(STATE_FILE).read().strip() == "online" if os.path.exists(STATE_FILE) else False

if online and not was_online:
    game = session.get("gameType", "?")
    mode = session.get("mode", "")
    body = json.dumps({"content": f"🟢 **{PLAYER}** is on Hypixel — {game} {mode}".strip()}).encode()
    req = urllib.request.Request(WEBHOOK, data=body, headers={"Content-Type": "application/json", "User-Agent": "hypixel-watch"})
    urllib.request.urlopen(req)

with open(STATE_FILE, "w") as f:
    f.write("online" if online else "offline")

print(f"{PLAYER}: {'online' if online else 'offline'}")
