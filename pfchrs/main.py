from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from base.router import helloRouter_create

from routes.pfchrs_router import router as pfchrs_router
from routes.credentialRouter import router as credential_router
from os import path
from config import settings
import pudb

with open(path.join(path.dirname(path.abspath(__file__)), "ABOUT")) as f:
    str_about: str = f.read()

with open(path.join(path.dirname(path.abspath(__file__)), "VERSION")) as f:
    str_version: str = f.read().strip()

tags_metadata: list = [
    {
        "name": "pfchrs endpoints",
        "description": """
            Endpoints for interacting with chrs.
            """,
    },
    {
        "name": "Credentialling services",
        "description": """
            Provide API endpoints for setting a vaultKey which is used to unlock
            sensitive data.
            """,
    },
    {
        "name": "pfchrs environmental detail",
        "description": """
            Provide API GET endpoints that provide information about the
            service itself and the compute environment in which the service
            is deployed.
            """,
    },
]

# On startup, check if a vaultKey has been set by the environment,
# and if so, check/lock the vault.
settings.vaultCheckLock(settings.vault)

app = FastAPI(title="pfchrs", version=str_version, openapi_tags=tags_metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

hello_router: APIRouter = helloRouter_create(
    name="pfchrs_hello", version=str_version, about=str_about
)

app.include_router(pfchrs_router, prefix="/api/v1")

app.include_router(credential_router, prefix="/api/v1")

app.include_router(hello_router, prefix="/api/v1")
