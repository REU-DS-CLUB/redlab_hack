import io
from pandas import read_table, DataFrame

from fastapi import APIRouter, UploadFile, Request, HTTPException, status
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import FileTarget, ValueTarget
from streaming_form_data.validators import MaxSizeValidator, ValidationError
from starlette.requests import ClientDisconnect
from starlette.status import HTTP_405_METHOD_NOT_ALLOWED, HTTP_200_OK

from . import service

MAX_FILE_SIZE = 1024 * 1024 * 1024 * 4
MAX_REQUEST_BODY_SIZE = MAX_FILE_SIZE + 1024

handlers = APIRouter(
    prefix="/handlers",
    tags=['handlers']
)


def list_as_tuple(l):
    return tuple(l or [])


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


@handlers.post('/upload')
async def upload(request: Request):
    body_validator = MaxBodySizeValidator(MAX_REQUEST_BODY_SIZE)
    filename = request.headers.get('Filename')

    if not filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail='Filename header is missing')
    try:
        file_ = ValueTarget(validator=MaxSizeValidator(MAX_FILE_SIZE))
        #filepath = os.path.join('./', os.path.basename(filename))
        #file_ = FileTarget(filepath, validator=MaxSizeValidator(MAX_FILE_SIZE))
        parser = StreamingFormDataParser(headers=request.headers)
        parser.register('file', file_)
        async for chunk in request.stream():
            body_validator(chunk)
            parser.data_received(chunk)

        columns = ['account_id', 'name', 'point', 'call_count', 'total_call_time', 'total_exclusive_time',
                   'min_call_time', 'max_call_time', 'sum_of_squares', 'instances', 'language', 'app_name',
                   'app_id', 'scope', 'host', 'display_host', 'pid', 'agent_version', 'labels']

        df = DataFrame([x.split('\t') for x in file_.value.decode('utf-8').replace('\r', '').split('\n')],
                       columns=columns)
        min_dt, max_dt = service.update_db(df)
        # df = pd.read_table(filepath)
        # return {"filepath": filepath, "file_": file_.multipart_filename, "df": str(df.head(0))}
        return {"min_dt": min_dt, "max_dt": max_dt}

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


@handlers.get('/simple')
async def simple(start_dt: str, end_dt: str):
    return service.query_db(start_dt, end_dt)


@handlers.get('/complicated')
async def complicated(start_dt: str, end_dt: str, flag: bool):
    return service.query_ml(start_dt, end_dt, flag)
