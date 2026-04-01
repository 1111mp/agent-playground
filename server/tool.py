from typing import Dict, List

from pydantic import BaseModel


class ToolParametersProperty(BaseModel):
    type: str
    description: str | None = ""
    title: str | None = None


class ToolParameters(BaseModel):
    type: str
    properties: Dict[str, ToolParametersProperty] | str | int | float | bool | None
    required: List[str]
    additionalProperties: bool


class Tool(BaseModel):
    name: str
    description: str
    strict: bool
    parameters: ToolParameters
    code: str
