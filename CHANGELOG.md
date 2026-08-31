# Changelog

All notable changes to this repository. The base model, its equations and its
parameter ranges have not changed since 1.0.2, so every number printed by 1.0.2
is reproduced line for line by every later version.

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
