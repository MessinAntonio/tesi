# Per farlo partire:
# cd C:/Users/messi/UNI/Tesi/scripts/project>
# py -m src.main

# ==== IMPORT ====
import logging
import matplotlib.pyplot as plt
import math
import json

from pprint import pprint

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
    process_data_raw_dir()

if __name__ == "__main__":
    main()