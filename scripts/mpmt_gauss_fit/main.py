import uproot
import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import os

# ==== INTERVALLI DI INTERESSE PER LE USCITE NUMERICHE DELL'ADC ====
INTERVALS = {
    "pedestal": [253,300], # Valori tipici per il piedistallo
    "pulse": [900,1100]    # Valori tipici per il segnale
} # I valori sono espressi in uscite numeriche dell'ADC (0-4095 per ADC a 12 bit)
NUMB_CHANNELS = range(1,20)

def fit_model(x, A, mu, sigma):
    return A*np.exp(-((x - mu)/sigma)**2/2)/math.sqrt(2*math.pi*sigma**2)

input_file_path = "C:/Users/messi/UNI/Tesi/scripts/mpmt_adc_preprocess/data/raw/1.3.2.1_FD_2.10.root"
filename = os.path.basename(input_file_path)
name = os.path.splitext(filename)[0]

with uproot.open(input_file_path) as file_root:
    for ttree_name in file_root.keys():
        if ttree_name == "pmt_events;1":
            ttree = file_root[ttree_name]

            data_dict = {}

            for branch in ttree.keys():
                values = ttree[branch].array(library="np")
                data_dict[branch] = values

            df = pd.DataFrame(data_dict)

            for interval_type, interval_range in INTERVALS.items():
                for idx, ch_id in enumerate(NUMB_CHANNELS): 
                    ch_key = f"{ch_id:02d}"

                    min_adc, max_adc = interval_range
                    df_ch = df.loc[(df.channel == idx) & (min_adc < df.adc) & (df.adc < max_adc)]

                    df_adc = df_ch[["adc"]]

                    mu_start, sigma_start = df_adc.mean().iloc[0], df_adc.std().iloc[0] 
    
                    df_hist = (
                        df_adc["adc"]
                        .value_counts()
                        .sort_index()
                        .rename_axis("x")
                        .reset_index(name="y")
                    )
                    df_hist["y_err"] = np.sqrt(df_hist["y"])

                    # stime iniziali
                    A0 = df_hist["y"].max()
                    mu0 = mu_start
                    sigma0 = sigma_start

                    # rimuovi outlier molto lontani
                    df_fit = df_hist[np.abs(df_hist["x"] - mu0) < 5]

                    data_x = df_fit["x"]
                    data_y = df_fit["y"]
                    data_yerr = df_fit["y_err"]

                    popt, pcov = curve_fit(
                        fit_model,
                        data_x,
                        data_y,
                        sigma=data_yerr,
                        absolute_sigma=True,
                        p0=[A0, mu0, sigma0],
                        bounds=([0, mu_start - 200, 0], [50000, mu_start + 200, 20])
                    )

                    A_fit, mu_fit, sigma_fit = popt
                    A_err, mu_err, sigma_err = np.sqrt(np.diag(pcov))

                    data_x_f = np.linspace(data_x.min(), data_x.max(), 400)
                    data_y_f = fit_model(data_x_f, *popt)

                    # Valori fittati
                    A_fit, mu_fit, sigma_fit = popt

                    # Valori calcolati dal modello
                    y_fit = fit_model(data_x, *popt)

                    # Calcolo del chi-quadro
                    chi2 = np.sum(((data_y - y_fit) / data_yerr) ** 2)

                    # Gradi di libertà
                    ndof = len(data_x) - len(popt)

                    # Chi quadro ridotto
                    chi2_red = chi2 / ndof

                    print(f'{name} - Channel {ch_key} - {interval_type}')
                    print("Chi2 =", chi2)
                    print("Ndof =", ndof)
                    print("Chi2_red =", chi2_red)
                    print(f"A     = {A_fit:.3f} ± {A_err:.3f}")
                    print(f"mu    = {mu_fit:.3f} ± {mu_err:.3f}")
                    print(f"sigma = {sigma_fit:.3f} ± {sigma_err:.3f}")
                    print()
                    print()
                    print()
                    print()

                    plt.figure(figsize=(10, 6))
                    plt.errorbar(data_x, data_y, data_yerr, fmt="o", label="point")
                    plt.plot(data_x_f, data_y_f, label="fit")
                    plt.xlabel('ADC output')
                    plt.ylabel('Frequenze')
                    plt.ylim(0)
                    plt.title(f'{name} - Channel {ch_key} - {interval_type}')
                    # --- CREAZIONE TESTO DELLA LEGENDA ---
                    fit_info = [
                        rf"$\mu = {mu_fit:.3f} \pm {mu_err:.3f}$",
                        rf"$\sigma = {sigma_fit:.3f} \pm {sigma_err:.3f}$",
                    ]
                    plt.legend(title="\n".join(fit_info))
                    plt.show()