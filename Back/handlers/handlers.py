"""
Ручки API-сервиса
"""
import csv
from datetime import datetime
from io import StringIO
from typing import Optional

import pandas as pd
from pandas import DataFrame

from fastapi import APIRouter, Request, HTTPException, status, UploadFile, File
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from starlette.requests import ClientDisconnect

from . import service

MAX_FILE_SIZE = 1024 * 1024 * 1024 * 2
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024

handlers = APIRouter(
    prefix='/handlers',
    tags=['handlers']
)


# классы для проверки ограничений ручки по приему файлов
class MaxBodySizeException(Exception):
    def __init__(self, body_len: str):
        self.body_len = body_len


class MaxBodySizeValidator:
    def __init__(self, max_size: int):
        self.body_len = 0
        self.max_size = max_size

    def __call__(self, chunk: bytes):
        self.body_len += len(chunk)
        if self.body_len > self.max_size:
            raise MaxBodySizeException(body_len=str(self.body_len))


@handlers.post('/upload',
               description='upload new data')
#async def upload(request: Request) -> dict[str, str]:
async def upload(request: Request):
    """
    Ручка по загрузке новой порции данных в БД с определенными ограничениями в реализации на данный момент
    (только .tsv, до 2gb, неповторяющиеся временные интервалы)

    :param request: запрос от пользователя с открытым файлом и заголовками
    :return: минимальная и максимальная дата в данных
    """

    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('Filename')

    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='Filename header is missing')
    # загружаем файл в память из стрима
    try:
        file_ = ValueTarget(validator=MaxSizeValidator(MAX_FILE_SIZE))
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)

        # переводим данные в датафрейм
        columns = ['account_id', 'name', 'point', 'call_count', 'total_call_time', 'total_exclusive_time',
                   'min_call_time', 'max_call_time', 'sum_of_squares', 'instances', 'language', 'app_name',
                   'app_id', 'scope', 'host', 'display_host', 'pid', 'agent_version', 'labels']

        df = DataFrame([x.split('\t') for x in file_.value.decode('utf-8').replace('\r', '').split('\n')],
                       columns=columns)

        df.astype({'call_count': 'float'})
        df.astype({'total_call_time': 'float'})
        df.astype({'total_exclusive_time': 'float'})

        # отправляем данные на предобработку и сохранение
        try:
            service.update_db(df)
            #service.update_db(service.get_labeled_df(df))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f'Error while preprocessing: {e}')

    except ClientDisconnect:
        print("Client Disconnected")

    except MaxBodySizeException as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'Maximum request body size limit ({MAX_REQUEST_BODY_SIZE} bytes) exceeded ({e.body_len} bytes read)')
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f'Maximum file size limit ({MAX_FILE_SIZE} bytes) exceeded')
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'There was an error uploading the file: {e}')

    return {"message": "success"}


@handlers.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = file.file.read()

        return contents

        with open(file.filename, 'wb') as f:
            f.write(contents)
    except Exception as e:
        return {"message": f"There was an error uploading the file: {e}"}
    finally:
        file.file.close()
        return pd.read_csv(file.filename, sep='\t').head(10).to_json()

        df = pd.read_csv(file.filename,
                         sep='\t',
                         names=['account_id', 'name', 'point', 'call_count', 'total_call_time',
                                'total_exclusive_time', 'min_call_time', 'max_call_time', 'sum_of_squares',
                                'instances', 'language', 'app_name', 'app_id', 'scope', 'host', 'display_host',
                                'pid', 'agent_version', 'labels'])

        df['call_count'] = df['call_count'].astype('float')
        df['total_call_time'] = df['total_call_time'].astype('float')
        df['total_exclusive_time'] = df['total_exclusive_time'].astype('float')

        try:
            service.update_db(df)
            #service.update_db(service.get_labeled_df(df))
            return {"message": ":)"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f'Error while preprocessing: {e}')


@handlers.get('/global_detection',
              description='get global predictions')
async def global_algo(start_dt: str, end_dt: str) -> Optional[list[dict]]:
    """
    Ручка по получению глобальных аномалий (аномалий относительно всего временного ряда)

    :param start_dt: левая граница временного интервала приближения
    :param end_dt: правая граница временного интервала приближения
    :return: списочное представление датафрейма для визуализации на фронте (либо exception)
    """

    # проверяем корректность заданных параметров
    if end_dt > start_dt:
        return service.query_db(start_dt, end_dt)
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='End date is earlier then start')


@handlers.get('/local_detection',
              description='get local predictions')
async def local_algo(start_dt: str, end_dt: str) -> Optional[dict]:
    """
    Ручка по получению глобальных аномалий (аномалий относительно всего временного ряда)

    :param start_dt: левая граница временного интервала приближения
    :param end_dt: правая граница временного интервала приближения
    :return: списочное представление датафрейма для визуализации на фронте (либо exception)
    """

    # проверяем корректность заданных параметров
    if end_dt > start_dt:
        return service.query_ml(datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S"),
                                datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S"))
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail='End date is earlier then start')
