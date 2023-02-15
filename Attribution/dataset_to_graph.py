#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# グラフを表示する
# %%
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime
import json

if __name__=='__main__':
    import sys
    sys.path.append('../')
    from Smoothing import whittaker_smooth
else:
    from ..Smoothing import whittaker_smooth

# %%
def dataset_to_graph(dataset_path, year_range=(2001, 2005)):
    # データセットの読み込み
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    print(f'LULC:{dataset["LULC"]["values"]}')
    
    # NDVI関連のデータ整形
    NDVI_get    = np.array(dataset['NDVI']['values'])
    NDVI_arr    = whittaker_smooth(NDVI_get, lmbd=1)
    NDVI_date   = pd.to_datetime(dataset['NDVI']['date'])
    NDVI_mean   = np.array(
        list(np.nanmean(NDVI_arr.reshape(-1, 23), axis=0))*20).flatten()
    NDVI_std    = np.array(
        list(np.nanstd(NDVI_arr.reshape(-1, 23), axis=0))*20).flatten()

    # CCIs関連のデータ読み込み
    mR95pT_arr  = np.array(dataset['mR95pT']['values'])
    mR95pT_date = pd.to_datetime(dataset['mR95pT']['date'])
    SPI3_arr    = np.array(dataset['SPI3']['values'])
    SPI3_date   = pd.to_datetime(dataset['SPI3']['date'])

    # グラフの作成
    # 1. 初期設定
    plt.rcParams['font.size']=16
    fig, ax = plt.subplots(2,1, figsize=(12, 11))
    plt.tight_layout(rect=(0.05, 0.05, 0.8, 0.93))


    # 2. 線の描写
    for i in range(2):
        # 2.1.1. SPI>=0の描写
        ax[i].fill_between(
            SPI3_date, np.where(SPI3_arr>=0, SPI3_arr,0), np.zeros_like(SPI3_arr),
            color='blue', alpha=0.3, label=['SPI>=0' if i==0 else None][0]
        )
        # 2.1.2. SPI<0の描写
        ax[i].fill_between(
            SPI3_date, np.where(SPI3_arr<0, SPI3_arr, 0), np.zeros_like(SPI3_arr),
            color='orange', alpha=0.3, label=['SPI<0' if i==0 else None][0]
        )
        # 2.2. mR95pT>0.5の描写
        ax[i].vlines(
            mR95pT_date[mR95pT_arr>0.5], ymin=-3, ymax=3,
            colors='red', label=['mR95pT>0.5' if i==0 else None][0]
            )
    # 2.3. NDVIの描写
    ax_ndvi = ax[0].twinx()
    ax_ndvi.fill_between(
        NDVI_date, NDVI_mean+NDVI_std, NDVI_mean-NDVI_std,
        color='black', alpha=0.3, label='NDVI ave+-std'
        )
    ax_ndvi.plot(
        NDVI_date, NDVI_mean,
        linestyle=':', linewidth=3, c='black', label='NDVI ave')
    ax_ndvi.plot(
        NDVI_date, NDVI_arr,
        c='green', linewidth=3, label='NDVI obs')
    ax[1].bar( NDVI_date, (NDVI_arr-NDVI_mean)/NDVI_std, color='green', width=3)
    ax[1].plot(NDVI_date, (NDVI_arr-NDVI_mean)/NDVI_std, c    ='green', marker='x', label='NDVI Z-score')


    # 3.描写範囲の設定
    for i in range(2):
        ax[i].set_xlim(datetime.datetime(year_range[0],1,1), datetime.datetime(year_range[1], 12, 31))
        ax[i].set_ylim(-3,3)
        ax_ndvi.set_ylim(0, 0.8)
    
    # 4.軸表示の設定
    for i in range(2):
        ax[i].set_xticks(
            pd.date_range(f'{year_range[0]}/1/1', f'{year_range[1]}/12/31', freq='YS'),
            [year for year in range(year_range[0], year_range[1]+1)])
        ax[i].grid()
    fig.supxlabel('Date', fontsize=20)
    ax[0].set_ylabel('SPI', fontsize=20)
    ax[1].set_ylabel('SPI & NDVI(Z-Score)', fontsize=20)
    ax_ndvi.set_ylabel('NDVI', fontsize=20)

    # 5.ラベルの表示設定
    fig.legend(bbox_to_anchor=(1.0,0.4))
    fig.suptitle(
        'Heavy Rain & NDVI {}~{}\n({}, lat:{},lon:{})'.format(
            year_range[0], year_range[1],
            dataset['meta']['name'],dataset ['meta']['lat'], dataset['meta']['lon']
        ),
        fontsize=24
    )
    return fig

if __name__=='__main__':

    start_year=2016
    fig = dataset_to_graph(
        '../../sample/dataset/Malawi1.json',
        year_range=(start_year, start_year+4))

    fig.savefig('../../img/Atribution.png')
# %%
