from __future__ import annotations

import asyncio
import contextlib
import hashlib
import json
import logging
import os
import ssl
import sys
import uuid as uuidlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple

import dolphin_memory_engine as dme  # type: ignore
import websockets

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:
    tk = None
    messagebox = None

from knd_memory_map_real_v2 import KNDMemoryMapReal

GAME_NAME = "Codename: Kids Next Door (GC)"
CLIENT_TAGS = ["KND", "Dolphin", "EasyLauncher"]
ITEMS_HANDLING = 0b001 | 0b010 | 0b100
BASE_DIR = Path(__file__).resolve().parent
STATE_DIR = BASE_DIR / ".knd_client_state"
PROFILE_DIR = STATE_DIR / "profiles"
STATE_DIR.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)
CONFIG_PATH = STATE_DIR / "launcher_config.json"

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("KNDEasy")


# ----------------------------
# UI / config helpers
# ----------------------------
def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_config(cfg: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def prompt_settings() -> Dict[str, str]:
    cfg = load_config()
    defaults = {
        "connect": str(cfg.get("connect", "ws://localhost:38281")),
        "player": str(cfg.get("player", "")),
        "password": str(cfg.get("password", "")),
        "profile_override": str(cfg.get("profile_override", "")),
    }

    # Fall back to console prompts if tkinter is unavailable
    if tk is None:
        connect = input(f"Server [{defaults['connect']}]: ").strip() or defaults["connect"]
        player = input(f"Player [{defaults['player']}]: ").strip() or defaults["player"]
        password = input(f"Password [{defaults['password']}]: ").strip() or defaults["password"]
        profile_override = input(f"Profile name override (optional) [{defaults['profile_override']}]: ").strip() or defaults["profile_override"]
        return {
            "connect": connect,
            "player": player,
            "password": password,
            "profile_override": profile_override,
        }

    result: Dict[str, str] = {}
    root = tk.Tk()
    root.title("KND Archipelago Easy Client")
    root.geometry("560x250")
    root.resizable(False, False)

    entries: Dict[str, tk.Entry] = {}
    labels = [
        ("connect", "Server (host:port or ws://...)", defaults["connect"]),
        ("player", "Player name", defaults["player"]),
        ("password", "Password (optional)", defaults["password"]),
        ("profile_override", "Profile name override (optional)", defaults["profile_override"]),
    ]

    for row, (key, label, value) in enumerate(labels):
        tk.Label(root, text=label, anchor="w").grid(row=row, column=0, sticky="w", padx=12, pady=(12 if row == 0 else 6, 2))
        ent = tk.Entry(root, width=55)
        ent.insert(0, value)
        if key == "password":
            ent.config(show="*")
        ent.grid(row=row, column=1, padx=12, pady=(12 if row == 0 else 6, 2), sticky="ew")
        entries[key] = ent

    status = tk.Label(root, text="Tip: leave Profile override blank to auto-separate saves by player + seed.", anchor="w", fg="#444")
    status.grid(row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 0))

    def start() -> None:
        result.update({k: e.get().strip() for k, e in entries.items()})
        if not result.get("connect") or not result.get("player"):
            if messagebox:
                messagebox.showerror("Missing info", "Server and Player are required.")
            return
        root.destroy()

    def quit_app() -> None:
        root.destroy()
        raise SystemExit(0)

    btn_frame = tk.Frame(root)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=18)
    tk.Button(btn_frame, text="Start", width=16, command=start).pack(side="left", padx=8)
    tk.Button(btn_frame, text="Cancel", width=16, command=quit_app).pack(side="left", padx=8)

    root.mainloop()
    if not result:
        raise SystemExit(0)
    save_config(result)
    return result


# ----------------------------
# Profile state helpers
# ----------------------------
def _slug(text: str, limit: int = 80) -> str:
    safe = "".join(c if c.isalnum() or c in "-_ ." else "_" for c in text).strip().replace(" ", "_")
    return safe[:limit] or "default"


def _seed_fingerprint(roominfo: Dict[str, Any], url: str) -> str:
    candidates = [
        roominfo.get("seed_name"),
        roominfo.get("room_id"),
        roominfo.get("server_address"),
        url,
    ]
    raw = next((str(x) for x in candidates if x), url)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"{_slug(raw, 36)}__{digest}"


def _legacy_state_path(slot_name: str) -> Path:
    safe = _slug(slot_name, 64)
    return STATE_DIR / f"{safe}.json"


def _profile_state_path(player: str, seed_key: str, override: str = "") -> Path:
    if override:
        return PROFILE_DIR / f"{_slug(override, 96)}.json"
    return PROFILE_DIR / f"{_slug(player, 40)}__{_slug(seed_key, 60)}.json"


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def ensure_state(profile_path: Path, player: str) -> Dict[str, Any]:
    st = _load_json(profile_path)
    if not st:
        legacy = _legacy_state_path(player)
        if legacy.exists():
            st = _load_json(legacy)
            if st:
                log.info(f"Imported previous state from {legacy.name} into {profile_path.name}")
        if not st:
            st = {}
    if "uuid" not in st:
        st["uuid"] = str(uuidlib.uuid4())
    st.setdefault("last_item_index", -1)
    st.setdefault("sent_location_names", [])
    _save_json(profile_path, st)
    return st


# ----------------------------
# Dolphin helpers
# ----------------------------
class DolphinRW:
    def __init__(self, mem: KNDMemoryMapReal):
        self.mem = mem
        self._hooked = False

    def ensure_hooked(self) -> bool:
        if self._hooked and dme.is_hooked():
            return True
        try:
            if not dme.is_hooked():
                dme.hook()
            self._hooked = dme.is_hooked()
            return self._hooked
        except Exception:
            return False

    def read_u8(self, addr: int) -> int:
        return int(dme.read_bytes(addr, 1)[0])

    def write_u8(self, addr: int, value: int) -> None:
        dme.write_bytes(addr, bytes([value & 0xFF]))

    def safe_write_u8(self, addr: Optional[int], value: int, label: str) -> None:
        if addr is None:
            log.info(f"[SKIP] No address for {label}")
            return
        self.write_u8(addr, value)


# ----------------------------
# AP item application
# ----------------------------
def build_item_handlers(rw: DolphinRW) -> Dict[str, Callable[[], None]]:
    m = rw.mem
    handlers: Dict[str, Callable[[], None]] = {}

    # Stable item writes currently known / already used in your project.
    handlers.update({
        # tech toggles that were already in your v3 client
        "2x4_N2_Musket": lambda: rw.safe_write_u8(m.STAGE_02_TECH_ENABLE, 1, "Stage 02 Tech Enable"),
        "2x4_N3_Gumzooka": lambda: rw.safe_write_u8(m.STAGE_02_TECH_ENABLE, 1, "Stage 02 Tech Enable (Gumzooka)"),
        "2x4_N3_Smellmet": lambda: rw.safe_write_u8(m.STAGE_03_TECH_ENABLE, 1, "Stage 03 Tech Enable (Smellmet)"),
        "2x4_N4_Spank_Happy_Splanker": lambda: rw.safe_write_u8(m.STAGE_05_TECH_ENABLE, 1, "Stage 05 Tech Enable (Splanker)"),
        "2x4_N3_Hamsterama_Frappe": lambda: rw.safe_write_u8(m.STAGE_06_TECH_ENABLE, 1, "Stage 06 Tech Enable (Frappe)"),
        "2x4_N1_Spankarific_Scampp": lambda: rw.safe_write_u8(m.STAGE_07_TECH_ENABLE, 1, "Stage 07 Tech Enable (Scampp)"),
        "2x4_N3_Brush_Off_Thumper": lambda: rw.safe_write_u8(m.STAGE_10_TECH_ENABLE, 1, "Stage 10 Tech Enable (Thumper)"),
        "2x4_N1_Cavity_Cave_Bajooka": lambda: rw.safe_write_u8(m.STAGE_11_TECH_ENABLE, 1, "Stage 11 Tech Enable (Bajooka)"),
    })

    # Treat stage unlock items as the stable stage-complete/slot-unlock bytes from your real map.
    stage_unlocks = {
        "Stage_01_Tutorial_Unlock": m.STAGE_01_COMPLETE,
        "Stage_02_Donutty_Unlock": m.STAGE_02_COMPLETE,
        "Stage_03_Boogification_Unlock": m.STAGE_03_COMPLETE,
        "Stage_04_SnotBomber_Unlock": m.STAGE_04_COMPLETE,
        "Stage_05_Spank_Happy_Unlock": m.STAGE_05_COMPLETE,
        "Stage_06_Hamsterama_Unlock": m.STAGE_06_COMPLETE,
        "Stage_07_Spankarific_Unlock": m.STAGE_07_COMPLETE,
        "Stage_08_Tarpoon_Unlock": m.STAGE_08_COMPLETE,
        "Stage_09_Ship_Shape_Unlock": m.STAGE_09_COMPLETE,
        "Stage_10_Brush_Off_Unlock": m.STAGE_10_COMPLETE,
        "Stage_11_Cavity_Cave_Unlock": m.STAGE_11_COMPLETE,
        "Stage_12_Overflow_Unlock": m.STAGE_12_COMPLETE,
        "Stage_13_MoonTrip_Unlock": m.STAGE_13_COMPLETE,
        "Stage_14_Lunarumble_Unlock": m.STAGE_14_COMPLETE,
    }
    for item_name, addr in stage_unlocks.items():
        handlers[item_name] = (lambda a=addr, n=item_name: rw.safe_write_u8(a, 1, n))

    if m.N1_NUMBUH_86_ALT is not None:
        handlers["Outfit_N1_N86"] = lambda: rw.safe_write_u8(m.N1_NUMBUH_86_ALT, 1, "Numbuh 86 Alt")

    return handlers


# ----------------------------
# Check polling
# ----------------------------
@dataclass(frozen=True)
class FlagCheck:
    location_name: str
    addr: int


@dataclass(frozen=True)
class MultiAddrFlagCheck:
    location_name: str
    addrs: Tuple[int, ...]


@dataclass(frozen=True)
class MonkeyTierCheck:
    stage_region: str
    tier_addr: int


class ProgressWatcher:
    def __init__(self, rw: DolphinRW):
        self.rw = rw
        m = rw.mem
        self.completions: List[FlagCheck] = []
        completion_pairs = [
            ("Stage_01_Tutorial_Complete", m.STAGE_01_COMPLETE),
            ("Stage_02_Donutty_Complete", m.STAGE_02_COMPLETE),
            ("Stage_03_Boogification_Complete", m.STAGE_03_COMPLETE),
            ("Stage_04_SnotBomber_Complete", m.STAGE_04_COMPLETE),
            ("Stage_05_Spank_Happy_Complete", m.STAGE_05_COMPLETE),
            ("Stage_06_Hamsterama_Complete", m.STAGE_06_COMPLETE),
            ("Stage_07_Spankarific_Complete", m.STAGE_07_COMPLETE),
            ("Stage_08_Tarpoon_Complete", m.STAGE_08_COMPLETE),
            ("Stage_09_Ship_Shape_Complete", m.STAGE_09_COMPLETE),
            ("Stage_10_Brush_Off_Complete", m.STAGE_10_COMPLETE),
            ("Stage_11_Cavity_Cave_Complete", m.STAGE_11_COMPLETE),
            ("Stage_12_Overflow_Complete", m.STAGE_12_COMPLETE),
            ("Stage_13_MoonTrip_Complete", m.STAGE_13_COMPLETE),
            ("Stage_14_Lunarumble_Complete", m.STAGE_14_COMPLETE),
        ]
        for name, addr in completion_pairs:
            if addr is not None:
                self.completions.append(FlagCheck(name, addr))

        self.secrets: List[MultiAddrFlagCheck] = [
            MultiAddrFlagCheck("Stage_01_Tutorial_SooperSecret", m.STAGE_01_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_03_Boogification_SooperSecret_1", m.STAGE_03_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_03_Boogification_SooperSecret_2", m.STAGE_03_SOOPER_SECRET_2),
            MultiAddrFlagCheck("Stage_05_Spank_Happy_SooperSecret", m.STAGE_05_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_06_Hamsterama_SooperSecret", m.STAGE_06_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_07_Spankarific_SooperSecret_1", m.STAGE_07_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_07_Spankarific_SooperSecret_2", m.STAGE_07_SOOPER_SECRET_2),
        ]

        self.other_flags: List[FlagCheck] = []
        if m.N1_NUMBUH_86_ALT is not None:
            self.other_flags.append(FlagCheck("Outfit_N1_N86_Unlocked", m.N1_NUMBUH_86_ALT))
        if m.STAGE_01_12_MONKEYS_TOILETNATOR_CARD is not None:
            self.other_flags.append(FlagCheck("Stage_01_Toiletnator_Card_Unlocked", m.STAGE_01_12_MONKEYS_TOILETNATOR_CARD))

        monkey_pairs = [
            ("Stage_02_Donutty", m.STAGE_02_MONKEY_TIER),
            ("Stage_03_Boogification", m.STAGE_03_MONKEY_TIER),
            ("Stage_04_SnotBomber", m.STAGE_04_MONKEY_TIER),
            ("Stage_05_Spank_Happy", m.STAGE_05_MONKEY_TIER),
            ("Stage_06_Hamsterama", m.STAGE_06_MONKEY_TIER),
            ("Stage_07_Spankarific", m.STAGE_07_MONKEY_TIER),
            ("Stage_08_Tarpoon", m.STAGE_08_MONKEY_TIER),
            ("Stage_09_Ship_Shape", m.STAGE_09_MONKEY_TIER),
            ("Stage_10_Brush_Off", m.STAGE_10_MONKEY_TIER),
            ("Stage_11_Cavity_Cave", m.STAGE_11_MONKEY_TIER),
            ("Stage_12_Overflow", m.STAGE_12_MONKEY_TIER),
            ("Stage_13_MoonTrip", m.STAGE_13_MONKEY_TIER),
            ("Stage_15_Credits", m.STAGE_15_MONKEY_TIER),
        ]
        self.monkey_tiers: List[MonkeyTierCheck] = [MonkeyTierCheck(s, a) for s, a in monkey_pairs if a is not None]

        self._seen_persistent: Set[str] = set()
        self._monkey_highwater: Dict[str, int] = {}
        self._monkey_last: Dict[str, int] = {}

    @staticmethod
    def _clamp_tier(v: int) -> int:
        return 0 if v < 0 else 4 if v > 4 else v

    def poll(self) -> List[str]:
        new_checks: List[str] = []
        for chk in self.completions + self.other_flags:
            if chk.location_name in self._seen_persistent:
                continue
            try:
                if self.rw.read_u8(chk.addr) == 1:
                    self._seen_persistent.add(chk.location_name)
                    new_checks.append(chk.location_name)
            except Exception:
                continue

        for chk in self.secrets:
            if chk.location_name in self._seen_persistent:
                continue
            try:
                if any(self.rw.read_u8(addr) == 1 for addr in chk.addrs):
                    self._seen_persistent.add(chk.location_name)
                    new_checks.append(chk.location_name)
            except Exception:
                continue

        for mt in self.monkey_tiers:
            try:
                tier = self._clamp_tier(self.rw.read_u8(mt.tier_addr))
            except Exception:
                continue
            last = self._monkey_last.get(mt.stage_region)
            self._monkey_last[mt.stage_region] = tier
            if last is not None and last > 0 and tier == 0:
                self._monkey_highwater[mt.stage_region] = 0
            hi = self._monkey_highwater.get(mt.stage_region, 0)
            if tier > hi:
                stage_milestone_suffix = {
                    "Stage_15_Credits": {1: "10", 2: "20", 3: "30", 4: "40"},
                }
                milestone_suffix = stage_milestone_suffix.get(mt.stage_region, {1: "25", 2: "50", 3: "75", 4: "100"})
                for t in range(hi + 1, tier + 1):
                    sfx = milestone_suffix.get(t)
                    if sfx:
                        new_checks.append(f"{mt.stage_region}_Secret_{sfx}_Monkeys")
                self._monkey_highwater[mt.stage_region] = tier

        return new_checks


# ----------------------------
# Client runtime
# ----------------------------
async def _send(ws, obj: Dict[str, Any]) -> None:
    await ws.send(json.dumps([obj]))


async def run_client(connect: str, player: str, password: str, profile_override: str = "") -> None:
    url = connect.strip()
    if "://" not in url:
        url = "ws://" + url
    url = url.replace("archipelago://", "ws://")
    ssl_ctx = ssl.create_default_context() if url.startswith("wss://") else None

    rw = DolphinRW(KNDMemoryMapReal())
    handlers = build_item_handlers(rw)
    watcher = ProgressWatcher(rw)

    print(f"[AP] Connecting to {url} as '{player}'")
    async with websockets.connect(url, ping_interval=None, ping_timeout=None, ssl=ssl_ctx) as ws:
        roominfo = None
        while roominfo is None:
            msgs = json.loads(await ws.recv())
            roominfo = next((m for m in msgs if m.get("cmd") == "RoomInfo"), None)

        seed_key = _seed_fingerprint(roominfo or {}, url)
        profile_path = _profile_state_path(player, seed_key, profile_override)
        state = ensure_state(profile_path, player)
        sent_location_names: Set[str] = set(str(x) for x in state.get("sent_location_names", []))
        last_idx = int(state.get("last_item_index", -1))
        client_uuid = str(state["uuid"])

        print(f"[STATE] Profile: {profile_path.name}")
        print(f"[STATE] Seed key: {seed_key}")

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
                print(f"[AP] Connected! team={connected.get('team')} slot={connected.get('slot')}")
                break

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
        print(f"[AP] DataPackage ok. locations={len(location_name_to_id)} items={len(item_name_to_id)}")

        print("[DOLPHIN] Waiting for Dolphin hook...")
        while not rw.ensure_hooked():
            await asyncio.sleep(0.5)
        print("[DOLPHIN] Hooked! Ready to play.")

        async def watch_loop() -> None:
            nonlocal sent_location_names
            while True:
                try:
                    if not rw.ensure_hooked():
                        await asyncio.sleep(1.0)
                        continue
                    names = watcher.poll()
                    if names:
                        ids: List[int] = []
                        for nm in names:
                            if nm in sent_location_names:
                                continue
                            loc_id = location_name_to_id.get(nm)
                            if loc_id is None:
                                log.info(f"[NEED] Location name not in DataPackage: {nm}")
                                continue
                            sent_location_names.add(nm)
                            ids.append(int(loc_id))
                        if ids:
                            await _send(ws, {"cmd": "LocationChecks", "locations": ids})
                            state["sent_location_names"] = sorted(sent_location_names)
                            _save_json(profile_path, state)
                            print(f"[CHECK] Sent {len(ids)} check(s).")
                    await asyncio.sleep(0.10)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.5)

        watch_task = asyncio.create_task(watch_loop())

        print("[KND] Running. Leave this window open while you play.")
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
                            print(f"[ITEM] idx={item_index} {item_name}")
                            try:
                                if rw.ensure_hooked():
                                    handler = handlers.get(item_name)
                                    if handler:
                                        handler()
                                        print(f"[APPLY] {item_name}")
                            except Exception as e:
                                print(f"[ERR] Apply item {item_name}: {e}")
                            last_idx = item_index
                            state["last_item_index"] = int(last_idx)
                            _save_json(profile_path, state)
                    elif cmd == "PrintJSON":
                        print(f"[MSG] {m.get('type')}: {m.get('data')}")
        finally:
            watch_task.cancel()
            with contextlib.suppress(Exception):
                await watch_task


def main() -> None:
    try:
        settings = prompt_settings()
        asyncio.run(run_client(
            settings["connect"],
            settings["player"],
            settings.get("password", ""),
            settings.get("profile_override", ""),
        ))
    except KeyboardInterrupt:
        pass
    except SystemExit:
        raise
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to close...")


if __name__ == "__main__":
    main()
