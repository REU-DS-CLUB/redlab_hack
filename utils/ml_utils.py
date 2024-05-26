"""
Вспомогательные функции для работы ML'я
"""
import json
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from sklearn.preprocessing import MinMaxScaler


def metrics(df: pd.DataFrame, mask: np.array, metrics_name: str) -> dict:
    """
    Промежуточная функция получения метрик для использвоания в модели

    :param df: сырой набор данных
    :param mask: значение маски
    :param metrics_name: название метрики
    :return: словарь метрик
    """

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
    Функция нормализации данных в массиве от 0 до 1

    :param array: numpy массив данных
    :return: нормализованный numpy массив
    """

    scaler = MinMaxScaler()
    array_normalized = scaler.fit_transform(array.reshape(-1, 1))
    return array_normalized.flatten()


def calculate_weight(data: pd.DataFrame, col_names: list[str], start: datetime, end: datetime) -> dict[str, int]:
    """
    Функция для получения весов, на которые мы должны домножить предсказания за определенный период

    :param data: сырой датафрейм
    :param col_names: названия колонок
    :param start: левая граница временного интервала
    :param end: левая граница временного интервала
    """

    weights = {}

    for col_name in col_names:
        overall_var = data[col_name].var()
        overall_mean = data[col_name].mean()

        with_out_anomaly_var = np.mean((overall_mean - data[(data.time >= start) & (data.time <= end)][col_name]) ** 2)

        weights[col_name] = with_out_anomaly_var / overall_var

    return weights


def ml(data: pd.DataFrame, start_date: datetime, end_date: datetime) -> Dict[str, json]:
    """
    Функция с пайплайном предобработки данных и инференса

    :param data: датафрейм с поминтуными метриками
    :param start_date: левая граница временного интервала приближения
    :param end_date: правая граница временного интервала приближения
    :return: словарь с ключами - названиями метрик и значениями - размеченными датафреймами (
            1. Таймстемп datetime
            2. Булево значение по аномалии label
            3. Вероятность по аномалии probability
            4. Изначальное значение value)
    """

    def fit_clf(model, data: pd.DataFrame) -> pd.DataFrame:
        model.fit(data)
        labels = model.labels_
        scores = model.decision_scores_
        threshold = model.threshold_
        threshold = (threshold - np.min(scores)) / (np.max(scores) - np.min(scores))
        # print("Threshold: ", threshold)

        return pd.DataFrame({
            "labels": labels,
            "probability": normalize_data(scores)
        })

    column_names = ["web_response", "throughput", "apdex", "error"]
    column_names.extend(['time', 'time_numeric'])
    filtered_df = data[(data['time'] >= start_date) & (data['time'] <= end_date)][column_names]

    result = {}

    for column in column_names:
        data_values = filtered_df[['time_numeric', column]].values

        if column in ["web_response", "error"]:
            clf = IForest(contamination=0.001)
        elif column == "apdex":
            clf = IForest(contamination=0.003)
        elif column == "throughput":
            clf = HBOS(contamination=0.0035)
        else:
            continue

        clf_df = fit_clf(clf, data_values)
        clf_df["time"] = filtered_df["time"].values
        clf_df["value"] = filtered_df[column].values
        result[column] = clf_df.to_json()

    return result


def get_data_labels(metrics_table: pd.DataFrame) -> pd.DataFrame:
    """
    Функция разметки лейблов для датафрейма с поминтуными метриками

    :param metrics_table: датафрейм с поминтуными метриками
    :return: размеченный датафрейм
    """

    labeled_df = pd.DataFrame()
    labeled_df["time"] = metrics_table["time"]

    max_date = np.max(metrics_table["time"])
    min_date = np.min(metrics_table["time"])

    dict_dfs_metrics = ml(metrics_table, min_date, max_date)

    for metrics_name in dict_dfs_metrics.keys():
        metric_df = dict_dfs_metrics[metrics_name]
        labeled_df[f"{metrics_name}_labels"] = metric_df["labels"]

    return labeled_df
