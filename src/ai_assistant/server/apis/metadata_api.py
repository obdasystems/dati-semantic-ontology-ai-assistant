# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from ai_assistant.server.apis.metadata_api_base import BaseMetadataApi
import ai_assistant.server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
    Request
)

from pydantic import StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from fastapi import File, UploadFile
from ai_assistant.server.models.extra_models import TokenModel  # noqa: F401
from ai_assistant.server.security_api import get_token_jwt

router = APIRouter()

ns_pkg = ai_assistant.server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/ai/ontologyDraft/metadata",
    responses={
        200: {"model": str, "description": "OK"},
        401: {"description": "Unhauthorized"},
    },
    tags=["Metadata"],
    summary="Download a new version to the ontology enriched with the metadata provided in the request body.",
    response_model_by_alias=True,
)
async def post_ai_ontology_draft_metadata(
    request: Request,
    format: Optional[str] = Query(None, description="", alias="format"),
    new_version: Optional[str] = Query(None, description="", alias="newVersion"),
    file: Optional[UploadFile] = File(None, description="", alias="file"),
    metadata: Optional[UploadFile] = File(None, description="", alias="metadata"),
    token_jwt: TokenModel = Security(
        get_token_jwt
    ),
) -> str:
    if not BaseMetadataApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMetadataApi.subclasses[0]().post_ai_ontology_draft_metadata(request, format, new_version, file, metadata)
