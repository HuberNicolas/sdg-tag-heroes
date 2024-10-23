import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from api.app.routes import publications
from api.app.routes import authors
from api.app.routes import authentication

from fastapi_pagination import add_pagination

log = logging.getLogger(__name__)


app = FastAPI()
add_pagination(app)  # important! add pagination to your app

app.include_router(publications.router)
app.include_router(authors.router)
app.include_router(authentication.router)

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
        title="Your API Title",
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
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
