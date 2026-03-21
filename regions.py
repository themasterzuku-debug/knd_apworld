# regions.py
# KND (GameCube) Archipelago world - Regions/Connections builder
#
# This file builds the region graph only.
# Locations are attached later (typically in locations.py / world.py).
#
# Expected region names (must match your regions.json / locations.json):
#   Menu
#   Stage_01_Tutorial ... Stage_15_Credits

from __future__ import annotations

from typing import Dict, List, Tuple

from BaseClasses import MultiWorld, Region, Entrance


# If you want to keep your region names centralized:
REGION_MENU = "Menu"
STAGE_REGIONS: List[str] = [
    "Stage_01_Tutorial",
    "Stage_02_Donutty",
    "Stage_03_Boogification",
    "Stage_04_SnotBomber",
    "Stage_05_Spank_Happy",
    "Stage_06_Hamsterama",
    "Stage_07_Spankarific",
    "Stage_08_Tarpoon",
    "Stage_09_Ship_Shape",
    "Stage_10_Brush_Off",
    "Stage_11_Cavity_Cave",
    "Stage_12_Overflow",
    "Stage_13_MoonTrip",
    "Stage_14_Lunarumble",
    "Stage_15_Credits",
]


def create_regions(world: "KNDWorld") -> Dict[str, Region]:
    """
    Create Region objects and hook up entrances.

    Note:
      - This does NOT attach locations.
      - This does NOT set access rules yet (that happens in world.py rules).
      - Menu connects to each stage region via a named entrance.

    Returns:
      dict mapping region name -> Region object
    """
    multiworld: MultiWorld = world.multiworld
    player: int = world.player

    regions: Dict[str, Region] = {}

    # Create Menu region
    menu = Region(REGION_MENU, player, multiworld)
    multiworld.regions.append(menu)
    regions[REGION_MENU] = menu

    # Create stage regions
    for rname in STAGE_REGIONS:
        reg = Region(rname, player, multiworld)
        multiworld.regions.append(reg)
        regions[rname] = reg

    # Connect Menu -> each stage region
    # (We do NOT create stage -> menu connections; those don't enforce in-game routing anyway.)
    for stage in STAGE_REGIONS:
        _connect(multiworld, player, regions[REGION_MENU], regions[stage], f"Menu -> {stage}")

    return regions


def _connect(multiworld: MultiWorld, player: int, source: Region, target: Region, name: str) -> Entrance:
    """
    Create an Entrance from source to target and register it in the region graph.
    """
    entrance = Entrance(player, name, source)
    source.exits.append(entrance)
    entrance.connect(target)
    return entrance
