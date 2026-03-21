# knd_client.py
from __future__ import annotations

import asyncio
import logging
from typing import Dict, Callable

# Archipelago client base
from CommonClient import CommonContext, get_base_parser
import Utils

# Dolphin memory engine (install below)
import dolphin_memory_engine as dme  # type: ignore

from knd_memory_map import KNDMemoryMap

log = logging.getLogger("KNDClient")
logging.basicConfig(level=logging.INFO)


# ----------------------------
# Dolphin helpers
# ----------------------------

class DolphinWriter:
    def __init__(self, mem: KNDMemoryMap):
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

    def write_u8(self, addr: int, value: int) -> None:
        # Dolphin Memory Engine expects bytes
        dme.write_bytes(addr, bytes([value & 0xFF]))

    def write_stage_slot_table(self, slot_to_stage: Dict[int, int]) -> None:
        """
        slot_to_stage: {0..14 -> stage_id}
        stage_id convention is yours; common is 1..15 or 0..14. Pick one and stick to it.
        """
        base = self.mem.STAGE_SLOT_TABLE
        for slot, stage in slot_to_stage.items():
            self.write_u8(base + slot, stage)


# ----------------------------
# AP -> Game mapping
# ----------------------------

def build_item_handlers(writer: DolphinWriter) -> Dict[str, Callable[[], None]]:
    m = writer.mem

    # Keep these names EXACTLY matching your items.py item names.
    return {
        # --- Operatives ---
        "Operative_N1": lambda: writer.write_u8(m.OPERATIVE_N1, 1),
        "Operative_N2": lambda: writer.write_u8(m.OPERATIVE_N2, 1),
        "Operative_N3": lambda: writer.write_u8(m.OPERATIVE_N3, 1),
        "Operative_N4": lambda: writer.write_u8(m.OPERATIVE_N4, 1),
        "Operative_N5": lambda: writer.write_u8(m.OPERATIVE_N5, 1),

        # --- Stage Unlocks ---
        "Stage_01_Tutorial_Unlock": lambda: writer.write_u8(m.STAGE_01, 1),
        "Stage_02_Donutty_Unlock": lambda: writer.write_u8(m.STAGE_02, 1),
        "Stage_03_Boogification_Unlock": lambda: writer.write_u8(m.STAGE_03, 1),
        "Stage_04_SnotBomber_Unlock": lambda: writer.write_u8(m.STAGE_04, 1),
        "Stage_05_Spank_Happy_Unlock": lambda: writer.write_u8(m.STAGE_05, 1),
        "Stage_06_Hamsterama_Unlock": lambda: writer.write_u8(m.STAGE_06, 1),
        "Stage_07_Spankarific_Unlock": lambda: writer.write_u8(m.STAGE_07, 1),
        "Stage_08_Tarpoon_Unlock": lambda: writer.write_u8(m.STAGE_08, 1),
        "Stage_09_Ship_Shape_Unlock": lambda: writer.write_u8(m.STAGE_09, 1),
        "Stage_10_Brush_Off_Unlock": lambda: writer.write_u8(m.STAGE_10, 1),
        "Stage_11_Cavity_Cave_Unlock": lambda: writer.write_u8(m.STAGE_11, 1),
        "Stage_12_Overflow_Unlock": lambda: writer.write_u8(m.STAGE_12, 1),
        "Stage_13_MoonTrip_Unlock": lambda: writer.write_u8(m.STAGE_13, 1),
        "Stage_14_Lunarumble_Unlock": lambda: writer.write_u8(m.STAGE_14, 1),
        "Stage_15_Credits_Unlock": lambda: writer.write_u8(m.STAGE_15, 1),

        # --- Moves ---
        "Move_N1_Grappluh": lambda: writer.write_u8(m.MOVE_GRAPPLUH, 1),
        "Move_N3_DoubleJump": lambda: writer.write_u8(m.MOVE_N3_DOUBLEJUMP, 1),
        "Move_N3_Glide": lambda: writer.write_u8(m.MOVE_N3_GLIDE, 1),
        "Move_N4_DoubleJump": lambda: writer.write_u8(m.MOVE_N4_DOUBLEJUMP, 1),
        "Move_N5_DoubleJump": lambda: writer.write_u8(m.MOVE_N5_DOUBLEJUMP, 1),
        "Move_N5_WallJump": lambda: writer.write_u8(m.MOVE_N5_WALLJUMP, 1),

        # You can add weapons/outfits/etc the same way once you know their flags/addresses.
    }


# ----------------------------
# Archipelago Client Context
# ----------------------------

class KNDContext(CommonContext):
    game = "Codename: Kids Next Door (GC)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.writer = DolphinWriter(KNDMemoryMap())
        self.handlers = build_item_handlers(self.writer)

        # Track what we've already applied so reconnects don’t spam writes
        self.applied_item_indices = set()

    async def server_auth(self, password_requested: bool = False):
        await super().server_auth(password_requested=password_requested)

    def on_package(self, cmd: str, args: dict):
        super().on_package(cmd, args)

        # The most important packet for us is ReceivedItems
        if cmd == "ReceivedItems":
            self._handle_received_items(args)

    def _handle_received_items(self, args: dict) -> None:
        if not self.writer.ensure_hooked():
            return

        items = args.get("items", [])
        for it in items:
            idx = it.get("index")
            if idx is None or idx in self.applied_item_indices:
                continue

            item_name = self.item_names.lookup_in_game(it["item"])  # AP item id -> name
            handler = self.handlers.get(item_name)

            if handler:
                try:
                    handler()
                    log.info(f"Applied item: {item_name}")
                    self.applied_item_indices.add(idx)
                except Exception as e:
                    log.error(f"Failed applying {item_name}: {e}")
            else:
                # Not all AP items have to do anything yet (eg. filler)
                log.debug(f"No handler for item: {item_name}")


async def main():
    Utils.init_logging("KNDClient")

    parser = get_base_parser()
    parser.add_argument("--connect", default=None, help="Archipelago server address (host:port)")
    parser.add_argument("--player", default=None, help="Player name")
    parser.add_argument("--password", default=None, help="Password (if required)")

    args = parser.parse_args()

    ctx = KNDContext(None, args.player, args.password)
    ctx.server_address = args.connect

    if not ctx.server_address or not ctx.auth:
        print("Example:")
        print("  python knd_client.py --connect localhost:38281 --player YourName")
        return

    await ctx.connect()
    await ctx.console_loop()
    await ctx.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
