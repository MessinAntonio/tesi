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
    err_mean = std/math.sqrt(n_points)
    err_std = 0

    mean = round_sig(mean,err_mean)
    std = round_sig(std,std)
    err_mean = round_sig(err_mean,err_mean)

    return n_points, mean, std, err_mean, err_std


def compute_summary(DataFrame):
    if DataFrame.empty:
        return None
    return DataFrame.adc.value_counts().sort_index().to_dict()
