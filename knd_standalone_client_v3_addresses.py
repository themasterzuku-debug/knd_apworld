import asyncio
import contextlib
import json
import os
import ssl
import uuid as uuidlib
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

import websockets
import dolphin_memory_engine as dme

# MUST match your AP world game string exactly:
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


def load_sent_location_names(slot_name: str) -> Set[str]:
    st = _load_state(slot_name)
    raw = st.get("sent_location_names", [])
    if isinstance(raw, list):
        return set(str(x) for x in raw)
    return set()


def save_sent_location_names(slot_name: str, names: Set[str]) -> None:
    st = _load_state(slot_name)
    st["sent_location_names"] = sorted(names)
    _save_state(slot_name, st)


def try_hook_dolphin() -> bool:
    if dme.is_hooked():
        return True
    try:
        dme.hook()
        return dme.is_hooked()
    except Exception:
        return False


def read_u8(addr: int) -> int:
    return int(dme.read_bytes(addr, 1)[0])


def write_u8(addr: int, value: int) -> None:
    dme.write_bytes(addr, bytes([value & 0xFF]))


async def _send(ws, obj: Dict[str, Any]) -> None:
    await ws.send(json.dumps([obj]))


@dataclass(frozen=True)
class FlagCheck:
    location_name: str
    addr: int


@dataclass(frozen=True)
class TierCheck:
    stage_region: str
    addr: int


class Watcher:
    """
    Uses ONLY the addresses you listed in chat.
    - Completion flags: u8 == 1
    - Sooper secrets: u8 == 1
    - Monkey tier: u8 0..4 maps to 25/50/75/100 checks
    """
    def __init__(self) -> None:
        # Completion flags
        self.flags: List[FlagCheck] = [
            FlagCheck("Stage_01_Tutorial_Complete", 0x8076F54F),
            FlagCheck("Stage_02_Donutty_Complete", 0x8076F4AF),
            FlagCheck("Stage_03_Boogification_Complete", 0x8076F5BF),
            FlagCheck("Stage_04_SnotBomber_Complete", 0x8076F4EF),
            FlagCheck("Stage_05_Spank_Happy_Complete", 0x8076F57F),
            FlagCheck("Stage_06_Hamsterama_Complete", 0x8076F55F),
            FlagCheck("Stage_07_Spankarific_Complete", 0x8076F44F),
            FlagCheck("Stage_08_Tarpoon_Complete", 0x8076F50F),
            FlagCheck("Stage_09_Ship_Shape_Complete", 0x8076F4DF),
            FlagCheck("Stage_10_Brush_Off_Complete", 0x8076F46F),
            FlagCheck("Stage_11_Cavity_Cave_Complete", 0x8076F48F),
            FlagCheck("Stage_12_Overflow_Complete", 0x8076F59F),
            FlagCheck("Stage_13_MoonTrip_Complete", 0x8076F52F),
            FlagCheck("Stage_14_Lunarumble_Complete", 0x8076F4CF),
        ]

        # L1 "secret" (you said Toiletnator Card / 12 monkeys unlock — used as bosskey loc)
        self.flags.append(FlagCheck("Stage_01_Tutorial_Secret", 0x8077026F))

        # Sooper secrets you listed (only those that exist in your AP locations list)
        self.flags += [
            FlagCheck("Stage_01_Tutorial_SooperSecret", 0x8077027F),
            FlagCheck("Stage_03_Boogification_SooperSecret_1", 0x807716A7),
            FlagCheck("Stage_03_Boogification_SooperSecret_2", 0x807716A3),
            FlagCheck("Stage_05_Spank_Happy_SooperSecret_1", 0x807702DF),
            FlagCheck("Stage_07_Spankarific_SooperSecret_1", 0x8077013F),
            FlagCheck("Stage_07_Spankarific_SooperSecret_2", 0x807715B3),
            # If/when you confirm addresses for Stage_10 / Stage_12 sooper secrets, add here.
        ]

        # Monkey tiers (0..4 => 25/50/75/100)
        self.tiers: List[TierCheck] = [
            TierCheck("Stage_02_Donutty", 0x8077020F),       # you labeled L2 monkeys
            TierCheck("Stage_03_Boogification", 0x8077030F),
            TierCheck("Stage_04_SnotBomber", 0x8077023F),
            TierCheck("Stage_05_Spank_Happy", 0x807702CF),
            TierCheck("Stage_06_Hamsterama", 0x8077029F),
            TierCheck("Stage_07_Spankarific", 0x8077012F),
            TierCheck("Stage_08_Tarpoon", 0x8077024F),
            TierCheck("Stage_09_Ship_Shape", 0x8077022F),
            TierCheck("Stage_10_Brush_Off", 0x8077018F),
            TierCheck("Stage_11_Cavity_Cave", 0x807701CF),
            TierCheck("Stage_12_Overflow", 0x807702FF),
            TierCheck("Stage_13_MoonTrip", 0x8077025F),
            TierCheck("Stage_15_Credits", 0x8077033F),
        ]

        self._seen: Set[str] = set()
        self._tier_high: Dict[str, int] = {}
        self._tier_last: Dict[str, int] = {}

    @staticmethod
    def _clamp(v: int) -> int:
        return 0 if v < 0 else 4 if v > 4 else v

    def poll(self) -> List[str]:
        out: List[str] = []

        for chk in self.flags:
            if chk.location_name in self._seen:
                continue
            try:
                if read_u8(chk.addr) == 1:
                    self._seen.add(chk.location_name)
                    out.append(chk.location_name)
            except Exception:
                continue

        # Tier milestones
        suffix = {1: "25", 2: "50", 3: "75", 4: "100"}
        for t in self.tiers:
            try:
                tier = self._clamp(read_u8(t.addr))
            except Exception:
                continue

            last = self._tier_last.get(t.stage_region)
            self._tier_last[t.stage_region] = tier

            # If tier resets (e.g., leaving level), reset highwater so you can earn milestones again if needed
            if last is not None and last > 0 and tier == 0:
                self._tier_high[t.stage_region] = 0

            hi = self._tier_high.get(t.stage_region, 0)
            if tier > hi:
                for x in range(hi + 1, tier + 1):
                    sfx = suffix.get(x)
                    if sfx:
                        out.append(f"{t.stage_region}_Secret_{sfx}_Monkeys")
                self._tier_high[t.stage_region] = tier

        return out


def apply_item_by_name(item_name: str) -> None:
    """
    Minimal item writes using the "active for level start" tech-enable addresses you gave.
    This uses substring matching so it works regardless of your exact item prefixes.
    """
    name = item_name.lower()

    # If you decide to "redirect" weapon gain into these, this is where that goes.
    mapping = [
        ("gumzooka", 0x8076F4BF),
        ("smellmet", 0x8076F5CF),
        ("coolbus", None),   # multiple coolbus upgrades exist; handled below
        ("snot", 0x8076F4FF),
        ("splanker", 0x8076F58F),
        ("frappe", 0x8076F56F),
        ("scampp", 0x8076F45F),
        ("tarpoon", 0x8076F51F),
        ("thumper", 0x8076F47F),
        ("bajooka", 0x8076F49F),
        ("sluggah", 0x8076F5AF),
        ("moontrip", 0x8076F53F),
    ]

    # CoolBus variants
    if "coolbus" in name and "snot" in name:
        write_u8(0x8076F4FF, 1)
        return
    if "coolbus" in name and "tarpoon" in name:
        write_u8(0x8076F51F, 1)
        return
    if "coolbus" in name and "moontrip" in name:
        write_u8(0x8076F53F, 1)
        return

    for key, addr in mapping:
        if key in name and addr is not None:
            write_u8(addr, 1)
            return


async def run_client(connect: str, player: str, password: str) -> None:
    url = connect.strip()
    if "://" not in url:
        url = "ws://" + url
    url = url.replace("archipelago://", "ws://")

    ssl_ctx = None
    if url.startswith("wss://"):
        ssl_ctx = ssl.create_default_context()

    client_uuid = ensure_uuid(player)
    last_idx = get_last_item_index(player)
    sent_location_names = load_sent_location_names(player)

    print(f"[AP] Connecting to {url} as '{player}' (uuid={client_uuid})", flush=True)

    async with websockets.connect(url, ping_interval=None, ping_timeout=None, ssl=ssl_ctx) as ws:
        # RoomInfo
        roominfo = None
        while roominfo is None:
            msgs = json.loads(await ws.recv())
            roominfo = next((m for m in msgs if m.get("cmd") == "RoomInfo"), None)
        print(f"[AP] RoomInfo ok. password_required={roominfo.get('password')}", flush=True)

        server_version = roominfo.get("version") or {"major": 0, "minor": 6, "build": 5, "class": "Version"}

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

        while True:
            msgs = json.loads(await ws.recv())
            refused = next((m for m in msgs if m.get("cmd") == "ConnectionRefused"), None)
            if refused:
                raise RuntimeError(f"ConnectionRefused: {refused.get('errors')}")
            connected = next((m for m in msgs if m.get("cmd") == "Connected"), None)
            if connected:
                print(f"[AP] Connected! team={connected.get('team')} slot={connected.get('slot')}", flush=True)
                break

        # DataPackage: map location names -> ids and items -> names
        await _send(ws, {"cmd": "GetDataPackage"})
        datapkg = None
        while datapkg is None:
            msgs = json.loads(await ws.recv())
            dp = next((m for m in msgs if m.get("cmd") == "DataPackage"), None)
            if dp:
                datapkg = dp.get("data")

        game_dp = (datapkg or {}).get("games", {}).get(GAME_NAME, {})
        location_name_to_id: Dict[str, int] = game_dp.get("location_name_to_id", {}) or {}
        item_name_to_id: Dict[str, int] = game_dp.get("item_name_to_id", {}) or {}
        item_id_to_name: Dict[int, str] = {int(v): k for k, v in item_name_to_id.items()}

        print(f"[AP] DataPackage ok. locations={len(location_name_to_id)} items={len(item_name_to_id)}", flush=True)

        print("[DOLPHIN] Waiting for Dolphin hook...", flush=True)
        while not try_hook_dolphin():
            await asyncio.sleep(0.5)
        print("[DOLPHIN] Hooked!", flush=True)

        watcher = Watcher()

        async def watch_loop() -> None:
            nonlocal sent_location_names
            while True:
                try:
                    if not dme.is_hooked():
                        await asyncio.sleep(0.5)
                        continue

                    names = watcher.poll()
                    if names:
                        ids: List[int] = []
                        for nm in names:
                            if nm in sent_location_names:
                                continue
                            loc_id = location_name_to_id.get(nm)
                            if loc_id is None:
                                print(f"[NEED] Location name not in DataPackage: {nm}", flush=True)
                                continue
                            sent_location_names.add(nm)
                            ids.append(int(loc_id))

                        if ids:
                            await _send(ws, {"cmd": "LocationChecks", "locations": ids})
                            save_sent_location_names(player, sent_location_names)
                            print(f"[CHECK] Sent {len(ids)} check(s).", flush=True)

                    await asyncio.sleep(0.10)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.5)

        watch_task = asyncio.create_task(watch_loop())

        print("[AP] Ready. Waiting for items...", flush=True)
        try:
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

                            item_id = int(net_item.get("item"))
                            item_name = item_id_to_name.get(item_id, f"ItemID_{item_id}")
                            print(f"[ITEM] idx={item_index} {item_name} (id={item_id})", flush=True)

                            try:
                                apply_item_by_name(item_name)
                            except Exception as e:
                                print(f"[ERR] Apply item {item_name}: {e}", flush=True)

                            last_idx = item_index
                            set_last_item_index(player, last_idx)

                    elif cmd == "PrintJSON":
                        # leave as raw-ish to keep it compact
                        print(f"[MSG] {m.get('type')}: {m.get('data')}", flush=True)

        finally:
            watch_task.cancel()
            with contextlib.suppress(Exception):
                await watch_task


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--connect", required=True, help="host:port or ws://host:port or wss://host:port")
    ap.add_argument("--player", required=True, help="Slot name exactly as in the room")
    ap.add_argument("--password", default="", help="Room password, if any")
    args = ap.parse_args()
    asyncio.run(run_client(args.connect, args.player, args.password))


if __name__ == "__main__":
    main()
