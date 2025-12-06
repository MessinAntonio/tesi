# Per farlo partire:
# cd C:/Users/messi/UNI/Tesi/scripts/project>
# py -m src.main

# ==== IMPORT ====
import json

# ==== IMPORT VARIABILI E FILE ====
from .parser import *
from .config import *
from .utils.root_processor import *
from .utils.plot_hist import *
from .utils.build_json import *

def main():

    for dir in REQUIRED_DIRS:
        ensure_directory(dir)

    clean_processed_if_reset()

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
    for file_raw in os.listdir(DATA_RAW_DIR):
        file_raw_path = os.path.join(DATA_RAW_DIR, file_raw)

        if os.path.isfile(file_raw_path) and file_raw.endswith(".root"):
            json_single_file = process_raw_file(file_raw_path, PROCESSED_DATA_DIR, fixed_range_x, fixed_range_y)
            if json_single_file:
                ALL_RESULTS.update(json_single_file)

    with open(json_all_file_name, "w") as json_all:
        json.dump(ALL_RESULTS, json_all, indent=4, separators=(",", ": ")) 

if __name__ == "__main__":
    main()