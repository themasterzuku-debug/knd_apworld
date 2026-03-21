# locations.py
# KND (GameCube) Archipelago world - Location definitions + IDs
#
# Authoritative AP-side location list for:
#   Codename: Kids Next Door – Operation: V.I.D.E.O.G.A.M.E. (GameCube)
#
# IMPORTANT:
# - This file must be valid Python. (Earlier drafts accidentally included JSON fragments.)
# - world.py consumes LOCATION_DATA to attach locations and set access rules.
# - Client-side Dolphin checks can be implemented later; it's fine if some locations are not
#   checkable yet in-game as long as the AP world builds and generates.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


KND_LOCATION_ID_BASE = 0x4B4E0000  # 'KN' themed base


@dataclass(frozen=True)
class LocationData:
    name: str
    region: str
    category: str
    requires: Tuple[str, ...] = ()
    requires_by_difficulty: Optional[Dict[str, Tuple[str, ...]]] = None
    notes: str = ""


# --- Location data list (authoritative) ---
LOCATION_DATA: List[LocationData] = [
    # -------- Stage 01 Tutorial (N1) --------
    LocationData("Stage_01_Tutorial_Complete", "Stage_01_Tutorial", "stage_clear"),
    LocationData("Stage_01_Tutorial_Secret", "Stage_01_Tutorial", "secret"),
    LocationData("Stage_01_Tutorial_SooperSecret", "Stage_01_Tutorial", "sooper_secret"),

    # -------- Stage 02 Donutty (N1) --------
    LocationData(
        "Stage_02_Donutty_Complete",
        "Stage_02_Donutty",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
        notes="Std/Mod assume Grappluh for safe completion path.",
    ),
    LocationData("Stage_02_Donutty_Secret_25_Monkeys", "Stage_02_Donutty", "secret"),
    LocationData(
        "Stage_02_Donutty_Secret_50_Monkeys",
        "Stage_02_Donutty",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_02_Donutty_Secret_75_Monkeys",
        "Stage_02_Donutty",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_02_Donutty_Secret_100_Monkeys",
        "Stage_02_Donutty",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_02_Donutty_Weapon_Check",
        "Stage_02_Donutty",
        "weapon_check",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
        notes="Bundled 'weapon check' location; client implementation optional for v0.",
    ),

    # -------- Stage 03 Boogification (N5) --------
    LocationData(
        "Stage_03_Boogification_Complete",
        "Stage_03_Boogification",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData("Stage_03_Boogification_Secret_25_Monkeys", "Stage_03_Boogification", "secret"),
    LocationData(
        "Stage_03_Boogification_Secret_50_Monkeys",
        "Stage_03_Boogification",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_03_Boogification_Secret_75_Monkeys",
        "Stage_03_Boogification",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_03_Boogification_Secret_100_Monkeys",
        "Stage_03_Boogification",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump", "2x4_N5_Boogification_Smellmet"),
            "moderate": ("Move_N5_DoubleJump", "Move_N5_WallJump", "2x4_N5_Boogification_Smellmet"),
            "hard": ("Move_N5_DoubleJump",),
            "expert": ("Move_N5_DoubleJump",),
        },
    ),
    LocationData("Stage_03_Boogification_SooperSecret_1", "Stage_03_Boogification", "sooper_secret"),
    LocationData(
        "Stage_03_Boogification_SooperSecret_2",
        "Stage_03_Boogification",
        "sooper_secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_03_Boogification_Weapon_Check",
        "Stage_03_Boogification",
        "weapon_check",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump",),
            "hard": ("Move_N5_DoubleJump",),
            "expert": ("Move_N5_DoubleJump",),
        },
    ),

    # -------- Stage 04 SnotBomber --------
    LocationData("Stage_04_SnotBomber_Complete", "Stage_04_SnotBomber", "stage_clear"),
    LocationData("Stage_04_SnotBomber_Secret_25_Monkeys", "Stage_04_SnotBomber", "secret"),
    LocationData("Stage_04_SnotBomber_Secret_50_Monkeys", "Stage_04_SnotBomber", "secret"),
    LocationData("Stage_04_SnotBomber_Secret_75_Monkeys", "Stage_04_SnotBomber", "secret"),
    LocationData("Stage_04_SnotBomber_Secret_100_Monkeys", "Stage_04_SnotBomber", "secret"),
    LocationData("Stage_04_SnotBomber_Weapon_Check", "Stage_04_SnotBomber", "weapon_check"),

    # -------- Stage 05 Spank Happy (N4) --------
    LocationData(
        "Stage_05_Spank_Happy_Complete",
        "Stage_05_Spank_Happy",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("2x4_N4_Spank_Happy_Splanker",),
            "moderate": ("2x4_N4_Spank_Happy_Splanker",),
            "hard": (),
            "expert": (),
        },
        notes="Std/Mod require Splanker to progress; Hard/Expert can skip to boss.",
    ),
    LocationData("Stage_05_Spank_Happy_Secret_25_Monkeys", "Stage_05_Spank_Happy", "secret"),
    LocationData("Stage_05_Spank_Happy_Secret_50_Monkeys", "Stage_05_Spank_Happy", "secret"),
    LocationData("Stage_05_Spank_Happy_Secret_75_Monkeys", "Stage_05_Spank_Happy", "secret"),
    LocationData("Stage_05_Spank_Happy_Secret_100_Monkeys", "Stage_05_Spank_Happy", "secret"),
    LocationData("Stage_05_Spank_Happy_SooperSecret_1", "Stage_05_Spank_Happy", "sooper_secret"),
    LocationData("Stage_05_Spank_Happy_Weapon_Check", "Stage_05_Spank_Happy", "weapon_check"),

    # -------- Stage 06 Hamsterama (N3) --------
    LocationData("Stage_06_Hamsterama_Complete", "Stage_06_Hamsterama", "stage_clear"),
    LocationData("Stage_06_Hamsterama_Secret_25_Monkeys", "Stage_06_Hamsterama", "secret"),
    LocationData("Stage_06_Hamsterama_Secret_50_Monkeys", "Stage_06_Hamsterama", "secret"),
    LocationData(
        "Stage_06_Hamsterama_Secret_75_Monkeys",
        "Stage_06_Hamsterama",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "moderate": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "hard": ("Move_N3_Glide",),
            "expert": ("Move_N3_Glide",),
        },
    ),
    LocationData(
        "Stage_06_Hamsterama_Secret_100_Monkeys",
        "Stage_06_Hamsterama",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "moderate": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "hard": ("Move_N3_Glide",),
            "expert": ("Move_N3_Glide",),
        },
    ),
    LocationData(
        "Stage_06_Hamsterama_SooperSecret",
        "Stage_06_Hamsterama",
        "sooper_secret",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "moderate": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "hard": ("Move_N3_Glide",),
            "expert": ("Move_N3_Glide",),
        },
    ),
    LocationData(
        "Stage_06_Hamsterama_Weapon_Check",
        "Stage_06_Hamsterama",
        "weapon_check",
        notes="Bundled check: requires collecting 4 pieces (out of 16 possible spawn locations).",
    ),

    # -------- Stage 07 Spankarific (N1) --------
    LocationData(
        "Stage_07_Spankarific_Complete",
        "Stage_07_Spankarific",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("Move_N1_Grappluh",),
            "moderate": ("Move_N1_Grappluh",),
            "hard": (),
            "expert": (),
        },
        notes="Hard/Expert: completion possible without Grappluh.",
    ),
    LocationData("Stage_07_Spankarific_Secret_25_Monkeys", "Stage_07_Spankarific", "secret"),
    LocationData("Stage_07_Spankarific_Secret_50_Monkeys", "Stage_07_Spankarific", "secret"),
    LocationData(
        "Stage_07_Spankarific_Secret_75_Monkeys",
        "Stage_07_Spankarific",
        "secret",
        requires=("Move_N1_Grappluh",),
        notes="Conservative until further testing.",
    ),
    LocationData(
        "Stage_07_Spankarific_Secret_100_Monkeys",
        "Stage_07_Spankarific",
        "secret",
        requires=("Move_N1_Grappluh",),
        notes="Conservative until further testing.",
    ),
    LocationData("Stage_07_Spankarific_SooperSecret_1", "Stage_07_Spankarific", "sooper_secret"),
    LocationData("Stage_07_Spankarific_SooperSecret_2", "Stage_07_Spankarific", "sooper_secret"),
    LocationData(
        "Stage_07_Spankarific_Weapon_Check",
        "Stage_07_Spankarific",
        "weapon_check",
        requires=("Move_N1_Grappluh",),
        notes="Conservative until tested otherwise.",
    ),

    # -------- Stage 08 Tarpoon --------
    LocationData("Stage_08_Tarpoon_Complete", "Stage_08_Tarpoon", "stage_clear"),
    LocationData("Stage_08_Tarpoon_Secret_25_Monkeys", "Stage_08_Tarpoon", "secret"),
    LocationData("Stage_08_Tarpoon_Secret_50_Monkeys", "Stage_08_Tarpoon", "secret"),
    LocationData("Stage_08_Tarpoon_Secret_75_Monkeys", "Stage_08_Tarpoon", "secret"),
    LocationData("Stage_08_Tarpoon_Secret_100_Monkeys", "Stage_08_Tarpoon", "secret"),
    LocationData("Stage_08_Tarpoon_Weapon_Check", "Stage_08_Tarpoon", "weapon_check"),

    # -------- Stage 09 Ship Shape (N5) --------
    LocationData(
        "Stage_09_Ship_Shape_Complete",
        "Stage_09_Ship_Shape",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "hard": ("Move_N5_DoubleJump",),
            "expert": ("Move_N5_DoubleJump",),
        },
    ),
    LocationData("Stage_09_Ship_Shape_Secret_25_Monkeys", "Stage_09_Ship_Shape", "secret"),
    LocationData("Stage_09_Ship_Shape_Secret_50_Monkeys", "Stage_09_Ship_Shape", "secret"),
    LocationData(
        "Stage_09_Ship_Shape_Secret_75_Monkeys",
        "Stage_09_Ship_Shape",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "hard": ("Move_N5_DoubleJump",),
            "expert": ("Move_N5_DoubleJump",),
        },
    ),
    LocationData(
        "Stage_09_Ship_Shape_Secret_100_Monkeys",
        "Stage_09_Ship_Shape",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "moderate": ("Move_N5_DoubleJump", "Move_N5_WallJump"),
            "hard": ("Move_N5_DoubleJump",),
            "expert": ("Move_N5_DoubleJump",),
        },
    ),

    # -------- Stage 10 Brush Off (N3) --------
    LocationData(
        "Stage_10_Brush_Off_Complete",
        "Stage_10_Brush_Off",
        "stage_clear",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "moderate": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "hard": ("Move_N3_DoubleJump",  "Move_N3_Glide"),
            "expert": ("Move_N3_DoubleJump",  "Move_N3_Glide"),
        },
    ),
    LocationData("Stage_10_Brush_Off_Secret_25_Monkeys", "Stage_10_Brush_Off", "secret"),
    LocationData("Stage_10_Brush_Off_Secret_50_Monkeys", "Stage_10_Brush_Off", "secret"),
    LocationData(
        "Stage_10_Brush_Off_Secret_75_Monkeys",
        "Stage_10_Brush_Off",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump",),
            "moderate": ("Move_N3_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),
    LocationData(
        "Stage_10_Brush_Off_Secret_100_Monkeys",
        "Stage_10_Brush_Off",
        "secret",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "moderate": ("Move_N3_DoubleJump", "Move_N3_Glide"),
            "hard": ("Move_N3_DoubleJump",),
            "expert": ("Move_N3_DoubleJump",),
        },
    ),
    LocationData("Stage_10_Brush_Off_SooperSecret_1", "Stage_10_Brush_Off", "sooper_secret"),
    LocationData("Stage_10_Brush_Off_SooperSecret_2", "Stage_10_Brush_Off", "sooper_secret"),
    LocationData(
        "Stage_10_Brush_Off_Weapon_Check",
        "Stage_10_Brush_Off",
        "weapon_check",
        requires_by_difficulty={
            "standard": ("Move_N3_DoubleJump",),
            "moderate": ("Move_N3_DoubleJump",),
            "hard": (),
            "expert": (),
        },
    ),

    # -------- Stage 11 Cavity Cave (N1) --------
    LocationData(
        "Stage_11_Cavity_Cave_Complete",
        "Stage_11_Cavity_Cave",
        "stage_clear",
        requires=("Move_N1_Grappluh",),
    ),
    LocationData("Stage_11_Cavity_Cave_Secret_25_Monkeys", "Stage_11_Cavity_Cave", "secret"),
    LocationData(
        "Stage_11_Cavity_Cave_Secret_50_Monkeys",
        "Stage_11_Cavity_Cave",
        "secret",
        requires=("Move_N1_Grappluh",),
    ),
    LocationData(
        "Stage_11_Cavity_Cave_Secret_75_Monkeys",
        "Stage_11_Cavity_Cave",
        "secret",
        requires=("Move_N1_Grappluh",),
    ),
    LocationData(
        "Stage_11_Cavity_Cave_Secret_100_Monkeys",
        "Stage_11_Cavity_Cave",
        "secret",
        requires=("Move_N1_Grappluh",),
    ),
    LocationData(
        "Stage_11_Cavity_Cave_Weapon_Check",
        "Stage_11_Cavity_Cave",
        "weapon_check",
        requires=("Move_N1_Grappluh",),
    ),

    # -------- Stage 12 Overflow (N4) --------
    LocationData("Stage_12_Overflow_Complete", "Stage_12_Overflow", "stage_clear", requires=("Move_N4_DoubleJump",)),
    LocationData("Stage_12_Overflow_Secret_25_Monkeys", "Stage_12_Overflow", "secret"),
    LocationData("Stage_12_Overflow_Secret_50_Monkeys", "Stage_12_Overflow", "secret"),
    LocationData("Stage_12_Overflow_Secret_75_Monkeys", "Stage_12_Overflow", "secret"),
    LocationData("Stage_12_Overflow_Secret_100_Monkeys", "Stage_12_Overflow", "secret", requires=("Move_N4_DoubleJump",)),
    LocationData("Stage_12_Overflow_SooperSecret_1", "Stage_12_Overflow", "sooper_secret"),
    LocationData("Stage_12_Overflow_Weapon_Check", "Stage_12_Overflow", "weapon_check"),

    # -------- Stage 13 MoonTrip --------
    LocationData("Stage_13_MoonTrip_Complete", "Stage_13_MoonTrip", "stage_clear"),
    LocationData("Stage_13_MoonTrip_Secret_25_Monkeys", "Stage_13_MoonTrip", "secret"),
    LocationData("Stage_13_MoonTrip_Secret_50_Monkeys", "Stage_13_MoonTrip", "secret"),
    LocationData("Stage_13_MoonTrip_Secret_75_Monkeys", "Stage_13_MoonTrip", "secret"),
    LocationData("Stage_13_MoonTrip_Secret_100_Monkeys", "Stage_13_MoonTrip", "secret"),
    LocationData("Stage_13_MoonTrip_Weapon_Check", "Stage_13_MoonTrip", "weapon_check"),

    # -------- Stage 14 Lunarumble (Victory) --------
    LocationData("Stage_14_Lunarumble_Complete", "Stage_14_Lunarumble", "event"),

    # -------- Stage 15 Credits --------
    LocationData("Stage_15_Credits_Complete", "Stage_15_Credits", "stage_clear"),
    LocationData("Stage_15_Credits_Secret_10_Monkeys", "Stage_15_Credits", "secret"),
    LocationData("Stage_15_Credits_Secret_20_Monkeys", "Stage_15_Credits", "secret"),
    LocationData("Stage_15_Credits_Secret_30_Monkeys", "Stage_15_Credits", "secret"),
    LocationData("Stage_15_Credits_Secret_40_Monkeys", "Stage_15_Credits", "secret"),
]


# --- ID table (name -> numeric id) ---
LOCATION_ID_TABLE: Dict[str, int] = {
    loc.name: KND_LOCATION_ID_BASE + i
    for i, loc in enumerate(LOCATION_DATA)
}


def get_location_data(name: str) -> LocationData:
    for loc in LOCATION_DATA:
        if loc.name == name:
            return loc
    raise KeyError(f"Unknown location: {name}")


def all_location_names() -> List[str]:
    return [loc.name for loc in LOCATION_DATA]
