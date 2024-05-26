import pandas as pd
from typing import Dict
import matplotlib.pyplot as plt


def web_response(data: pd.DataFrame) -> pd.DataFrame:
    # фильтрация данных
    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'HttpDispatcher')]

    # преобразование столбца 'point' в datetime
    filtered_data["point"] = pd.to_datetime(filtered_data["point"])
    filtered_data['time'] = filtered_data['point']

    # группировка данных по времени и вычисление отношения сумм total_call_time к call_count
    grouped_data = filtered_data.groupby('time').agg({
        'total_call_time': 'sum',
        'call_count': 'sum'
    }).reset_index()

    # вычисление web_response как отношение сумм total_call_time к call_count
    grouped_data['web_response'] = grouped_data['total_call_time'] / grouped_data['call_count']
    grouped_data['web_response'] = grouped_data['web_response'].fillna(0)

    # сортировка по времени
    result_data = grouped_data[['time', 'web_response']].sort_values(by='time')

    return result_data


def throughput(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'HttpDispatcher')]
    # throughput
    #
    filtered_data["point"] = pd.to_datetime(filtered_data["point"])
    aggregated_data = filtered_data.groupby('point').agg({'call_count': 'sum'}).reset_index()
    aggregated_data.rename(columns={'point': 'time', "call_count": "throughput"}, inplace=True)
    result_data = aggregated_data.sort_values(by='time')
    return result_data


def apdex(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'Apdex')
        ]
    filtered_data["point"] = pd.to_datetime(filtered_data["point"])
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

    aggregated_data['apdex'] = (aggregated_data['s'] + aggregated_data['t'] / 2) / (
                aggregated_data['s'] + aggregated_data['t'] + aggregated_data['f'])

    aggregated_data.rename(columns={'point': 'time'}, inplace=True)
    result_data = aggregated_data.sort_values(by='time')

    return result_data[["time", "apdex"]]


def error(data: pd.DataFrame) -> pd.DataFrame:
    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'].isin(['HttpDispatcher', 'Errors/allWeb']))
        ]
    filtered_data["point"] = pd.to_datetime(filtered_data["point"])
    agg_httpdispatcher = filtered_data[filtered_data['name'] == 'HttpDispatcher'].groupby('point').agg(
        {'call_count': 'sum'}).reset_index()
    agg_errors = filtered_data[filtered_data['name'] == 'Errors/allWeb'].groupby('point').agg(
        {'call_count': 'sum'}).reset_index()

    agg_httpdispatcher.rename(columns={'call_count': 'httpdispatcher_call_count'}, inplace=True)
    agg_errors.rename(columns={'call_count': 'errors_call_count'}, inplace=True)

    merged_data = pd.merge(agg_httpdispatcher, agg_errors, on='point', how='outer').fillna(0)

    merged_data['error'] = merged_data['errors_call_count'] / merged_data['httpdispatcher_call_count']

    merged_data.rename(columns={'point': 'time'}, inplace=True)

    result_data = merged_data.sort_values(by='time')

    return result_data[["time", "error"]]


def make_table(data: pd.DataFrame) -> pd.DataFrame:
    web_response_table = web_response(data)
    throughput_table = throughput(data)
    apdex_table = apdex(data)
    error_table = error(data)
    time_numeric = pd.to_datetime(throughput_table['time']).astype(int) / 10 ** 9 / 60

    metrics_table = pd.DataFrame({
        "time": throughput_table["time"],
        'time_numeric': time_numeric,
        "web_response": web_response_table["web_response"],
        "throughput": throughput_table["throughput"],
        "apdex": apdex_table["apdex"],
        "error": error_table["error"]
    })

    return metrics_table


def plot_anomalies(data: Dict[str, pd.DataFrame], feature_name: str):
    df = data[feature_name]

    plt.figure(figsize=(20, 8))

    plt.plot(df['time'], df['value'], color='blue', label=f'Значения показателя {feature_name}')
    anomalies = df[df['labels'] == 1]
    plt.scatter(anomalies['time'], anomalies['value'], color='red', s=100, label='Аномалия')
    plt.title(f'Временной ряд с аномалиями показателя {feature_name}')
    plt.xlabel('Временной ряд')
    plt.ylabel(f'{feature_name}')
    plt.legend()
    plt.grid(True)
    plt.show()
