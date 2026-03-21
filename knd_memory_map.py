# knd_memory_map.py
from __future__ import annotations
from dataclasses import dataclass

# NOTE:
# These addresses are placeholders. You will replace them with real addresses after you find them in Dolphin.
#
# Convention:
# - We assume 1 byte flags for unlocks (0 = locked, 1 = unlocked)
# - You can change types later to bitfields, ints, etc.

@dataclass(frozen=True)
class KNDMemoryMap:
    # --- Example flag blocks (placeholders) ---
    # Operatives (5 bytes)
    OPERATIVE_N1: int = 0x80000000
    OPERATIVE_N2: int = 0x80000001
    OPERATIVE_N3: int = 0x80000002
    OPERATIVE_N4: int = 0x80000003
    OPERATIVE_N5: int = 0x80000004

    # Stage unlocks (15 bytes)
    STAGE_01: int = 0x80000010
    STAGE_02: int = 0x80000011
    STAGE_03: int = 0x80000012
    STAGE_04: int = 0x80000013
    STAGE_05: int = 0x80000014
    STAGE_06: int = 0x80000015
    STAGE_07: int = 0x80000016
    STAGE_08: int = 0x80000017
    STAGE_09: int = 0x80000018
    STAGE_10: int = 0x80000019
    STAGE_11: int = 0x8000001A
    STAGE_12: int = 0x8000001B
    STAGE_13: int = 0x8000001C
    STAGE_14: int = 0x8000001D
    STAGE_15: int = 0x8000001E

    # Moves (bytes)
    MOVE_GRAPPLUH: int = 0x80000030
    MOVE_N3_DOUBLEJUMP: int = 0x80000031
    MOVE_N3_GLIDE: int = 0x80000032
    MOVE_N4_DOUBLEJUMP: int = 0x80000033
    MOVE_N5_DOUBLEJUMP: int = 0x80000034
    MOVE_N5_WALLJUMP: int = 0x80000035

    # (Later) Slot shuffle table (15 bytes, each value = stage id)
    STAGE_SLOT_TABLE: int = 0x80000100  # base address of array[15]
