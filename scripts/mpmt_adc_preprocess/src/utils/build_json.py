import json

from ..config import *
from ..parser import *

from .stats_utils import *

def build_single_json(file_name, df, dir_path, ttree_name):
    range_valid_json = "C:/Users/messi/UNI/Tesi/scripts/output_ranges.json"

    # container temporanei
    channels_dict = {}
    file_summary = {}

    with open(range_valid_json, "r") as file_range_json:
        range_json = json.load(file_range_json)
    
    for idx, ch_id in enumerate(NUMB_CHANNELS): 
        ch_key = f"{ch_id:02d}"
        channels_dict[ch_key] = {}

        for interval_type, interval_range in INTERVALS.items():
            min_adc, max_adc = interval_range
            
            df_ch = df.loc[(df.channel == idx) & (min_adc < df.adc) & (df.adc < max_adc)]

            mu_interval = range_json[interval_type][f"{ch_id:02d}"]["mu"]
            sigma_interval = range_json[interval_type][f"{ch_id:02d}"]["sigma"]

            print(f"Analisi file: {file_name} -- canale {ch_id} -- segnale: {interval_type}")
            print(mu_interval[0], mu_interval[1])
            print(sigma_interval[0], sigma_interval[1])

            n_points_ch, mu_ch, sigma_ch, err_mu_ch, err_sigma_ch = compute_stats(df_ch)
            print("daje1")
            mu_valid, sigma_valid = compute_summary(mu_ch, sigma_ch, mu_interval, sigma_interval)
            print("daje2")

            channels_dict[ch_key][interval_type] = {
                "stats": {
                    "n_points": n_points_ch,
                    "mu": mu_ch,
                    "sigma": sigma_ch,
                    "err_mu": err_mu_ch,
                    "err_sigma": err_sigma_ch
                },
                "summary": {
                    "mu_valid": mu_valid,
                    "sigma_valid": sigma_valid
                }
            }
            print("daje3")
            if interval_type not in file_summary:
                file_summary[interval_type] = {
                    "mu_failed": [],
                    "sigma_failed": []
                }
            print("daje4")
            if mu_valid == "Fail":
                file_summary[interval_type]["mu_failed"].append(f"{ch_id:02d}")   
            print("daje5")
            if sigma_valid == "Fail":
                file_summary[interval_type]["sigma_failed"].append(f"{ch_id:02d}")
            print("daje6")
    # Inserisco il summary nel JSON del file
    final_file_json = {
        file_name: {
            "info_test": file_summary,
            **channels_dict 
        }
    }
    print("daje7")
    json_output_path = os.path.join(
        dir_path, f"{ttree_name[:-2]}_{file_name}.json"
    )
    print("daje8")
    with open(json_output_path, "w") as f_json:
        json.dump(final_file_json, f_json, indent=4)    

    return final_file_json