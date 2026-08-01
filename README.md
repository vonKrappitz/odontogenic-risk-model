# Pre-flight odontogenic-risk decision model

Companion code for the decision-analytic model in the manuscript
**"Pre-flight elimination of odontogenic risk in missions without evacuation:
a threshold hypothesis and decision-analysis framework."**

The model is fully synthetic: it uses no patient data. It compares four
mutually exclusive pre-flight dental policies for long-duration, no-evacuation
spaceflight and locates, under wide uncertainty, the isolation threshold at
which the harm-minimising policy shifts. This repository reproduces every
number and figure in the paper from scratch.

> **A note on the file names.** This study was written and developed in Polish,
> and the source files keep their original Polish names as a record of that.
> The table below maps every file to its English meaning and to the figure or
> output it produces, so the code is fully navigable without Polish. All
> figure axes, titles and legends in the generated output are in English.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21728788.svg)](https://doi.org/10.5281/zenodo.21728788)

**Archived version DOI:** https://doi.org/10.5281/zenodo.21728789 (version 1.0.0)  
**Concept DOI (always resolves to the latest version):** https://doi.org/10.5281/zenodo.21728788

## Policies

| | Policy | Meaning |
|---|---|---|
| P1 | Retention | current qualification standards, treat only what meets terrestrial indications |
| P2 | Selective extraction | remove every tooth above a defined risk threshold |
| P3 | Tooth-preserving sanation | replace high-risk restorations, treat borderline teeth, extract only hopeless ones |
| P4 | Full dental clearance | remove the whole dentition |

Onboard capability `c` is a scenario parameter (0 to 1), not a competing policy.

## Files (Polish name to English meaning)

| File (Polish) | Literal meaning | What it is / produces |
|---|---|---|
| `model_decyzyjny_v4.py` | "decision model, v4" | **The model.** Run it to print all reported numbers: scenario optimality shares, Table 4 effect sizes, the log-uniform robustness check, the tau sensitivity, and the EVPPI values. Writes no figures. |
| `ryzyko_populacyjne.py` | "population risk" | **Fig 1** — population risk `P(n) = 1 - (1 - p)^n` |
| `figura_urwana_miarka.py` | "truncated ruler figure" | **Fig 2** — mission duration vs the caries-development window |
| `figura_drzewo_decyzyjne.py` | "decision tree figure" | **Fig 3** — decision structure of policies P1-P4 |
| `figura_mapa_margines.py` | "margin map figure" | **Fig 4** — decision-margin map (imports the model) |
| `figura_przejscie_optimum.py` | "optimum transition figure" | **Fig 5** — optimality share vs time to definitive care (imports the model) |

The output image files are also Polish-named:
`ryzyko_populacyjne` (Fig 1), `figura_urwana_miarka` (Fig 2),
`figura_drzewo_decyzyjne` (Fig 3), `figura_mapa_progowa` (Fig 4, "threshold map"),
`figura_przejscie_optimum` (Fig 5).

Figures 4 and 5 read `model_decyzyjny_v4.py`, so keep all files in one folder.

## Reproduce

```bash
pip install -r requirements.txt

python3 model_decyzyjny_v4.py          # prints every number in the paper
python3 ryzyko_populacyjne.py          # each figure script writes a PNG and a PDF
python3 figura_urwana_miarka.py
python3 figura_drzewo_decyzyjne.py
python3 figura_mapa_margines.py
python3 figura_przejscie_optimum.py
```

All random seeds are fixed in the code, so results are deterministic. The
uncertain quantities are drawn from elicited triangular distributions used for
probabilistic sensitivity analysis (Table 3 in the paper), not empirical
estimates. Code comments are in Polish; this README is the English guide to them.

## How to cite

If you use this code, please cite the paper (full reference to be added on
acceptance) and the archived code release:

```
Kasperek, M. M. Pre-flight odontogenic-risk decision model (version 1.0.0)
[software]. Zenodo. https://doi.org/10.5281/zenodo.21728789
```

## License

Released under the Apache License 2.0. See `LICENSE` and `NOTICE`.
