# knd_memory_map_real_v2.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple

# CONFIRMED stable memory map for KND GC (GameCube) based on your latest list.
#
# Rules you requested:
# - DO NOT use any placeholder/example addresses for "correct" memory spots.
# - Only include addresses you explicitly listed as correct unlock/completion/toggles.
# - Unknowns remain None.

@dataclass(frozen=True)
class KNDMemoryMapReal:
    # ----------------------------
    # Stage completion flags (persistent, one-time)
    # ----------------------------
    STAGE_01_COMPLETE: Optional[int] = 0x8076F54F
    STAGE_02_COMPLETE: Optional[int] = 0x8076F4AF
    STAGE_03_COMPLETE: Optional[int] = 0x8076F5BF
    STAGE_04_COMPLETE: Optional[int] = 0x8076F4EF
    STAGE_05_COMPLETE: Optional[int] = 0x8076F57F
    STAGE_06_COMPLETE: Optional[int] = 0x8076F55F
    STAGE_07_COMPLETE: Optional[int] = 0x8076F44F
    STAGE_08_COMPLETE: Optional[int] = 0x8076F50F
    STAGE_09_COMPLETE: Optional[int] = 0x8076F4DF
    STAGE_10_COMPLETE: Optional[int] = 0x8076F46F
    STAGE_11_COMPLETE: Optional[int] = 0x8076F48F
    STAGE_12_COMPLETE: Optional[int] = 0x8076F59F
    STAGE_13_COMPLETE: Optional[int] = 0x8076F52F
    STAGE_14_COMPLETE: Optional[int] = 0x8076F4CF
    STAGE_15_COMPLETE: Optional[int] = None  # not provided in your latest list

    # ----------------------------
    # Tech enable toggles (persistent, on/off)
    # Encoding: 0 Off, 1 On
    # These are the "active for level start" toggles you listed after each completion.
    # ----------------------------
    STAGE_02_TECH_ENABLE: Optional[int] = 0x8076F4BF  # Gumzooka active for level start
    STAGE_03_TECH_ENABLE: Optional[int] = 0x8076F5CF  # Smellmet
    STAGE_04_TECH_ENABLE: Optional[int] = 0x8076F4FF
    STAGE_05_TECH_ENABLE: Optional[int] = 0x8076F58F
    STAGE_06_TECH_ENABLE: Optional[int] = 0x8076F56F
    STAGE_07_TECH_ENABLE: Optional[int] = 0x8076F45F
    STAGE_08_TECH_ENABLE: Optional[int] = 0x8076F51F
    STAGE_09_TECH_ENABLE: Optional[int] = None  # you noted "does not have one"
    STAGE_10_TECH_ENABLE: Optional[int] = 0x8076F47F
    STAGE_11_TECH_ENABLE: Optional[int] = 0x8076F49F
    STAGE_12_TECH_ENABLE: Optional[int] = 0x8076F5AF
    STAGE_13_TECH_ENABLE: Optional[int] = 0x8076F53F
    STAGE_14_TECH_ENABLE: Optional[int] = None  # not provided
    STAGE_01_TECH_ENABLE: Optional[int] = None
    STAGE_15_TECH_ENABLE: Optional[int] = None

    # ----------------------------
    # Rainbow Monkey tier bytes (per-stage session)
    # Encoding: 25/50/75/100 -> 1/2/3/4 (0 = below 25)
    # ----------------------------
    STAGE_02_MONKEY_TIER: Optional[int] = 0x8077020F
    STAGE_03_MONKEY_TIER: Optional[int] = 0x8077030F
    STAGE_04_MONKEY_TIER: Optional[int] = 0x8077023F
    STAGE_05_MONKEY_TIER: Optional[int] = 0x807702CF
    STAGE_06_MONKEY_TIER: Optional[int] = 0x8077029F
    STAGE_07_MONKEY_TIER: Optional[int] = 0x8077012F
    STAGE_08_MONKEY_TIER: Optional[int] = 0x8077024F
    STAGE_09_MONKEY_TIER: Optional[int] = 0x8077022F
    STAGE_10_MONKEY_TIER: Optional[int] = 0x8077018F
    STAGE_11_MONKEY_TIER: Optional[int] = 0x807701CF
    STAGE_12_MONKEY_TIER: Optional[int] = 0x807702FF
    STAGE_13_MONKEY_TIER: Optional[int] = 0x8077025F
    STAGE_14_MONKEY_TIER: Optional[int] = None
    STAGE_15_MONKEY_TIER: Optional[int] = 0x8077033F
    STAGE_01_MONKEY_TIER: Optional[int] = None

    # ----------------------------
    # Sooper Secrets (persistent). Some have alternates; we keep both.
    # ----------------------------
    STAGE_01_SOOPER_SECRET_1: Tuple[int, ...] = (0x8077027F,)
    STAGE_03_SOOPER_SECRET_1: Tuple[int, ...] = (0x807716A7,)  # Fire_Place
    STAGE_03_SOOPER_SECRET_2: Tuple[int, ...] = (0x807716A3,)  # DJ_Booth
    STAGE_05_SOOPER_SECRET_1: Tuple[int, ...] = (0x807702DF,)
    STAGE_06_SOOPER_SECRET_1: Tuple[int, ...] = (0x807702AF, 0x80771603)  # you noted either
    STAGE_07_SOOPER_SECRET_1: Tuple[int, ...] = (0x8077013F,)
    STAGE_07_SOOPER_SECRET_2: Tuple[int, ...] = (0x807715B3,)

    # ----------------------------
    # Other persistent unlocks you listed
    # ----------------------------
    N1_NUMBUH_86_ALT: Optional[int] = 0x807715B8
    STAGE_01_12_MONKEYS_TOILETNATOR_CARD: Optional[int] = 0x8077026F
