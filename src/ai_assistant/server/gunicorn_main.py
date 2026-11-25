# coding: utf-8
import re
from contextlib import asynccontextmanager
import os
import shutil
import json
import asyncio
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc, set_verbose_debug, logger as lrag_logger
from lightrag.namespace import NameSpace
from lightrag.rerank import custom_rerank, RerankModel

from ai_assistant.server.config.config import (
    global_args,
#     update_uvicorn_mode_config,
#     get_default_host,
)
from ai_assistant.server.models.rdf_graph import RDFGraph
from ai_assistant.server.models.vector_db_status import VectorDBStatus
from ai_assistant.gscape import load_gscape
from ai_assistant.utils import logger
from ai_assistant.rag import OntoRAG, ainitialize_ontorag
from ai_assistant.jvm import startJVM
from ai_assistant.llm.openai import (
    vllm_embed,
    vllm_model_complete,
)
from ai_assistant.server.apis.convert_api import router as ConvertApiRouter
from ai_assistant.server.apis.prompt_api import router as PromptApiRouter
from ai_assistant.server.apis.rag_api import router as RAGApiRouter
from ai_assistant.server.apis.rag_api import router as RAGApiRouter
from ai_assistant.server.apis.metadata_api import router as MetadataApiRouter

def create_app(args):

    # Setup logging
    log_dir = os.getenv("LOG_DIR", os.path.abspath(os.sep.join([os.getcwd(), "logs"])))
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_file_path = os.sep.join([log_dir, args.log_file])
    logger.setLevel(args.log_level)
    set_verbose_debug(args.verbose) # only for logger
    lrag_logger.setLevel(args.log_level)

    # Setup working dir
    working_dir = args.working_dir
    
    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        """Lifespan of the server."""
        ########################################
        # Startup event
        ########################################
#        load_dotenv(override=False)
        prefix = os.getenv("ROOT_PATH")
        if prefix:
            app_instance.mount(prefix, app_instance)
        try:
            if not hasattr(app_instance, "designer_rag"):
                # Questa inizializzazione di ontorag funziona solo se l'opzione 
                # Gunicorn preload è False
                logger.warning(f"Not created ontorag per process {str(os.getpid())}. Created in app")
                app_instance.designer_rag = await ainitialize_ontorag(
                    working_dir = os.getenv("WORKING_DIR"),
                    workspace = str(os.getpid()),
                    not_initialize_storages=True,
                )

            # Initialize database connections
            await app_instance.designer_rag.initialize_storages()

            await initialize_pipeline_status()
            startJVM()
            logger.info("Ontology AI-Assistant public version")
            yield
        finally:
            ########################################
            # Shutdown event
            ########################################
            # Clean up database connections
            await app_instance.designer_rag.finalize_storages()
            # Delete workspace if persist not enabled
            if os.getenv("ENABLE_DISK_PERSIST", "False").strip().lower() == "false":
                workspace_path = os.path.join(
                    app_instance.designer_rag.working_dir,
                    app_instance.designer_rag.workspace
                )
                shutil.rmtree(workspace_path, ignore_errors=False)
                logger.info(f"Delete the workspace: {workspace_path}")
    
    app = FastAPI(
        title="AI assistant API model",
        description="This is the API for the AI assistant module",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(ConvertApiRouter)
    app.include_router(PromptApiRouter)
    app.include_router(RAGApiRouter)
    app.include_router(MetadataApiRouter)


    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
        logger.error(f"{request}: {exc_str}")
        content = {'status_code': 10422, 'message': exc_str, 'data': None}
        return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    return app

def get_application(args=None):
    """Factory function for creating the FastAPI application"""
    if args is None:
        args = global_args
    return create_app(args)

