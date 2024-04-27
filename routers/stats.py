import fastapi

from mtgoResultsTracker.adapters.repository import MongoRepository
from mtgoResultsTracker.service_layer import stats
from mtgoResultsTracker.service_layer.services import get_mongo_db

router = fastapi.APIRouter(prefix="/stats", tags=["items"])


@router.get('/')
def get_stats_overview():
    return stats.get_stats(MongoRepository(get_mongo_db()))
