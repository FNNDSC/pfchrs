from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel
import pudb
from config import settings
from fastapi import File, UploadFile


class ChRSResponse(BaseModel):
    stdout: bytes = b""
    stderr: bytes = b""
    returncode: int = 0
