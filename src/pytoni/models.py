from pydantic import BaseModel, Field
from uuid import uuid4


class UserMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    message: str


class AssistantMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    message: str
