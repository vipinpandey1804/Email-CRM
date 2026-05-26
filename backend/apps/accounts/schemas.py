from ninja import Schema
from uuid import UUID


class LoginIn(Schema):
    email: str
    password: str


class TokenOut(Schema):
    access: str
    refresh: str


class GoogleAuthIn(Schema):
    id_token: str


class MeOut(Schema):
    id: UUID
    email: str
    full_name: str
    is_staff: bool
