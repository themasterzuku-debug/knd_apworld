# knd_ap_client_v3.py
# Updated "working copy" Dolphin client:
# - Uses ONLY the stable addresses you marked as correct.
# - Adds completion flags for L1-L14.
# - Adds monkey tiers for L2-L13 (plus L15).
# - Does NOT use any placeholder/sample instance-field addresses as "correct".

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from CommonClient import CommonContext, get_base_parser
import Utils

import dolphin_memory_engine as dme  # type: ignore

from knd_memory_map_real_v2 import KNDMemoryMapReal

log = logging.getLogger("KNDClient")
logging.basicConfig(level=logging.INFO)


class DolphinRW:
    def __init__(self, mem: KNDMemoryMapReal):
        self.mem = mem
        self._hooked = False

    def ensure_hooked(self) -> bool:
        if self._hooked:
            return True
        try:
            dme.hook()
            self._hooked = True
            log.info("Hooked into Dolphin process.")
            return True
        except Exception as e:
            log.warning(f"Could not hook Dolphin yet: {e}")
            return False

    def read_u8(self, addr: int) -> int:
        b = dme.read_bytes(addr, 1)
        return int(b[0])

    def safe_write_u8(self, addr: Optional[int], value: int, label: str) -> None:
        if addr is None:
            log.info(f"[SKIP] No address yet for {label}")
            return
        dme.write_bytes(addr, bytes([value & 0xFF]))


def build_item_handlers(rw: DolphinRW) -> Dict[str, Callable[[], None]]:
    """
    IMPORTANT:
    - This draft only wires "tech enable toggles" because those are stable and confirmed.
    - You can extend this mapping as your item list stabilizes.
    """
    m = rw.mem
    handlers: Dict[str, Callable[[], None]] = {}

    # You may need to adjust item names here to exactly match your items.py.
    # These are common names from your items.json list.
    handlers.update({
        "2x4_N2_Musket": lambda: rw.safe_write_u8(m.STAGE_02_TECH_ENABLE, 1, "Stage 02 Tech Enable"),
        "2x4_N3_Gumzooka": lambda: rw.safe_write_u8(m.STAGE_02_TECH_ENABLE, 1, "Stage 02 Tech Enable (Gumzooka)"),
        "2x4_N3_Smellmet": lambda: rw.safe_write_u8(m.STAGE_03_TECH_ENABLE, 1, "Stage 03 Tech Enable (Smellmet)"),
        # Add more tech items -> stage tech enable here if you want
    })

    return handlers


@dataclass(frozen=True)
class FlagCheck:
    location_name: str
    addr: int


@dataclass(frozen=True)
class MultiAddrFlagCheck:
    """Location check that triggers if ANY of the provided addresses is 1."""
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

        # Completion checks L1-L14
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

        # Sooper secrets (including L6 alternate addresses)
        self.secrets: List[MultiAddrFlagCheck] = [
            MultiAddrFlagCheck("Stage_01_Tutorial_SooperSecret", m.STAGE_01_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_03_Boogification_SooperSecret_1", m.STAGE_03_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_03_Boogification_SooperSecret_2", m.STAGE_03_SOOPER_SECRET_2),
            MultiAddrFlagCheck("Stage_05_Spank_Happy_SooperSecret", m.STAGE_05_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_06_Hamsterama_SooperSecret", m.STAGE_06_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_07_Spankarific_SooperSecret_1", m.STAGE_07_SOOPER_SECRET_1),
            MultiAddrFlagCheck("Stage_07_Spankarific_SooperSecret_2", m.STAGE_07_SOOPER_SECRET_2),
        ]

        # Other unlocks you listed (optional checks if you made them locations)
        self.other_flags: List[FlagCheck] = []
        if m.N1_NUMBUH_86_ALT is not None:
            self.other_flags.append(FlagCheck("Outfit_N1_N86_Unlocked", m.N1_NUMBUH_86_ALT))
        if m.STAGE_01_12_MONKEYS_TOILETNATOR_CARD is not None:
            self.other_flags.append(FlagCheck("Stage_01_Toiletnator_Card_Unlocked", m.STAGE_01_12_MONKEYS_TOILETNATOR_CARD))

        # Monkey tiers (L2-L13 + L15)
        self.monkey_tiers: List[MonkeyTierCheck] = []
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
        for stage, addr in monkey_pairs:
            if addr is not None:
                self.monkey_tiers.append(MonkeyTierCheck(stage, addr))

        self._seen_persistent: Set[str] = set()
        self._monkey_highwater: Dict[str, int] = {}
        self._monkey_last: Dict[str, int] = {}

    def _clamp_tier(self, v: int) -> int:
        # encoding 0..4, clamp defensive
        return 0 if v < 0 else 4 if v > 4 else v

    def poll(self) -> List[str]:
        new_checks: List[str] = []

        # Persistent flags
        for chk in self.completions + self.other_flags:
            if chk.location_name in self._seen_persistent:
                continue
            try:
                v = self.rw.read_u8(chk.addr)
            except Exception:
                continue
            if v == 1:
                self._seen_persistent.add(chk.location_name)
                new_checks.append(chk.location_name)

        for chk in self.secrets:
            if chk.location_name in self._seen_persistent:
                continue
            hit = False
            for addr in chk.addrs:
                try:
                    if self.rw.read_u8(addr) == 1:
                        hit = True
                        break
                except Exception:
                    continue
            if hit:
                self._seen_persistent.add(chk.location_name)
                new_checks.append(chk.location_name)

        # Monkey tiers: emit milestone checks when tier increases
        for mt in self.monkey_tiers:
            try:
                raw = self.rw.read_u8(mt.tier_addr)
            except Exception:
                continue
            tier = self._clamp_tier(raw)

            last = self._monkey_last.get(mt.stage_region)
            self._monkey_last[mt.stage_region] = tier

            # session heuristic: drop to 0 after progress => new session reset
            if last is not None and last > 0 and tier == 0:
                self._monkey_highwater[mt.stage_region] = 0

            hi = self._monkey_highwater.get(mt.stage_region, 0)
            if tier > hi:
                # Location naming convention expected by your world:
                #   {Stage}_Secret_{25|50|75|100}_Monkeys
                milestone_suffix = {1: "25", 2: "50", 3: "75", 4: "100"}
                for t in range(hi + 1, tier + 1):
                    sfx = milestone_suffix.get(t)
                    if sfx:
                        new_checks.append(f"{mt.stage_region}_Secret_{sfx}_Monkeys")
                self._monkey_highwater[mt.stage_region] = tier

        return new_checks


class KNDContext(CommonContext):
    game = "Codename: Kids Next Door (GC)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rw = DolphinRW(KNDMemoryMapReal())
        self.handlers = build_item_handlers(self.rw)

        self.applied_item_indices: Set[int] = set()
        self.watcher = ProgressWatcher(self.rw)
        self._watch_task: Optional[asyncio.Task] = None
        self._sent_location_names: Set[str] = set()

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)
        if cmd == "ReceivedItems":
            self._handle_received_items(args)

    def _handle_received_items(self, args: dict) -> None:
        if not self.rw.ensure_hooked():
            return
        for it in args.get("items", []):
            idx = it.get("index")
            if idx is None or idx in self.applied_item_indices:
                continue
            item_name = self.item_names.lookup_in_game(it["item"])
            handler = self.handlers.get(item_name)
            if handler:
                try:
                    handler()
                    log.info(f"Applied item: {item_name}")
                    self.applied_item_indices.add(idx)
                except Exception as e:
                    log.error(f"Failed applying {item_name}: {e}")
            else:
                log.debug(f"No handler for item: {item_name}")

    async def _watch_loop(self) -> None:
        while True:
            try:
                if not self.rw.ensure_hooked():
                    await asyncio.sleep(1.0)
                    continue
                new_names = self.watcher.poll()
                if new_names:
                    await self._send_location_checks_by_name(new_names)
                await asyncio.sleep(0.10)
            except asyncio.CancelledError:
                return
            except Exception:
                await asyncio.sleep(0.5)

    def start_watcher(self) -> None:
        if self._watch_task is None or self._watch_task.done():
            self._watch_task = asyncio.create_task(self._watch_loop())

    async def _send_location_checks_by_name(self, location_names: Iterable[str]) -> None:
        ids: List[int] = []
        for name in location_names:
            if name in self._sent_location_names:
                continue
            loc_id = self._lookup_location_id(name)
            if loc_id is None:
                log.info(f"[NEED] Location name not in datapackage: {name}")
                continue
            self._sent_location_names.add(name)
            ids.append(loc_id)
        if not ids:
            return
        await self.send_msgs([{"cmd": "LocationChecks", "locations": ids}])
        log.info(f"Checked {len(ids)} location(s).")

    def _lookup_location_id(self, name: str) -> Optional[int]:
        try:
            if hasattr(self.location_names, "lookup_id"):
                return int(self.location_names.lookup_id(name))
        except Exception:
            pass
        try:
            dp = getattr(self, "data_package", None)
            if isinstance(dp, dict):
                locs = dp.get("games", {}).get(self.game, {}).get("location_name_to_id", {})
                if name in locs:
                    return int(locs[name])
        except Exception:
            pass
        return None


async def main():
    Utils.init_logging("KNDClient")
    parser = get_base_parser()
    parser.add_argument("--connect", default=None)
    parser.add_argument("--player", default=None)
    parser.add_argument("--password", default=None)
    args = parser.parse_args()

    ctx = KNDContext(None, args.player, args.password)
    ctx.server_address = args.connect

    if not ctx.server_address or not ctx.auth:
        print("Example:")
        print("  python knd_ap_client_v3.py --connect localhost:38281 --player YourName")
        return

    await ctx.connect()
    ctx.start_watcher()
    await ctx.console_loop()
    await ctx.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
