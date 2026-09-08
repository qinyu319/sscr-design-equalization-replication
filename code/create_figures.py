from __future__ import annotations

import ast
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "analysis_outputs"
OUT = ROOT / "figures"
DATA = OUT / "figure_data"
OUT.mkdir(exist_ok=True); DATA.mkdir(exist_ok=True)

COL = {"blue":"#0072B2", "orange":"#E69F00", "green":"#009E73", "red":"#D55E00", "purple":"#CC79A7", "sky":"#56B4E9", "black":"#333333", "gray":"#8A8A8A"}
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":9, "axes.spines.top":False, "axes.spines.right":False,
                     "axes.titleweight":"bold", "figure.dpi":140, "savefig.dpi":320})

def save(fig, stem):
    fig.savefig(OUT/f"{stem}.png", bbox_inches="tight", facecolor="white")
    fig.savefig(OUT/f"{stem}.svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)

def figure1():
    fig, ax = plt.subplots(figsize=(7.2,4.5)); ax.set_xlim(0,10); ax.set_ylim(0,7); ax.axis("off")
    boxes = [
        (0.4,5.5,2.0,0.9,"1. Inspect factors\nfor bundled intensity",COL["blue"]),
        (3.0,5.5,2.0,0.9,"2. Retain the\nbenchmark",COL["blue"]),
        (5.6,5.5,2.0,0.9,"3. Identify spread\nat a fixed center",COL["orange"]),
        (3.0,3.7,2.0,0.9,"4. Equalize at\nmultiple anchors",COL["orange"]),
        (5.6,3.7,2.0,0.9,"5. Separate design\nand Monte Carlo SS",COL["green"]),
        (8.0,3.7,1.6,0.9,"6. Allocate\ninteractions",COL["green"]),
        (3.0,1.7,2.0,0.9,"7. Run no-op\nnegative control",COL["purple"]),
        (5.6,1.7,2.0,0.9,"8. Run structural\npositive control",COL["purple"]),
        (8.0,1.7,1.6,0.9,"9. Report\nretention",COL["red"]),
    ]
    for x,y,w,h,t,c in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=.08",fc="white",ec=c,lw=1.8))
        ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=8.5)
    arrows=[((2.4,5.95),(3.0,5.95)),((5.0,5.95),(5.6,5.95)),((6.6,5.5),(4.0,4.6)),((5.0,4.15),(5.6,4.15)),((7.6,4.15),(8.0,4.15)),((4.0,3.7),(4.0,2.6)),((5.0,2.15),(5.6,2.15)),((7.6,2.15),(8.0,2.15)),((8.8,3.7),(8.8,2.6))]
    for a,b in arrows: ax.add_patch(FancyArrowPatch(a,b,arrowstyle="-|>",mutation_scale=10,color=COL["gray"],lw=1.2))
    ax.text(.4,.55,"Interpret jointly: anchor curves + benchmark-denominator retention + control behavior",fontsize=9.5,weight="bold",color=COL["black"])
    ax.text(.4,.2,"Equalization is diagnostic only when orthogonal structural contrasts can survive it.",fontsize=8.5,color=COL["gray"])
    save(fig,"figure1_audit_protocol")

def figure2():
    b=pd.read_csv(AN/"bootstrap_key_metrics.csv")
    b=b[(b.outcome=="mean_total_shift")&(b.metric=="shapley_share__seeding_regime")]
    orig=["C-D1","C-D5","C-D10","C-D50"]; cent=["CS-0","CS-15","CS-30","CS-45"]
    xorig=[0,.20,.45,2.45]; xcent=[0,.30,.60,.90]
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.1),sharey=True)
    for ax,names,xs,title,color in [(axs[0],orig,xorig,"Original contrast-set series",COL["blue"]),(axs[1],cent,xcent,"Centered-span series (mean = 0.50N)",COL["orange"])]:
        q=b.set_index("design").loc[names]
        y=q["median"].to_numpy(); lo=y-q["lo95"].to_numpy(); hi=q["hi95"].to_numpy()-y
        ax.errorbar(xs,y,yerr=[lo,hi],marker="o",lw=2,capsize=3,color=color)
        ax.set_title(title); ax.set_xlabel("Assigned-dose range (N)"); ax.set_ylim(-.03,1); ax.grid(axis="y",alpha=.22)
        for x,yy,n in zip(xs,y,names): ax.annotate(n,(x,yy),xytext=(0,6),textcoords="offset points",ha="center",fontsize=7.5)
    axs[0].set_ylabel("Seeding Shapley share of systematic SS")
    fig.suptitle("Seeding allocation rises with dose contrast; centered designs isolate spread",y=1.03,fontsize=11,weight="bold")
    pd.concat([b[b.design.isin(orig)].assign(series="original"),b[b.design.isin(cent)].assign(series="centered")]).to_csv(DATA/"figure2_data.csv",index=False)
    save(fig,"figure2_contrast_and_centered_span")

def figure3():
    m=pd.read_csv(AN/"factor_metrics.csv")
    z=m[(m.outcome=="mean_total_shift")&(m.allocation=="shapley")]
    fig=plt.figure(figsize=(7.2,5.7)); gs=fig.add_gridspec(2,3,height_ratios=[1,1.15],hspace=.42,wspace=.40)
    ax1=fig.add_subplot(gs[0,0]); ax2=fig.add_subplot(gs[0,1]); ax3=fig.add_subplot(gs[0,2])
    dose=[("C-D1",.05),("CS-0",.50),("D-A95",.95)]
    strength=[("S-A06",.06),("E-S",.14),("S-A18",.18)]
    for ax,pairs,title,xlab in [(ax1,dose,"Dose anchors\n(retained strengths)","Common dose (N)"),(ax2,strength,"Strength anchors\n(C-D50 doses)","Common strength")]:
        for f,label,c in [("seeding_regime","Seeding retention",COL["blue"]),("message_condition","Message retention",COL["orange"])]:
            vals=[]
            for name,x in pairs: vals.append(z[(z.design==name)&(z.factor==f)].rho.iloc[0])
            ax.plot([x for _,x in pairs],vals,marker="o",label=label,color=c,lw=2)
        ax.axhline(1,color=COL["gray"],lw=1,ls="--"); ax.set_title(title); ax.set_xlabel(xlab); ax.set_ylabel("Factor retention, ρ"); ax.grid(axis="y",alpha=.2)
    ax1.legend(frameon=False,fontsize=7,loc="upper left")
    # Systematic signal retention for the same anchors.
    for pairs,label,c in [(dose,"Dose anchors",COL["green"]),(strength,"Strength anchors",COL["purple"])]:
        xs=[x for _,x in pairs]; ys=[z[z.design==n].tau.iloc[0] for n,_ in pairs]
        ax3.plot(range(3),ys,marker="o",label=label,color=c,lw=2)
    ax3.set_xticks(range(3),["low","mid","high"]); ax3.axhline(1,color=COL["gray"],lw=1,ls="--"); ax3.set_ylabel("Total systematic retention, τ"); ax3.set_title("Anchor-dependent\nsignal magnitude"); ax3.grid(axis="y",alpha=.2); ax3.legend(frameon=False,fontsize=7)
    joint={(.06,.05):"J-S06-D05",(.06,.50):"J-S06-D50",(.06,.95):"J-S06-D95",(.14,.05):"E-SD",(.14,.50):"J-S14-D50",(.14,.95):"J-S14-D95",(.18,.05):"J-S18-D05",(.18,.50):"J-S18-D50",(.18,.95):"J-S18-D95"}
    for j,(field,title) in enumerate([("tau","Joint τ"),("seeding_regime","Seeding Shapley share"),("message_condition","Message Shapley share")]):
        ax=fig.add_subplot(gs[1,j]); arr=np.zeros((3,3))
        for iy,s in enumerate([.06,.14,.18]):
            for ix,d in enumerate([.05,.50,.95]):
                row=z[z.design==joint[(s,d)]]
                arr[iy,ix]=row.tau.iloc[0] if field=="tau" else row[row.factor==field].p_sys.iloc[0]
        im=ax.imshow(arr,cmap="YlGnBu",vmin=0,vmax=(arr.max() if field=="tau" else 1),aspect="auto")
        for iy in range(3):
            for ix in range(3): ax.text(ix,iy,f"{arr[iy,ix]:.3f}",ha="center",va="center",fontsize=7,color="black")
        ax.set_xticks(range(3),[".05",".50",".95"]); ax.set_yticks(range(3),[".06",".14",".18"]); ax.set_xlabel("Dose anchor (N)"); ax.set_ylabel("Strength anchor"); ax.set_title(title); fig.colorbar(im,ax=ax,fraction=.046,pad=.03)
    z[z.design.isin([x[0] for x in dose+strength]+list(joint.values()))].to_csv(DATA/"figure3_data.csv",index=False)
    fig.suptitle("Equalization diagnosis is robust, but remaining signal depends on the anchor",y=.995,fontsize=11,weight="bold")
    save(fig,"figure3_anchor_sensitivity")

def figure4():
    m=pd.read_csv(AN/"factor_metrics.csv")
    designs=["C-D50","CS-45","E-S","E-SD"]; labels={"topology":"Topology","message_condition":"Message","inoculation":"Inoculation","seeding_regime":"Seeding"}
    fig,axs=plt.subplots(2,2,figsize=(7.2,6.2),sharey=True); axs=axs.ravel()
    for ax,design in zip(axs,designs):
        q=m[(m.design==design)&(m.outcome=="mean_total_shift")]
        x=np.arange(4); main=[q[(q.factor==f)&(q.allocation=="main")].p_sys.iloc[0] for f in FACTORS_LOCAL]
        sha=[q[(q.factor==f)&(q.allocation=="shapley")].p_sys.iloc[0] for f in FACTORS_LOCAL]
        ax.bar(x-.18,main,.36,label="Main effect",color=COL["sky"]); ax.bar(x+.18,sha,.36,label="Shapley",color=COL["blue"])
        ax.set_xticks(x,[labels[f] for f in FACTORS_LOCAL],rotation=15,ha="right"); ax.set_title(design,pad=8); ax.set_ylim(0,1.05); ax.grid(axis="y",alpha=.2)
    axs[0].set_ylabel("Share of systematic SS"); axs[2].set_ylabel("Share of systematic SS"); axs[0].legend(frameon=False,fontsize=8)
    fig.subplots_adjust(hspace=.58,wspace=.20,top=.91,bottom=.09)
    fig.suptitle("Shapley allocation makes interaction-bundled importance visible",y=.985,fontsize=11,weight="bold")
    m[(m.design.isin(designs))&(m.outcome=="mean_total_shift")].to_csv(DATA/"figure4_data.csv",index=False)
    save(fig,"figure4_main_vs_shapley")

FACTORS_LOCAL=["topology","message_condition","inoculation","seeding_regime"]

def figure5():
    m=pd.read_csv(AN/"factor_metrics.csv"); d=pd.read_csv(ROOT/"data"/"combined_runs_120960.csv.gz",usecols=["design","seeding_regime","mean_total_shift"])
    mapping={"CS-0":0,"PC-M01":.01,"PC-M05":.05}
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.2))
    q=m[(m.outcome=="mean_total_shift")&(m.factor=="seeding_regime")&(m.design.isin(mapping))]
    for kind,label,c in [("main","Main effect",COL["sky"]),("shapley","Shapley",COL["blue"])]:
        y=[q[(q.design==n)&(q.allocation==kind)].p_sys.iloc[0] for n in mapping]
        axs[0].plot(list(mapping.values()),y,marker="o",lw=2,label=label,color=c)
    axs[0].set(xlabel="Opinion-reversion parameter, μ",ylabel="Seeding share of systematic SS",title="A. Timing contribution"); axs[0].grid(axis="y",alpha=.2); axs[0].legend(frameon=False)
    means=d[d.design.isin(mapping)].groupby(["design","seeding_regime"],as_index=False).mean(); means["mu"]=means.design.map(mapping)
    for reg,c in [("single_shot",COL["orange"]),("burst",COL["green"]),("continuous",COL["purple"])]:
        s=means[means.seeding_regime==reg].sort_values("mu"); axs[1].plot(s.mu,s.mean_total_shift,marker="o",lw=2,label=reg.replace("_"," "),color=c)
    axs[1].set(xlabel="Opinion-reversion parameter, μ",ylabel="Mean total shift at T=50",title="B. Endpoint regime means"); axs[1].grid(axis="y",alpha=.2); axs[1].legend(frameon=False,fontsize=8)
    fig.subplots_adjust(wspace=.24,top=.82)
    fig.suptitle("Positive control: timing survives equalization under constructed opinion reversion",y=.98,fontsize=11,weight="bold")
    q.to_csv(DATA/"figure5_contribution_data.csv",index=False); means.to_csv(DATA/"figure5_outcome_data.csv",index=False)
    save(fig,"figure5_positive_control")

def figure6():
    d=pd.read_csv(ROOT/"data"/"combined_runs_120960.csv.gz",usecols=["design","seeding_regime","cumulative_total_shift_by_step"])
    d=d[d.design=="CS-0"].copy(); rows=[]
    for reg,g in d.groupby("seeding_regime"):
        arr=np.vstack([np.asarray(ast.literal_eval(x),float) for x in g.cumulative_total_shift_by_step])
        mean=arr.mean(axis=0); se=arr.std(axis=0,ddof=1)/np.sqrt(arr.shape[0])
        for t,(mm,ss) in enumerate(zip(mean,se),1): rows.append({"seeding_regime":reg,"step":t,"mean":mm,"lo95":mm-1.96*ss,"hi95":mm+1.96*ss})
    q=pd.DataFrame(rows); fig,ax=plt.subplots(figsize=(7.2,3.4))
    for reg,c in [("single_shot",COL["orange"]),("burst",COL["green"]),("continuous",COL["purple"])]:
        s=q[q.seeding_regime==reg]; ax.plot(s.step,s["mean"],lw=2,label=reg.replace("_"," "),color=c); ax.fill_between(s.step,s.lo95,s.hi95,color=c,alpha=.14)
    ax.set(xlabel="Simulation step",ylabel="Cumulative mean total opinion shift",title="Equal total dose preserves distinct temporal paths (CS-0, 0.50N)"); ax.grid(axis="y",alpha=.2); ax.legend(frameon=False)
    q.to_csv(DATA/"figure6_data.csv",index=False); save(fig,"figure6_equal_dose_trajectories")

if __name__=="__main__":
    figure1(); figure2(); figure3(); figure4(); figure5(); figure6(); print("created 6 figures")



