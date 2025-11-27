import json
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os

# ==== PARSING ARGOMENTI DA LINEA DI COMANDO ====
parser = argparse.ArgumentParser(description = "Analisi ADC schede")
parser.add_argument(
    "-d", "--DEBUG", 
    action="store_true",
    help = "Se selezionato, stampa informazioni di debug durante l'esecuzione. "
)
args = parser.parse_args()

# ==== PER DEBUG ====
DEBUG = args.DEBUG
def printDebug(x):
    if DEBUG:
        print(x)

dpi = 150

input_file = "C:/Users/messi/UNI/Tesi/scripts/to_store/ALL_RESULTS.json"
output_file = "C:/Users/messi/UNI/Tesi/scripts/to_develop/non_so_nome.csv"
output_dir = "plots"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r") as file_json:
    data = json.load(file_json)  

rows = []

for board_name, board_data in data.items(): 
    for measurement_type in ["pedestal", "pulse"]:
        if measurement_type in board_data:
            for channel, channel_info in board_data[measurement_type].items():
                stats = channel_info["stats"]
                row = {
                    "board": board_name,
                    "measurement_type": measurement_type,
                    "channel": channel
                }

                for stat_key, stat_value in stats.items():
                    row[stat_key] = stat_value

                rows.append(row) 

df = pd.DataFrame(rows)
df.to_csv(output_file, index=False)

data_types = ["mean", "std"]

# fai plot x vs y 
# x vaire schede
# y valore medio per canale
# ==== PLOT GIGI ====
for measurement_type in df["measurement_type"].unique():    
    df_measurement_type = df.loc[df.measurement_type == measurement_type]
    for channel in df_measurement_type["channel"].unique():
        df_channel = df_measurement_type.loc[df.channel == channel]
        for data_type in data_types:
            id = df_channel.columns.get_loc(data_type) + 2

            df_channel = df_channel.dropna()
            print(df_channel)

            plt.figure(figsize=(10,6))
            plt.errorbar(df_channel['board'], df_channel[data_type], df_channel.iloc[:, id], marker='o', color='blue', linestyle='')
            plt.xticks(rotation=45, ha='right')
            plt.ylabel(f'{data_type}')
            plt.xlabel('Board')
            plt.title(f'{data_type} vs board - Ch{channel} - {measurement_type}')
            plt.tight_layout()
            plt.savefig(
                os.path.join(
                    output_dir,
                    f'{data_type} vs board - Ch{channel} - {measurement_type}.png'
                ), dpi = dpi
            )
            # plt.show(block = False)
            # plt.pause(1)
            plt.close()

# calcoalre media di medie e deviazioni standard, con errore
# Graficarele per fare istogrammi e fit
