import pandas as pd
from Database.connections import get_connection, get_engine
from utils.utils import web_response, throughput, apdex, error


class Service:
    """
    Service to handle requests with params
    """

    def update_db(self, df_raw: pd.DataFrame):
        """
        Функция для загрузки дополнительных данных в БД

        :param df_raw: полученный через API и открытый Pandas DataFrame
        :return: None
        """
        df_metrics = web_response(df_raw)
        df_metrics['throughput'] = throughput(df_raw)['call_count']
        df_metrics['apdex'] = apdex(df_raw)['metric']
        df_metrics['error_rate'] = error(df_raw)['metric']

        # df_raw.to_sql(name='raw', con=get_engine(), if_exists='append')
        df_metrics.to_sql(name='metrics', con=get_engine(), if_exists='append', schema='postgres')
