import fastapi
from routers import stats

app = fastapi.FastAPI()
app.include_router(stats.router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
