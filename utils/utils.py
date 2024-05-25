import pandas as pd
import numpy as np


def web_response(data: pd.DataFrame) -> pd.DataFrame:

    filtered_data = data[
        (data['language'] == 'java') &
        (data['app_name'] == '[GMonit] Collector') &
        (data['scope'].isna()) &
        (data['name'] == 'HttpDispatcher')]

    filtered_data["point"] = pd.to_datetime(filtered_data["point"])
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
        (data['name'] == 'HttpDispatcher')]
    #throughput
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

    aggregated_data['apdex'] = (aggregated_data['s'] + aggregated_data['t'] / 2) / (aggregated_data['s'] + aggregated_data['t'] + aggregated_data['f'])

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
    throughput_table =  throughput(data)
    apdex_table = apdex(data)
    error_table = error(data)

    metrics_table = pd.DataFrame({
        "time": web_response_table["time"],
        "web_response": web_response_table["web_response"],
        "throughput": throughput_table["throughput"],
        "apdex": apdex_table["apdex"],
        "error": error_table["error"]
    })

    return metrics_table
    
