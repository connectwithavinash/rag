from pydantic import BaseModel
from typing import Any

class SuccessResponse(BaseModel):
    message: str = "Success"
    status: str = "success"
    data: Any = None

class FailureResponse(BaseModel):
    message: str = "Failure"
    status: str = "failure"
    data: Any = None