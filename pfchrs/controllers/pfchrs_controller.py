# from fastapi import APIRouter, Query, Request, UploadFile
#
# from fastapi.encoders import jsonable_encoder
# from fastapi.concurrency import run_in_threadpool
# from pydantic import BaseModel, Field
# from typing import Optional, List, Dict, Callable, Any
#
import asyncio

# from pydantic_core.core_schema import ExpectedSerializationTypes
from models import iresponse, credentialModel
import os
from datetime import datetime

import json
import pudb
from config import settings
from controllers import credentialController

from argparse import Namespace, ArgumentParser
import sys
from loguru import logger
import shutil

import tempfile
from pathlib import Path
import uuid
from uuid import UUID
from lib import jobController

from starlette.responses import FileResponse

LOG = logger.debug

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> │ "
    "<level>{level: <5}</level> │ "
    "<yellow>{name: >28}</yellow>::"
    "<cyan>{function: <30}</cyan> @"
    "<cyan>{line: <4}</cyan> ║ "
    "<level>{message}</level>"
)
logger.remove()
logger.opt(colors=True)
logger.add(sys.stderr, format=logger_format)
LOG = logger.info


def noop():
    """
    A dummy function that does nothing.
    """
    return {"status": True}


async def cmd_exec(cmd: str, username: str, key: str) -> iresponse.ChRSResponse:
    resp: iresponse.ChRSResponse = iresponse.ChRSResponse()
    access: credentialModel.CredentialsStatus = (
        credentialController.credentialAccess_check(key)
    )
    if not access.status:
        resp.stderr = "Incorrect vault key supplied. CLI not executed.".encode()
        resp.returncode = -1
        return resp
    passwdData: credentialModel.Passwd = credentialController.passwd_get(key)
    if username not in passwdData.entry.keys():
        resp.stderr = "User not found in internal DB. CLI not executed.".encode()
        resp.returncode = -2
        return resp
    chrsCli: str = (
        f"/home/localuser/.cargo/bin/chrs --cube {passwdData.entry[username].cubeURL} --username {username} --password '{passwdData.entry[username].password}' {cmd}"
    )
    shell = jobController.jobber({})
    try:
        d_ret: dict = await shell.job_runFromScript(chrsCli)
        resp.stdout = d_ret["stdout"]
        resp.stderr = d_ret["stderr"]
        resp.returncode = d_ret["returncode"]
    except Exception as e:
        resp.stderr = f"{e}".encode("utf-8")
        resp.returncode = -3

    return resp
