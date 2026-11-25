"""
Configs for the Ontolog-IA API.
"""

import os
import argparse
import logging
from dotenv import load_dotenv
from lightrag.utils import get_env_value

from ai_assistant.constants import (
    DEFAULT_LOG_FILENAME,
    DEFAULT_WOKERS,
    DEFAULT_TIMEOUT,
)

load_dotenv(override=False)

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments with environment variable fallback

    Args:
        is_uvicorn_mode: Whether running under uvicorn mode

    Returns:
        argparse.Namespace: Parsed arguments
    """

    parser = argparse.ArgumentParser(
        description="Ontology generative AI assistant with separate working and input directories"
    )

    # Logging configuration
    parser.add_argument(
#        "-L", 
        "--log-file",
        type=str,
        default=DEFAULT_LOG_FILENAME,
        help="Log to the given output file.",
    )
    parser.add_argument(
        "--log-level",
        default=get_env_value("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: from env or INFO)",
    )
    parser.add_argument(
#         "-v", 
        "--verbose",
#         action="count",
        action="store_true",
#         default=0,
        default=get_env_value("VERBOSE", False, bool),
#         help="Produce verbose output. Multiple occurrences increase verbosity.",
        help="Enable verbose debug output(only valid for DEBUG log-level)",
    )

    # Server configuration
    parser.add_argument(
        "--host",
        default=get_env_value("HOST", "127.0.0.1"),
        help="Server host (default: from env or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=get_env_value("PORT", 8200, int),
        help="Server port (default: from env or 8200)",
    )

    # Directory configuration
    parser.add_argument(
        "--working-dir",
        default=get_env_value("WORKING_DIR", "./rag_storage"),
        help="Working directory for RAG storage (default: from env or ./rag_storage)",
    )
    parser.add_argument(
        "--input-dir",
        default=get_env_value("INPUT_DIR", "./inputs"),
        help="Directory containing input documents (default: from env or ./inputs)",
    )

    parser.add_argument(
        "--timeout",
        default=get_env_value("TIMEOUT", DEFAULT_TIMEOUT, int, special_none=True),
        type=int,
        help="Timeout in seconds (useful when using slow AI). Use None for infinite timeout",
    )

    # RAG configuration
    parser.add_argument(
        "--max-async",
        type=int,
        default=get_env_value("MAX_ASYNC", 4, int),
        help="Maximum async operations (default: from env or 4)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=get_env_value("MAX_TOKENS", 32000, int),
        help="Maximum token size (default: from env or 32768)",
    )

    # Namespace
    parser.add_argument(
        "--workspace",
        type=str,
        default=get_env_value("WORKSPACE", ""),
        help="Default workspace for all storage",
    )

    # Server workers configuration
    parser.add_argument(
        "--workers",
        type=int,
        default=get_env_value("WORKERS", DEFAULT_WOKERS, int),
        help="Number of worker processes (default: from env or 1)",
    )

    parser.add_argument(
        "-m", "--mount",
        type=str,
        default="",
        help="The path to mount the main router to (defaults to /).",
    )
    parser.add_argument(
        "-P", "--root-path", 
        type=str,
        default="",
        help="The root path that is used to serve the API from (defaults to /).",
    )

    args = parser.parse_args()

    # convert relative path to absolute path
    args.working_dir = os.path.abspath(args.working_dir)
    os.environ["WORKING_DIR"] = args.working_dir
    args.input_dir = os.path.abspath(args.input_dir)
    # se in args è indicato un file di log, lo imposto nell'env
    if args.log_file:
        os.environ["LOG_FILENAME"] = args.log_file
    # è il parametro da passare a FastAPI app
    if args.mount:
        os.environ["ROOT_PATH"] = args.mount
    # è il parametro da passare a Uvicorn worker
    if args.root_path:
        os.environ["UVICORN_ROOT_PATH"] = args.root_path

    return args


def update_uvicorn_mode_config():
    # If in uvicorn mode and workers > 1, force it to 1 and log warning
    if global_args.workers > 1:
        original_workers = global_args.workers
        global_args.workers = 1
        # Log warning directly here
        logging.warning(
            f"In uvicorn mode, workers parameter was set to {original_workers}. Forcing workers=1"
        )


global_args = parse_args()
