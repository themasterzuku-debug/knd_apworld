import asyncio
import json
import os
import uuid as uuidlib
from typing import Any, Dict, Optional

import websockets  # pip install websockets
import dolphin_memory_engine as dme


# MUST match your AP world "game" string exactly:
GAME_NAME = "Codename: Kids Next Door (GC)"

CLIENT_TAGS = ["KNDStandalone", "Dolphin"]
# Receive remote items + own items + starting inventory
ITEMS_HANDLING = 0b001 | 0b010 | 0b100

STATE_DIR = os.path.join(os.path.dirname(__file__), ".knd_client_state")
os.makedirs(STATE_DIR, exist_ok=True)


def _state_path(slot_name: str) -> str:
    safe = "".join(c for c in slot_name if c.isalnum() or c in ("-", "_"))[:64]
    return os.path.join(STATE_DIR, f"{safe}.json")


def _load_state(slot_name: str) -> Dict[str, Any]:
    p = _state_path(slot_name)
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_state(slot_name: str, data: Dict[str, Any]) -> None:
    p = _state_path(slot_name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def ensure_uuid(slot_name: str) -> str:
    st = _load_state(slot_name)
    if "uuid" not in st:
        st["uuid"] = str(uuidlib.uuid4())
        _save_state(slot_name, st)
    return str(st["uuid"])


def get_last_item_index(slot_name: str) -> int:
    st = _load_state(slot_name)
    return int(st.get("last_item_index", -1))


def set_last_item_index(slot_name: str, idx: int) -> None:
    st = _load_state(slot_name)
    st["last_item_index"] = int(idx)
    _save_state(slot_name, st)


def try_hook_dolphin() -> bool:
    if dme.is_hooked():
        return True
    try:
        dme.hook()
        return dme.is_hooked()
    except Exception:
        return False


async def _send(ws, obj: Dict[str, Any]) -> None:
    await ws.send(json.dumps([obj]))


async def run_client(connect: str, player: str, password: str) -> None:
    # Accept host:port or ws://host:port
    url = connect.strip()
    if "://" not in url:
        url = "ws://" + url
    url = url.replace("archipelago://", "ws://")

    client_uuid = ensure_uuid(player)
    last_idx = get_last_item_index(player)

    print(f"[AP] Connecting to {url} as '{player}' (uuid={client_uuid})", flush=True)

    async with websockets.connect(url, ping_interval=None, ping_timeout=None) as ws:
        # Wait for RoomInfo
        while True:
            msgs = json.loads(await ws.recv())
            roominfo = next((m for m in msgs if m.get("cmd") == "RoomInfo"), None)
            if roominfo:
                break
        print(f"[AP] RoomInfo ok. password_required={roominfo.get('password')}", flush=True)

        # Send Connect (version: use server's version dict if present, else a safe default)
        server_version = roominfo.get("version") or {"major": 0, "minor": 6, "build": 4, "class": "Version"}
        await _send(ws, {
            "cmd": "Connect",
            "password": password or "",
            "game": GAME_NAME,
            "name": player,
            "uuid": client_uuid,
            "version": server_version,
            "items_handling": ITEMS_HANDLING,
            "tags": CLIENT_TAGS,
            "slot_data": True,
        })

        # Wait for Connected / ConnectionRefused
        while True:
            msgs = json.loads(await ws.recv())
            refused = next((m for m in msgs if m.get("cmd") == "ConnectionRefused"), None)
            if refused:
                raise RuntimeError(f"ConnectionRefused: {refused.get('errors')}")
            connected = next((m for m in msgs if m.get("cmd") == "Connected"), None)
            if connected:
                print(f"[AP] Connected! team={connected.get('team')} slot={connected.get('slot')}", flush=True)
                break

        print("[DOLPHIN] Waiting for Dolphin hook...", flush=True)
        while not try_hook_dolphin():
            await asyncio.sleep(0.5)
        print("[DOLPHIN] Hooked!", flush=True)

        print("[AP] Ready. Waiting for items...", flush=True)
        async for raw in ws:
            msgs = json.loads(raw)
            for m in msgs:
                cmd = m.get("cmd")
                if cmd == "ReceivedItems":
                    start_index = int(m["index"])
                    items = m.get("items", [])
                    first_item_index = start_index - len(items)

                    for i, net_item in enumerate(items):
                        item_index = first_item_index + i
                        if item_index <= last_idx:
                            continue

                        print(
                            f"[ITEM] idx={item_index} item={net_item.get('item')} "
                            f"from_player={net_item.get('player')} loc={net_item.get('location')} flags={net_item.get('flags')}",
                            flush=True
                        )

                        # TODO: Apply items to game memory here (writes using dolphin_memory_engine)

                        last_idx = item_index
                        set_last_item_index(player, last_idx)

                elif cmd == "PrintJSON":
                    print(f"[MSG] {m.get('type')}: {m.get('data')}", flush=True)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--connect", required=True, help="host:port or ws://host:port (example: archipelago.gg:38281)")
    ap.add_argument("--player", required=True, help="Slot name exactly as in the room")
    ap.add_argument("--password", default="", help="Room password, if any")
    args = ap.parse_args()
    asyncio.run(run_client(args.connect, args.player, args.password))


if __name__ == "__main__":
    main()
