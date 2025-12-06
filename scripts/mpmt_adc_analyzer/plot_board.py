import os
import pandas as pd
import matplotlib.pyplot as plt

"""
                board  channel measurement_type  n_points        mu  sigma  err_mu  err_sigma
0     1.3.2.1_FD_2.10        1         pedestal   49242.0   264.185    0.6   0.003        0.0
1     1.3.2.1_FD_2.10        1            pulse     234.0  1043.400    3.0   0.200        0.0
2     1.3.2.1_FD_2.10        2         pedestal   49234.0   263.220    0.6   0.003        0.0
3     1.3.2.1_FD_2.10        2            pulse     239.0  1025.800    3.0   0.200        0.0
4     1.3.2.1_FD_2.10        3         pedestal   49374.0   260.420    3.0   0.010        0.0
..                ...      ...              ...       ...       ...    ...     ...        ...
223  1.3.2.1_FD_2.12D       17            pulse    1977.0   950.650    1.0   0.020        0.0
224  1.3.2.1_FD_2.12D       18         pedestal    1023.0   257.190    0.5   0.020        0.0
225  1.3.2.1_FD_2.12D       18            pulse    1982.0   977.370    1.0   0.020        0.0
226  1.3.2.1_FD_2.12D       19         pedestal    1023.0   257.330    0.5   0.020        0.0
227  1.3.2.1_FD_2.12D       19            pulse    1989.0   985.160    1.0   0.030        0.0
"""

input_csv = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_analyzer/mpmt_adc_channels.csv"
output_dir_board = "output_plot_board" # Cartella in cui saranno salvati i plot per canale

os.makedirs(output_dir_board, exist_ok=True)

data_types = ["mu", "sigma"]

df = pd.read_csv(input_csv)

for mainBoard in df["board"].unique():
    df_board = df.loc[df.board == mainBoard]
    for measurement_type in df_board["measurement_type"].unique():
        df_measurement = df_board.loc[df.measurement_type == measurement_type]
        print(df_measurement)
    
        for data_type in data_types:
            x = df_measurement["channel"]
            y = df_measurement[f"{data_type}"]

            if data_type == "mu":
                y_err = 3*df_measurement["sigma"]
            else: 
                y_err = 0

            print(x)
            print(y)
            print(y_err)

            y_min, y_max = y.min(), y.max()
            print(y_min, y_max)

            fig, ax = plt.subplots(figsize=(10, 6))
            plt.errorbar(x, y, yerr=y_err, marker='o', linestyle = "")
            plt.xlabel("Channel")
            plt.ylabel(f"{data_type}")
            plt.title(f"{mainBoard} - {measurement_type} - {data_type}")
            ax.set_xticks(x)
            plt.ylim(0.9*y_min, 1.1*y_max)
            # plt.yscale("log")
            plt.show()