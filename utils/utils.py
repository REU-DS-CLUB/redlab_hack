import pandas as pd
import numpy as np


def web_response(data: pd.DataFrame) -> pd.DataFrame:

    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'HttpDispatcher')]

    filtered_data['time'] = filtered_data['point']
    filtered_data['web_response'] = filtered_data['total_call_time'].sum() / filtered_data['call_count'].sum()
    grouped_data = filtered_data.groupby('time').agg({
        'web_response': 'sum'
    }).reset_index()
    result_data = grouped_data.sort_values(by='time')

    return result_data


def throughput(data: pd.DataFrame) -> pd.DataFrame:

    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'HttpDispatcher')
    ]

    aggregated_data = filtered_data.groupby('point').agg({'call_count': 'sum'}).reset_index()
    aggregated_data.rename(columns={'point': 'time'}, inplace=True)
    result_data = aggregated_data.sort_values(by='time')
    return result_data


def apdex(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[
    (data['language'] == 'java') &
    (data['app_name'] == '[GMonit] Collector') &
    (data['scope'].isna()) &
    (data['name'] == 'Apdex')
]

    aggregated_data = filtered_data.groupby('point').agg({
        'call_count': 'sum',
        'total_call_time': 'sum',
        'total_exclusive_time': 'sum'
    }).reset_index()
    pass

    aggregated_data.rename(columns={
        'call_count': 's',
        'total_call_time': 't',
        'total_exclusive_time': 'f'
    }, inplace=True)

    aggregated_data['metric'] = (aggregated_data['s'] + aggregated_data['t'] / 2) / (aggregated_data['s'] + aggregated_data['t'] + aggregated_data['f'])

    aggregated_data.rename(columns={'point': 'time'}, inplace=True)
    result_data = aggregated_data.sort_values(by='time')

    return result_data[["time", "metric"]]


def error(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'].isin(['HttpDispatcher', 'Errors/allWeb']))
        ]

    agg_httpdispatcher = filtered_data[filtered_data['name'] == 'HttpDispatcher'].groupby('point').agg(
        {'call_count': 'sum'}).reset_index()
    agg_errors = filtered_data[filtered_data['name'] == 'Errors/allWeb'].groupby('point').agg(
        {'call_count': 'sum'}).reset_index()

    agg_httpdispatcher.rename(columns={'call_count': 'httpdispatcher_call_count'}, inplace=True)
    agg_errors.rename(columns={'call_count': 'errors_call_count'}, inplace=True)

    merged_data = pd.merge(agg_httpdispatcher, agg_errors, on='point', how='outer').fillna(0)

    merged_data['metric'] = merged_data['errors_call_count'] / merged_data['httpdispatcher_call_count']

    merged_data.rename(columns={'point': 'time'}, inplace=True)

    result_data = merged_data.sort_values(by='time')

    return result_data[["time", "metric"]]

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

