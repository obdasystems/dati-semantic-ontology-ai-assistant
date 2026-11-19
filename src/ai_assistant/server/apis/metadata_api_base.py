# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401
from fastapi import Request

from pydantic import StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from fastapi import File, UploadFile
from ai_assistant.server.security_api import get_token_jwt

class BaseMetadataApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseMetadataApi.subclasses = BaseMetadataApi.subclasses + (cls,)
    async def post_ai_ontology_draft_metadata(
        self,
        request: Request,
        format: Optional[str],
        new_version: Optional[str],
        file: Optional[UploadFile],
        metadata: Optional[UploadFile],
    ) -> str:
        ...
