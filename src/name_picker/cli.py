"""Command-line interface for the family name picker."""

from __future__ import annotations

import argparse

from .picker import MAX_TRIES, SessionResult, run_session


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pick a baby name with fair randomized rounds.")
    parser.add_argument("-n", "--names", nargs="+", help="Names to consider (2–10).")
    parser.add_argument("-t", "--tries", type=int, help=f"Number of randomized rounds (1–{MAX_TRIES}).")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    names = args.names or _ask_names()
    tries = args.tries or _ask_tries()

    while True:
        try:
            result = run_session(names, tries)
        except ValueError as error:
            raise SystemExit(f"Error: {error}") from error
        _print_result(result)
        if result.has_clear_winner:
            break
        answer = input("\nNo clear winner this time. Run another fresh round? [Y/n] ").strip().lower()
        if answer in {"n", "no", "q", "quit", "exit"}:
            break


def _ask_names() -> list[str]:
    print("Enter 2–10 names, separated by commas:")
    return [name.strip() for name in input("> ").split(",")]


def _ask_tries() -> int:
    while True:
        try:
            value = int(input("How many randomized rounds? ").strip())
            if 1 <= value <= MAX_TRIES:
                return value
        except ValueError:
            pass
        print(f"Please enter a whole number from 1 to {MAX_TRIES}.")


def _print_result(result: SessionResult) -> None:
    print("The chits are flying...\n")
    for round_result in result.rounds:
        print(f"  {round_result.round_number:>2}. {' · '.join(round_result.finalists)} → {round_result.winner}")
    print("\nScoreboard")
    for name, score in sorted(result.scores.items(), key=lambda item: (-item[1], item[0].casefold())):
        print(f"  {name:<20} {'●' * score or '–'} ({score})")
    leaders = result.leaders
    if result.has_clear_winner:
        print(f"\n🎉 The winner is: {leaders[0]}!")
    else:
        print(f"\n🤝 It’s a tie between: {', '.join(leaders)}")


if __name__ == "__main__":
    main()
