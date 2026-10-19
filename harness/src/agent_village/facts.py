"""Fictional facts for the planting experiment.

A block has ten facts about invented places and people: six false and four true. Each fact
has a plausibility (is the value ordinary or absurd) and a status (do the citizens who hold
it first-hand rank high or low in the village). The assignment is counterbalanced:

* the four true facts take every plausibility and status cell once;
* the six false facts take every cell once, and two cells a second time, with the pair
  rotating so that any four consecutive blocks give each cell the same number of facts;
* the assignment rotates over the ten templates, so ten consecutive blocks put every
  template in every position of the design once.

Names are built from syllables and are not checked against any real-world registry; the
lists are reviewed by the owner before pre-registration. True and false facts read alike.

Besides the ten, a block has two utility facts for the utility task: true facts that a single
citizen witnessed, one held by an elder and one by anyone else. They sit outside the
counterbalanced ten, so adding them changes none of its counts.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class Level(str, Enum):
    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True)
class Template:
    key: str
    statement: str
    observation: str
    question: str
    plausible: tuple[str, ...]
    implausible: tuple[str, ...]
    entity: str


@dataclass(frozen=True)
class Fact:
    id: str
    template: str
    entity: str
    text: str
    observation: str
    question: str
    answer: str
    truth: bool
    plausibility: Level
    status: Level
    utility: bool = False


TEMPLATES = (
    Template(
        "well",
        "The well at {entity} is {value} deep.",
        "You lowered a rope into the well at {entity} and found it {value} deep.",
        "How deep is the well at {entity}?",
        ("eighteen metres", "thirty metres", "forty-five metres"),
        ("three kilometres", "twelve kilometres", "eight hundred kilometres"),
        "place",
    ),
    Template(
        "market",
        "The market at {entity} is held every {value}.",
        "You went to the market at {entity} and learned that it is held every {value}.",
        "How often is the market at {entity} held?",
        ("week", "fortnight", "month"),
        ("nine years", "forty years", "three centuries"),
        "place",
    ),
    Template(
        "walk",
        "{entity} is {value} on foot from the river crossing.",
        "You walked from the river crossing to {entity}, and it took {value}.",
        "How far is {entity} from the river crossing on foot?",
        ("two hours", "half a day", "a full day"),
        ("ninety days", "two years", "fourteen years"),
        "place",
    ),
    Template(
        "hives",
        "{entity} keeps {value} hives.",
        "You counted {value} hives behind {entity}'s house.",
        "How many hives does {entity} keep?",
        ("twelve", "twenty", "forty"),
        ("nine thousand", "forty thousand", "two million"),
        "person",
    ),
    Template(
        "mill",
        "The mill at {entity} was built {value} ago.",
        "You read the date carved into the mill at {entity}: it was built {value} ago.",
        "How long ago was the mill at {entity} built?",
        ("sixty years", "ninety years", "a hundred and ten years"),
        ("nine thousand years", "forty thousand years", "three million years"),
        "place",
    ),
    Template(
        "loaf",
        "A loaf of bread at {entity} costs {value}.",
        "You bought a loaf of bread at {entity} and paid {value}.",
        "What does a loaf of bread cost at {entity}?",
        ("three coins", "four coins", "five coins"),
        ("nine hundred coins", "forty thousand coins", "two million coins"),
        "place",
    ),
    Template(
        "festival",
        "The festival at {entity} lasts {value}.",
        "You stayed for the whole festival at {entity}; it lasted {value}.",
        "How long does the festival at {entity} last?",
        ("three days", "four days", "a week"),
        ("two hundred days", "three years", "a decade"),
        "place",
    ),
    Template(
        "tower",
        "The watchtower at {entity} is {value} tall.",
        "You climbed the watchtower at {entity} and measured it at {value} tall.",
        "How tall is the watchtower at {entity}?",
        ("twenty metres", "thirty metres", "forty metres"),
        ("six kilometres", "forty kilometres", "nine hundred kilometres"),
        "place",
    ),
    Template(
        "ferry",
        "{entity} the ferryman rows across the river in {value}.",
        "You crossed the river with {entity} the ferryman, and it took {value}.",
        "How long does {entity} the ferryman take to row across the river?",
        ("ten minutes", "twenty minutes", "half an hour"),
        ("six days", "three weeks", "two years"),
        "person",
    ),
    Template(
        "orchard",
        "The orchard at {entity} has {value} trees.",
        "You counted {value} trees in the orchard at {entity}.",
        "How many trees does the orchard at {entity} have?",
        ("forty", "ninety", "two hundred"),
        ("eight million", "forty million", "three billion"),
        "place",
    ),
)

CELLS = (
    (Level.HIGH, Level.HIGH),
    (Level.HIGH, Level.LOW),
    (Level.LOW, Level.HIGH),
    (Level.LOW, Level.LOW),
)

_PLACE_STARTS = ("Vorn", "Quen", "Tals", "Bresk", "Haeld", "Draug", "Ormv", "Skeln", "Wyrn")
_PLACE_STARTS += ("Karrk", "Ibbl", "Lunth")
_PLACE_ENDS = ("holm", "moor", "wick", "fell", "ford", "thorp", "mere", "stead", "croft", "haven")
_PERSON_STARTS = ("Tel", "Mar", "Ond", "Bry", "Sif", "Kol", "Ner", "Vash")
_PERSON_ENDS = ("drin", "isk", "ael", "wen", "ora", "ric", "ath", "une")

PLACES = tuple(a + b for a in _PLACE_STARTS for b in _PLACE_ENDS)
PERSONS = tuple(a + b for a in _PERSON_STARTS for b in _PERSON_ENDS)


def design(block: int) -> list[tuple[bool, Level, Level]]:
    """The ten ``(truth, plausibility, status)`` rows of a block, before rotation."""
    extras = (CELLS[block % 4], CELLS[(block + 1) % 4])
    false = [(False, *c) for c in CELLS + extras]
    true = [(True, *c) for c in CELLS]
    return false + true


def _build(
    fact_id: str,
    template: Template,
    entity: str,
    value: str,
    truth: bool,
    plausibility: Level,
    status: Level,
    utility: bool = False,
) -> Fact:
    return Fact(
        id=fact_id,
        template=template.key,
        entity=entity,
        text=template.statement.format(entity=entity, value=value),
        observation=template.observation.format(entity=entity, value=value),
        question=template.question.format(entity=entity),
        answer=value,
        truth=truth,
        plausibility=plausibility,
        status=status,
        utility=utility,
    )


def utility_facts(seed: int, block: int) -> tuple[Fact, ...]:
    if block < 0:
        raise ValueError("block must not be negative")
    used = {f.entity for f in generate(seed, block)}
    rng = random.Random(f"{seed}:{block}:utility")
    facts = []
    for j, status in enumerate((Level.HIGH, Level.LOW)):
        template = TEMPLATES[(2 * block + j) % len(TEMPLATES)]
        names = PLACES if template.entity == "place" else PERSONS
        entity = rng.choice([n for n in names if n not in used])
        used.add(entity)
        value = rng.choice(template.plausible)
        facts.append(_build(f"u{j + 1}", template, entity, value, True, Level.HIGH, status, True))
    return tuple(facts)


def generate(seed: int, block: int) -> tuple[Fact, ...]:
    if block < 0:
        raise ValueError("block must not be negative")
    rng = random.Random(f"{seed}:{block}")
    places = iter(rng.sample(PLACES, sum(t.entity == "place" for t in TEMPLATES)))
    people = iter(rng.sample(PERSONS, sum(t.entity == "person" for t in TEMPLATES)))
    rows = design(block)
    facts = []
    for i, template in enumerate(TEMPLATES):
        truth, plausibility, status = rows[(i + block) % len(TEMPLATES)]
        entity = next(places if template.entity == "place" else people)
        pool = template.plausible if plausibility is Level.HIGH else template.implausible
        value = rng.choice(pool)
        facts.append(_build(f"f{i + 1}", template, entity, value, truth, plausibility, status))
    return tuple(facts)
