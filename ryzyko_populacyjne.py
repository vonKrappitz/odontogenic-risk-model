# -*- coding: utf-8 -*-
"""
Figure S1 (supplementary material). Population risk of a dental event during a mission.
Formula. P(at least one) = 1 - (1 - p)^n
p, the risk of a severe event per person over the mission.
n, the number of people in the crew or base.
Assumptions. Events independent and p equal for every person. This is a simplification.
Writes ryzyko_populacyjne.png and .pdf and prints the thresholds.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
matplotlib.rcParams['font.family']='DejaVu Sans'   # bundled with matplotlib, so the layout does not depend on the machine
import matplotlib.pyplot as plt

fig = None
ax = None

def P_co_najmniej_jeden(p, n):
    return 1.0 - (1.0 - p) ** n

def n_do_progu(p, cel):
    # smallest n such that P >= target, n = ln(1-target)/ln(1-p)
    import math
    return math.ceil(math.log(1.0 - cel) / math.log(1.0 - p))

def rysuj():
    global fig, ax
    poziomy = [0.01, 0.05, 0.10, 0.20]           # risk per person
    style = ["-", "--", "-.", ":"]
    grubosc = [1.6, 1.6, 1.8, 2.0]
    n = np.arange(1, 101)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    for p, s, g in zip(poziomy, style, grubosc):
        y = P_co_najmniej_jeden(p, n) * 100.0
        ax.plot(n, y, color="black", linestyle=s, linewidth=g,
                label=f"per-person risk p = {int(p*100)}%")

    # reference lines at 50, 90 and 99 percent
    for prog in [50, 90, 99]:
        ax.axhline(prog, color="0.6", linestyle=(0, (1, 3)), linewidth=0.8)
        # 50 and 90 sit at the right end, clear of the curves; 99 stays left, above the frame
        if prog == 99:
            ax.text(1.5, prog + 0.8, f"{prog}%", color="0.4", fontsize=8, va="bottom")
        else:
            ax.text(99, prog + 0.8, f"{prog}%", color="0.4", fontsize=8, va="bottom", ha="right")

    ax.set_xlim(1, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Crew or base population (n)")
    ax.set_ylabel("Probability of at least one event (%)")
    ax.grid(True, color="0.9", linewidth=0.6)
    ax.legend(loc="lower right", framealpha=1.0, edgecolor="0.7", fontsize=9)

    fig.tight_layout()
    fig.savefig("ryzyko_populacyjne.png", dpi=200)
    fig.savefig("ryzyko_populacyjne.pdf")

if __name__ == "__main__":
    rysuj()
    print("Progi, ile osob potrzeba by ryzyko grupowe osiagnelo dany poziom")
    print("p na osobe | do 50% | do 90% | do 99%")
    for p in [0.01, 0.05, 0.10, 0.20]:
        print(f"   {int(p*100):>3d}%    |  {n_do_progu(p,0.5):>4d}  |  {n_do_progu(p,0.9):>4d}  |  {n_do_progu(p,0.99):>4d}")
    print()
    print("Kontrola, wartosci P dla wybranych par (p, n)")
    for p in [0.01, 0.05, 0.10]:
        for nn in [6, 20, 80]:
            print(f"   p={int(p*100):>2d}%, n={nn:>3d} -> P = {P_co_najmniej_jeden(p, nn)*100:5.1f}%")
