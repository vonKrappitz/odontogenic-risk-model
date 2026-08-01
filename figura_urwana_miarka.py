# -*- coding: utf-8 -*-
"""
Figura 2. Urwana miarka, czas trwania misji wobec okna rozwoju prochnicy.
Pokazuje, ze ISS konczy sie zanim okno prochnicy sie zaczyna, a Mars w nie wchodzi.
Tworzy figura_urwana_miarka.png oraz .pdf.
"""
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt

fig = None
ax = None

def rysuj():
    global fig, ax
    fig, ax = plt.subplots(figsize=(7.4, 3.6))

    # okno rozwoju prochnicy u doroslego, 3 do 6 lat, od 2 przy wysokim ryzyku
    ax.axvspan(2, 6, color="0.82", zorder=0)
    ax.axvline(2, color="0.45", linestyle=(0, (4, 3)), linewidth=1.0, zorder=1)
    ax.text(4.0, 3.05, "adult caries-development window\n3 to 6 years, from 2 years at high risk",
            ha="center", va="bottom", fontsize=8.5, color="0.25")

    # slupki czasu misji
    misje = [("ISS", 1.2, "0.55"), ("Moon\nshort missions", 0.4, "0.4"), ("Mars", 2.7, "0.25")]
    y = [0, 1, 2]
    for (nazwa, dlug, kolor), yy in zip(misje, y):
        ax.barh(yy, dlug, height=0.5, color=kolor, edgecolor="black", zorder=3)
        ax.text(dlug + 0.08, yy, f"{dlug:g} years",
                va="center", ha="left", fontsize=9)

    # strzalka, czynniki kosmiczne przesuwaja okno w lewo
    ax.annotate("", xy=(2.05, 2.75), xytext=(3.6, 2.75),
                arrowprops=dict(arrowstyle="->", color="0.2", linewidth=1.4))
    ax.text(3.65, 2.75, "space factors\nshift the window left",
            va="center", ha="left", fontsize=8, color="0.2")

    ax.set_yticks(y)
    ax.set_yticklabels([m[0] for m in misje], fontsize=9)
    ax.set_xlabel("Time since launch (years)")
    ax.set_xlim(0, 6.6)
    ax.set_ylim(-0.6, 3.4)
    ax.set_axisbelow(True)
    ax.grid(True, axis="x", color="0.9", linewidth=0.6)

    fig.tight_layout()
    fig.savefig("figura_urwana_miarka.png", dpi=200)
    fig.savefig("figura_urwana_miarka.pdf")

if __name__ == "__main__":
    rysuj()
    print("Zapisano figure urwanej miarki.")
    print("Kontrola. ISS konczy sie na 1.2, okno prochnicy zaczyna od 2, wiec ISS nie dociera do okna.")
    print("Mars konczy sie na 2.7, wchodzi w okno 2 do 6, a strzalka przesuwa je w lewo.")
