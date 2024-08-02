import fastapi

import domain
from service_layer import stats
from service_layer.dependencies import RepoDep

router = fastapi.APIRouter(prefix="/stats", tags=["items"])


@router.get('/competition_scores')
def get_competition_scores(
        repo: RepoDep,
        max_days: int = 21,
) -> domain.CompetitionScoreListing:
    return stats.calculate_competition_score(repo, max_days)
