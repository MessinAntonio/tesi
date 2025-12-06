import math

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


def compute_stats(DataFrame):
    if DataFrame.empty:
        return None, None, None, None, None 

    n_points = len(DataFrame.adc)
    mean = DataFrame.adc.mean()
    std = DataFrame.adc.std()
    err_mean = DataFrame.adc.sem()
    err_std = 0

    mean = round_sig(mean,err_mean)
    # std = round_sig(std,std)
    err_mean = round_sig(err_mean,err_mean)

    return n_points, mean, std, err_mean, err_std


def compute_summary(x, y, x_interval, y_interval):
    x_valid, y_valid = "Fail", "Fail"

    if x_interval is not None and x is not None:
        try:
            if x_interval[0] < x < x_interval[1]:
                x_valid = "Ok"
        except Exception:
            # se gli intervali non sono indexable o non numerici
            x_valid = "Fail"

    if y_interval is not None and y is not None:
        try:
            if y_interval[0] < y < y_interval[1]:
                y_valid = "Ok"
        except Exception:
            y_valid = "Fail"

    return x_valid, y_valid

