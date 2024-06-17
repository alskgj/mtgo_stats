import abc
import httpx


class AbstractMtgoClient(abc.ABC):

    @abc.abstractmethod
    async def fetch_tournaments_page(self, year, month):
        ...

    @abc.abstractmethod
    async def fetch_tournament(self, url) -> str:
        ...

    @abc.abstractmethod
    async def fetch_tournament_data(self, url) -> dict:
        ...


class MtgoClient(AbstractMtgoClient):
    base_url = 'https://www.mtgo.com'

    async def fetch_tournaments_page(self, year, month) -> str:
        """
        Fetches an url like https://www.mtgo.com/decklists/2024/05
        and returns the whole page
        """
        url = f'{self.base_url}/decklists/{year}/{month:02}'

        # todo - replace with long living client?
        async with httpx.AsyncClient(timeout=60, transport=httpx.AsyncHTTPTransport(retries=3)) as client:
            r = await client.get(url)
        return r.text

    async def fetch_tournament(self, url) -> str:
        """
        Fetches an url like https://www.mtgo.com/decklist/pioneer-challenge-32-2024-05-3112643048
        and returns the whole page
        """
        # todo - replace with long living client?
        async with httpx.AsyncClient(timeout=60, transport=httpx.AsyncHTTPTransport(retries=3)) as client:
            r = await client.get(url)
        return r.text

    async def fetch_tournament_data(self, url) -> dict:
        """
        Fetches an api url from census.daybreakgames.com and returns the resulting json
        """
        # todo - replace with long living client?
        async with httpx.AsyncClient(timeout=60, transport=httpx.AsyncHTTPTransport(retries=3)) as client:
            r = await client.get(url)
        return r.json()
