# options.py
# KND (GameCube) Archipelago world - Player options
#
# These options define "Fixed vs Loose" logic, assumed difficulty, and progression pacing.
# They do not DO anything by themselves — world.py will read them and apply behavior.
#
# Defaults are conservative and beginner-friendly:
# - Logic Mode: Fixed
# - Difficulty: Standard
# - Starting Stage Slots: 1
# - Stage 14 placement: Always Last (classic "final stage" feel)
# - BossKeys: Fixed (locked placements)  [Loose logic can override later in world.py]
# - Auto-complete on victory: Enabled

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from Options import (
    Choice,
    Toggle,
    Range,
    PerGameCommonOptions,
)


class LogicMode(Choice):
    """How strict the logic assumptions are."""
    display_name = "Logic Mode"
    option_fixed = 0
    option_loose = 1
    default = 0


class DifficultyAssumption(Choice):
    """
    What difficulty tier the logic assumes the player can perform.
    This is used to interpret requires_by_difficulty in locations.py.
    """
    display_name = "Difficulty Assumption"
    option_standard = 0
    option_moderate = 1
    option_hard = 2
    option_expert = 3
    default = 0


class StartingStageSlots(Range):
    """
    How many stage slots are active/unlocked at the start.
    (You described 1–14, stopping at 14 so Stage 14 can still be reserved as final in classic mode.)
    """
    display_name = "Starting Stage Slots"
    range_start = 1
    range_end = 14
    default = 1


class Stage14Placement(Choice):
    """
    Whether Stage 14 (Lunarumble) is always the final stage slot, or allowed in the random pool.
    """
    display_name = "Stage 14 Placement"
    option_always_last = 0
    option_in_pool = 1
    default = 0


class BossKeyMode(Choice):
    """
    Whether BossKeys are locked to specific fixed locations (Fixed),
    or allowed to be shuffled into the item pool (Shuffle).

    Note:
      - Even if this is Fixed, LogicMode=Loose can later override in world.py (as requested).
    """
    display_name = "BossKey Mode"
    option_fixed = 0
    option_shuffle = 1
    default = 0


class AutoCompleteOnVictory(Toggle):
    """
    If enabled, once the player gets Victory, the world can auto-release remaining checks/items.
    (Implementation is in world.py; this just exposes the setting.)
    """
    display_name = "Auto-Complete Remaining Checks On Victory"
    default = 1


class IncludeFixedItemsInPoolWhenLoose(Toggle):
    """
    If enabled AND LogicMode is Loose, items that are normally "fixed" (locked placements)
    can be added to the random pool instead.

    This is your requested future behavior; world.py will implement the exact rules.
    """
    display_name = "Loose Logic: Include Fixed Items In Pool"
    default = 1


@dataclass
class KNDOptions(PerGameCommonOptions):
    logic_mode: LogicMode
    difficulty_assumption: DifficultyAssumption
    starting_stage_slots: StartingStageSlots
    stage14_placement: Stage14Placement
    bosskey_mode: BossKeyMode
    auto_complete_on_victory: AutoCompleteOnVictory
    include_fixed_items_in_pool_when_loose: IncludeFixedItemsInPoolWhenLoose
