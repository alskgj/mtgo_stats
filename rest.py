import asyncio
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from starlette.responses import FileResponse

from adapters.repository import MongoRepository
from cli import fetch
from routers import stats
from service_layer.services import get_mongo_db
from service_layer.stats import get_stats, create_html_table


async def generate_html_out():
    repo = MongoRepository(get_mongo_db())
    # fetch new tournaments
    fetch(months=1)

    # generate html
    s = get_stats(repo)
    table = create_html_table(s, colorize=True)
    with open('out.html', 'w') as f:
        f.write(table)


async def periodically_create_html():
    while True:
        await generate_html_out()
        await asyncio.sleep(300)


@asynccontextmanager
async def lifespan(app_: fastapi.FastAPI):
    # Load the ML model
    task = asyncio.create_task(periodically_create_html())
    print(task)
    yield
    print(task)

app = fastapi.FastAPI(lifespan=lifespan)
app.include_router(stats.router)


@app.get("/")
async def root():
    return FileResponse('out.html')
    # return fastapi.responses.RedirectResponse(url='/docs')


def main():
    uvicorn.run(app)


if __name__ == '__main__':
    main()
