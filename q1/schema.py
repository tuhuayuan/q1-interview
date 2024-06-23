from typing import Optional
from pydantic import BaseModel


class AddScoreRequest(BaseModel):
    user_id: str
    score: int
    score_modifier: Optional[int] = 1


class AddScoreResponse(BaseModel):
    user_id: str


class GetScoreResponse(BaseModel):
    user_id: str
    score: int


class TokenRequest(BaseModel):
    user_id: str


class TokenReponse(BaseModel):
    token: str
