# -*- coding: utf-8 -*-
"""Figura 3. Jak przebiega wybor miedzy czterema postepowaniami przedlotowymi P1-P4.
Autonomia pokladowa c wchodzi jako parametr, nie jako osobne postepowanie.
Tworzy figura_drzewo_decyzyjne.png oraz .pdf."""
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def box(ax,x,y,w,h,text,fc,fs=8.2,bold=False):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.02,rounding_size=0.08",
        lw=1.0,edgecolor="black",facecolor=fc,zorder=3))
    return ax.text(x,y,text,ha="center",va="center",fontsize=fs,zorder=4,
        fontweight=("bold" if bold else "normal"),color=("white" if fc=="0.20" else "black"))

def link(ax,x1,y1,x2,y2,label=None,lx=None,ly=None):
    ax.annotate("",xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle="-",color="0.35",lw=1.1),zorder=1)
    if label: return ax.text(lx,ly,label,fontsize=7.4,color="0.2",ha="center",va="center",zorder=5,
        bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none"))

def rysuj():
    fig,ax=plt.subplots(figsize=(7.48,4.5)); T=[]
    T.append(box(ax,1.4,3.0,2.4,0.86,"Evacuation or timely\ndefinitive care\navailable?","0.88"))
    T.append(box(ax,4.5,2.0,2.2,0.78,"Onboard capability c\n(scenario parameter)","0.82"))
    T.append(box(ax,6.9,1.0,2.0,0.72,"Crew dental\nrisk profile?","0.88"))
    T.append(box(ax,5.1,4.55,2.5,0.6,"P1  Retention\nand prophylaxis","0.93"))
    T.append(box(ax,7.7,3.5,2.7,0.6,"crew dental risk\nprofile -> P1 or P3","0.88"))
    T.append(box(ax,9.72,1.75,2.25,0.6,"P3  Tooth-preserving\ncomprehensive sanation","0.50"))
    T.append(box(ax,9.72,0.55,2.25,0.6,"P2  Selective\nextraction","0.72"))
    T.append(box(ax,6.9,-0.7,2.6,0.66,"P4  enters the candidate set\nfor formal evaluation","0.20",bold=True))
    T.append(link(ax,2.6,3.25,3.85,4.45,"yes",3.05,3.98))
    T.append(link(ax,2.6,2.8,3.45,2.15,"no",3.0,2.35))
    T.append(link(ax,5.6,2.3,6.4,3.4,"high c",5.95,3.0))
    T.append(link(ax,5.4,1.75,5.8,1.2,"low c",5.55,1.5))
    ax.annotate("",xy=(5.6,-0.6),xytext=(4.5,1.61),arrowprops=dict(arrowstyle="-",color="0.35",lw=1.1,linestyle=(0,(4,3))),zorder=1)
    T.append(ax.text(4.15,0.45,"extreme isolation\nand low P4 cost",fontsize=7.4,color="0.2",ha="center",va="center",zorder=5,bbox=dict(boxstyle="round,pad=0.15",fc="white",ec="none")))
    T.append(link(ax,7.9,1.2,8.55,1.7,"low risk",8.12,1.55))
    T.append(link(ax,7.9,0.8,8.55,0.6,"high risk",8.12,0.62))
    T.append(ax.text(6.9,-1.35,"extreme arm of the pre-flight-intervention axis,\noptimal only if the whole-life cost of edentulism is roughly halved",
        ha="center",va="center",fontsize=7.4,color="0.3",style="italic",zorder=5))
    ax.set_xlim(-0.1,11.1); ax.set_ylim(-1.8,5.2); ax.axis("off")
    fig.tight_layout()
    fig.savefig("figura_drzewo_decyzyjne.png",dpi=200)
    fig.savefig("figura_drzewo_decyzyjne.pdf")
    return fig,[t for t in T if t is not None]

if __name__=="__main__":
    fig,texts=rysuj()
    fig.canvas.draw(); r=fig.canvas.get_renderer()
    items=[(t.get_text()[:22].replace("\n"," "),t.get_window_extent(r)) for t in texts if t.get_text().strip()]
    def ov(a,b): return not (a.x1<=b.x0 or b.x1<=a.x0 or a.y1<=b.y0 or b.y1<=a.y0)
    k=0
    for i in range(len(items)):
        for j in range(i+1,len(items)):
            if ov(items[i][1],items[j][1]): print("KOLIZJA:",items[i][0],"<->",items[j][0]); k+=1
    print("Etykiet:",len(items),"Kolizji:",k)
