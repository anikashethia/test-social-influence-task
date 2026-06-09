"""
Stimuli management for the Social Influence Task.

Important: this task involves NO chatbot interaction and NO LLM calls.
Participants simply see a pre-set rating number next to each artwork and
re-rate it themselves. The "agent" is just a label paired with a fixed
number stored in agent_ratings.json; RNG conditions use seeded random numbers.

What this module does:
  - Loads artworks from stimuli/artworks.json
  - Loads pre-set agent ratings from stimuli/agent_ratings.json
  - Assigns artworks to conditions for each participant (counterbalancing)
  - Builds Phase 1 and Phase 2 trial lists

Artwork-condition assignment:
  12 conditions: Alex, Sam, Casey, Jordan, Morgan, Riley + RNG_1..RNG_6
  50 artworks:  ~4 per condition (conditions 0-1 get 5, rest get 4)
  Rotation:     every 12 participants = 1 complete rotation
  Rule:         (artwork_id - 1 + participant_index) mod 12 -> condition
"""

import json
import random
from pathlib import Path

STIMULI_DIR = Path(__file__).parent / "stimuli"
ARTWORKS_FILE = STIMULI_DIR / "artworks.json"
AGENT_RATINGS_FILE = STIMULI_DIR / "agent_ratings.json"

AGENT_CONDITIONS = ["Alex", "Sam", "Casey", "Jordan", "Morgan", "Riley"]
RNG_CONDITIONS = ["RNG_1", "RNG_2", "RNG_3", "RNG_4", "RNG_5", "RNG_6"]
ALL_CONDITIONS = AGENT_CONDITIONS + RNG_CONDITIONS
N_CONDITIONS = len(ALL_CONDITIONS)  # 12
TOTAL_ARTWORKS = 50


def is_rng(condition: str) -> bool:
    return condition.startswith("RNG_")


def load_artworks() -> list[dict]:
    return json.loads(ARTWORKS_FILE.read_text())


def load_agent_ratings() -> dict[str, dict[str, int]]:
    if AGENT_RATINGS_FILE.exists():
        return json.loads(AGENT_RATINGS_FILE.read_text())
    return {}


def get_agent_rating(condition: str, artwork_id: int, ratings: dict) -> int:
    if is_rng(condition):
        rng = random.Random(hash(condition) ^ (artwork_id * 1337))
        return rng.randint(10, 90)

    condition_ratings = ratings.get(condition, {})
    rating = condition_ratings.get(str(artwork_id))
    if rating is not None:
        return int(rating)

    rng = random.Random(hash(condition) + artwork_id)
    return rng.randint(30, 80)


def assign_artworks_to_conditions(participant_index: int) -> dict[str, list[dict]]:
    artworks = load_artworks()
    assert len(artworks) == TOTAL_ARTWORKS, (
        f"Expected {TOTAL_ARTWORKS} artworks in artworks.json, got {len(artworks)}."
    )

    offset = participant_index % N_CONDITIONS
    assignment: dict[str, list[dict]] = {c: [] for c in ALL_CONDITIONS}

    for artwork in artworks:
        condition_idx = ((artwork["id"] - 1) + offset) % N_CONDITIONS
        condition = ALL_CONDITIONS[condition_idx]
        assignment[condition].append(artwork)

    return assignment


def build_phase1_trials(
    participant_index: int,
    seed: int | None = None,
) -> list[dict]:
    artworks = load_artworks()
    trials = [
        {
            "artwork_id": a["id"],
            "title": a["title"],
            "artist": a["artist"],
            "year": a["year"],
            "image_url": a.get("image_url", ""),
            "wikiart_url": a.get("wikiart_url", ""),
            "trial_index": i,
        }
        for i, a in enumerate(artworks)
    ]
    rng = random.Random((seed if seed is not None else participant_index) + 99999)
    rng.shuffle(trials)
    for i, t in enumerate(trials):
        t["trial_index"] = i
    return trials


def build_phase2_trials(
    participant_index: int,
    seed: int | None = None,
) -> list[dict]:
    assignment = assign_artworks_to_conditions(participant_index)
    ratings = load_agent_ratings()

    trials = []
    for condition, artworks in assignment.items():
        for artwork in artworks:
            agent_rating = get_agent_rating(condition, artwork["id"], ratings)
            trials.append({
                "artwork_id": artwork["id"],
                "title": artwork["title"],
                "artist": artwork["artist"],
                "year": artwork["year"],
                "image_url": artwork.get("image_url", ""),
                "wikiart_url": artwork.get("wikiart_url", ""),
                "agent_condition": condition,
                "agent_rating": agent_rating,
                "is_rng": is_rng(condition),
            })

    rng = random.Random(seed if seed is not None else participant_index)
    rng.shuffle(trials)
    for i, t in enumerate(trials):
        t["trial_index"] = i

    return trials
