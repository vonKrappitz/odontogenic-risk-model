# -*- coding: utf-8 -*-
"""
Model v3. Poprawki po recenzji 10.
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

# ---------- TAU sensitivity (Mars) ----------
print("\n=== WRAZLIWOSC TAU, Mars, share ===")
for tauv in [7,30,90]:
    p=sample(100000,0); p["tau"]=np.full(100000,float(tauv))
    EHs=np.stack([EH(s,p,0.2,400,6,2.6) for s in range(4)]); w=EHs.argmin(0)
    print("  tau=%2d: "%tauv+" ".join("%s=%4.1f%%"%(POL[i],np.mean(w==i)*100) for i in range(4)))

# ---------- EVPPI (Mars, single-loop stratified) ----------
def evppi(c=0.2,t=400,n=6,T=2.6,N=120000,K=40,seed=7):
    p=sample(N,seed); p["tau"]=np.full(N,30.0)
    EHs=np.stack([EH(s,p,c,t,n,T) for s in range(4)]); base=EHs.mean(1).min(); out={}
    for k in RANGES:
        x=p[k]; order=np.argsort(x); bs=N//K; inner=0.0
        for b in range(K):
            idx=order[b*bs:(b+1)*bs] if b<K-1 else order[b*bs:]
            inner+=EHs[:,idx].mean(1).min()*len(idx)
        out[k]=base-inner/N
    return out
print("\n=== EVPPI (mission-impact units), 5 najwyzszych ===")
for k,v in sorted(evppi().items(),key=lambda x:-x[1])[:5]:
    print("  %-10s %.4f"%(k,v))
print("\nUWAGA: figury generuja osobne skrypty (figura_*.py). Ten plik liczy tylko liczby.")
