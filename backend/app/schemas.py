from pydantic import BaseModel


class LoginRequest(BaseModel):
    login: str
    password: str


class RegistrationRequest(BaseModel):
    login: str
    password: str
