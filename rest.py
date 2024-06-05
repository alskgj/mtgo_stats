import asyncio
import logging
import os
import traceback
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from starlette.responses import FileResponse

import adapters
from adapters.repository import MongoRepository
from cli import fetch
from routers import stats
from service_layer import services
from service_layer.services import get_mongo_db
from service_layer.stats import get_stats, create_html_table


def setup_logging():
    logger = logging.getLogger(__name__)

    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)

    logger.info('wow')
    return logger


async def generate_html_out():
    # fetch new tournaments
    repo = MongoRepository(get_mongo_db())
    api = adapters.MtgoAPI()
    await services.cache_tournaments(api, repo, months=2)

    # generate html
    s = get_stats(repo, max_days=21)[:20]
    table = create_html_table(s, colorize=True)
    with open('out.html', 'w') as f:
        f.write(table)


async def periodically_create_html():
    await asyncio.sleep(1)  # let the web server start first, any asyncio statement here is fine
    while True:
        logger.info('Generating new static page...')
        try:
            await generate_html_out()
        except Exception as e:
            logger.error(f'Error while generating static page: {e}\n{traceback.format_exc()}')
        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(app_: fastapi.FastAPI):
    task = asyncio.create_task(periodically_create_html())
    logger.info('Created task to periodically generate static page.')
    yield
    logger.warning('Stopping periodically creating static page.')
    task.cancel()

app = fastapi.FastAPI(lifespan=lifespan)
app.include_router(stats.router)


@app.get("/")
async def root():
    return FileResponse('out.html')


@app.get('/fetch')
async def cache_all_the_tournaments() -> list[str]:
    """
    Returns a list of newly cached tournaments, empty if no new tournaments have been cached.
    """
    # {start_time: {$gte: new Date('2024-06-1')}}
    repo = MongoRepository(get_mongo_db())
    api = adapters.MtgoAPI()
    return await services.cache_tournaments(api, repo)


def main():
    uvicorn.run(app)


logger = setup_logging()

if __name__ == '__main__':
    main()
