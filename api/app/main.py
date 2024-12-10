import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.app.routes import publications
from api.app.routes import authors
from api.app.routes import authentication
from api.app.routes import sdgs
from api.app.routes import votes
from api.app.routes import annotations
from api.app.routes import sdg_user_labels
from api.app.routes import dimensionality_reductions
from api.app.routes import users
from api.app.routes import sdg_predictions
from api.app.routes import profiles
from api.app.routes import summaries

from fastapi_pagination import add_pagination

log = logging.getLogger(__name__)


app = FastAPI()
add_pagination(app)  # important! add pagination to your app

app.include_router(publications.router)
app.include_router(authors.router)
app.include_router(authentication.router)
app.include_router(sdgs.router)
app.include_router(votes.router)
app.include_router(annotations.router)
app.include_router(sdg_user_labels.router)
app.include_router(dimensionality_reductions.router)
app.include_router(users.router)
app.include_router(sdg_predictions.router)
app.include_router(profiles.router)
app.include_router(summaries.router)

# CORS (development only)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Custom OpenAPI schema to include JWT in Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SDG Tag Heroes",
        version="1.0.0",
        description="API Documentation with JWT Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    # Apply globally to all routes
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
