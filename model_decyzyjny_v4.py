# -*- coding: utf-8 -*-
"""
Version 1.0.6. Relative to 1.0.5 this adds ONE printed block, ADDITIONS IN 1.0.6, at the very end:
the exposed-pulp table with the optimality share of every policy, the risk reductions applied to the
event rate instead of the event probability, the risk reductions rank-correlated with their own costs,
the two risk reductions rank-correlated with each other, and the rescue factor averaged over a transit
in which the time to care falls linearly to zero. Every line printed by 1.0.5 is unchanged.
Version 1.0.5. Relative to 1.0.4 this adds ONE printed sub-block, SS7, at the very end:
the Mars scenario with the event rate fixed at values published by NASA, the rate at
which sanation overtakes retention, and the result and the value of information under
event-rate ranges bracketed by those published values, and a pre-positioned surface facility
with a time to definitive care of 270 days, and minor incidents (exposed pulp) counted outside the
event rate, with a share escalating later to an abscess, and the residual hazard after clearance
set to zero. Every line printed by 1.0.4 is unchanged. In the paper the residual hazard after clearance
(lam_pros, pf_pros) is no longer called prosthetic, because denture problems are minor incidents whose
burden sits in the clearance costs. Printed labels that say prosthetic are kept so that the lines
printed by 1.0.4 stay byte for byte the same.
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
  P(E|P4) = 1 - exp(-lam_pros*T)               residual severe-event hazard after clearance
  rescue(t) = t/(t + tau)                      rises towards 1, tau is the half-saturation time
  P(F|E,P1..P3) = clip(pf0*(1 - c*k_cap)*rescue(t), 0, 1)
  P(F|E,P4)     = clip(pf_pros*rescue(t), 0, 1)
  L(E,F) = 1.0*(1 + 2/n)                       loss on failure, larger in a smaller crew
  EH(s)  = n*[P(E)*P(F)*L(E,F) + P(E)*(1-P(F))*L_S] + n*Cperson(s) + Cfixed(s)

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
# Corner of the Fig. 2 domain: zero capability, 500 days to care, crew of 6, mission of 2.6 years.
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

# --- SS4 microgravity multiplier m on lam_pros and pf_pros, the residual hazard after clearance ---
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

# --- SS7 event rate fixed at published values, and the rate at which the leader changes (added in 1.0.5) ---
# Sources of the fixed values: Gilkey et al., NASA/TP-2012-217120 (submarine prior, in-flight posterior,
# pre-flight astronaut count 19 abscesses in 475.2 person-years, in-flight record 0 in 31.9 person-years);
# Menon, NASA/TM-2012-217368 (Integrated Medical Model incidences for abscess and exposed pulp).
print("\n--- SS7 EVENT RATE FIXED AT PUBLISHED VALUES, Mars ---")
_p7=sample(100000,0)
def _fix(lam):
    q=dict(_p7); q["lambda_yr"]=np.full(100000,lam)
    return np.stack([EH(s,q,_MC,_MT,_MN,_MT2) for s in range(NP)])
_UB=-np.log(0.05)/31.9
for _lam,_lab in [(0.00353,"submarine prior"),(0.00816,"NASA in-flight posterior mean"),(0.0114,"NASA in-flight posterior 95th percentile"),
                  (0.0230,"IMM abscess"),(19/475.2,"astronauts pre-flight, 19 in 475.2 person-years"),
                  (0.0230+0.0201,"IMM abscess plus exposed pulp"),(_UB,"95% upper bound, 0 events in 31.9 person-years")]:
    _E=_fix(_lam); _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
    print("    lambda=%.5f  %s   share P1 %4.1f%% P3 %4.1f%%   %s" % (_lam,_summ(_E)[2],_sh[0],_sh[2],_lab))
_lo,_hi=0.001,0.10
for _ in range(40):
    _mid=(_lo+_hi)/2; _m=_fix(_mid).mean(1); _lo,_hi=(_mid,_hi) if _m[2]>_m[0] else (_lo,_mid)
_thr=(_lo+_hi)/2
print("    lambda at which sanation overtakes retention at the Mars point: %.4f per person-year" % _thr)
_a,_c3,_b=RANGES["lambda_yr"]
print("    probability mass above that rate: triangular range %.1f%%, log-uniform range %.1f%%" % (
      (_b-_thr)**2/((_b-_a)*(_b-_c3))*100, np.log(_b/_thr)/np.log(_b/_a)*100))
# Event rate drawn log-uniformly over a range bracketed by published figures instead of the author's range.
# The summary uses the scenario draws (seed 0); the value of information uses the draws of the EVPPI run
# (seed 7, 120000 draws, tau fixed at 30 days, 40 bins on lambda), so the first line reproduces the EVPPI block above.
def _evppi_lam(p,K=40):
    E=np.stack([EH(s,p,_MC,_MT,_MN,_MT2) for s in range(NP)]); o=np.argsort(p["lambda_yr"])
    return E.mean(1).min()-E[:,o].reshape(NP,K,-1).mean(2).min(0).mean(), E.mean(1).min()
_pe=sample(120000,7); _pe["tau"]=np.full(120000,30.0); _v,_b0=_evppi_lam(_pe)   # tau fixed at 30 days, as in the EVPPI block
print("    value of information on lambda, author range: %.4f MIU, %.1f%% of the best mean harm" % (_v,_v/_b0*100))
for _l,_h,_lab in [(0.00353,_UB,"submarine prior to flight-record bound"),(0.00816,_UB,"NASA in-flight posterior mean to flight-record bound")]:
    _r=np.random.default_rng(105)
    _q=dict(_p7); _q["lambda_yr"]=np.exp(_r.uniform(np.log(_l),np.log(_h),100000))
    _E=np.stack([EH(s,_q,_MC,_MT,_MN,_MT2) for s in range(NP)]); _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
    print("    log-uniform %.5f to %.5f  %s   share P1 %4.1f%% P3 %4.1f%%   mass above %.4f: %.1f%%   %s" % (
          _l,_h,_summ(_E)[2],_sh[0],_sh[2],_thr,np.log(_h/_thr)/np.log(_h/_l)*100,_lab))
    _r=np.random.default_rng(105)
    _qe=dict(_pe); _qe["lambda_yr"]=np.exp(_r.uniform(np.log(_l),np.log(_h),120000))
    _v,_b1=_evppi_lam(_qe)
    print("        value of information on lambda: %.4f MIU, %.1f%% of the best mean harm" % (_v,_v/_b1*100))
# Pre-positioned surface facility (added in 1.0.5 after the event-rate rows). Time to definitive care 270 days,
# about a minimum-energy Earth-Mars transfer (about 259 days) with margin. Crew, capability and parameter draws
# as at the Mars point. The second row counts exposure without care only on two 270-day transits; events treated
# at the surface are counted as harmless. The last line is the exposure at which sanation overtakes retention.
print("    pre-positioned surface facility, time to definitive care 270 days:")
for _T,_lab in [(_MT2,"exposure as at the Mars point"),(540/365.25,"without care only on two 270-day transits")]:
    _E=np.stack([EH(s,_p7,_MC,270.0,_MN,_T) for s in range(NP)]); _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
    print("    T=%.2f yr  %s   share P1 %4.1f%% P3 %4.1f%%   %s" % (_T,_summ(_E)[2],_sh[0],_sh[2],_lab))
_lo,_hi=0.5,_MT2
for _ in range(40):
    _mid=(_lo+_hi)/2; _m=np.stack([EH(s,_p7,_MC,270.0,_MN,_mid) for s in (0,2)]).mean(1); _lo,_hi=(_mid,_hi) if _m[1]>_m[0] else (_lo,_mid)
print("    exposure without care at which sanation overtakes retention, time to care 270 days: %.2f years" % ((_lo+_hi)/2))
# Minor incidents outside lambda (added in 1.0.5). Exposed pulp at the Integrated Medical Model incidence of
# 0.0201 per person-year (NASA/TM-2012-217368), each counted at the loss L_S of a managed incident. Traumatic
# exposures fall equally on P1 to P3; carious ones are reduced like severe events by r_sel and r_comp. Full dental
# clearance (P4) has none. A share q of the exposed pulps escalates later to an abscess, a new severe event.
print("    minor incidents outside lambda, exposed pulp at 0.0201 per person-year, Mars point:")
_ex=_MN*(1-np.exp(-0.0201*_MT2))
print("    expected exposed pulps per mission %.3f; added harm at L_S 0.02, 0.05, 0.10: %.4f, %.4f, %.4f" % (
      _ex,_ex*0.02,_ex*0.05,_ex*0.10))
_E0=np.stack([EH(s,_p7,_MC,_MT,_MN,_MT2) for s in range(NP)])
_f1=pF(0,_p7,_MC,_MT); _unit=_f1*crit(_MN)+(1-_f1)*_p7["L_S"]
_K={"traumatic":lambda s:[1.0,1.0,1.0,0.0][s],"carious":lambda s:[1.0,1-_p7["r_sel"],1-_p7["r_comp"],0.0][s]}
for _q in (0.0,0.05,0.10,0.20,0.30,0.50):
    for _nm in ("traumatic","carious"):
        _E=_E0.copy()
        for s in range(NP): _E[s]=_E0[s]+_ex*_K[_nm](s)*((1-_q)*_p7["L_S"]+_q*_unit)
        _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
        print("    escalating share q=%.2f  %-9s  %s   share P1 %4.1f%% P3 %4.1f%%" % (_q,_nm,_summ(_E)[2],_sh[0],_sh[2]))
# Residual severe-event hazard after full dental clearance set to zero (added in 1.0.5). Denture problems are
# minor incidents whose burden sits in the clearance costs; this row shows how much of the harm of P4 rests on
# lam_pros, the hazard of severe events that remain after clearance.
_q=dict(_p7); _q["lam_pros"]=np.zeros(100000)
_E=np.stack([EH(s,_q,_MC,_MT,_MN,_MT2) for s in range(NP)]); _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
print("    residual hazard after clearance set to zero  %s   share P1 %4.1f%% P3 %4.1f%%" % (_summ(_E)[2],_sh[0],_sh[2]))

# ======================================================================
# ADDITIONS IN 1.0.6. Everything above is unchanged and prints as in 1.0.5.
# Scenario unless stated: Mars, c=0.2, t=400 d, n=6, T=2.6 yr, the draws of SS7 (seed 0).
# ======================================================================
print("\n" + "="*70 + "\nADDITIONS IN 1.0.6\n" + "="*70)

# (a) Exposed pulps with a share q escalating to an abscess (Table S3): the optimality share of all four
# policies. Same draws and same harm as the escalation lines of SS7 above, which print P1 and P3 only.
print("\n--- exposed pulps, escalating share q, optimality share of every policy (Table S3) ---")
for _q in (0.0,0.05,0.10,0.20,0.30,0.50):
    for _nm in ("traumatic","carious"):
        _E=_E0.copy()
        for s in range(NP): _E[s]=_E0[s]+_ex*_K[_nm](s)*((1-_q)*_p7["L_S"]+_q*_unit)
        _sh=np.array([(_E.argmin(0)==s).mean() for s in range(NP)])*100
        print("    q=%.2f  %-9s  share P1 %4.1f%%  P2 %4.1f%%  P3 %4.1f%%  P4 %4.1f%%" % (_q,_nm,_sh[0],_sh[1],_sh[2],_sh[3]))

# (b) Risk reductions applied to the event rate instead of the event probability:
# P(E|P2) = 1 - exp(-lambda*(1-r_sel)*T), P(E|P3) = 1 - exp(-lambda*(1-r_comp)*T). P1 and P4 as in the base model.
def _pE_rate(s,p,T):
    l=p["lambda_yr"]
    return [1-np.exp(-l*T),1-np.exp(-l*(1-p["r_sel"])*T),1-np.exp(-l*(1-p["r_comp"])*T),1-np.exp(-p["lam_pros"]*T)][s]
def _EH_rate(s,p,c,t,n,T):
    e=_pE_rate(s,p,T); f=pF(s,p,c,t)
    return n*(e*f*crit(n)+e*(1-f)*p["L_S"])+n*Cp(s,p)+Cf(s,p)
print("\n--- risk reductions on the event rate instead of the event probability ---")
_E=np.stack([_EH_rate(s,_p7,_MC,_MT,_MN,_MT2) for s in range(NP)]); _m,_sh,_txt=_summ(_E)
print("    reduction on the rate  %s   share P1 %4.1f%% P2 %4.1f%% P3 %4.1f%%" % (_txt,_sh[0],_sh[1],_sh[2]))

# (c), (d) Rank correlation. Each value drawn above is kept and only the pairing changes, by an Iman-Conover-style
# reordering of one variable with normal scores, so every marginal distribution stays exactly as drawn.
# The target is a rank (Spearman) correlation, converted to the normal-score correlation 2*sin(pi*rho/6)
# that produces it.
# (c) Mean harm cannot change by construction: each cost is added to the harm of its own policy.
# (d) Only the mean of P3 can move, and only by Monte Carlo noise: r_comp multiplies the event probability under
# retention, P(E|P1), and the result is weighted by the failure probability and the losses of the same draw,
# so reordering r_comp changes its pairing with lambda and with all of these. The script prints that shift.
def _rank(x): return np.argsort(np.argsort(x))
def _nsc(rho): return 2*np.sin(np.pi*rho/6)   # normal-score correlation giving rank correlation rho
def _reorder(x,y,rho,rng):
    """Permute y so that its ranks follow normal scores correlated at rho with the ranks of x."""
    N=len(x); z1=np.empty(N); z1[np.argsort(x)]=np.sort(rng.standard_normal(N))
    z2=rho*z1+np.sqrt(1-rho**2)*rng.standard_normal(N)
    out=np.empty(N); out[np.argsort(z2)]=np.sort(y); return out
def _spearman(x,y): return np.corrcoef(_rank(x),_rank(y))[0,1]
_Eb=np.stack([EH(s,_p7,_MC,_MT,_MN,_MT2) for s in range(NP)]); _mb=_Eb.mean(1)
def _corr_line(label,q,pairs):
    _E=np.stack([EH(s,q,_MC,_MT,_MN,_MT2) for s in range(NP)]); _m,_sh,_txt=_summ(_E)
    rs=" ".join("rank r(%s,%s) %+.2f" % (a,b,_spearman(q[a],q[b])) for a,b in pairs)
    print("    %-10s %s   share P1 %4.1f%% P2 %4.1f%% P3 %4.1f%%   max |mean - base| %.1e   %s"
          % (label,_txt,_sh[0],_sh[1],_sh[2],np.abs(_m-_mb).max(),rs))
# Efficacy and cost rank-correlated within each policy, in both directions. A positive correlation fits a more
# extensive intervention that removes more risk and costs more. A negative one fits operator skill, which
# removes more risk at a lower cost.
print("\n--- each risk reduction rank-correlated with its own cost (r_sel with Cp_P2, r_comp with Cp_P3) ---")
for _rho in (-0.9,-0.5,0.5,0.9):
    _rng=np.random.default_rng(106); _q=dict(_p7)
    _q["Cp_P2"]=_reorder(_q["r_sel"],_q["Cp_P2"],_nsc(_rho),_rng); _q["Cp_P3"]=_reorder(_q["r_comp"],_q["Cp_P3"],_nsc(_rho),_rng)
    _corr_line("rank %+.1f" % _rho,_q,[("r_sel","Cp_P2"),("r_comp","Cp_P3")])
print("\n--- the two risk reductions rank-correlated with each other (r_sel with r_comp) ---")
for _rho in (0.5,0.9,-0.5):
    _rng=np.random.default_rng(107); _q=dict(_p7)
    _q["r_comp"]=_reorder(_q["r_sel"],_q["r_comp"],_nsc(_rho),_rng)
    _corr_line("rank %+.1f" % _rho,_q,[("r_sel","r_comp")])

# (e) Rescue factor t/(t+tau) averaged over a transit in which the time to definitive care falls linearly
# from the full mission to zero: (1/T) * integral_0^T u/(u+tau) du = 1 - (tau/T)*ln(1+T/tau), T in days.
print("\n--- rescue factor averaged over a transit, time to care falling linearly to zero, T=2.6 yr ---")
_Td=_MT2*365.25
for _tau in (7,30,90):
    print("    tau=%2d d  averaged %.3f   fixed t=400 d %.3f" % (_tau,1-(_tau/_Td)*np.log(1+_Td/_tau),400/(400+_tau)))
