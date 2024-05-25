import pandas as pd
import numpy as np


def metrics(df: pd.DataFrame, mask: np.array) -> dict:

    normalized_metric = (df['metric'] - np.mean(df['metric'])) / np.std(df['metric'])
    original_variance = np.var(normalized_metric)
    filtered_metric = normalized_metric[mask == 0]
    filtered_variance = np.var(filtered_metric)
    

    variance_difference = filtered_variance / original_variance * 100 - 100
    fraction_anomaly = len(mask[mask == 1]) / len(mask)

    metric = {
        "variance_diff": variance_difference,
        "fraction_anomaly": fraction_anomaly
    }

    return metric

