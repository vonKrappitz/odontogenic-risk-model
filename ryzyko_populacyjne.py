# -*- coding: utf-8 -*-
"""
Ryzyko populacyjne zdarzenia stomatologicznego w misji.
Wzor. P(co najmniej jedno) = 1 - (1 - p)^n
p, ryzyko powaznego zdarzenia na osobe w czasie misji.
n, liczba osob w zalodze lub bazie.
Zalozenia. Zdarzenia niezalezne i jednakowe p dla kazdej osoby. To uproszczenie.
Tworzy ryzyko_populacyjne.png oraz .pdf w skali szarosci i wypisuje progi.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt

# globalny dostep do fig, ax zgodnie z regula projektu
fig = None
ax = None

def P_co_najmniej_jeden(p, n):
    return 1.0 - (1.0 - p) ** n

def n_do_progu(p, cel):
    # najmniejsze n takie ze P >= cel, wzor n = ln(1-cel)/ln(1-p)
    import math
    return math.ceil(math.log(1.0 - cel) / math.log(1.0 - p))

def rysuj():
    global fig, ax
    poziomy = [0.01, 0.05, 0.10, 0.20]           # ryzyko na osobe
    style = ["-", "--", "-.", ":"]
    grubosc = [1.6, 1.6, 1.8, 2.0]
    n = np.arange(1, 101)

    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    for p, s, g in zip(poziomy, style, grubosc):
        y = P_co_najmniej_jeden(p, n) * 100.0
        ax.plot(n, y, color="black", linestyle=s, linewidth=g,
                label=f"per-person risk p = {int(p*100)}%")

    # linie odniesienia 50, 90, 99 procent
    for prog in [50, 90, 99]:
        ax.axhline(prog, color="0.6", linestyle=(0, (1, 3)), linewidth=0.8)
        ax.text(1.5, prog + 0.8, f"{prog}%", color="0.4", fontsize=8, va="bottom")

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
