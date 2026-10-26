# 🌙 Baby Name Picker — macOS Desktop App

Because choosing a name is serious business—but the chits can still be cute.

Baby Name Picker is a Python project and native macOS desktop app for two
soon-to-be parents. It recreates randomized name draws over 1–100 rounds,
supports 2–10 names, keeps a live score in memory, announces a clear leader,
and lets you rerun a tie with a newly randomized run.

The project has three ways to run: a command-line picker, a Tkinter desktop
GUI, and a million-session statistical simulator.

## Quick start

From the project directory, install the Python version declared in
`.tool-versions`, create a virtual environment, and install the project:

```bash
asdf install
asdf reshim python

python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the automated tests:

```bash
python -m pytest
```

Launch the interactive picker:

```bash
name-picker
```

Launch the native macOS desktop window:

```bash
name-picker-gui
```

The GUI provides ten name fields, a 1–100 rounds selector, a live scoreboard,
an all-time winner field, collapsible round history at the bottom, controls to
clear one round or reset all rounds, a shuffle/progress animation with a staged
scoreboard reveal, and a fresh-round prompt when the result is tied. If the
console command is not available, run it with:

```bash
python -m name_picker.gui
```

## Build and install the macOS app

To create a standalone double-clickable app named **Baby Name Picker**:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
./scripts/build_mac_app.sh
open "dist/Baby Name Picker.app"
```

The packaged app is created at `dist/Baby Name Picker.app`. It bundles the
Python runtime and the GUI, includes the cute baby icon in
`assets/baby-name-picker.icns`, and can be launched directly from Finder.
Build it again after changing the Python code. To install it, open the build
folder and drag **Baby Name Picker.app** into your Applications folder:

```bash
open dist
```

If an older copy is already installed, replace it with the newly built app
instead of keeping both copies.

Tkinter must be included in the Python build. If launching the GUI reports
`No module named '_tkinter'`, install the matching Homebrew Python and Tk
packages, then recreate `.venv`:

```bash
deactivate 2>/dev/null || true
rm -rf .venv
brew install python@3.15 python-tk@3.15
"$(brew --prefix python@3.15)/bin/python3.15" -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -c "import tkinter; print(tkinter.TkVersion)"
python -m name_picker.gui
```

The Homebrew `python-tk@3.15` package supplies the Tkinter support that the
asdf-built interpreter currently lacks.

Or provide names and the number of tries directly:

```bash
name-picker --names Aarav Milo Theo Leo --tries 100
```

The number of rounds defaults to 1 and can be set between 1 and 100.

The same command can be run with `python -m` if the console command is not
available in your shell:

```bash
python -m name_picker.cli --names Aarav Milo Theo Leo --tries 100
```

## Million-session simulation

To run one million independent sessions, with 10 rounds in each session:

```bash
./scripts/run_million.sh \
  --names Aarav Arjun Vir \
  --rounds 10
```

The script always runs exactly 1,000,000 sessions. It writes one winner per
session to `winner-results.csv` and prints the aggregate winner counts. If a
session itself is tied, one tied leader is chosen at random so every session
contributes exactly one winner.

For a smaller development run, use the Python module directly:

```bash
python -m name_picker.simulation \
  --names Aarav Arjun Vir \
  --rounds 10 \
  --simulations 1000 \
  --output /tmp/name-picker-results.csv
```

The same simulator is also available after installation:

```bash
name-picker-sim --names Aarav Arjun Vir --rounds 10
```

Each round always has three finalist slots. With 3–10 names, the finalists are
different. With exactly 2 names, the slots are drawn with replacement, so a
name can appear twice or three times and win the three-slot round naturally.
The example of three names is therefore just one valid input size—not a
special case or algorithmic requirement. If the top score is shared, the
program offers another run. Each run receives a fresh internal randomization
from the operating system. Nothing is written to disk: the score is
intentionally kept only for the current session.

## Development

Run the tests with:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

The reusable engine lives in `src/name_picker/picker.py`; the command-line
experience lives in `src/name_picker/cli.py`.

## A tiny note on fairness

Every name has the same chance to appear in each finalist slot, and every
finalist has the same chance to win its round. Each run is independently
randomized for family debates conducted with scientific seriousness.

Made with anticipation, spreadsheets, and a little bit of ✨ luck.
