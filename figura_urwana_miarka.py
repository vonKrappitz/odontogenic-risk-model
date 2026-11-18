# -*- coding: utf-8 -*-
"""
Figure S2 (supplementary material). The truncated ruler, mission duration against the window in which caries develops.
Shows that the longest flights on the ISS (374 days) and on Mir (437 days) end before the window opens,
while a Mars mission of 2.6 years, the duration used in the model, enters it. Since 1.0.6.
Writes figura_urwana_miarka.png and .pdf.
"""
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
matplotlib.rcParams['font.family']='DejaVu Sans'   # bundled with matplotlib, so the layout does not depend on the machine
import matplotlib.pyplot as plt

fig = None
ax = None

def rysuj():
    global fig, ax
    fig, ax = plt.subplots(figsize=(7.4, 3.6))

    # window for caries in an adult, 3 to 6 years, from 2 at high risk
    ax.axvspan(2, 6, color="0.82", zorder=0)
    ax.axvline(2, color="0.45", linestyle=(0, (4, 3)), linewidth=1.0, zorder=1)
    ax.text(4.0, 3.05, "adult caries-development window\n3 to 6 years, from 2 years at high risk",
            ha="center", va="bottom", fontsize=8.5, color="0.25")

    # mission duration bars
    misje = [("ISS record", 1.02, "0.55"), ("Mir record", 1.2, "0.4"), ("Mars mission", 2.6, "0.25")]
    y = [0, 1, 2]
    for (nazwa, dlug, kolor), yy in zip(misje, y):
        ax.barh(yy, dlug, height=0.5, color=kolor, edgecolor="black", zorder=3)
        ax.text(dlug + 0.08, yy, f"{dlug:g} years",
                va="center", ha="left", fontsize=9)

    # arrow, spaceflight factors shift the window to the left
    ax.annotate("", xy=(2.05, 2.75), xytext=(3.6, 2.75),
                arrowprops=dict(arrowstyle="->", color="0.2", linewidth=1.4))
    ax.text(3.65, 2.75, "space factors\nshift the window left",
            va="center", ha="left", fontsize=8, color="0.2")

    ax.set_yticks(y)
    ax.set_yticklabels([m[0] for m in misje], fontsize=9)
    ax.set_xlabel("Time since launch (years)")
    ax.set_xlim(0, 6.6)
    ax.set_ylim(-0.6, 3.9)   # room for the two-line window label
    ax.set_axisbelow(True)
    ax.grid(True, axis="x", color="0.9", linewidth=0.6)

    fig.tight_layout()
    fig.savefig("figura_urwana_miarka.png", dpi=200)
    fig.savefig("figura_urwana_miarka.pdf")

if __name__ == "__main__":
    rysuj()
    print("Zapisano figure urwanej miarki.")
    print("Kontrola. Rekord ISS 1.02 (374 dni) i rekord Mir 1.2 (437 dni) koncza sie przed oknem prochnicy od 2 lat.")
    print("Mars konczy sie na 2.6, wchodzi w okno 2 do 6, a strzalka przesuwa je w lewo.")
