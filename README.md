# Pre-flight odontogenic-risk decision model

Companion code for the decision-analytic model in the manuscript
**"Odontogenic risk as an unserviceable failure mode in Mars missions:
a decision-theoretic reliability analysis."**

The model is fully synthetic: it uses no patient data. It compares four
mutually exclusive pre-flight dental policies for long-duration, no-evacuation
spaceflight and locates, under wide uncertainty, the isolation threshold at
which the harm-minimising policy shifts. This repository reproduces every
number and figure in the paper from scratch.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21728788.svg)](https://doi.org/10.5281/zenodo.21728788)

**Archived on Zenodo:** https://doi.org/10.5281/zenodo.21728788

Version 1.0.5 is the release accompanying the manuscript. Relative to 1.0.4 it
adds one printed sub-block, SS7, and fixes the layout of the five figures. Every
line printed by 1.0.4 is unchanged.

This is the concept DOI. It always resolves to the latest archived release, so it
does not need updating when a new version is deposited. Zenodo lists the DOI of
each individual version on that page.

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
| `model_decyzyjny_v4.py` | "decision model, v4" | **The model.** Run it to print all reported numbers: scenario optimality shares, Table 3 effect sizes, seed stability, the extreme-corner analysis, the log-uniform robustness check, the tau sensitivity, the EVPPI values, and the structural-sensitivity block (regret intervals, harm-scale weights, Weibull hazard, prosthetic multiplier, correlated crew events, provisional acceptability term). Writes no figures. |
| `ryzyko_populacyjne.py` | "population risk" | **Fig. S1** (supplement) — population risk `P(n) = 1 - (1 - p)^n` |
| `figura_urwana_miarka.py` | "truncated ruler figure" | **Fig. S2** (supplement) — mission duration vs the caries-development window |
| `figura_drzewo_decyzyjne.py` | "decision tree figure" | **Fig. 1** — decision structure of policies P1-P4 |
| `figura_mapa_margines.py` | "margin map figure" | **Fig. 2** — decision-margin map (imports the model) |
| `figura_przejscie_optimum.py` | "optimum transition figure" | **Fig. 3** — optimality share vs time to definitive care (imports the model) |

The remaining files are `README.md`, `CHANGELOG.md` (what changed in each release),
`CITATION.cff` (machine-readable citation metadata), `requirements.txt`, `LICENSE`
and `NOTICE`. Docstrings and comments inside the scripts are in English; only the
file names are Polish, and they are kept so that the citation trail to earlier
archived releases stays unbroken.

The output image files are also Polish-named:
`ryzyko_populacyjne` (Fig. S1), `figura_urwana_miarka` (Fig. S2),
`figura_drzewo_decyzyjne` (Fig. 1), `figura_mapa_progowa` (Fig. 2, "threshold map"),
`figura_przejscie_optimum` (Fig. 3).

Figures 2 and 3 read `model_decyzyjny_v4.py`, so keep all files in one folder.

## Reproduce

```bash
pip install -r requirements.txt   # tested with Python 3.12.3, numpy 2.4.4, matplotlib 3.10.8

python3 model_decyzyjny_v4.py          # prints every number in the paper
python3 ryzyko_populacyjne.py          # each figure script writes a PNG and a PDF
python3 figura_urwana_miarka.py
python3 figura_drzewo_decyzyjne.py
python3 figura_mapa_margines.py
python3 figura_przejscie_optimum.py
```

All random seeds are fixed in the code, so results are deterministic. The
uncertain quantities are drawn from author-specified triangular ranges used for
probabilistic sensitivity analysis (Table 1 in the paper), not empirical
estimates.

The printed numbers are identical under Python 3.12.3 with numpy 2.4.4 and under
Python 3.13.18 with numpy 2.5.3. The figures in the paper were drawn with
matplotlib 3.11.2. Under matplotlib 3.10.8 they show the same data and differ
only in rendering details, such as where contour labels sit.

All generated figures are in English.

## How to cite

If you use this code, please cite the paper (full reference to be added on
acceptance) and the archived code release:

```
Kasperek, M. M. Pre-flight odontogenic-risk decision model [software].
Zenodo. https://doi.org/10.5281/zenodo.21728788
```

## License

Released under the Apache License 2.0. See `LICENSE` and `NOTICE`.
