# -*- coding: utf-8 -*-
"""Figura 5. Udzial optymalnosci w losowaniach niepewnosci wobec czasu do leczenia definitywnego.
Cztery polityki P1-P4, autonomia c=0.25, zaloga 6 osob, misja 2.6 roku.
Importuje model_decyzyjny_v4.py. Tworzy figura_przejscie_optimum.png oraz .pdf."""
import numpy as np, matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
src=open("model_decyzyjny_v4.py").read().split("def validate")[0]
ns={}; exec(src,ns)
sample=ns["sample"]; EH=ns["EH"]; POL=ns["POL"]; NAME=ns["NAME"]
GREY=["0.93","0.72","0.50","0.20"]
ts=np.linspace(0,600,25); p=sample(9000,5); share=np.zeros((len(ts),4))
for j,t in enumerate(ts):
    w=np.argmin(np.stack([EH(s,p,0.25,t,6,2.6) for s in range(4)]),0)
    share[j]=[np.mean(w==s) for s in range(4)]
fig,ax=plt.subplots(figsize=(7.0,3.9)); bottom=np.zeros(len(ts))
for s in range(4):
    ax.fill_between(ts,bottom,bottom+share[:,s],facecolor=GREY[s],edgecolor="white",linewidth=0.3,label=NAME[POL[s]]); bottom+=share[:,s]
for xr,lab in [(30,"30 d"),(180,"180 d")]:
    ax.axvline(xr,color="0.4",ls=":",lw=0.9); ax.annotate(lab,(xr,0.5),fontsize=8,ha="center",color="0.25",rotation=90,va="center")
ax.annotate("P4 < 1%",(520,0.985),fontsize=8,color="0.2",ha="center",arrowprops=dict(arrowstyle="->",color="0.4",lw=0.8),xytext=(520,0.9))
ax.set_xlim(0,600); ax.set_ylim(0,1)
ax.set_xlabel("Time to definitive care (days)")
ax.set_ylabel("Share of uncertainty draws in which policy is optimal")
ax.legend(loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False,fontsize=9)
fig.tight_layout()
fig.savefig("figura_przejscie_optimum.png",dpi=170,bbox_inches="tight")
fig.savefig("figura_przejscie_optimum.pdf",bbox_inches="tight")
if __name__=="__main__": print("Fig 5 zapisana z v4")
