import os
import matplotlib.pyplot as plt
import numpy as np

from ..config import *
from ..parser import *
from ..main import *

from .stats_utils import *

figsize = (10,6)
xlabel = 'ADC'
ylabel = 'Counts'


def empty_channel_hist(ax, ch_id, interval_type, filename, dir_output_plot_keys):
    ax.set_title(f"Ch{ch_id:02d} (EMPTY)")
    ax.grid(True, linestyle="--", alpha=0.4)

    fig_single = plt.figure(figsize=figsize)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(f'Histogram ADC Ch{ch_id:02d} - {interval_type} (EMPTY) - {filename}')
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.savefig(
        os.path.join(
            dir_output_plot_keys,
            f'{interval_type} - Histogram ADC Ch{ch_id:02d} - {filename}.png'
        ), dpi = dpi
    )
    plt.close(fig_single)
    return


def channel_hist(df_ch, ax, bins, ch_id, interval_type, filename, dir_output_plot_keys):
    n_points, df_ch_mean, df_ch_std, err_mean, err_std = compute_stats(df_ch)

    ax.hist(df_ch['adc'], bins, edgecolor='black', align='left')
    ax.set_title(fr"Ch{ch_id:02d} ($\mu$ = {df_ch_mean})")
    ax.grid(True, linestyle="--", alpha=0.4)

    ticks = np.linspace(min(bins), max(bins), 5, dtype=int)
    fig_single = plt.figure(figsize=figsize)
    plt.hist(df_ch['adc'], bins, edgecolor='black', align='left')
    plt.title(fr'Histogram ADC Ch{ch_id:02d} - {interval_type} ($\mu$ = {df_ch_mean} - $\sigma$ = {df_ch_std}) - {filename}')
    plt.xlabel(xlabel)
    plt.xticks(ticks)
    plt.ylabel(ylabel)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.savefig(
        os.path.join(
            dir_output_plot_keys,
            f'{interval_type} - Histogram ADC Ch{ch_id:02d} - {filename}.png'
        ), dpi = dpi
    )
    plt.close(fig_single)  
    return


def process_channel_hist(
        DataFrame,
        min_adc, max_adc,
        idx, ch_id,
        axes, interval_type,
        filename, dir_output_plot_keys
):
    df_ch = DataFrame.loc[(DataFrame.channel == idx) & (min_adc < DataFrame.adc) & (DataFrame.adc < max_adc)]
    ax = axes[idx]

    # Se non ci sono dati
    if df_ch.empty:
        empty_channel_hist(ax, ch_id, interval_type, filename, dir_output_plot_keys)
        return
    
    if fixed_range_x:
        bins = range(min_adc, max_adc)
    else:
        hist_min = df_ch['adc'].min()
        hist_max = df_ch['adc'].max() + 2
        bins = range(hist_min, hist_max)

    channel_hist(df_ch, ax, bins, ch_id, interval_type, filename, dir_output_plot_keys)


def save_combined_plot(fig, interval_type, filename, dir_output_plot):
    fig.suptitle(f"Histogram ADC BOARD '{interval_type}' — {filename}", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    plt.savefig(
        os.path.join(
            dir_output_plot, f'Histogram ALL CHANNELS - {interval_type} - {filename}.png'
        ), dpi = dpi
    )
    plt.close()


def plot_hist(DataFrame, dir_path, filename, fixed_range_x, fixed_range_y):
    dir_output_plot = os.path.join(dir_path, "plots")

    for interval_type, interval_range in INTERVALS.items():
        min_adc, max_adc = interval_range
        dir_output_plot_keys = os.path.join(dir_output_plot, interval_type)
        ensure_directory(dir_output_plot_keys)

        # Preparazione griglia per subplot
        fig, axes = plt.subplots(4, 5, figsize=(15, 9), sharex=fixed_range_x, sharey=fixed_range_y)
        axes = axes.flatten()

        for idx, ch_id in enumerate(NUMB_CHANNELS): 
            process_channel_hist(DataFrame,min_adc,max_adc,idx,ch_id,axes,interval_type,filename,dir_output_plot_keys)

        save_combined_plot(fig, interval_type, filename, dir_output_plot)