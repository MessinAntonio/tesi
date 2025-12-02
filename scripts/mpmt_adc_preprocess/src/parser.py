import os
import argparse

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

fixed_range_x = args.fixed_range_x
fixed_range_y = args.fixed_range_y
DEBUG = args.DEBUG
RESET = args.RESET

# ==== MAIN ====
def main_parser():
    current_file = os.path.basename(__file__)
    print(f"Sono nel file: {current_file}")

if __name__ == "__main__":
    main_parser()