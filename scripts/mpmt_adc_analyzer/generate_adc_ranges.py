import pandas as pd
import json
from pprint import pprint

input_csv = "mpmt_adc_mean.csv"
output_json = "../output_ranges.json"
n = 3

# Carica il dataframe
df = pd.read_csv(input_csv)
print(df)

# Dizionario finale
output = {}

# Per ogni tipo di segnale (pedestal, pulse, …)
for signal in df["signal"].unique():
    
    # Dizionario interno per il segnale corrente
    output[signal] = {}

    df_signal = df[df["signal"] == signal]

    for channel in df["channel"].unique():

        df_channel = df_signal[df_signal["channel"] == channel]
        
        mu = df_channel["mu"].iloc[0]
        sigma_mu = df_channel["sigma_mu"].iloc[0]

        sigma = df_channel["sigma"].iloc[0]
        sigma_sigma = df_channel["sigma_sigma"].iloc[0]
    
        mu_interval = [
            max(0, mu - n * sigma_mu) if pd.notna(mu - n * sigma_mu) else None, # Min
            max(0, mu + n * sigma_mu) if pd.notna(mu + n * sigma_mu) else None # Max
        ]
        sigma_interval = [
            max(0, sigma - n * sigma_sigma) if pd.notna(sigma - n * sigma_sigma) else None, # Min
            max(0, sigma + n * sigma_sigma) if pd.notna(sigma + n * sigma_sigma) else None  # Max
        ]

        # Dizionario interno per il canale corrente
        output[signal][f"{channel:02d}"] = {
            "mu": mu_interval if mu_interval else None,
            "sigma": sigma_interval if sigma_interval else None
        }
        
# Salva in JSON
with open(output_json, "w") as f:
    json.dump(output, f, indent=4)
