# Changelog

All notable changes to this repository. The base model, its equations and its
parameter ranges have not changed since 1.0.2, so every number printed by 1.0.2
is reproduced line for line by every later version.

## 1.0.5

One printed sub-block added to the model and the layout of the five figures
fixed. The 165 lines printed by 1.0.4 are reproduced byte for byte, and the new
lines follow them. Each figure script prints the same numbers as in 1.0.4.

### Added

- SS7 event rate fixed at published values: the Mars scenario with the event rate
  set to the submarine prior, the in-flight posterior and the pre-flight astronaut
  rate of NASA/TP-2012-217120, to the Integrated Medical Model incidences quoted
  in NASA/TM-2012-217368, and to the 95 percent upper bound implied by no event in
  31.9 person-years of flight. Followed by the event rate at which sanation
  overtakes retention at the Mars point, and the share of each stated range that
  lies above it. Then the Mars result and the value of information on the event
  rate under two log-uniform ranges bracketed by the published values, from the
  submarine prior and from the in-flight posterior mean up to the flight-record
  bound.
  Last, a pre-positioned surface facility: the Mars point with the time to
  definitive care set to 270 days, about a minimum-energy transfer with margin,
  once with the exposure of the Mars point and once with exposure without care
  only on two 270-day transits, and the exposure at which sanation overtakes
  retention at that time to care.
  Then minor incidents outside the event rate: exposed pulp at the Integrated
  Medical Model incidence of 0.0201 per person-year, counted at the loss of a
  managed incident, as traumatic (equal under retention, selective extraction
  and sanation) or carious (reduced like severe events), with a share from 0 to
  0.5 escalating later to an abscess. The base model is not changed by it.
  Last, the residual severe-event hazard after full dental clearance set to
  zero.

### Changed

- Comments and the docstring now call lam_pros and pf_pros the residual hazard
  after clearance instead of a prosthetic hazard. Denture problems are treated
  in the paper as minor incidents whose burden sits in the clearance costs.
  Printed labels are unchanged, so the lines printed by 1.0.4 stay identical.
- Figure numbers follow the paper as restructured for Reliability Engineering &
  System Safety. The decision structure, the margin map and the optimum
  transition are now Figs. 1, 2 and 3. The population-risk and truncated-ruler
  figures moved to the supplementary material as Figs. S1 and S2. Docstrings,
  one comment and the README follow the new numbers, and no image or printed
  number changed. The README now cites Table 1 for the parameter ranges and
  Table 3 for the effect sizes, and no longer says that the code comments are
  in Polish, which they are not.
- The README and requirements.txt name the environment in which the figures of the
  paper were drawn (Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2). The printed
  numbers are identical under the earlier tested environment.

### Fixed

- All five figure scripts now set the font to DejaVu Sans, which ships with
  matplotlib. Before, the layout depended on the default font of the machine.
- Fig. S1 (population risk): the 50 and 90 percent reference labels moved to the right end of
  their lines, clear of the curves.
- Fig. S2 (truncated ruler): the vertical range extended so that the two-line window label is no
  longer cut by the top frame.
- Fig. 1 (decision structure): the P4 box widened so that its text is no longer clipped. The labels
  "low c", "low risk" and "high risk" moved off the box edges.
- Fig. 2 (margin map): the three panels share one y axis, labelled once, under a constrained
  layout. The y label no longer runs into the neighbouring panel.
- Fig. 3 (optimum transition): the y label set on two lines. The "30 d" and "180 d" labels moved
  beside their reference lines.

### Notes

- The figures of this release were rendered with Python 3.13.18, numpy 2.5.3 and
  matplotlib 3.11.2. The first 165 lines printed by the model were checked
  against the 1.0.4 printout in that environment and are identical.

## 1.0.4

### Added

- Structural sensitivity block, printed after the base results, with six
  sub-blocks addressing assumptions raised in external peer review.
  - SS1 regret intervals: the 5 to 95 percent range across draws for each
    policy, and the Monte Carlo standard error of every mean regret over ten
    seeds.
  - SS2 harm-scale weights: sweeps of the loss on a managed event, the crew-size
    weight and the whole-life harm of edentulism, singly and as two-way grids,
    with the threshold at which the ranking changes.
  - SS3 Weibull hazard `H(T) = lambda*T0*(T/T0)^k` with `T0 = 1 year`, for shape
    parameters 0.7 to 2.0, applied to the dental hazard alone and to the dental
    and prosthetic hazards together.
  - SS4 microgravity multiplier on the prosthetic hazards.
  - SS5 correlated crew events: a shared frailty on the event rate and a cascade
    penalty for two unmanaged events at once.
  - SS6 a provisional acceptability term, author-specified and awaiting
    elicitation, with the replacement cost at which the ranking would change.

### Changed

- Docstrings and comments in all six scripts translated from Polish to English.
  No statement was changed. The abstract syntax tree outside docstrings is
  identical to 1.0.3, and the printed output is byte-identical.
- The paper title in the README and in the model docstring updated to the
  current manuscript title.
- The tested environment recorded in the README and in requirements.txt:
  Python 3.12.3, numpy 2.4.4, matplotlib 3.10.8.

### Notes

- The parameter `pE_pros` is used by no equation. It is kept in the range
  dictionary only so that the stream of random numbers stays identical to
  1.0.2. Removing it would shift every reported number by Monte Carlo noise.
- There was no public 1.0.3. Its two blocks are included here.

## 1.0.3 (not released publicly)

### Added

- Seed stability block. Runs the model at five independent seeds for the three
  scenarios and prints the largest spread of optimality shares together with the
  Monte Carlo standard error.
- Extreme corner block. Computes the mean harm and the optimality share of full
  dental clearance in the deepest corner of the Fig. 4 domain, at zero onboard
  capability and five hundred days to definitive care, for successive values of
  the harm of edentulism, and reports the threshold at which clearance becomes
  the lowest-mean-harm policy.

### Why

A reproducibility test showed that two paragraphs of the results section rested
on numbers the code did not print. These blocks make one execution print them.

## 1.0.2 and earlier

Initial public releases of the decision model, the population-risk script and
the four figure scripts.
