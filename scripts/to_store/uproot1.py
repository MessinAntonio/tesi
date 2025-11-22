import uproot
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
import json

# ==== PARSING ARGOMENTI DA LINEA DI COMANDO ====
parser = argparse.ArgumentParser(description = "Analisi ADC schede")
parser.add_argument(
    "--fixed_range", "-r",
    action="store_true",
    help = "Se True usa un range ADC fisso (800-1100). Se False usa un range variabile basato sui dati."
)
parser.add_argument(
    "--DEBUG", "-d", 
    action="store_true",
    help = "Abilita (True) o disabilita (False) la stampa dei messaggi di debug."
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
fixed_range = args.fixed_range

config = {
    "config": {
        "pedestal_range": intervals["pedestal"],
        "pulse_range": intervals["pulse"],
        "fixed_range": fixed_range
    }
}

# ==== DIRECTORY DEI FILE DA ANALIZZARE ====
input_dir = "mpmt-board-cli_fileROOT"

ALL_RESULTS = {}

for file in os.listdir(input_dir):
    input_file_path = os.path.join(input_dir, file)

    file_to_analyze = os.path.splitext(os.path.basename(input_file_path))[0] # Prendiamo il nome del file senza estensione.
    output_file_name = f"mean_dev_{file_to_analyze}"

    # Directory dove salvare tutti i file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, file_to_analyze)
    output_plot_dir = os.path.join(output_dir, "plots")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(output_plot_dir, exist_ok=True)

    # ==== PER JSON SINGOLI ====
    results = {
        **config,
        file_to_analyze: {
            key: {} for key in intervals.keys()
        }
    }

    # ==== COSE PER ROOT ====
    tree_name = "pmt_events"
    file = uproot.open(input_file_path)
    tree = file[tree_name]

    ch = tree["channel"].array(library="np") + 1 
    adc = tree["adc"].array(library="np")
    df = pd.DataFrame({
        "ch": ch,
        "adc": adc
    })
    df.to_csv(os.path.join(output_dir, f"{file_to_analyze}.csv"), index=False)

    channels = range(1,20)
    for keys, values in intervals.items():
        min_adc = values[0]
        max_adc = values[1]
        for ch_id in channels:
            bins = None
            df_ch = df.loc[(df.ch == ch_id) & (min_adc < df.adc) & (df.adc < max_adc)] 
            # Se non ci sono dati
            if df_ch.empty:
                results[file_to_analyze][keys][f"{ch_id:02d}"] = None

                # --- Istogramma vuoto ---
                plt.figure(figsize=(10,6))
                plt.hist(df_ch['adc'], bins, edgecolor='black', align='left')
                plt.xlabel('ADC')
                plt.ylabel('Counts')
                plt.title(f'Histogram ADC Ch{ch_id:02d} - {keys} (EMPTY) - {file_to_analyze}')
                plt.grid(True, alpha = 0.3)
                plt.savefig(
                    os.path.join(
                        output_plot_dir,
                        f'{keys} - Histogram ADC Ch{ch_id:02d} - {file_to_analyze}.png'
                    )
                )
                plt.close()
                continue

            df_ch_mean = df_ch.adc.mean()
            df_ch_std = df_ch.adc.std(ddof = 0)
            df_ch_point = len(df_ch.adc)

            results[file_to_analyze][keys][f"{ch_id:02d}"] = {
                "mean": df_ch_mean,
                "std": df_ch_std,
                "n_points": df_ch_point
            }

            if fixed_range:
                bins = range(min_adc, max_adc)
            else:
                bins = range(df_ch['adc'].min(), df_ch['adc'].max() + 2)

            # --- istogramma ---
            plt.figure(figsize=(10,6))
            plt.hist(df_ch['adc'], bins, edgecolor='black', align='left')
            plt.title(f'Histogram ADC Ch{ch_id:02d} - {keys} (Mean: {df_ch_mean:.2f} - Std Dev: {df_ch_std:.2f}) - {file_to_analyze}')
            plt.xlabel('ADC')
            plt.ylabel('Counts')
            plt.xticks(bins)
            plt.grid(True, alpha = 0.3)
            plt.savefig(
                os.path.join(
                    output_plot_dir,
                    f'{keys} - Histogram ADC Ch{ch_id:02d} - {file_to_analyze}.png'
                )
            )
            plt.close()

    with open(os.path.join(output_dir, f"{output_file_name}_stats.json"), "w") as f_json:
        json.dump(results, f_json, indent=4)

    ALL_RESULTS.update(results)

with open("ALL_RESULTS.json", "w") as f_all:
    json.dump(ALL_RESULTS, f_all, indent=4)







# salva i singoli plot e la schermata con tutti i plot.
# salva su json medie e dev dei canali. ci devono essere sempre 19 voci per i canali. Se nel file root non ci sono indica un fail.
# Ripeti questa procedura per tot scjede e poi analizziamo medie e deviazioni per ottenere dei valori di validazione della scheda.


# Volgiamo differenza tra, non ci sono dati oppure non c'è proprio il canale?












# ch_pedestal = ch[(200 < adc) & (adc < 350)]
# adc_pedestal = adc[(200 < adc) & (adc < 350)]
# ch_puls = ch[(800 < adc) & (adc < 1100)]
# adc_puls = adc[(800 < adc) & (adc < 1100)]

# channels=range(1,20)
# # for idx, ch_id in enumerate(channels):
# #     printDebug(f"info: indice {idx}")
# #     printDebug(f"info: valore {ch_id:02d}")
# #     adc_ch = adc_puls[ch_puls == ch_id]
# #     printDebug(f"info: len {len(adc_ch)}")
# #     printDebug(f"{adc_ch}\n")

# # # # Read into a pandas DataFrame
# # printDebug(adc)
# # printDebug(adc_pedestal)
# # printDebug(adc_puls)
# # #df = tree.arrays(library="pd")
# # #print(df.head())

# bin_width=10

# #  # --- Determine histogram range ---
# # if np.size(adc) > 0:
# #     hist_min = int(np.min(adc) - 5 * bin_width)
# #     hist_max = int(np.max(adc) + 5 * bin_width)
# # else:
# #     hist_min, hist_max = 0, 4095 

# hist_min, hist_max = 0, 4095

# bin_edges = None
# fixed_range = True
#     # --- Determine bin edges ---
# if bin_edges is None:
#     if fixed_range:
#         bin_edges = np.arange(hist_min, hist_max + bin_width, bin_width, dtype=int)
#     else:
#         bin_edges = None
# else:
#     bin_width = bin_edges[1] - bin_edges[0]


#   # --- Prepare figure ---
# fig, axes = plt.subplots(4, 5, figsize=(15, 9), sharex=fixed_range, sharey=fixed_range)
# axes = axes.flatten()

#     # --- Plot each channel ---
# for idx, ch_id in enumerate(channels):
#     ax = axes[idx]
#     adc_ch = adc_puls[ch_puls == ch_id]
#     #print(ch_id, adc_ch)

#     if adc_ch.size == 0:
#         ax.set_title(f"Ch {ch_id:02d} (no data)")
#         ax.grid(True, linestyle="--", alpha=0.4)
#         continue

#         # Per-channel bin edges if not fixed
#     if bin_edges is None:
#         ch_min = int(np.min(adc_ch) - 3 * bin_width)
#         ch_max = int(np.max(adc_ch) + 3 * bin_width)
#         edges = np.arange(ch_min, ch_max + bin_width, bin_width, dtype=int)
#     else:
#         edges = bin_edges

#     counts, edges = np.histogram(adc_ch, bins=edges)
#     centers = 0.5 * (edges[:-1] + edges[1:])

#         # --- Draw histogram ---
#     ax.bar(
#         centers, counts,
#         width=bin_width, color="salmon", alpha=0.5,
#         edgecolor="black", linewidth=0.4, label="Data"
#     )

#     ax.set_title(f"Ch {ch_id:02d}", fontsize=9)
#     ax.set_xlabel("ADC")
#     ax.set_ylabel("Counts")
#     ax.grid(True, linestyle="--", alpha=0.4)
    
#     # --- Remove unused subplot (for 19 channels) ---
# if len(axes) > 19:
#     fig.delaxes(axes[19])

#     # --- Beautify ---
# fig.suptitle(
#     f"ADC histograms with Gaussian fits — {os.path.basename(root_file)}",
#     y=0.98,
#     )
# plt.tight_layout(rect=[0, 0, 1, 0.96])

# #plt.savefig(save, dpi=200, bbox_inches="tight")
# plt.show()