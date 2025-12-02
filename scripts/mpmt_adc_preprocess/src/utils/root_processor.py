import logging
import uproot
import pandas as pd
import os
import json
import math

from ..config import *
from ..parser import *

from .plot_hist import *
from .stats_utils import *

def process_branch(ttree):
    """Estrae tutti i branch di un Ttree in un DataFrame."""
    data_dict = {}

    for branch in ttree.keys():
        values = ttree[branch].array(library="np")
        data_dict[branch] = values

    df = pd.DataFrame(data_dict)
    return df


def save_df_csv(DataFrame, directory, ttree_name, filename):
    sub_dir_path = os.path.join(
        directory,
        f"{ttree_name[:-2]}"
    )
    ensure_directory(sub_dir_path)

    csv_path = os.path.join(
        sub_dir_path,
        f"{ttree_name[:-2]}_{filename}.csv"        
    )
    DataFrame.to_csv(csv_path, index=False)

    return sub_dir_path


def process_single_raw_file(file_path, dir_path, fixed_range_x, fixed_range_y):
    """Processa un singolo file ROOT e lo esporta in CSV."""
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    sub_dir_path = os.path.join(dir_path, file_name)

    if not RESET and os.path.exists(sub_dir_path):
        return
    
    ensure_directory(sub_dir_path) 

    try:
        with uproot.open(file_path) as file_root:
            for ttree_name in file_root.keys():
                ttree = file_root[ttree_name]

                df = process_branch(ttree)
                tree_name_dir_path = save_df_csv(df, sub_dir_path, ttree_name, file_name)

                # ==== BLOCCO JSON ====
                if "pmt_events" in ttree_name:
                    json_single_file = build_single_json(file_name, df, tree_name_dir_path, ttree_name)
                    plot_hist(df, tree_name_dir_path, file_name, fixed_range_x, fixed_range_y)

    except Exception as e:
        logging.error(f"Errore durante l'elaborazione del file {file_path}: {e}.")

    return json_single_file


def process_data_raw_dir():
    """Itera sulle cartelle di raw e processa tutti i file ROOT."""
    # Ispezioniamo ogni file nella cartella data\raw
    for dir_raw_name in os.listdir(DATA_RAW_DIR):
        dir_raw_path = os.path.join(DATA_RAW_DIR, dir_raw_name)

        # Se è una cartella, creiamo la cartella corrispondente in data\processed
        if os.path.isdir(dir_raw_path):
            dir_processed_path = os.path.join(PROCESSED_DATA_DIR, dir_raw_name)

            ensure_directory(dir_processed_path) # Creiamo la cartella in processed se non c'è

            # Carica il JSON finale se esiste già
            json_all_file_name = "../ALL_RESULTS.json"

            if os.path.exists(json_all_file_name):
                with open(json_all_file_name, "r") as f:
                    ALL_RESULTS = json.load(f)
            else:
                ALL_RESULTS = {}
                with open(json_all_file_name, "w") as file_all_json:
                    json.dump(ALL_RESULTS, file_all_json, indent=4)

            # Per ogni file in una cartella in data\raw, creiamo una cartella corrispondente in data\processed\
            for file_raw in os.listdir(dir_raw_path):
                file_raw_path = os.path.join(dir_raw_path, file_raw)

                if os.path.isfile(file_raw_path) and file_raw.endswith(".root"):
                    json_single_file = process_single_raw_file(file_raw_path, dir_processed_path, fixed_range_x, fixed_range_y)
                    if json_single_file:
                        ALL_RESULTS.update(json_single_file)

    with open(json_all_file_name, "w") as json_all:
        json.dump(ALL_RESULTS, json_all, indent=4) 