import fastapi

import domain
from adapters.repository import MongoRepository
from domain.rules import universal_classifier
from service_layer import stats
from service_layer.dependencies import RepoDep, MtgoDep
from service_layer.services import get_mongo_db

router = fastapi.APIRouter(prefix="/stats", tags=["items"])


@router.get('/decks')
def get_stats_overview(
        repo: RepoDep,
        max_days: int = 21,
) -> list[domain.DeckStat]:
    return stats.get_stats(repo, max_days=max_days)
