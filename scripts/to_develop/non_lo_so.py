import json
import pandas as pd

input_file = "C:/Users/messi/UNI/Tesi/scripts/to_store/ALL_RESULTS.json"
output_file = "C:/Users/messi/UNI/Tesi/scripts/to_develop/non_so_nome.csv"

with open(input_file, "r") as file_json:
    data = json.load(file_json)  

rows = []

for acq_name, acq_data in data.items(): 
    for measurement_type in ["pedestal", "pulse"]:
        if measurement_type in acq_data:
            for channel, channel_info in acq_data[measurement_type].items():
                stats = channel_info.get("stats", {})
                mean = stats.get("mean")
                std = stats.get("std")
                row = {
                    "acquisition": acq_name,
                    "measurement_type": measurement_type,
                    "channel": channel,
                    "means": mean,
                    "stds": std
                }

                rows.append(row)  

df = pd.DataFrame(rows)

print(df.loc[df.channel == "01"].loc[df.measurement_type == "pulse"].means.mean())
print(df.loc[df.channel == "01"].loc[df.measurement_type == "pulse"].stds.mean())


# calcoalre media di medie e deviazioni standard, con errore
# Graficarele per fare istogrammi e fit
