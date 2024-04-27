import fastapi
import uvicorn
from routers import stats

app = fastapi.FastAPI()
app.include_router(stats.router)


@app.get("/")
async def root():
    return fastapi.responses.RedirectResponse(url='/docs')


def main():
    uvicorn.run(app)


if __name__ == '__main__':
    main()
