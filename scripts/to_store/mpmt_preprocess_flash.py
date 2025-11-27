import uproot
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
import json
import time
import math

# ==== PARSING ARGOMENTI DA LINEA DI COMANDO ====
parser = argparse.ArgumentParser(description = "Analisi ADC schede")
parser.add_argument(
    "-x", "--fixed_range_x",
    action="store_true",
    help = "Se selezionato, l'asse X degli istogrammi avrà un range fisso basato sull'intervallo definito (pedestal/pulse)."
)
parser.add_argument(
    "-y", "--fixed_range_y",
    action="store_true",
    help = "Se selezionato, l'asse Y degli istogrammi avrà un range fisso basato sul valore di frequenza massimo registrato."
)
parser.add_argument(
    "-d", "--DEBUG", 
    action="store_true",
    help = "Se selezionato, stampa informazioni di debug durante l'esecuzione."
)
args = parser.parse_args()

# ==== PER DEBUG ====
DEBUG = args.DEBUG
def printDebug(x):
    if DEBUG:
        print(x)

# ==== CONFIGURAZIONE ==== 
intervals = {
    "pedestal": [200,400],
    "pulse": [800,1100]
}

fixed_range_x = args.fixed_range_x
fixed_range_y = args.fixed_range_y
dpi = 200

input_dir = "mpmt-board-cli_fileROOT"
files = os.listdir(input_dir)
string = "Seleziona file da analizzare:\n"

for i in range(len(files)):
    string += f" - Digita '{i}' per {files[i]}\n"
print(string)

idx_file = int(input())
file_name = files[idx_file]

print(f"hai scelto il file {file_name}")

# ==== COSE PER ROOT ====
input_file_path = os.path.join(input_dir, file_name)
tree_name = "pmt_events"
file = uproot.open(input_file_path)
tree = file[tree_name]

ch = tree["channel"].array(library="np") + 1 
adc = tree["adc"].array(library="np")
df = pd.DataFrame({
    "ch": ch,
    "adc": adc
})

print(df)

channels = range(1,20)
for keys, values in intervals.items():
    min_adc = values[0]
    max_adc = values[1]

    # Preparazione griglia per subplot
    fig, axes = plt.subplots(4, 5, figsize=(10, 6), sharex=fixed_range_x, sharey=fixed_range_y)
    axes = axes.flatten()
    
    for idx, ch_id in enumerate(channels): 
        printDebug(f"info: Analisi dei {keys} per canale {ch_id} di file '{os.path.basename(input_file_path)}'")

        bins = None
        df_ch = df.loc[(df.ch == ch_id) & (min_adc < df.adc) & (df.adc < max_adc)] 
        df_ch_mean = df_ch["adc"].mean()
        ax = axes[idx]

        # Se non ci sono dati
        if df_ch.empty:
            # subplot
            ax.set_title(f"Ch{ch_id:02d} (EMPTY)")
            ax.grid(True, linestyle="--", alpha=0.4)
            continue

        if fixed_range_x:
            bins = range(min_adc, max_adc)
        else:
            hist_min = df_ch['adc'].min()
            hist_max = df_ch['adc'].max() + 2
            bins = range(hist_min, hist_max)

        ax.hist(df_ch['adc'], bins, edgecolor='black', align='left')
        ax.set_title(fr"Ch{ch_id:02d} ($\mu$ = {df_ch_mean:.2f})")
        ax.grid(True, linestyle="--", alpha=0.4)

    fig.suptitle(f"Histogram ADC BOARD '{keys}' — {file_name}", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show(block=False)
    plt.pause(0.01)
    # plt.close()

input()