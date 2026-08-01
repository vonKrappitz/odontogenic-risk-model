# -*- coding: utf-8 -*-
"""Figura 4. Mapa marginesu decyzji, roznica sredniej oczekiwanej szkody sanacja minus retencja.
Gradient, pogrubiona linia progu, opisane izolinie, etykiety regionow.
Importuje model_decyzyjny_v4.py. Tworzy figura_mapa_progowa.png oraz .pdf."""
import numpy as np, matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
src=open("model_decyzyjny_v4.py").read().split("def validate")[0]
ns={}; exec(src,ns)
sample=ns["sample"]; EH=ns["EH"]

def margin_grid(n,T,tmax,N=9000,grid=120,seed=3):
    cs=np.linspace(0,1,grid); ts=np.linspace(0,tmax,grid)
    p=sample(N,seed)
    D=np.zeros((grid,grid))          # meanEH(P1 retencja) - meanEH(P3 sanacja)
    for i,c in enumerate(cs):
        for j,t in enumerate(ts):
            eh_p1=EH(0,p,c,t,n,T).mean(); eh_p3=EH(2,p,c,t,n,T).mean()
            D[i,j]=eh_p1-eh_p3           # >0 sanacja lepsza, <0 retencja lepsza
    return ts,cs,D

panels=[(6,2.6,500,"Crew 6, 2.6-year mission",(400,0.2,"Mars")),
        (4,2.6,500,"Crew 4, 2.6-year mission",(400,0.2,"Mars")),
        (6,1.0,365,"Crew 6, 1-year mission",None)]
grids=[margin_grid(n,T,tmax) for n,T,tmax,_,_ in panels]
vmax=max(np.abs(D).max() for _,_,D in grids)
norm=TwoSlopeNorm(vmin=-vmax,vcenter=0,vmax=vmax)
cmap=plt.cm.RdBu_r   # niebieski = retencja, czerwony/pomaranczowy = sanacja

fig,axes=plt.subplots(1,3,figsize=(7.48,3.1))
for ax,(n,T,tmax,title,marker),(ts,cs,D) in zip(axes,panels,grids):
    im=ax.pcolormesh(ts,cs,D,cmap=cmap,norm=norm,shading="gouraud")
    # linia progu, tam gdzie margines = 0
    CS=ax.contour(ts,cs,D,levels=[0.0],colors="black",linewidths=2.0)
    # cienkie izolinie marginesu dla czytelnosci
    CS2=ax.contour(ts,cs,D,levels=[-0.09,-0.05,-0.02,0.02,0.05],colors="0.3",linewidths=0.5,alpha=0.75)
    ax.clabel(CS2,inline=True,fontsize=5.5,fmt="%.2f")
    ax.set_xlabel("Time to definitive care (days)",fontsize=8); ax.set_ylabel("Onboard capability c",fontsize=8)
    ax.tick_params(labelsize=7)
    ax.set_title(title,fontsize=8); ax.set_xlim(0,tmax); ax.set_ylim(0,1)
    # etykiety regionow, gdzie sie mieszcza
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
