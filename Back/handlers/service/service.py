import pandas as pd
from Database.connections import get_connection
from utils.utils import make_table


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

        return df_raw.shape, list(df_raw.columns)

        # TODO пустой дф получается после make_table (подозреваю типы данных)
        df_metrics = make_table(df_raw)
        df_metrics.to_csv('data.tsv', sep='\t', header=False, index=False)

        try:
            with get_connection() as cnn:
                with cnn.cursor() as cur:
                    with open('data.tsv', "r") as f:
                        with cur.copy(f"COPY metrics "
                                      f"FROM STDIN (format 'csv', delimiter '\t', header true)") as copy:
                            while data := f.read():
                                copy.write(data)
            cnn.close()
            return min(df_metrics['time']), max(df_metrics['time'])
        except Exception as e:
            return e, 'error'

    def query_db(self, start_dt: str, end_dt: str):

        try:
            with get_connection() as cnn:
                with cnn.cursor() as cur:
                    cur.execute(f"SELECT * FROM METRICS WHERE time BETWEEN {start_dt} AND {end_dt}")
                    res = cur.fetchall()
            cnn.close()
            return res
        except Exception as e:
            raise e

    def query_ml(self, start_dt: str, end_dt: str, metrics: list):



        pass
