"""
Вспомогательные фунцкии для ручек API-сервиса
"""
from datetime import datetime
from typing import Optional
import pandas as pd

from Database.connections import get_connection
from utils.utils import make_table, web_response, throughput, apdex, error
from utils.ml_utils import ml, get_data_labels


class Service:

    def update_db(self, df_raw: pd.DataFrame) -> Optional[tuple]:
        """
        Функция для загрузки дополнительных данных в БД

        :param df_raw: полученный через API и открытый Pandas DataFrame
        :return: минимальная и максимальная дата в данных (границы доступного интервала)
        """

        # предобработка сырых данных
        df_metrics = make_table(df_raw)
        df_metrics.to_csv('data.tsv', sep='\t', header=False, index=False)

        # загрузка данных в БД
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
            raise e

    def query_db(self, start_dt: str, end_dt: str):
        """
        Функция получения разметки без задействования машинного обучения (перерасчета)

        :param start_dt: левая граница временного интервала приближения
        :param end_dt: правая граница временного интервала приближения
        :return: списочное представление датафрейма для визуализации на фронте (либо exception)
        """

        try:
            with get_connection() as cnn:
                with cnn.cursor() as cur:
                    cur.execute(f"SELECT * "
                                f"FROM metrics "
                                f"INNER JOIN labels ON labels.time = metrics.time "
                                f"WHERE labels.time BETWEEN '{start_dt}' AND '{end_dt}';")
                    res = cur.fetchall()
            cnn.close()
            return res
        except Exception as e:
            raise e

    def query_ml(self, start_dt: datetime, end_dt: datetime) -> Optional[dict]:
        """
        Функция получения разметки с задействованием машинного обучения (перерасчет)

        :param start_dt: левая граница временного интервала приближения
        :param end_dt: правая граница временного интервала приближения
        :return: словарь названий метрик и датафреймов с элементами инференса для них
        """

        try:
            with get_connection() as cnn:
                with cnn.cursor() as cur:
                    cur.execute(f"SELECT * FROM METRICS;")
                    res = cur.fetchall()
            cnn.close()
            return ml(pd.DataFrame(res, columns=['time', 'time_numeric', 'time_numeric', 'web_response', 'throughput',
                                                 'apdex', 'error']), start_dt, end_dt)
        except Exception as e:
            raise e

    def get_labeled_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Функция получения разметки для датафрейма метрик

        :param df: сырой датафрейм
        :return: размеченный датафрейм
        """

        return get_data_labels(make_table(df))
