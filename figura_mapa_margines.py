# -*- coding: utf-8 -*-
"""Figure 2. By how much and in which direction the choice tilts between sanation and retention.
Gradient, a bold threshold line, labelled contours, region labels.
Imports model_decyzyjny_v4.py. Writes figura_mapa_progowa.png and .pdf."""
import numpy as np, matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
matplotlib.rcParams['font.family']='DejaVu Sans'   # bundled with matplotlib, so the layout does not depend on the machine
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
src=open("model_decyzyjny_v4.py").read().split("def validate")[0]
ns={}; exec(src,ns)
sample=ns["sample"]; EH=ns["EH"]

def margin_grid(n,T,tmax,N=9000,grid=120,seed=3):
    cs=np.linspace(0,1,grid); ts=np.linspace(0,tmax,grid)
    p=sample(N,seed)
    D=np.zeros((grid,grid))          # meanEH(P1 retention) - meanEH(P3 sanation)
    for i,c in enumerate(cs):
        for j,t in enumerate(ts):
            eh_p1=EH(0,p,c,t,n,T).mean(); eh_p3=EH(2,p,c,t,n,T).mean()
            D[i,j]=eh_p1-eh_p3           # >0 sanation better, <0 retention better
    return ts,cs,D

panels=[(6,2.6,500,"Crew 6, 2.6-year mission",(400,0.2,"Mars")),
        (4,2.6,500,"Crew 4, 2.6-year mission",(400,0.2,"Mars")),
        (6,1.0,365,"Crew 6, 1-year mission",None)]
grids=[margin_grid(n,T,tmax) for n,T,tmax,_,_ in panels]
vmax=max(np.abs(D).max() for _,_,D in grids)
norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
cmap=plt.cm.RdBu_r   # blue = retention, red/orange = sanation

fig,axes=plt.subplots(1,3,figsize=(7.48,3.1),sharey=True,constrained_layout=True)
for ax,(n,T,tmax,title,marker),(ts,cs,D) in zip(axes,panels,grids):
    im=ax.pcolormesh(ts,cs,D,cmap=cmap,norm=norm,shading="gouraud")
    # threshold line, where the margin is 0
    CS=ax.contour(ts,cs,D,levels=[0.0],colors="black",linewidths=2.0)
    # thin margin contours for readability
    CS2=ax.contour(ts,cs,D,levels=[-0.09,-0.05,-0.02,0.02,0.05],colors="0.3",linewidths=0.5,alpha=0.75)
    ax.clabel(CS2,inline=True,fontsize=5.5,fmt="%.2f")
    ax.set_xlabel("Time to definitive care (days)",fontsize=8)
    if ax is axes[0]: ax.set_ylabel("Onboard capability c",fontsize=8)   # shared axis, labelled once
    ax.tick_params(labelsize=7)
    ax.set_title(title,fontsize=8); ax.set_xlim(0,tmax); ax.set_ylim(0,1)
    # region labels, where they fit
    if D.max()>0.02:
        ax.text(0.72*tmax,0.12,"Sanation\nfavoured",ha="center",va="center",fontsize=7,color="0.15",
                bbox=dict(boxstyle="round,pad=0.2",fc="white",ec="0.6",alpha=0.85))
    ax.text(0.30*tmax if D.max()>0.02 else 0.5*tmax,0.82,"Retention\nfavoured",ha="center",va="center",
            fontsize=7,color="0.15",bbox=dict(boxstyle="round,pad=0.2",fc="white",ec="0.6",alpha=0.85))
    if marker:
        mx,my,ml=marker
        ax.plot(mx,my,"o",ms=6,mfc="none",mec="black",mew=1.4)
        ax.annotate(ml,(mx,my),fontsize=7.5,fontweight="bold",ha="center",va="bottom",xytext=(mx,my+0.06))
cbar=fig.colorbar(im,ax=axes,fraction=0.022,pad=0.015)
cbar.set_label("Sanation minus retention, mean harm\n(mission-impact units)",fontsize=7)
cbar.ax.tick_params(labelsize=6.5)
fig.savefig("figura_mapa_progowa.png",dpi=175,bbox_inches="tight")
fig.savefig("figura_mapa_progowa.pdf",bbox_inches="tight")
print("Zapisano mape marginesu. vmax=",round(vmax,3))
for (n,T,tmax,title,_),(ts,cs,D) in zip(panels,grids):
    print(f"  {title}: margines od {D.min():+.3f} do {D.max():+.3f}  (dodatni=sanacja)")
