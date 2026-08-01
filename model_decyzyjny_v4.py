# -*- coding: utf-8 -*-
"""
Model v3. Poprawki po recenzji 10.
- Cztery KONKURUJACE polityki interwencji przedlotowej, P1 retencja, P2 selektywna ekstrakcja,
  P3 tooth-preserving comprehensive sanation, P4 full dental clearance.
- Autonomia pokladowa c jest PARAMETREM (0..1), nie polityka.
- Rozklady trojkatne = elicited uncertainty distributions for probabilistic sensitivity analysis.
- Jawne rownania zaleznosci (ponizej).
- Raport WIELKOSCI EFEKTU, srednia EH, przedzial 5-95, dEH vs best, oczekiwany zal (regret), optimality share.
- Rozdzielone dwa kryteria, min sredniej (mapa) kontra optimality share (wykres warstwowy).
- Odpornosc na logarytmiczny rozklad lambda.
- Figury po angielsku, dyskretna legenda, os misji rocznej ucieta do 365 dni.

RÓWNANIA (wszystkie jawne):
  P(E|P1) = 1 - exp(-lambda*T)                          zdarzenie, retencja, model wykladniczy w czasie
  P(E|P2) = P(E|P1)*(1 - r_sel)                          selektywna ekstrakcja usuwa udzial r_sel
  P(E|P3) = P(E|P1)*(1 - r_comp)                         sanacja z zachowaniem zebow, redukcja r_comp
  P(E|P4) = pE_pros                                      rezydualne zdarzenie protetyczne po bezzebiu
  rescue(t) = t/(t+30)                                   rosnie ku 1 z czasem do leczenia, t_half=30 d
  P(F|E,P1..P3) = clip( pf0*(1 - c*k_cap)*rescue(t), 0,1)  niepowodzenie leczenia, malejace z autonomia c
  P(F|E,P4)     = clip( pf_pros*rescue(t), 0,1)          zdarzenia protetyczne w wiekszosci obsluzalne
  L(E,F) = 1.0 * (1 + 2/n)                               strata przy niepowodzeniu, wieksza w malej zalodze
  EH(P) = n*[P(E)P(F)L(E,F) + P(E)(1-P(F))L_S] + n*Cperson(P) + Cfixed(P)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

POL = ["P1","P2","P3","P4"]
NAME = {"P1":"P1 Retention","P2":"P2 Selective extraction",
        "P3":"P3 Tooth-preserving sanation","P4":"P4 Full dental clearance"}
NP = 4
RANGES = {
 "lambda_yr":(0.01,0.03,0.10),"r_sel":(0.30,0.50,0.70),"r_comp":(0.20,0.40,0.60),
 "pE_pros":(0.005,0.02,0.05),"pf0":(0.30,0.55,0.80),"k_cap":(0.40,0.65,0.85),
 "pf_pros":(0.05,0.15,0.30),"L_S":(0.02,0.05,0.10),
 "tau":(7.0,30.0,90.0),"lam_pros":(0.002,0.008,0.02),
 "Cp_P1":(0.000,0.005,0.02),"Cp_P2":(0.02,0.04,0.08),"Cp_P3":(0.01,0.025,0.05),
 "Cp_P4":(0.08,0.14,0.24),"Cf_P4":(0.02,0.05,0.10),
}
def sample(N,seed,lam_log=False):
    rng=np.random.default_rng(seed)
    d={k:rng.triangular(*RANGES[k],N) for k in RANGES}
    if lam_log:  # odpornosc, logarytmiczny rozklad lambda na [0.01,0.10]
        d["lambda_yr"]=np.exp(rng.uniform(np.log(0.01),np.log(0.10),N))
    return d
def pE(s,p,T):
    base=1-np.exp(-p["lambda_yr"]*T)
    return [base,base*(1-p["r_sel"]),base*(1-p["r_comp"]),1-np.exp(-p["lam_pros"]*T)][s]
def pF(s,p,c,t):
    rf=t/(t+p["tau"])
    if s==3: return np.clip(p["pf_pros"]*rf,0,1)
    return np.clip(p["pf0"]*(1-c*p["k_cap"])*rf,0,1)
def crit(n): return 1.0+2.0/n
def Cp(s,p): return [p["Cp_P1"],p["Cp_P2"],p["Cp_P3"],p["Cp_P4"]][s]
def Cf(s,p): return [0.0,0.0,0.0,p["Cf_P4"]][s]
def EH(s,p,c,t,n,T):
    e=pE(s,p,T); f=pF(s,p,c,t)
    return n*(e*f*crit(n)+e*(1-f)*p["L_S"])+n*Cp(s,p)+Cf(s,p)

def validate():
    p=sample(20000,1); ok=True
    for s in range(NP):
        if np.any((pE(s,p,2.6)<0)|(pE(s,p,2.6)>1)): ok=False
        if np.any((pF(s,p,0.3,400)<0)|(pF(s,p,0.3,400)>1)): ok=False
    print("WALIDACJA v3:", "OK" if ok else "BLAD")
validate()

# ---------- TABELA WIELKOSCI EFEKTU ----------
def effect(name,c,t,n,T,N=100000,seed=0,lam_log=False):
    p=sample(N,seed,lam_log)
    EHs=np.stack([EH(s,p,c,t,n,T) for s in range(NP)])
    mean=EHs.mean(1); lo=np.percentile(EHs,5,1); hi=np.percentile(EHs,95,1)
    best=mean.min(); rowmin=EHs.min(0); regret=(EHs-rowmin).mean(1)
    win=EHs.argmin(0); share=np.array([np.mean(win==s) for s in range(NP)])
    print(f"\n=== {name} ===  best-mean: {POL[int(mean.argmin())]}")
    print(f"  pol  meanEH   [5-95]           dEHvsBest  regret  share%")
    for s in range(NP):
        print(f"  {POL[s]}  {mean[s]:6.3f}  [{lo[s]:5.3f}-{hi[s]:5.3f}]   {mean[s]-best:8.3f}  {regret[s]:6.3f}  {share[s]*100:5.1f}")
    return mean,lo,hi,regret,share

effect("LEO short, high capability (c=0.6, t=12 d, n=6, T=0.5 yr)",0.6,12,6,0.5)
effect("Moon medium (c=0.4, t=90 d, n=6, T=1.0 yr)",0.4,90,6,1.0)
effect("Mars, no rescue, low capability (c=0.2, t=400 d, n=6, T=2.6 yr)",0.2,400,6,2.6)
print("\n--- ODPORNOSC, Mars z logarytmicznym rozkladem lambda ---")
effect("Mars, log-uniform lambda",0.2,400,6,2.6,lam_log=True)

# ---------- FIG 4, mapa min sredniej, dyskretna legenda, os roczna ucieta ----------
GREY=["0.93","0.72","0.50","0.20"]
def tmap(n,T,tmax,N=6000,grid=60,seed=3):
    cs=np.linspace(0,1,grid); ts=np.linspace(0,tmax,grid); M=np.zeros((grid,grid),int)
    p=sample(N,seed)
    for i,c in enumerate(cs):
        for j,t in enumerate(ts):
            M[i,j]=int(np.argmin([EH(s,p,c,t,n,T).mean() for s in range(NP)]))
    return ts,cs,M
from matplotlib.colors import ListedColormap,BoundaryNorm
cmap=ListedColormap(GREY); norm=BoundaryNorm([-.5,.5,1.5,2.5,3.5],cmap.N)
fig,axes=plt.subplots(1,3,figsize=(15,4.7))
panels=[(6,2.6,500,"Crew 6, 2.6-year mission"),(4,2.6,500,"Crew 4, 2.6-year mission"),(6,1.0,365,"Crew 6, 1-year mission")]
for ax,(n,T,tmax,tt) in zip(axes,panels):
    ts,cs,M=tmap(n,T,tmax); ax.pcolormesh(ts,cs,M,cmap=cmap,norm=norm,shading="auto")
    ax.set_xlabel("Time to definitive care (days)"); ax.set_ylabel("Onboard capability c (0 to 1)")
    ax.set_title(tt,fontsize=10); ax.set_xlim(0,tmax)
    if T>2:
        ax.plot(400,0.2,"o",ms=9,mfc="none",mec="white",mew=1.8)
        ax.annotate("Mars",(400,0.2),color="white",fontsize=8,ha="center",xytext=(400,0.27))
    print(f"  Fig4 [{tt}] policies:",[POL[k] for k in sorted(set(M.flatten()))])
axes[-1].legend(handles=[Patch(facecolor=GREY[i],edgecolor="black",label=NAME[POL[i]]) for i in range(NP)],
                loc="center left",bbox_to_anchor=(1.02,0.5),frameon=False,fontsize=8.5)
fig.suptitle("Lowest-mean-expected-harm policy across the decision space",fontsize=12)
fig.text(0.5,-0.02,"Grid 60 x 60. Cell colour is the policy with the lowest MEAN expected mission harm (not optimality share).",ha="center",fontsize=8)
fig.savefig("figura_mapa_progowa.png",dpi=170,bbox_inches="tight")

# ---------- FIG 5, optimality share, oczyszczony ----------
ts=np.linspace(0,600,25); p=sample(9000,5)
share=np.zeros((len(ts),NP))
for j,t in enumerate(ts):
    w=np.argmin(np.stack([EH(s,p,0.25,t,6,2.6) for s in range(NP)]),0)
    share[j]=[np.mean(w==s) for s in range(NP)]
fig,ax=plt.subplots(figsize=(9,4.9)); bottom=np.zeros(len(ts))
for s in range(NP):
    ax.fill_between(ts,bottom,bottom+share[:,s],facecolor=GREY[s],edgecolor="white",linewidth=0.3,label=NAME[POL[s]]); bottom+=share[:,s]
for xr,lab in [(30,"30 d"),(180,"180 d")]:
    ax.axvline(xr,color="0.4",ls=":",lw=0.9); ax.annotate(lab,(xr,0.5),fontsize=8,ha="center",color="0.25",rotation=90,va="center")
ax.annotate("P4 < 1%",(520,0.985),fontsize=8,color="0.2",ha="center",
            arrowprops=dict(arrowstyle="->",color="0.4",lw=0.8),xytext=(520,0.9))
ax.set_xlim(0,600); ax.set_ylim(0,1)
ax.set_xlabel("Time to definitive care (days)")
ax.set_ylabel("Share of uncertainty draws in which policy is optimal")
ax.set_title("Optimality share across uncertainty draws as time to definitive care increases",fontsize=10)
ax.legend(loc="center left",bbox_to_anchor=(1.01,0.5),frameon=False,fontsize=9)
fig.tight_layout()
fig.savefig("figura_przejscie_optimum.png",dpi=170,bbox_inches="tight")
print("\nZapisano figury 4 i 5 (v3, P1-P4, dyskretna legenda).")

# ---------- KONTROLA, pelne mozliwosci ziemskie (przywolana w Sekcji 6) ----------
# Model ogranicza k_cap do 0.85, co odpowiada tranzytowi i wczesnej bazie.
# Ta kontrola zdejmuje ograniczenie: c=1 i k_cap=1 oznaczaja centrum medyczne
# zdolne wykonac to samo co klinika na Ziemi. P(F|E) spada wtedy do zera.
print("\n=== KONTROLA, capability equivalent to terrestrial care ===")
_q = sample(100000, 0)
_q["k_cap"] = np.ones(100000)
print("  P(F|E) przy c=1, k_cap=1: %.6f" % pF(0, _q, 1.0, 400).mean())
for _T in [2.6, 10.0, 20.0]:
    _E = np.stack([EH(s, _q, 1.0, 400, 6, _T) for s in range(4)])
    _m = _E.mean(1)
    print("  T=%4.1f lat: " % _T + " ".join("%s=%.3f" % (POL[i], _m[i]) for i in range(4))
          + "  -> %s" % POL[int(_m.argmin())])
