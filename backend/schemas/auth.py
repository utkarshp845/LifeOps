from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
