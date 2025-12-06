import json
import pandas as pd
import matplotlib.pyplot as plt
import os
import math
from pprint import pprint

dpi = 150

input_file = "C:/Users/messi/UNI/Tesi/scripts/ALL_RESULTS.json"
input_file_1 = "C:/Users/messi/UNI/Tesi/scripts/output_ranges.json"
output_file = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_analyzer/mpmt_adc_channels.csv"
output_file_1 = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_analyzer/mpmt_adc_mean.csv"
output_dir_channel = "output_plot_channel" # Cartella in cui saranno salvati i plot per canale

# ==== INTERVALLI DI INTERESSE PER LE USCITE NUMERICHE DELL'ADC ====
INTERVALS = {
    "pedestal": [200,300], # Valori tipici per il piedistallo
    "pulse": [900,1100]    # Valori tipici per il segnale
} # I valori sono espressi in uscite numeriche dell'ADC (0-4095 per ADC a 12 bit)

def round_sig(x,y):
    """Arrotonda x usando y come riferimento di significatività."""
    if x is None or math.isnan(x):
        return None
    if x == 0:
        return 0
    if y is None or y == 0 or math.isnan(y):
        return round(x)

    ndigits = int(math.floor(math.log10(abs(y))))
    return round(x, - ndigits)


def compute_stats(DataFrame, column):

    n_points = len(DataFrame[column])
    mean = DataFrame[column].mean()
    std = DataFrame[column].std()
    err_mean = std/math.sqrt(n_points)

    mean = round_sig(mean,err_mean)
    std = round_sig(std,std)
    err_mean = round_sig(err_mean,err_mean)

    return mean, std, err_mean


os.makedirs(output_dir_channel, exist_ok=True)

with open(input_file, "r") as file_json:
    json_data = json.load(file_json)  

with open(input_file_1, "r") as file_json:
    json_ranges = json.load(file_json)  

rows = []

for board_name_key, board_name_value in json_data.items(): 
    for channel_id_key, channel_id_value in board_name_value.items():
        if channel_id_key != "info_test":
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

data_types = ["mu", "sigma"]

rows = []

# ==== PLOT PER CANALE ====
for measurement_type in df["measurement_type"].unique():    
    df_measurement_type = df.loc[df.measurement_type == measurement_type]
    for channel in df_measurement_type["channel"].unique():
        df_channel = df_measurement_type.loc[df_measurement_type.channel == channel]

        row = {
            "channel": channel,
            "signal": measurement_type           
        }

        for data_type in data_types:
            # Restituisce l'indice della colonna corrispondente all'errore sul valore che stiamo analizzando.
            # La formattazione adottata è la seguente:
            # dato_1, dato_2, ... , dato_N, err_dato_1, err_dato_2, ... , err_dato_N 
            column_id = df_channel.columns.get_loc(data_type) + len(data_types)

            mu, std, err_mu = compute_stats(df_channel, data_type)
            x0, x1 = INTERVALS[measurement_type]
            print(x0, x1)

            row.update({
                f"{data_type}": mu,
                f"sigma_{data_type}": std,
                f"err_{data_type}": err_mu
            })

            plt.figure(figsize=(12,6))
            plt.errorbar(y = df_channel['board'], x = df_channel[data_type], xerr = df_channel.iloc[:, column_id], marker='o', color='blue', linestyle='', label="Cacca")
            if not pd.isna(mu) and not pd.isna(std):
                if data_type == "mu":
                    label_sigma = fr"$\sigma_\mu = {std}$"
                    label_mu = fr"$\mu_\mu = {mu} \pm {err_mu}$"
                    label_mu_sigma = fr"$\mu_\mu \pm \sigma_\mu$" 
                    label_mu_2sigma = fr"$\mu_\mu \pm 2\sigma_\mu$" 
                    label_mu_3sigma = fr"$\mu_\mu \pm 3\sigma_\mu$" 
                elif data_type == "sigma":
                    label_sigma = fr"$\sigma_\sigma = {std}$"
                    label_mu = fr"$\mu_\sigma = {mu} \pm {err_mu}$"
                    label_mu_sigma = fr"$\mu_\sigma \pm \sigma_\sigma$" 
                    label_mu_2sigma = fr"$\mu_\sigma \pm 2\sigma_\sigma$" 
                    label_mu_3sigma = fr"$\mu_\sigma \pm 3\sigma_\sigma$" 

                plt.plot([], [], color='black', linestyle='', label=label_sigma)
                plt.axvline(mu, color="red", linestyle="--", label=label_mu)
                plt.axvline(mu+std, color="blue", linestyle="--", label=label_mu_sigma)
                plt.axvline(mu-std, color="blue", linestyle="--")
                plt.axvline(mu+2*std, color="yellow", linestyle="--", label=label_mu_2sigma)
                plt.axvline(mu-2*std, color="yellow", linestyle="--")
                plt.axvline(mu+3*std, color="yellow", linestyle="--", label=label_mu_3sigma)
                plt.axvline(mu-3*std, color="yellow", linestyle="--")
            plt.ylabel('Board')
            plt.xlabel(f'{data_type}')

            if std is not None:
                plt.xlim(mu-5*std, mu+5*std)

            plt.title(f'{data_type} vs board - Ch{channel} - {measurement_type}')
            plt.tight_layout()
            plt.legend()
            plt.savefig(
                os.path.join(
                    output_dir_channel,
                    f'{data_type} vs board - Ch{channel} - {measurement_type}.png'
                ), dpi = dpi
            )
            plt.close()

        rows.append(row)

# ==== CSV MEDIE PER CANALE ====
df_mean = pd.DataFrame(rows)
df_mean.to_csv(output_file_1, index=False)
print(df_mean)