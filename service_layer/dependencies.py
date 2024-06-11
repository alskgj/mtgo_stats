from typing import Annotated

from fastapi import Depends

from adapters import MtgoAPI, MtgoClient
from adapters.mtgo.api import AbstractAPI
from adapters.repository import MongoRepository, AbstractRepository
from service_layer.services import get_mongo_db


def get_repo() -> AbstractRepository:
    return MongoRepository(get_mongo_db())


def get_mtgo_api() -> AbstractAPI:
    return MtgoAPI(MtgoClient())


RepoDep = Annotated[AbstractRepository, Depends(get_repo)]
MtgoDep = Annotated[AbstractAPI, Depends(get_mtgo_api)]
