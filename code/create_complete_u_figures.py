"""Figures for complete-U estimator validation."""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]; AN=ROOT/'analysis_outputs'; FIG=ROOT/'figures'

def split_figure():
    x=pd.read_csv(AN/'bootstrap_split_count_sensitivity.csv')
    colors={'E-SD':'#0072b2','J-S06-D05':'#d55e00','J-S18-D05':'#009e73'}
    fig,ax=plt.subplots(1,2,figsize=(8.4,3.7))
    for d,g in x.groupby('design',sort=False):
        g=g.sort_values('splits_per_draw'); c=colors[d]
        ax[0].plot(g.splits_per_draw,g.point_absolute_difference,marker='o',color=c,label=d)
        ax[1].plot(g.splits_per_draw,g.range_width,marker='o',color=c,label=d)
    ax[0].set_title('A. Distance from complete-U point')
    ax[0].set_ylabel('Absolute difference in seeding q')
    ax[1].set_title('B. Incomplete-split bootstrap range width')
    ax[1].set_ylabel('2.5th–97.5th range width')
    for a in ax:
        a.set_xlabel('Balanced splits per estimate'); a.set_yscale('log'); a.grid(axis='y',alpha=.2)
    ax[0].legend(frameon=False,fontsize=8)
    fig.suptitle('Random split averaging converges toward the complete cross-replication estimator',y=1.02,fontsize=11,weight='bold')
    fig.tight_layout(); fig.savefig(FIG/'figure5_split_count_sensitivity.png',dpi=300,bbox_inches='tight'); plt.close(fig)

def toy_figure():
    t=pd.read_csv(AN/'toy_complete_u_validation.csv')
    non=t[t.factor!='D'].groupby(['noise','R','estimator'],as_index=False).agg(rmse=('rmse','mean'))
    null=t[t.factor=='D'].copy()
    fig,ax=plt.subplots(1,2,figsize=(8.4,3.7))
    styles={'in-sample':('#d55e00','--'),'complete-U':('#0072b2','-')}
    for est,g in non[non.noise=='homoskedastic'].groupby('estimator'):
        c,ls=styles[est]; ax[0].plot(g.R,g.rmse,marker='o',color=c,ls=ls,label=est)
    for est,g in null[null.noise=='homoskedastic'].groupby('estimator'):
        c,ls=styles[est]; ax[1].plot(g.R,g.bias.abs(),marker='o',color=c,ls=ls,label=est)
    ax[0].set_title('A. Mean RMSE, non-null factors'); ax[0].set_ylabel('RMSE of B allocation')
    ax[1].set_title('B. Absolute bias, null factor D'); ax[1].set_ylabel('Absolute bias')
    for a in ax: a.set_xlabel('Replications per cell'); a.grid(axis='y',alpha=.2)
    ax[0].legend(frameon=False,fontsize=8)
    fig.suptitle('Known-truth validation of the complete cross-replication estimator',y=1.02,fontsize=11,weight='bold')
    fig.tight_layout(); fig.savefig(FIG/'figure6_complete_u_toy_validation.png',dpi=300,bbox_inches='tight'); plt.close(fig)

if __name__=='__main__': split_figure(); toy_figure(); print('created complete-U figures')

