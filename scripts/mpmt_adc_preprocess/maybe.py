import os
import pandas as pd

from scipy.signal import find_peaks
from pprint import pprint

inputFolder = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_preprocess/data/processed"

for test_dir_name in os.listdir(inputFolder):
    test_dir_path = os.path.join(inputFolder, test_dir_name)
    for typ_events_name in os.listdir(test_dir_path):
        if typ_events_name == "pmt_events":
            typ_events_path = os.path.join(test_dir_path, typ_events_name)
            for file_name in os.listdir(typ_events_path):
                file_path = os.path.join(typ_events_path, file_name)
                if os.path.isfile(file_path) and file_name.endswith(".csv"):
                    print(52*"=")
                    print(f"========== Test MainBoard {test_dir_name} ==========")
                    print(52*"=")
                    # --- Load and select channel ---
                    df = pd.read_csv(file_path)
                    for idx, ch_id in enumerate(range(1,20)):
                        df_channel = df.loc[(df.channel == idx)]
                        df_adc = df_channel["adc"]
                        print(f" -Analisi canale {ch_id}")

                        df_summary = df_adc.value_counts().sort_index()
                        adc_values = df_summary.index.values       # X-axis (unique ADC values)
                        frequencies = df_summary.values            # Y-axis (counts)

                        peaks, properties = find_peaks(
                            frequencies,  height=1, prominence=10, width=1
                        )
                        
                        print("Peak indices:", peaks)
                        print("Peak frequencies:", frequencies[peaks])
                        print("Peak ADC values:", adc_values[peaks])
                        pprint(properties)

                        # --- Costruisci intervalli ADC dai picchi ---
                        left_bases = properties['left_bases']
                        right_bases = properties['right_bases']

                        intervals = [(adc_values[left], adc_values[right]) 
                                     for left, right in zip(left_bases, right_bases)]
                        print("Intervalli ADC dei picchi:", intervals)
                        print()
                        print()
