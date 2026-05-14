from fastapi import FastAPI
from backend.app.routes.shorten import router as shorten_router

app = FastAPI()

app.include_router(shorten_router)

try:
    from backend.app.routes.redirect import router as redirect_router
    app.include_router(redirect_router)
except ImportError:
    pass

try:
    from backend.app.routes.stats import router as stats_router
    app.include_router(stats_router)
except ImportError:
    pass

try:
    from backend.app.routes.delete import router as delete_router
    app.include_router(delete_router)
except ImportError:
    pass


@app.get("/health")
def health_check():
    return {"status": "healthy"}
