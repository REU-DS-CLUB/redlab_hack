import io
from pandas import read_csv

from fastapi import APIRouter, HTTPException
from fastapi import UploadFile
from starlette.status import HTTP_405_METHOD_NOT_ALLOWED, HTTP_200_OK

from . import service

handlers = APIRouter(
    prefix="/handlers",
    tags=['handlers']
)


def list_as_tuple(l):
    return tuple(l or [])


@handlers.post(path="/file",
               description="upload tsv dataset",
               response_model=None,
               status_code=HTTP_200_OK)
async def file_update(file: UploadFile):
    """
    :param file: required to update db
    :return: status code
    """

    if file.filename.endswith('.tsv'):
        f = await file.read()
        file = io.BytesIO(f)
        df = read_csv(file, sep='/t')
        service.update_db(df)

    elif file.filename.endswith('.gz'):
        f = await file.read()
        file = io.BytesIO(f)
        df = read_csv(file, compression='gzip', sep='/t')
        service.update_db(df)

    else:
        raise HTTPException(status_code=HTTP_405_METHOD_NOT_ALLOWED)
