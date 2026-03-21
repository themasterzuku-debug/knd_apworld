# items.py
# KND (GameCube) Archipelago world - Item definitions + IDs
#
# This is a COMPLETE items module based on your current item list.
# It is also future-proofed for the "Fixed vs Loose" BossKey mode:
#   - BossKey is defined as a progression item (counted item).
#   - world.py will decide whether BossKeys are lock-placed (Fixed) or added to the pool (Loose).
#
# Notes:
# - Archipelago item classification is important for logic and spoiler behavior.
# - "Victory" is an EVENT item and should NOT be in the pool (world.py will place it on Stage 14).
#
# Conventions:
# - IDs are stable and must not change once published.
# - Names must match what you reference in locations.py and world.py rules.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from BaseClasses import Item, ItemClassification


KND_ITEM_ID_BASE = 0x4B4E1000  # 'KN' themed base, separate from location range


@dataclass(frozen=True)
class ItemData:
    name: str
    classification: ItemClassification
    count: int = 1
    # For future: you can add flags like "is_progressive", "stage_specific", etc.
    # without breaking the rest of the architecture.


# ---- Item list (authoritative) ----
ITEM_DATA: List[ItemData] = [
    # ---- Core Progression: Operatives ----
    ItemData("Operative_N1", ItemClassification.progression),
    ItemData("Operative_N2", ItemClassification.progression),
    ItemData("Operative_N3", ItemClassification.progression),
    ItemData("Operative_N4", ItemClassification.progression),
    ItemData("Operative_N5", ItemClassification.progression),

    # ---- Core Progression: Stage Unlocks ----
    ItemData("Stage_01_Tutorial_Unlock", ItemClassification.progression),
    ItemData("Stage_02_Donutty_Unlock", ItemClassification.progression),
    ItemData("Stage_03_Boogification_Unlock", ItemClassification.progression),
    ItemData("Stage_04_SnotBomber_Unlock", ItemClassification.progression),
    ItemData("Stage_05_Spank_Happy_Unlock", ItemClassification.progression),
    ItemData("Stage_06_Hamsterama_Unlock", ItemClassification.progression),
    ItemData("Stage_07_Spankarific_Unlock", ItemClassification.progression),
    ItemData("Stage_08_Tarpoon_Unlock", ItemClassification.progression),
    ItemData("Stage_09_Ship_Shape_Unlock", ItemClassification.progression),
    ItemData("Stage_10_Brush_Off_Unlock", ItemClassification.progression),
    ItemData("Stage_11_Cavity_Cave_Unlock", ItemClassification.progression),
    ItemData("Stage_12_Overflow_Unlock", ItemClassification.progression),
    ItemData("Stage_13_MoonTrip_Unlock", ItemClassification.progression),
    ItemData("Stage_14_Lunarumble_Unlock", ItemClassification.progression),
    ItemData("Stage_15_Credits_Unlock", ItemClassification.progression),

    # ---- Core Progression: Moves (character-specific) ----
    ItemData("Move_N1_Grappluh", ItemClassification.progression),

    ItemData("Move_N3_DoubleJump", ItemClassification.progression),
    ItemData("Move_N3_Glide", ItemClassification.progression),

    ItemData("Move_N4_DoubleJump", ItemClassification.progression),

    ItemData("Move_N5_DoubleJump", ItemClassification.progression),
    ItemData("Move_N5_WallJump", ItemClassification.progression),

    # ---- Core Progression: N1 2x4 Progressives ----
    ItemData("2x4_N1_Progressive_1_Gumzooka", ItemClassification.progression),
    ItemData("2x4_N1_Progressive_2_Scampp", ItemClassification.progression),
    ItemData("2x4_N1_Progressive_3_Bajooka", ItemClassification.progression),

    # ---- Core Progression: N2 Coolbus Progressives (SnotBomber) ----
    ItemData("2x4_N2_SnotBomber_Progressive_1", ItemClassification.progression),
    ItemData("2x4_N2_SnotBomber_Progressive_2", ItemClassification.progression),
    ItemData("2x4_N2_SnotBomber_Progressive_3", ItemClassification.progression),
    ItemData("2x4_N2_SnotBomber_Progressive_4", ItemClassification.progression),

    # ---- Core Progression: N2 Coolbus Progressives (Tarpoon) ----
    ItemData("2x4_N2_Tarpoon_Progressive_1", ItemClassification.progression),
    ItemData("2x4_N2_Tarpoon_Progressive_2", ItemClassification.progression),
    ItemData("2x4_N2_Tarpoon_Progressive_3", ItemClassification.progression),
    ItemData("2x4_N2_Tarpoon_Progressive_4", ItemClassification.progression),
    ItemData("2x4_N2_Tarpoon_Progressive_5", ItemClassification.progression),

    # ---- Core Progression: N2 Coolbus Progressives (MoonTrip) ----
    ItemData("2x4_N2_MoonTrip_Progressive_1", ItemClassification.progression),
    ItemData("2x4_N2_MoonTrip_Progressive_2", ItemClassification.progression),
    ItemData("2x4_N2_MoonTrip_Progressive_3", ItemClassification.progression),
    ItemData("2x4_N2_MoonTrip_Progressive_4", ItemClassification.progression),
    ItemData("2x4_N2_MoonTrip_Progressive_5", ItemClassification.progression),

    # ---- Core Progression: Required weapon-ish item ----
    ItemData("2x4_N4_Spank_Happy_Splanker", ItemClassification.progression),

    # ---- Core Progression: Final gate cosmetic ----
    ItemData("Outfit_N1_N86", ItemClassification.progression),

    # ---- Filler: Outfits ----
    ItemData("Outfit_N1_Vampire", ItemClassification.filler),
    ItemData("Outfit_N1_Sooper_Deformed", ItemClassification.filler),
    ItemData("Outfit_N2_Elimonator", ItemClassification.filler),
    ItemData("Outfit_N2_Scamper", ItemClassification.filler),
    ItemData("Outfit_N3_Vampire", ItemClassification.filler),
    ItemData("Outfit_N3_Sooper_Deformed", ItemClassification.filler),
    ItemData("Outfit_N4_Vampire", ItemClassification.filler),
    ItemData("Outfit_N4_Sooper_Deformed", ItemClassification.filler),
    ItemData("Outfit_N5_Vampire", ItemClassification.filler),
    ItemData("Outfit_N5_Sooper_Deformed", ItemClassification.filler),

    # ---- Filler: Stage-specific 2x4 / upgrades / cosmetics ----
    ItemData("2x4_N1_Donutty_Gumzooka", ItemClassification.filler),
    ItemData("2x4_N5_Boogification_Smellmet", ItemClassification.filler),
    ItemData("2x4_N2_SnotBomber_Full_Upgrade", ItemClassification.filler),
    ItemData("2x4_N3_Hamsterama_Frappe", ItemClassification.filler),
    ItemData("2x4_N1_Spankarific_Scampp", ItemClassification.filler),
    ItemData("2x4_N2_Tarpoon_Full_Upgrade", ItemClassification.filler),
    ItemData("2x4_N3_Brush_Off_Thumper", ItemClassification.filler),
    ItemData("2x4_N1_Cavity_Cave_Bajooka", ItemClassification.filler),
    ItemData("2x4_N2_MoonTrip_Full_Upgrade", ItemClassification.filler),
    ItemData("2x4_N2_Credits_Full_Upgrade", ItemClassification.filler),

    # ---- Stackables ----
    # Rainbow Monkeys: small filler that can be used as currency/requirements later if desired.
    ItemData("Rainbow_Monkey", ItemClassification.filler, count=12),

    # BossKeys: progression items; Fixed vs Loose logic will decide placement behavior.
    ItemData("BossKey", ItemClassification.progression, count=8),

    # ---- Event ----
    # Not in pool; world.py will place it on Stage_14_Lunarumble_Complete.
    ItemData("Victory", ItemClassification.progression, count=1),

    # ---- Filler (to balance itempool vs locations when Victory + fixed BossKeys are lock-placed) ----
    ItemData("Filler_Junk", ItemClassification.filler, count=3),
]


# --- ID table (name -> numeric id) ---
# IDs must be stable across versions once you publish.
_ITEM_NAMES_EXPANDED: List[str] = []
for it in ITEM_DATA:
    # For counted items (BossKey, Rainbow_Monkey), a single ID is fine; count is handled in pool creation.
    _ITEM_NAMES_EXPANDED.append(it.name)

ITEM_ID_TABLE: Dict[str, int] = {
    name: KND_ITEM_ID_BASE + i
    for i, name in enumerate(_ITEM_NAMES_EXPANDED)
}


def all_item_names() -> List[str]:
    return [it.name for it in ITEM_DATA]


def get_item_data(name: str) -> ItemData:
    for it in ITEM_DATA:
        if it.name == name:
            return it
    raise KeyError(f"Unknown item: {name}")


class KNDItem(Item):
    game = "Codename: Kids Next Door (GC)"


def make_item(name: str, player: int) -> KNDItem:
    """
    Factory helper used by world.py.
    """
    data = get_item_data(name)
    return KNDItem(name, data.classification, ITEM_ID_TABLE[name], player)