from datetime import datetime
import pandas as pd
import numpy as np
from typing import List, Dict
from pyod.models.ecod import ECOD
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from sklearn.preprocessing import MinMaxScaler

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


def normalize_data(array: np.ndarray) -> np.ndarray:
    """
    Нормализует данные в массиве от 0 до 1.

    :param array: numpy массив данных
    :return: нормализованный numpy массив
    """
    scaler = MinMaxScaler()
    array_normalized = scaler.fit_transform(array.reshape(-1, 1))
    return array_normalized.flatten()

def calculate_weight(data: pd.DataFrame, col_names: list[str], start: datetime, end: datetime) -> dict[str, int]:
    '''
    function return a weight on which we need to multiply predictions of models on period
    '''
    weights = {}

    for col_name in col_names:

        overall_var = data[col_name].var()
        overall_mean = data[col_name].mean()

        with_out_anomaly_var = np.mean((overall_mean - data[(data.time >= start) & (data.time <= end)][col_name])**2)

        weights[col_name] = (with_out_anomaly_var**0.5) / (overall_var**0.5)
    
    return weights

def ml(data: pd.DataFrame, start_date: datetime, end_date: datetime) -> Dict[str, pd.DataFrame]:

    """
    Вход 
    - список колонок по которым нужно обучить модель list(str) 
    - дата начала промежутка datetime
    - дата конца промежутка datetime
    - датафрейм с поминутными метриками

    Выход
    dict: 
        - датафрейм с колонками 
            1. Таймстемп datetime
            2. Булево значение по аномалии label
            3. Вероятность по аномалии probability 
            4. Изначальное значение value
    """

    def fit_clf(model, data: np.ndarray) -> pd.DataFrame:
        model.fit(data)
        labels = model.labels_
        scores = model.decision_scores_
        threshold = model.threshold_
        threshold = (threshold - np.min(scores)) / (np.max(scores) - np.min(scores))

        return pd.DataFrame({
            "labels": labels,
            "probability": normalize_data(scores)
        }), threshold
    
    column_names = ["web_response", "throughput", "apdex", "error"]
    weights = calculate_weight(data, column_names, start_date, end_date)
    
    column_names.extend(['time', 'time_numeric'])
    filtered_df = data[(data['time'] >= start_date) & (data['time'] <= end_date)][column_names]

    result = {}

    for column in column_names:
        data_values = filtered_df[['time_numeric', column]].values

        if column == "apdex":
            clf = ECOD(contamination=0.004, n_jobs=-1)
        elif column == "web_response":
            clf = IForest(contamination=0.001)
        elif column == "throughput":
            clf = HBOS(contamination=0.0035)
        elif column == "error":
            clf = IForest(contamination=0.0011)
        else:
            continue

        clf_df, threshold = fit_clf(clf, data_values)
        clf_df["time"] = filtered_df["time"].values
        clf_df["value"] = filtered_df[column].values
        result[column] = clf_df

        scaled_weight = (weights[column] / (weights[column] + 1)) * 2
        for index, row in result[column].iterrows():
            result[column].at[index, "probability"] = row["probability"] * scaled_weight
        # result[column].probability *= scaled_weight
        result[column].labels = (result[column].probability > threshold).astype(int)

    return result