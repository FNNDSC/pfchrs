from os import walk
from shutil import ignore_patterns
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks, Request
from fastapi import File, UploadFile, Path, Form
from typing import List, Dict, Any, Union, Annotated

from starlette.responses import FileResponse

from models import credentialModel
from models import iresponse
from controllers import pfchrs_controller
from routes import credentialRouter
from pathlib import Path as PathLib
from config import settings
from pftag import pftag
import pudb

router = APIRouter()
router.tags = ["pfchrs endpoints"]


@router.post(
    "/chrs/{cmd}",
    response_model=iresponse.ChRSResponse,
    summary="""
    POST a command to chrs.
    """,
)
async def chrs_cmdExec(
    cmd: str,
    username: str,
    vaultKey: str,
) -> iresponse.ChRSResponse:
    """
    Description
    -----------

    POST a command to a `chrs` app and return its response.

    Returns
    -------
    * `iresponse.ChRSResponse`: The response from chrs.
    """
    # pudb.set_trace()
    resp: iresponse.ChRSResponse = iresponse.ChRSResponse()
    resp = await pfchrs_controller.cmd_exec(cmd, username, vaultKey)

    return resp
