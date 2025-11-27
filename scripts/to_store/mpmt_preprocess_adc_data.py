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
parser.add_argument(
    "-r", "--RESET", 
    action="store_true",
    help = "Se selezionato, riesegue tutto il programma per tutti i file ignorando se questi sono già stati analizzati."
)
args = parser.parse_args()

RESET = args.RESET

# ==== PER DEBUG ====
DEBUG = args.DEBUG
def printDebug(x):
    if DEBUG:
        print(x)

# ========== PER SALVATAGGIO STATISTICHE IN JSON ==========
EMPTY_STATS = {
    "mean": None,
    "std": None,
    "err_mean": None,
    "err_std": None,
    "n_points": None
}

def round_sig(x, sig=1):
    if x == 0 or x is None:
        return 0
    return round(x, sig - int(math.floor(math.log10(abs(x)))) - 1)

# ==== STATISTICHE ==== 
def compute_stats(series):
    if series.empty:
        return EMPTY_STATS.copy()
    
    n_points = len(series)
    mean = series.mean()
    std = series.std()
    err_mean = std/math.sqrt(n_points)

    # std = round(std, -math.floor(math.log10(abs(std))))

    # ordine_mean = math.floor(math.log10(abs(err_mean)))
    # err_mean = round(err_mean, -ordine_mean)
    # mean = round(mean, -ordine_mean)
    
    return {
        "mean": mean,
        "std": std,
        "err_mean": err_mean,
        "err_std": 0,
        "n_points": n_points
    }

# ==== RIEPILOGO ====
def compute_summary(series):
    if series.empty:
        return None
    return series.value_counts().sort_index().to_dict()

# ==== CONFIGURAZIONE ==== 
intervals = {
    "pedestal": [200,400],
    "pulse": [800,1100]
}

fixed_range_x = args.fixed_range_x
fixed_range_y = args.fixed_range_y
dpi = 200

# ==== DIRECTORY DEI FILE DI INPUT E OUTPUT ====
input_dir = "mpmt-board-cli_fileROOT"
output_dir = f"{input_dir}_analyzed"
os.makedirs(output_dir, exist_ok=True)

# Carica il JSON finale se esiste già
all_results_file = "ALL_RESULTS.json"
if os.path.exists(all_results_file):
    with open(all_results_file, "r") as f:
        ALL_RESULTS = json.load(f)
else:
    ALL_RESULTS = {}

for file in os.listdir(input_dir):
    input_file_path = os.path.join(input_dir, file)
    file_to_analyze = os.path.splitext(os.path.basename(input_file_path))[0] # Prendiamo il nome del file senza estensione.
    output_file_name = f"mean_dev_{file_to_analyze}"
    print(f"info: inzio analisi file '{os.path.basename(input_file_path)}'")
    
    config = {
        "configure": {
            "pedestal_range": intervals["pedestal"],
            "pulse_range": intervals["pulse"],
            "time": time.strftime("%Y%m%d_%H%M%S", time.localtime())
        }
    }

    # Directory dove salvare tutti i file
    output_sub_dir = os.path.join(output_dir, file_to_analyze)

    # Se già presente nel JSON e cartella e non vogliamo fare reset, saltare analisi
    if os.path.exists(output_sub_dir) and file_to_analyze in ALL_RESULTS and not RESET:
        printDebug(f"File '{file_to_analyze}' già analizzato, passo al prossimo.")
        continue

    output_plot_dir = os.path.join(output_sub_dir, "plots")
    os.makedirs(output_sub_dir, exist_ok=True)
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
    df.to_csv(os.path.join(output_sub_dir, f"{file_to_analyze}.csv"), index=False)

    channels = range(1,20)
    for keys, values in intervals.items():
        printDebug(f"info: Analisi dei {keys} per file '{os.path.basename(input_file_path)}'")
        min_adc = values[0]
        max_adc = values[1]
        output_plot_dir_keys = os.path.join(output_plot_dir, keys)
        os.makedirs(output_plot_dir_keys, exist_ok=True)

        # Preparazione griglia per subplot
        fig, axes = plt.subplots(4, 5, figsize=(15, 9), sharex=fixed_range_x, sharey=fixed_range_y)
        axes = axes.flatten()

        for idx, ch_id in enumerate(channels): 
            printDebug(f"info: Analisi dei {keys} per canale {ch_id} di file '{os.path.basename(input_file_path)}'")

            bins = None
            df_ch = df.loc[(df.ch == ch_id) & (min_adc < df.adc) & (df.adc < max_adc)] 
            ax = axes[idx]

            stats = compute_stats(df_ch.adc)
            summary = compute_summary(df_ch.adc)

            # Se non ci sono dati
            if df_ch.empty:
                results[file_to_analyze][keys][f"{ch_id:02d}"] = {
                    "stats": stats,
                    "summary": summary 
                }

                # subplot
                ax.set_title(f"Ch{ch_id:02d} (EMPTY)")
                ax.grid(True, linestyle="--", alpha=0.4)

                printDebug(f"info: Creazione istogramma vuoto per {keys} di canale {ch_id}")
                # Istogramma vuoto
                plt.figure(figsize=(10,6))
                plt.xlabel('ADC')
                plt.ylabel('Counts')
                plt.title(f'Histogram ADC Ch{ch_id:02d} - {keys} (EMPTY) - {file_to_analyze}')
                plt.grid(True, linestyle="--", alpha=0.4)
                plt.savefig(
                    os.path.join(
                        output_plot_dir_keys,
                        f'{keys} - Histogram ADC Ch{ch_id:02d} - {file_to_analyze}.png'
                    ), dpi = dpi
                )
                plt.close()
                continue

            results[file_to_analyze][keys][f"{ch_id:02d}"] = {
                "stats": stats,
                "summary": summary 
            }

            if fixed_range_x:
                bins = range(min_adc, max_adc)
            else:
                hist_min = df_ch['adc'].min()
                hist_max = df_ch['adc'].max() + 2
                bins = range(hist_min, hist_max)

            df_ch_mean = stats.get("mean")
            df_ch_std = stats.get("std")

            ax.hist(df_ch['adc'], bins, edgecolor='black', align='left')
            ax.set_title(fr"Ch{ch_id:02d} ($\mu$ = {df_ch_mean:.2f})")
            ax.grid(True, linestyle="--", alpha=0.4)

            printDebug(f"info: Creazione istogramma per {keys} di canale {ch_id}")
            # istogramma
            plt.figure(figsize=(10,6))
            plt.hist(df_ch['adc'], bins, edgecolor='black', align='left')
            plt.title(fr'Histogram ADC Ch{ch_id:02d} - {keys} ($\mu$ = {df_ch_mean:.2f} - $\sigma$ = {df_ch_std:.2f}) - {file_to_analyze}')
            plt.xlabel('ADC')
            plt.ylabel('Counts')
            plt.xticks(bins)
            plt.grid(True, linestyle="--", alpha=0.4)
            plt.savefig(
                os.path.join(
                    output_plot_dir_keys,
                    f'{keys} - Histogram ADC Ch{ch_id:02d} - {file_to_analyze}.png'
                ), dpi = dpi
            )
            plt.close()

        fig.suptitle(f"Histogram ADC BOARD '{keys}' — {file_to_analyze}", y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig(os.path.join(output_plot_dir,
                                 f'{keys} - Histogram ALL CHANNELS - {file_to_analyze}.png'),
                    dpi=dpi)
        # plt.show()
        plt.close()

    with open(os.path.join(output_sub_dir, f"{output_file_name}_stats.json"), "w") as f_json:
        json.dump(results, f_json, indent=4)
 
    ALL_RESULTS[file_to_analyze] = {
        "configure": config["configure"],
        **results[file_to_analyze]
    }

    print(f"info: fine analisi file '{os.path.basename(input_file_path)}'")

with open("ALL_RESULTS.json", "w") as f_all:
    json.dump(ALL_RESULTS, f_all, indent=4)


# Aggiungere un sommario per ogni file analizzato in cui inseriamo quanti canali hanno dati dati e quanti vuoti
# Sistemare le cifre significative di media e varianza. Serve per step successivo


# analizza sono un file, stampa a temrinale i valori, tramite parser decidi quale file analizzare e decidi se far visualizzare o meno i plot. Non deve salvare niente. 