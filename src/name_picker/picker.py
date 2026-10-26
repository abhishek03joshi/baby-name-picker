"""The deterministic core of the baby-name picker."""

from __future__ import annotations

from dataclasses import dataclass
import random
import secrets

MAX_NAMES = 10
MAX_TRIES = 100


@dataclass(frozen=True)
class RoundResult:
    """The public record of one three-slot finalist round."""

    round_number: int
    finalists: tuple[str, ...]
    winner: str


@dataclass(frozen=True)
class SessionResult:
    """Everything needed to review or reproduce a completed run."""

    seed: int
    rounds: tuple[RoundResult, ...]
    scores: dict[str, int]

    @property
    def leaders(self) -> tuple[str, ...]:
        highest = max(self.scores.values(), default=0)
        return tuple(name for name, score in self.scores.items() if score == highest)

    @property
    def has_clear_winner(self) -> bool:
        return len(self.leaders) == 1


def run_session(names: list[str] | tuple[str, ...], tries: int, seed: int | None = None) -> SessionResult:
    """Run ``tries`` fair three-slot finalist rounds using one independent seed.

    A supplied seed makes a run exactly reproducible. When omitted, a fresh
    seed comes from the operating system's cryptographically secure source.
    Each round has three finalist slots. With two names, slots are drawn with
    replacement; with three or more names, they are drawn without replacement.
    """

    cleaned = _validate_names(names)
    if not 1 <= tries <= MAX_TRIES:
        raise ValueError(f"tries must be between 1 and {MAX_TRIES}")
    if len(cleaned) < 2:
        raise ValueError("please provide at least 2 different names")

    actual_seed = secrets.randbits(128) if seed is None else seed
    rng = random.Random(actual_seed)
    scores = {name: 0 for name in cleaned}
    rounds: list[RoundResult] = []

    for round_number in range(1, tries + 1):
        finalists = (
            tuple(rng.choices(cleaned, k=3))
            if len(cleaned) == 2
            else tuple(rng.sample(cleaned, k=3))
        )
        winner = rng.choice(finalists)
        scores[winner] += 1
        rounds.append(RoundResult(round_number, finalists, winner))

    return SessionResult(actual_seed, tuple(rounds), scores)


def _validate_names(names: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    cleaned = tuple(name.strip() for name in names if name.strip())
    if len(cleaned) != len(set(cleaned)):
        raise ValueError("names must be unique (case-sensitive)")
    if any(not name for name in cleaned):
        raise ValueError("names cannot be empty")
    if len(cleaned) > MAX_NAMES:
        raise ValueError(f"the game supports at most {MAX_NAMES} names; please remove some names and try again")
    return cleaned
