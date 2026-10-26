"""Large-scale winner simulation for Name Picker."""

from __future__ import annotations

import argparse
import csv
import random
import secrets
from pathlib import Path

from .picker import MAX_NAMES, MAX_TRIES, _validate_names


DEFAULT_SIMULATIONS = 1_000_000


def simulate_winners(
    names: list[str] | tuple[str, ...],
    rounds: int,
    simulations: int = DEFAULT_SIMULATIONS,
    output: Path | None = None,
) -> dict[str, int]:
    """Run independent sessions and count the winner of each session.

    A session winner is the name with the most round wins. If a session ends
    tied, one of the tied leaders is selected randomly so every simulation has
    exactly one winner in the output log.

    The optimized inner loop draws a uniformly random name per round. This is
    mathematically equivalent to drawing three finalists and choosing one:
    every name has the same 1/N chance to win a round.
    """

    cleaned = _validate_names(names)
    if not 1 <= rounds <= MAX_TRIES:
        raise ValueError(f"rounds must be between 1 and {MAX_TRIES}")
    if simulations < 1:
        raise ValueError("simulations must be at least 1")

    rng = random.Random(secrets.randbits(128))
    winner_counts = {name: 0 for name in cleaned}
    writer = None
    output_file = None
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output_file = output.open("w", newline="", encoding="utf-8")
        writer = csv.writer(output_file)
        writer.writerow(("simulation", "winner"))

    try:
        for simulation_number in range(1, simulations + 1):
            scores = [0] * len(cleaned)
            for _ in range(rounds):
                scores[rng.randrange(len(cleaned))] += 1
            highest = max(scores)
            leaders = [index for index, score in enumerate(scores) if score == highest]
            winner = cleaned[rng.choice(leaders)]
            winner_counts[winner] += 1
            if writer is not None:
                writer.writerow((simulation_number, winner))
    finally:
        if output_file is not None:
            output_file.close()

    return winner_counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run many independent Name Picker sessions.")
    parser.add_argument("--names", nargs="+", required=True, help=f"Names to consider (2–{MAX_NAMES}).")
    parser.add_argument("--rounds", type=int, required=True, help=f"Rounds per session (1–{MAX_TRIES}).")
    parser.add_argument("--simulations", type=int, default=DEFAULT_SIMULATIONS, help=f"Sessions to run (default: {DEFAULT_SIMULATIONS:,}).")
    parser.add_argument("--output", type=Path, default=Path("winner-results.csv"), help="CSV file for every session winner.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        counts = simulate_winners(args.names, args.rounds, args.simulations, args.output)
    except ValueError as error:
        raise SystemExit(f"Error: {error}") from error

    highest = max(counts.values())
    leaders = [name for name, count in counts.items() if count == highest]
    print(f"Completed {args.simulations:,} simulations × {args.rounds} rounds.")
    print(f"Winner log: {args.output}")
    print("\nSession winner counts:")
    for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].casefold())):
        print(f"  {name:<20} {count:,}")
    print(f"\nTop winner: {', '.join(leaders)} ({highest:,})")


if __name__ == "__main__":
    main()
