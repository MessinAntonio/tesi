import json
import pandas as pd
import matplotlib.pyplot as plt
import os

dpi = 150

input_file = "../ALL_RESULTS.json"
output_file = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_analyzer/mpmt_adc_channels.csv"
output_dir = "output"

os.makedirs(output_dir, exist_ok=True)

with open(input_file, "r") as file_json:
    json_data = json.load(file_json)  

rows = []

for board_name_key, board_name_value in json_data.items(): 
    for channel_id_key, channel_id_value in board_name_value.items():
        for measurement_type_key, measurement_type_value in channel_id_value.items():
            stats = measurement_type_value["stats"]
            row = {
            "board": board_name_key,
            "channel": channel_id_key,
            "measurement_type": measurement_type_key                    
            }

            for stat_key, stat_value in stats.items():
                row[stat_key] = stat_value

            rows.append(row) 

df = pd.DataFrame(rows)
df.to_csv(output_file, index=False)

data_types = ["mean", "std"]

# # ==== PLOT ====
for measurement_type in df["measurement_type"].unique():    
    df_measurement_type = df.loc[df.measurement_type == measurement_type]
    for channel in df_measurement_type["channel"].unique():
        df_channel = df_measurement_type.loc[df.channel == channel]
        for data_type in data_types:

            # Restituisce l'indice della colonna corrispondente all'errore sul valore che stiamo analizzando.
            # La formattazione adottata è la seguente:
            # dato_1, dato_2, ... , dato_N, err_dato_1, err_dato_2, ... , err_dato_N 
            column_id = df_channel.columns.get_loc(data_type) + len(data_types)

            df_channel = df_channel.dropna()
            print(df_channel)

            plt.figure(figsize=(10,6))
            plt.errorbar(df_channel['board'], df_channel[data_type], df_channel.iloc[:, column_id], marker='o', color='blue', linestyle='')
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

# # calcoalre media di medie e deviazioni standard, con errore
# # Graficarele per fare istogrammi e fit
