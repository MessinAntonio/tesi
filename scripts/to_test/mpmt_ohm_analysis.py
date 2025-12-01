import os
import json
import time
import pandas as pd
import matplotlib.pyplot as plt

input_dir = "input"

rows = []  

dirs = os.listdir(input_dir)
dirs = sorted(dirs, key=lambda x: int(x))

for dir_name in dirs:
    dir_path = os.path.join(input_dir, dir_name)

    latest_file = None
    latest_ctime = 0

    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)

        stats = os.stat(file_path)
        ctime = stats.st_ctime

        if ctime > latest_ctime:
            latest_ctime = ctime
            latest_file = (filename, stats)

    if latest_file:
        filename, stats = latest_file
        input_file_path = os.path.join(dir_path, filename)
        
        print(f"In cartella '{dir_name}':")
        print("File più recente:", filename)
        print("Dimensione:", stats.st_size, "byte")
        print("Creazione:", time.ctime(stats.st_ctime))
        print()
            
        with open(input_file_path, "r") as file_json:
                data = json.load(file_json)
                rows.append(data)

# Converte tutte le righe in un DataFrame
df = pd.DataFrame(rows)
print(df)

cols_to_select = [col for i, col in enumerate(df.columns) if i == 0 or "Measurement" in col]

df_data = df[cols_to_select]

for idx in range(1, len(df_data.columns)):
    colX = df_data.columns[0]
    colY = df_data.columns[idx]

    df_temp = df_data[[colX, colY]].copy()

    df_temp[colY] = pd.to_numeric(df_temp[colY], errors='coerce')

    print(df_temp[colY].mean())
    print(df_temp[colY].std())
    print()

    # fig, ax = plt.subplots(figsize=(9, 6))
    # n_bins = 50
    # x_range = (0, 100)
    # data_y, bins, patches = ax.hist(evt_x, n_bins, range=x_range, density=False, 
    # histtype=u'step', edgecolor='b', linewidth=2, label='histogram')
    # ax.hist(evt_x, n_bins, range=x_range, density=False, color='b', alpha=0.2)
    # ax.scatter(evt_x, np.full_like(evt_x, 0.5), marker='o', color='r', s=10, alpha=0.2, linewidth=0, label='entries')
    # plt.xlabel('$x$')
    # plt.ylabel(r'$\Delta N$')
    # plt.legend()
    # plt.show()

    # col0 = df_data.columns[0] 
    # colX = df_data.columns[idx]

    # df_temp = df[[col0, colX]]
    



"""
{
    "Board SN": "17",
    "RFID": "",
    "Time": 1764320940.0,
    "1V - GND jumper continuity": "OK",
    "1V8 - GND jumper continuity": "OK",
    "3V3 - GND jumper continuity": "OK",
    "1V35 - GND jumper continuity": "OK",
    "2V5 - GND jumper continuity": "OK",
    "5VA - GND jumper continuity": "OK",
    "5VA1 - GND jumper continuity": "OK",
    "C26 - GND jumper continuity": "OK",
    "D21 Presence Measurement": "0.5",
    "D22 Presence Measurement": "0.5",
    "": "OK",
    "5V on W5VA Measurement": "5",
    "5V on W5VA1 Measurement": "5",
    "Jumpers closed": "OK",
    "1V on W1V0 Measurement": "1",
    "1.8V on W1V8 Measurement": "1.8",
    "3.3V on W3V3 Measurement": "3.3",
    "1.35V on W1V35 Measurement": "1.35",
    "2.5V on W2V5 Measurement": "2.5"
}
"""


# Unique Part Identifier


# fare la stessa cosa per i plot in cui puoi selezionare da tasttiera la singola scheda da voler analizzare
