# Flip-7 statistics

A small simulator that estimates scores for the "Flip-7" game by running many simulated games and plotting simple statistics.

This repository contains a compact simulation and a small interactive entry point.

## Features
- Run many simulated games and collect score statistics.
- Compute running averages and present simple visualizations using tkinter.
- Small, focused codebase for experimentation and analysis.

## Project layout
- `main.py` — UI / entry point that prompts for simulation parameters and displays results.
- `game.py` — Simulation core (contains `run_experiment` and `ExperimentResults`).
- `player.py` — `Player` model used by the simulation.
- `.gitignore` — Ignored files.

## Requirements
- Python 3.9+
- numpy
- tkinter (usually included with Python; on some Linux distributions install `python3-tk`)

Install the dependency:

```powershell
python -m pip install --upgrade pip
pip install numpy
```

## Usage
Run the interactive GUI (it will prompt for the number of simulated hands):

```powershell
python main.py
```

Or run the simulation programmatically from a Python REPL or script:

```py
from game import run_experiment

results = run_experiment(hands=100000, seed=42)
print("Final running average:", results.running_avg[-1])
```

## Notes
- The codebase uses modern type hints (e.g. `list[int]`) so use Python 3.9 or newer.
- If the GUI does not appear on Linux, ensure `python3-tk` (or equivalent) is installed.
- There are currently no automated tests in the repository; consider adding a small test harness if you plan to refactor the simulation.

## License
Add a license file (e.g., `LICENSE`) or replace this section with your preferred license.

---

If you'd like, I can also:
- add a minimal `requirements.txt` or `pyproject.toml`;
- add a short example script under `examples/`;
- or create a small unit test for `game.run_experiment`.
