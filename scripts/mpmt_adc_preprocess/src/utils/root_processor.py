import logging
import uproot
import pandas as pd
import os

from ..config import *
from ..parser import *

from .plot_hist import *
from .stats_utils import *
from .build_json import *

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


def process_raw_file(file_path, dir_path, fixed_range_x, fixed_range_y):
    """Apre un file ROOT e lo esporta in CSV."""
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