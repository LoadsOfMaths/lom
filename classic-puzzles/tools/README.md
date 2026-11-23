# Matchstick puzzle generator

Generates and checks candidate puzzles on rectangular (2x2, 3x2, 3x3, with 45-degree "diamond" slots) and triangular (side 2, 3) lattices.

- `lat.py` builds the lattices, lists every square/triangle, and the lattice symmetries.
- `srch.cpp` (g++ -O2 -o srch srch.cpp) enumerates every move / add / take-away set up to the limits given on the command line.
- `run.py <lattice> <seed> <number of starts>` samples start figures and records the minimum-move puzzles (raw_<lattice>.json).
- `select_.py` scores and picks the best candidates, `review.py` writes `review.html` + `candidates.json`.
- `verify.py` recounts every start and answer from the geometry alone, as an independent check.

Review page: `../review/index.html`. Chosen puzzle IDs come back from its "Copy chosen IDs" button.
