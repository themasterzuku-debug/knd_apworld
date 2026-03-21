# world.py
# KND (GameCube) Archipelago world - Core world glue
#
# This file:
# - Builds regions (via regions.py)
# - Adds locations (via locations.py)
# - Creates item pool (via items.py)
# - Applies access rules (difficulty + fixed/loose behaviors)
# - Locks Victory onto Stage_14_Lunarumble_Complete
#
# IMPORTANT:
# - This is “full world.py” for the AP side.
# - It does NOT patch the GameCube ROM or enforce in-game routing. That is client/patch work.
# - It DOES define the logic graph + item placement + completion condition.

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from BaseClasses import MultiWorld, Region, Location
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import set_rule

from .regions import create_regions, STAGE_REGIONS, REGION_MENU
from .locations import LOCATION_DATA, LOCATION_ID_TABLE, LocationData
from .items import (
    ITEM_DATA,
    ITEM_ID_TABLE,
    ItemData,
    make_item,
)
from .options import KNDOptions, LogicMode, DifficultyAssumption, BossKeyMode


# -------------------------
# World metadata
# -------------------------

class KNDWeb(WebWorld):
    theme = "party"
    tutorials = []


class KNDLocation(Location):
    game = "Codename: Kids Next Door (GC)"


class KNDWorld(World):
    """
    Codename: Kids Next Door (GC) Archipelago world.
    """
    game = "Codename: Kids Next Door (GC)"
    web = KNDWeb()

    options_dataclass = KNDOptions  # type: ignore
    options: KNDOptions

    # AP expects these for ID lookup
    item_name_to_id = ITEM_ID_TABLE
    location_name_to_id = LOCATION_ID_TABLE

    # If you ever want grouped hints, keep these:
    item_name_groups: Dict[str, List[str]] = {}

    # Stage -> operative mapping (per your confirmed mapping)
    STAGE_TO_OPERATIVE: Dict[str, str] = {
        "Stage_01_Tutorial": "Operative_N1",
        "Stage_02_Donutty": "Operative_N1",
        "Stage_03_Boogification": "Operative_N5",
        "Stage_04_SnotBomber": "Operative_N2",
        "Stage_05_Spank_Happy": "Operative_N4",
        "Stage_06_Hamsterama": "Operative_N3",
        "Stage_07_Spankarific": "Operative_N1",
        "Stage_08_Tarpoon": "Operative_N2",
        "Stage_09_Ship_Shape": "Operative_N5",
        "Stage_10_Brush_Off": "Operative_N3",
        "Stage_11_Cavity_Cave": "Operative_N1",
        "Stage_12_Overflow": "Operative_N4",
        "Stage_13_MoonTrip": "Operative_N2",
        "Stage_14_Lunarumble": "Operative_N1",  # you said “we’ll say N1”
        "Stage_15_Credits": "Operative_N2",
    }

    # Region name -> Stage unlock item
    STAGE_TO_UNLOCK_ITEM: Dict[str, str] = {
        "Stage_01_Tutorial": "Stage_01_Tutorial_Unlock",
        "Stage_02_Donutty": "Stage_02_Donutty_Unlock",
        "Stage_03_Boogification": "Stage_03_Boogification_Unlock",
        "Stage_04_SnotBomber": "Stage_04_SnotBomber_Unlock",
        "Stage_05_Spank_Happy": "Stage_05_Spank_Happy_Unlock",
        "Stage_06_Hamsterama": "Stage_06_Hamsterama_Unlock",
        "Stage_07_Spankarific": "Stage_07_Spankarific_Unlock",
        "Stage_08_Tarpoon": "Stage_08_Tarpoon_Unlock",
        "Stage_09_Ship_Shape": "Stage_09_Ship_Shape_Unlock",
        "Stage_10_Brush_Off": "Stage_10_Brush_Off_Unlock",
        "Stage_11_Cavity_Cave": "Stage_11_Cavity_Cave_Unlock",
        "Stage_12_Overflow": "Stage_12_Overflow_Unlock",
        "Stage_13_MoonTrip": "Stage_13_MoonTrip_Unlock",
        "Stage_14_Lunarumble": "Stage_14_Lunarumble_Unlock",
        "Stage_15_Credits": "Stage_15_Credits_Unlock",
    }

    # Fixed BossKey placements (your “toilet key + boss keys tied to specific stages” baseline)
    # 8 total: Tutorial Toilet Secret + Stage clears for 2,4,5,7,9,11,12
    FIXED_BOSSKEY_LOCATIONS: Tuple[str, ...] = (
        "Stage_01_Tutorial_Secret",         # Toilet secret -> BossKey (hilarious, as requested)
        "Stage_02_Donutty_Complete",        # Stuffum
        "Stage_04_SnotBomber_Complete",     # Common Cold
        "Stage_05_Spank_Happy_Complete",    # Vampire KND
        "Stage_07_Spankarific_Complete",    # Count Spankulot
        "Stage_09_Ship_Shape_Complete",     # Stickybeard
        "Stage_11_Cavity_Cave_Complete",    # Knightbrace
        "Stage_12_Overflow_Complete",       # Toiletnator
    )

    # Victory location name (event)
    VICTORY_LOCATION = "Stage_14_Lunarumble_Complete"

    # “Gate” items for final stage (tuned later if you add options)
    FINAL_REQUIRED_BOSSKEYS = 8
    FINAL_REQUIRED_COSMETIC = "Outfit_N1_N86"

    # -------------------------
    # AP lifecycle
    # -------------------------

    def create_regions(self) -> None:
        # Build regions + Menu->Stage entrances
        self._regions = create_regions(self)

        # Attach locations to regions
        for loc in LOCATION_DATA:
            region = self._regions[loc.region]
            loc_obj = KNDLocation(self.player, loc.name, LOCATION_ID_TABLE[loc.name], region)
            region.locations.append(loc_obj)

    def create_items(self) -> None:
        # Determine bosskey placement behavior.
        # Your requested behavior: in Loose logic, allow “fixed” to be included in pool.
        bosskey_mode = self.options.bosskey_mode.value

        if self.options.logic_mode.value == LogicMode.option_loose and self.options.include_fixed_items_in_pool_when_loose.value:
            # Override for fun: loose logic defaults to shuffled pool behavior.
            bosskey_mode = BossKeyMode.option_shuffle

        # Build the pool
        pool = []

        for it in ITEM_DATA:
            # Victory is an event: never in pool (we place it directly on Stage 14 completion)
            if it.name == "Victory":
                continue

            # If BossKeys are fixed, do not add them to the pool (they are lock-placed).
            if it.name == "BossKey" and bosskey_mode == BossKeyMode.option_fixed:
                continue

            # Add N copies for counted items
            for _ in range(max(1, it.count)):
                pool.append(make_item(it.name, self.player))

        self.multiworld.itempool += pool

    def set_rules(self) -> None:
        # Difficulty key for requires_by_difficulty
        diff_key = self._difficulty_key()

        # 1) Stage entrance rules (Menu -> Stage_X)
        menu = self._regions[REGION_MENU]
        for stage_region_name in STAGE_REGIONS:
            # Find the entrance created in regions.py:
            # name is "Menu -> {stage}"
            entrance_name = f"Menu -> {stage_region_name}"
            entrance = next(e for e in menu.exits if e.name == entrance_name)

            unlock_item = self.STAGE_TO_UNLOCK_ITEM[stage_region_name]
            operative_item = self.STAGE_TO_OPERATIVE[stage_region_name]

            # Base: need both stage unlock + correct operative
            def _base_stage_rule(state, u=unlock_item, op=operative_item):
                return state.has(u, self.player) and state.has(op, self.player)

            set_rule(entrance, _base_stage_rule)

        # 2) Final stage extra gates (bosskeys + N86 outfit)
        final_entrance = next(e for e in self._regions[REGION_MENU].exits if e.name == "Menu -> Stage_14_Lunarumble")

        def _final_rule(state):
            return (
                state.has(self.STAGE_TO_UNLOCK_ITEM["Stage_14_Lunarumble"], self.player)
                and state.has(self.STAGE_TO_OPERATIVE["Stage_14_Lunarumble"], self.player)
                and state.has(self.FINAL_REQUIRED_COSMETIC, self.player)
                and state.has("BossKey", self.player, self.FINAL_REQUIRED_BOSSKEYS)
            )

        set_rule(final_entrance, _final_rule)

        # 3) Location rules (difficulty requirements + unconditional requires)
        for loc in LOCATION_DATA:
            loc_obj = self.multiworld.get_location(loc.name, self.player)

            req_all: List[str] = list(loc.requires)

            if loc.requires_by_difficulty:
                req_all.extend(list(loc.requires_by_difficulty.get(diff_key, ())))
            if req_all:
                set_rule(loc_obj, self._items_required_rule(tuple(req_all)))

        # 4) Completion condition: obtain Victory (placed on Stage 14 completion location)
        self.multiworld.completion_condition[self.player] = lambda state: state.has("Victory", self.player)

    def generate_basic(self) -> None:
        """
        Locked placements + starting items (safe, deterministic AP-side behaviors).
        """
        # Place Victory on Stage 14 completion
        victory_loc = self.multiworld.get_location(self.VICTORY_LOCATION, self.player)
        victory_loc.place_locked_item(make_item("Victory", self.player))

        # BossKey placement policy
        bosskey_mode = self.options.bosskey_mode.value
        if self.options.logic_mode.value == LogicMode.option_loose and self.options.include_fixed_items_in_pool_when_loose.value:
            bosskey_mode = BossKeyMode.option_shuffle

        if bosskey_mode == BossKeyMode.option_fixed:
            # Lock place 8 BossKeys on your chosen “fixed” locations
            for loc_name in self.FIXED_BOSSKEY_LOCATIONS:
                self.multiworld.get_location(loc_name, self.player).place_locked_item(make_item("BossKey", self.player))

        # Starting slots: precollect stage unlock + operative for the starting playable stages
        self._grant_starting_slots()

    # -------------------------
    # Helpers
    # -------------------------

    def _difficulty_key(self) -> str:
        # Map options enum -> string key used in locations.py
        val = self.options.difficulty_assumption.value
        if val == DifficultyAssumption.option_standard:
            return "standard"
        if val == DifficultyAssumption.option_moderate:
            return "moderate"
        if val == DifficultyAssumption.option_hard:
            return "hard"
        return "expert"

    def _items_required_rule(self, required: Tuple[str, ...]):
        def rule(state):
            return all(state.has(name, self.player) for name in required)
        return rule

    def _grant_starting_slots(self) -> None:
        """
        Grants starting Stage unlock(s) + required operative(s) so the player is never softlocked.
        This is AP-side gating only. Your ROM/client patch will handle stage-slot randomization separately.
        """
        count = int(self.options.starting_stage_slots.value)

        # Choose starting stages randomly from the non-final stages by default
        # (We still allow Stage 15 in the mix; Stage 14 is gated as "final" via entrance rules anyway.)
        candidate_stages = [s for s in STAGE_REGIONS if s != "Stage_14_Lunarumble"]

        # Deterministic per-slot selection using the AP RNG
        chosen = self.random.sample(candidate_stages, k=min(count, len(candidate_stages)))

        for stage in chosen:
            unlock_item = self.STAGE_TO_UNLOCK_ITEM[stage]
            op_item = self.STAGE_TO_OPERATIVE[stage]

            self.multiworld.push_precollected(make_item(unlock_item, self.player))
            self.multiworld.push_precollected(make_item(op_item, self.player))
