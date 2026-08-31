# -*- coding: utf-8 -*-
"""
Version 1.0.4. Relative to 1.0.3 this adds ONE printed block, STRUCTURAL SENSITIVITY,
with six sub-blocks (regret intervals, harm-scale weight sweeps, Weibull hazard,
prosthetic multiplier, correlated crew events, provisional acceptability term).
The base model, its equations and its parameters are UNCHANGED, so every number
from 1.0.2 and 1.0.3 reproduces digit for digit. New results are appended below them.
Decision-analytic Monte Carlo model. Compares ways of reducing odontogenic risk before flight.
Code accompanying the paper "Odontogenic risk as an unserviceable failure mode in Mars missions:
a decision-theoretic reliability analysis".

Four mutually exclusive pre-flight policies. Onboard capability c is a PARAMETER, not a policy.
  P1 retention, P2 selective extraction, P3 tooth-preserving comprehensive sanation,
  P4 full dental clearance.

Triangular ranges stated by the author, for the purpose of sensitivity analysis.
They are not distributions estimated from data, nor Bayesian priors.

EQUATIONS (all explicit):
  P(E|P1) = 1 - exp(-lambda*T)                 severe event, retention, exponential hazard
  P(E|P2) = P(E|P1)*(1 - r_sel)                selective extraction
  P(E|P3) = P(E|P1)*(1 - r_comp)               tooth-preserving sanation
  P(E|P4) = 1 - exp(-lam_pros*T)               residual prosthetic hazard after clearance
  rescue(t) = t/(t + tau)                      rises towards 1, tau is the half-saturation time
  P(F|E,P1..P3) = clip(pf0*(1 - c*k_cap)*rescue(t), 0, 1)
  P(F|E,P4)     = clip(pf_pros*rescue(t), 0, 1)
  L(E,F) = 1.0*(1 + 2/n)                       loss on failure, larger in a smaller crew
  EH(P)  = n*[P(E)*P(F)*L(E,F) + P(E)*(1-P(F))*L_S] + n*Cperson(P) + Cfixed(P)

Running the script prints every number reported in the paper. How often each policy is
optimal in each scenario, the effect sizes of the effect-size table, the robustness check
under a log-uniform event rate, the sensitivity to tau, the EVPPI values, and the control
run at full terrestrial treatment capability.

It draws no figures. That is done by the separate scripts figura_*.py and ryzyko_populacyjne.py.
"""
import numpy as np

POL = ["P1","P2","P3","P4"]
NAME = {"P1":"P1 Retention","P2":"P2 Selective extraction",
        "P3":"P3 Tooth-preserving sanation","P4":"P4 Full dental clearance"}
NP = 4
RANGES = {
 "lambda_yr":(0.01,0.03,0.10),"r_sel":(0.30,0.50,0.70),"r_comp":(0.20,0.40,0.60),
 "pE_pros":(0.005,0.02,0.05),  # UNUSED by any equation; kept so the random stream of 1.0.2 is preserved
 "pf0":(0.30,0.55,0.80),"k_cap":(0.40,0.65,0.85),
 "pf_pros":(0.05,0.15,0.30),"L_S":(0.02,0.05,0.10),
 "tau":(7.0,30.0,90.0),"lam_pros":(0.002,0.008,0.02),
 "Cp_P1":(0.000,0.005,0.02),"Cp_P2":(0.02,0.04,0.08),"Cp_P3":(0.01,0.025,0.05),
 "Cp_P4":(0.08,0.14,0.24),"Cf_P4":(0.02,0.05,0.10),
}
def sample(N,seed,lam_log=False):
    rng=np.random.default_rng(seed)
    d={k:rng.triangular(*RANGES[k],N) for k in RANGES}
    if lam_log:  # robustness, log-uniform lambda on [0.01,0.10]
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
    print("WALIDACJA:", "OK" if ok else "BLAD")
validate()

# ---------- EFFECT SIZES, the three scenarios of the effect-size table ----------
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

# ---------- SENSITIVITY TO TAU, Mars scenario ----------
print("\n=== TAU SENSITIVITY, Mars, share ===")
for tauv in [7, 30, 90]:
    _p = sample(100000, 0); _p["tau"] = np.full(100000, float(tauv))
    _w = np.stack([EH(s, _p, 0.2, 400, 6, 2.6) for s in range(4)]).argmin(0)
    print("  tau=%2d: " % tauv + " ".join("%s=%4.1f%%" % (POL[i], np.mean(_w == i) * 100) for i in range(4)))

# ---------- EVPPI, Mars scenario, single-loop stratified method ----------
def evppi(c=0.2, t=400, n=6, T=2.6, N=120000, K=40, seed=7):
    p = sample(N, seed); p["tau"] = np.full(N, 30.0)
    EHs = np.stack([EH(s, p, c, t, n, T) for s in range(4)])
    base = EHs.mean(1).min(); out = {}
    for k in RANGES:
        x = p[k]; order = np.argsort(x); bs = N // K; inner = 0.0
        for b in range(K):
            idx = order[b*bs:(b+1)*bs] if b < K-1 else order[b*bs:]
            inner += EHs[:, idx].mean(1).min() * len(idx)
        out[k] = base - inner / N
    return out
print("\n=== EVPPI (mission-impact units), top 5 ===")
for k, v in sorted(evppi().items(), key=lambda x: -x[1])[:5]:
    print("  %-10s %.4f" % (k, v))

# ---------- SEED STABILITY, quoted in Section 6 ----------
print("\n=== SEED STABILITY, five independent seeds ===")
_worst = 0.0
for _nm, _c, _t, _n, _T in [("LEO", 0.6, 12, 6, 0.5), ("Moon", 0.4, 90, 6, 1.0), ("Mars", 0.2, 400, 6, 2.6)]:
    _sh = []
    for _s in range(5):
        _p = sample(100000, _s)
        _E = np.stack([EH(k, _p, _c, _t, _n, _T) for k in range(4)])
        _sh.append([np.mean(_E.argmin(0) == k) * 100 for k in range(4)])
    _sh = np.array(_sh)
    _r = (_sh.max(0) - _sh.min(0)).max()
    _worst = max(_worst, _r)
    print("  %-5s largest spread across seeds: %.3f pp" % (_nm, _r))
print("  largest spread overall: %.3f pp" % _worst)
print("  Monte Carlo standard error at share 0.52, N=100000: %.3f pp"
      % (np.sqrt(0.52 * 0.48 / 100000) * 100))

# ---------- EXTREME CORNER, quoted in Section 6 ----------
# Corner of the Fig. 4 domain: zero capability, 500 days to care, crew of 6, mission of 2.6 years.
# Cp_P4 FIXED at successive values, all remaining uncertainty retained.
print("\n=== EXTREME CORNER, c=0, t=500 d, n=6, T=2.6 yr ===")
_C, _T500, _N6, _TT = 0.0, 500, 6, 2.6
_L = crit(_N6)
print("  Cp_P4   mean P4   best mean   best policy   P4 share   exchange rate")
for _v in [0.24, 0.20, 0.14, 0.10, 0.08, 0.06, 0.04]:
    _sh, _mm = [], []
    for _s in range(3):
        _p = sample(120000, _s)
        _p["Cp_P4"] = np.full(120000, _v)
        _E = np.stack([EH(k, _p, _C, _T500, _N6, _TT) for k in range(4)])
        _sh.append(np.mean(_E.argmin(0) == 3) * 100)
        _mm.append(_E.mean(1))
    _m = np.mean(_mm, axis=0)
    print("  %5.3f   %7.3f   %9.3f   %-11s %7.2f%%   1/%.1f"
          % (_v, _m[3], _m.min(), POL[int(_m.argmin())], np.mean(_sh), _L / _v))
# threshold at which P4 becomes the lowest-mean-harm policy
_lo, _hi = 0.01, 0.20
for _ in range(35):
    _mid = (_lo + _hi) / 2
    _p = sample(150000, 0)
    _p["Cp_P4"] = np.full(150000, _mid)
    _m = np.stack([EH(k, _p, _C, _T500, _N6, _TT) for k in range(4)]).mean(1)
    _lo, _hi = (_mid, _hi) if int(_m.argmin()) == 3 else (_lo, _mid)
print("  threshold where P4 becomes lowest-mean-harm: Cp_P4 = %.4f" % _lo)
print("  that is %.0f%% of the modal 0.14, exchange rate 1/%.1f" % (_lo / 0.14 * 100, _L / _lo))

# ---------- CONTROL RUN, full terrestrial capability ----------
# The model caps k_cap at 0.85, which corresponds to transit and an early base.
# This control lifts the cap. c=1 and k_cap=1 mean a medical centre
# able to do what a clinic on Earth does. P(F|E) then falls to zero.
print("\n=== KONTROLA, capability equivalent to terrestrial care ===")
_q = sample(100000, 0)
_q["k_cap"] = np.ones(100000)
print("  P(F|E) przy c=1, k_cap=1: %.6f" % pF(0, _q, 1.0, 400).mean())
for _T in [2.6, 10.0, 20.0]:
    _E = np.stack([EH(s, _q, 1.0, 400, 6, _T) for s in range(4)])
    _m = _E.mean(1)
    print("  T=%4.1f lat: " % _T + " ".join("%s=%.3f" % (POL[i], _m[i]) for i in range(4))
          + "  -> %s" % POL[int(_m.argmin())])

# ======================================================================
# STRUCTURAL SENSITIVITY (added in 1.0.4). Base model above is untouched.
# Six switches named by the reviewers, each with its own sub-block.
# Scenario unless stated: Mars, c=0.2, t=400 d, n=6, T=2.6 yr, seed 0.
# ======================================================================
print("\n" + "="*70 + "\nSTRUCTURAL SENSITIVITY (1.0.4)\n" + "="*70)
_MC, _MT, _MN, _MT2 = 0.2, 400, 6, 2.6
def _EHk(s,p,c,t,n,T,kcrew=2.0):
    """EH with a variable crew weight L(E,F)=1+kcrew/n (base model uses kcrew=2)."""
    e=pE(s,p,T); f=pF(s,p,c,t)
    return n*(e*f*(1.0+kcrew/n)+e*(1-f)*p["L_S"])+n*Cp(s,p)+Cf(s,p)
def _summ(E):
    m=E.mean(1); sh=np.array([(E.argmin(0)==s).mean() for s in range(NP)])*100
    return m, sh, ("  ".join("%.3f"%m[s] for s in range(NP))
                   + "   best %s  P3-P1 %+.3f   P4 share %4.1f%%" % (POL[int(m.argmin())], m[2]-m[0], sh[3]))

# --- SS1 regret intervals: per-draw 5-95% and Monte Carlo SE over 10 seeds ---
print("\n--- SS1 REGRET INTERVALS ---")
for _nm,(_c,_t,_n,_T) in {"LEO":(0.6,12,6,0.5),"Moon":(0.4,90,6,1.0),"Mars":(_MC,_MT,_MN,_MT2)}.items():
    _ms=[]
    for _sd in range(10):
        _p=sample(100000,_sd); _E=np.stack([EH(s,_p,_c,_t,_n,_T) for s in range(NP)]); _R=_E-_E.min(0); _ms.append(_R.mean(1))
        if _sd==0: _lo,_hi=np.percentile(_R,5,1),np.percentile(_R,95,1)
    _ms=np.array(_ms); _m=_ms.mean(0); _se=_ms.std(0,ddof=1)
    print("  %s:" % _nm)
    for s in range(NP):
        print("    %s regret %.3f  MC-SE %.4f  per-draw [%.3f-%.3f]" % (POL[s],_m[s],_se[s],_lo[s],_hi[s]))

# --- SS2 harm-scale weights ---
print("\n--- SS2 HARM-SCALE WEIGHTS, Mars ---")
print("  L_S fixed:")
for _v in [0.0,0.02,0.05,0.10,0.20,0.30]:
    _p=sample(100000,0); _p["L_S"]=np.full(100000,_v)
    print("    L_S=%.2f  %s" % (_v,_summ(np.stack([EH(s,_p,_MC,_MT,_MN,_MT2) for s in range(NP)]))[2]))
print("  crew weight L(E,F)=1+k/n, k fixed:")
for _k in [0.0,1.0,2.0,4.0,8.0]:
    _p=sample(100000,0)
    print("    k=%.0f  %s" % (_k,_summ(np.stack([_EHk(s,_p,_MC,_MT,_MN,_MT2,_k) for s in range(NP)]))[2]))
print("  Cp_P4 fixed (whole-life harm of edentulism):")
for _v in [0.24,0.14,0.10,0.08,0.06,0.04,0.02]:
    _p=sample(100000,0); _p["Cp_P4"]=np.full(100000,_v)
    print("    Cp_P4=%.2f  %s   exchange 1/%.1f" % (_v,_summ(np.stack([EH(s,_p,_MC,_MT,_MN,_MT2) for s in range(NP)]))[2],crit(_MN)/_v))
_lo,_hi=0.01,0.20
for _ in range(30):
    _mid=(_lo+_hi)/2; _p=sample(150000,0); _p["Cp_P4"]=np.full(150000,_mid)
    _m=np.stack([EH(s,_p,_MC,_MT,_MN,_MT2) for s in range(NP)]).mean(1); _lo,_hi=(_mid,_hi) if int(_m.argmin())==3 else (_lo,_mid)
print("  threshold at the Mars point where P4 becomes lowest-mean-harm: Cp_P4 = %.4f (%.0f%% of modal 0.14, exchange 1/%.1f)" % (_lo,_lo/0.14*100,crit(_MN)/_lo))
print("  two-way Cp_P4 x k, best policy by mean:")
_ks=[0.0,1.0,2.0,4.0,8.0]; _cps=[0.24,0.14,0.10,0.08,0.06,0.04,0.02]
print("    Cp_P4\\k " + "".join("%6.0f"%k for k in _ks))
for _v in _cps:
    _row=[]
    for _k in _ks:
        _p=sample(60000,0); _p["Cp_P4"]=np.full(60000,_v); _m=np.stack([_EHk(s,_p,_MC,_MT,_MN,_MT2,_k) for s in range(NP)]).mean(1); _row.append(POL[int(_m.argmin())])
    print("    %5.2f   " % _v + "".join("%6s"%r for r in _row))

# --- SS3 Weibull hazard H(T) = lambda * T^k, lambda calibrated at one year ---
print("\n--- SS3 WEIBULL HAZARD, H(T)=lambda*T0*(T/T0)^k with T0=1 year (rate calibrated at one year) ---")
def _pEw(s,p,T,k,both):
    b=1-np.exp(-p["lambda_yr"]*T**k); Hp=p["lam_pros"]*(T**k if both else T)
    return [b,b*(1-p["r_sel"]),b*(1-p["r_comp"]),1-np.exp(-Hp)][s]
def _EHw(s,p,c,t,n,T,k,both):
    e=_pEw(s,p,T,k,both); f=pF(s,p,c,t)
    return n*(e*f*crit(n)+e*(1-f)*p["L_S"])+n*Cp(s,p)+Cf(s,p)
for _both,_lab in [(True,"k on dental AND prosthetic hazard (reported)"),(False,"k on dental hazard only")]:
    print("  " + _lab + ", Mars:")
    for _k in [0.7,1.0,1.5,2.0]:
        _p=sample(100000,0); _E=np.stack([_EHw(s,_p,_MC,_MT,_MN,_MT2,_k,_both) for s in range(NP)])
        print("    k=%.1f  P(E|P1)=%.3f  %s" % (_k,_pEw(0,_p,_MT2,_k,_both).mean(),_summ(_E)[2]))
print("  alternative calibration (same cumulative hazard at T=2.6 yr) would make k irrelevant by construction, because the base model uses only P(E|T), not event timing.")

# --- SS4 prosthetic microgravity multiplier m on lam_pros and pf_pros ---
print("\n--- SS4 PROSTHETIC MICROGRAVITY MULTIPLIER m, Mars ---")
for _mm in [1,2,4,8]:
    _p=sample(100000,0); _p["lam_pros"]=_p["lam_pros"]*_mm; _p["pf_pros"]=np.clip(_p["pf_pros"]*_mm,0,1)
    print("    m=%d  %s" % (_mm,_summ(np.stack([EH(s,_p,_MC,_MT,_MN,_MT2) for s in range(NP)]))[2]))
print("  extreme corner c=0, t=500 d, Cp_P4 fixed 0.06:")
for _mm in [1,2,4]:
    _p=sample(100000,0); _p["lam_pros"]=_p["lam_pros"]*_mm; _p["pf_pros"]=np.clip(_p["pf_pros"]*_mm,0,1); _p["Cp_P4"]=np.full(100000,0.06)
    print("    m=%d  %s" % (_mm,_summ(np.stack([EH(s,_p,0.0,500,_MN,_MT2) for s in range(NP)]))[2]))

# --- SS5 correlated crew events: shared frailty on lambda + cascade penalty ---
print("\n--- SS5 CORRELATED CREW EVENTS, Mars, crew simulated per draw (N=200000, seed 11) ---")
def _EHcrew(p,rng,cv,casc,c=_MC,t=_MT,n=_MN,T=_MT2):
    N=len(p["lambda_yr"]); Z=np.ones(N) if cv==0 else rng.gamma(1/cv**2,cv**2,N)
    out=[]
    for s in range(NP):
        if s==3: pe=1-np.exp(-p["lam_pros"]*Z*T)
        else:
            b=1-np.exp(-p["lambda_yr"]*Z*T); pe=[b,b*(1-p["r_sel"]),b*(1-p["r_comp"])][s]
        pf=pF(s,p,c,t); ev=rng.binomial(n,pe); fl=rng.binomial(ev,pf); mg=ev-fl
        out.append(fl*crit(n)+mg*p["L_S"]+casc*(fl>=2)+n*Cp(s,p)+Cf(s,p))
    return np.stack(out)
for _cv in [0.0,0.3,0.6,1.0]:
    for _casc in [0.0,0.5,1.0]:
        _rng=np.random.default_rng(11); _p=sample(200000,0); _E=_EHcrew(_p,_rng,_cv,_casc)
        _m,_sh,_txt=_summ(_E); _q=np.percentile(_E,95,1)
        print("    frailty CV=%.1f cascade=%.1f  %s   p95 P1 %.2f P3 %.2f" % (_cv,_casc,_txt,_q[0],_q[2]))

# --- SS6 acceptability placeholder A(P) = n * p_refuse(P) * L_replace ---
print("\n--- SS6 ACCEPTABILITY PLACEHOLDER (author-specified, awaiting elicitation), Mars ---")
_PR={"P1":None,"P2":(0.02,0.05,0.10),"P3":(0.01,0.03,0.05),"P4":(0.20,0.50,0.80)}; _LR=(0.02,0.05,0.10)
def _acc(seed,scale=1.0,lr=None):
    rng=np.random.default_rng(seed+100); p=sample(100000,seed)
    L=np.full(100000,lr) if lr is not None else rng.triangular(*_LR,100000); E=[]
    for s in range(NP):
        pr=np.zeros(100000) if _PR[POL[s]] is None else np.clip(rng.triangular(*_PR[POL[s]],100000)*scale,0,1)
        E.append(EH(s,p,_MC,_MT,_MN,_MT2)+_MN*pr*L)
    return np.stack(E)
print("    no acceptability term:     %s" % _summ(np.stack([EH(s,sample(100000,0),_MC,_MT,_MN,_MT2) for s in range(NP)]))[2])
print("    placeholder ranges:        %s" % _summ(_acc(0))[2])
print("    refusal probabilities x2:  %s" % _summ(_acc(0,2.0))[2])
_lo,_hi=0.0,3.0
for _ in range(30):
    _mid=(_lo+_hi)/2; _m=_acc(0,1.0,_mid).mean(1); _lo,_hi=(_mid,_hi) if _m[2]<_m[0] else (_lo,_mid)
print("    L_replace at which sanation stops beating retention: %.3f MIU per replacement" % _lo)
