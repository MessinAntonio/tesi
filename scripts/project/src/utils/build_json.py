import json

from ..config import *
from ..parser import *

from .stats_utils import *

def build_single_json(file_name, df, dir_path, ttree_name):
    json_single_file = {}
    json_single_file[file_name] = {}

    for idx, ch_id in enumerate(NUMB_CHANNELS): 
        ch_key = f"{ch_id:02d}"
        json_single_file[file_name][ch_key] = {}

        for interval_type, interval_range in INTERVALS.items():
            json_single_file[file_name][ch_key][interval_type] = {}
            min_adc, max_adc = interval_range
            df_ch = df.loc[(df.channel == idx) & (min_adc < df.adc) & (df.adc < max_adc)]

            n_points_ch, mean_ch, std_ch, err_mean_ch, err_std = compute_stats(df_ch)

            json_single_file[file_name][ch_key][interval_type] = {
                "stats": {
                    "n_points": n_points_ch,
                    "mean": mean_ch,
                    "std": std_ch,
                    "err_mean": err_mean_ch,
                    "err_std": err_std
                },
                "summary": compute_summary(df_ch)
            }

    json_output_path = os.path.join(
        dir_path,
        f"{ttree_name[:-2]}_{file_name}.json"
    )

    with open(json_output_path, "w") as f_json:
        json.dump(json_single_file, f_json, indent=4)    

    return json_single_file