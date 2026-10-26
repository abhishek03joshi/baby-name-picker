import csv

from name_picker.simulation import simulate_winners


def test_simulation_counts_each_session_and_writes_winners(tmp_path):
    output = tmp_path / "winners.csv"
    counts = simulate_winners(["A", "B", "C"], rounds=3, simulations=20, output=output)

    assert set(counts) == {"A", "B", "C"}
    assert sum(counts.values()) == 20
    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 20
    assert {row["winner"] for row in rows} <= {"A", "B", "C"}
