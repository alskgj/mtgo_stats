import pytest

from adapters import MtgoAPI
from adapters.mtgo.client import MtgoClient

pytestmark = pytest.mark.slow


@pytest.fixture
def real_api() -> MtgoAPI:
    return MtgoAPI(MtgoClient())


@pytest.mark.asyncio
async def test_fetch_links(real_api: MtgoAPI):
    links = await real_api.fetch_tournament_links(months=2)

    assert len(links) > 0
    assert 'mtgo.com/decklist' in links[0]


@pytest.mark.asyncio
async def test_fetch_tournament(real_api: MtgoAPI):
    links = await real_api.fetch_tournament_links(months=2)
    tournament = await real_api.fetch_tournament(links[0])

    assert len(tournament.players) > 0
