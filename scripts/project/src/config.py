import os
import logging
import shutil

# ==== IMPORT FILE ====
from .parser import *

# ==== DIRECTORY DEL PROGETTO ====
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = os.path.basename(PROJECT_ROOT) # Nome della directory base del progetto 

# ==== IMPOSTAZIONE DEI LOG ====
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, PROJECT_NAME)
logging.basicConfig(
    filename=f'{LOG_FILE_PATH}.log', 
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# ========== INPUT ==========
# ==== DIRECTORY ====
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# ========== OUTPUT ==========
# ==== DIRECTORY ====
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# ==== DIRECTORYS DA VERIFICARE ====
REQUIRED_DIRS = [
    DATA_DIR,           # Cartella in cui sono presenti i dati, da elaborare ed elaborati
    DATA_RAW_DIR,       # Cartella contenente i file da elaborare
    PROCESSED_DATA_DIR, # Cartella contenente diversi file estrapolati dai dati elaborati
    OUTPUT_DIR          # Cartella con gli output importanti (json)
]

# ==== INTERVALLI DI INTERESSE PER LE USCITE NUMERICHE DELL'ADC ====
INTERVALS = {
    "pedestal": [200,400], # Valori tipici per il piedistallo
    "pulse": [800,1100]    # Valori tipici per il segnale
} # I valori sono espressi in uscite numeriche dell'ADC (0-4095 per ADC a 12 bit)

NUMB_CHANNELS = range(1,20)
dpi = 200

# ==== FUNZIONE PER VERIFICARE LA PRESENZA DELLE CARTELLE NECESSARIE ====
def ensure_directory(directory: str) -> None:
    """Verifica la presenza della cartella necessaria e le crea se non esiste."""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def clean_processed_if_reset():
    """Se RESET è True, elimina TUTTE le cartelle e i file dentro PROCESSED_DATA_DIR."""
    if not RESET:
        return

    for name in os.listdir(PROCESSED_DATA_DIR):
        path = os.path.join(PROCESSED_DATA_DIR, name)

        if os.path.isfile(path):
            os.remove(path)

        elif os.path.isdir(path):
            shutil.rmtree(path)

# ==== FUNZIONE PER STAMPARE IL NOME DEL FILE ====
def main_config():
    current_file = os.path.basename(__file__)
    print(f"Sono nel file: {current_file}")

if __name__ == "__main__":
    main_config()