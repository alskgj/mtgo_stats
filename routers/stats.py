from typing import List

import fastapi

import domain
from adapters.repository import MongoRepository
from service_layer import stats
from service_layer.services import get_mongo_db

router = fastapi.APIRouter(prefix="/stats", tags=["items"])


@router.get('/')
def get_stats_overview() -> List[domain.DeckStat]:
    return stats.get_stats(MongoRepository(get_mongo_db()))
