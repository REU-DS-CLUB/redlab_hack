import pandas as pd
import numpy as np


def metrics(df: pd.DataFrame, mask: np.array, metrics_name: str) -> dict:

    normalized_metric = (df[metrics_name] - np.mean(df[metrics_name])) / np.std(df[metrics_name])
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

