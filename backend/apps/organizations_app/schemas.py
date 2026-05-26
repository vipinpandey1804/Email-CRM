from ninja import Schema
from typing import Optional


class OrgOut(Schema):
    id: int
    name: str
    slug: str
    is_active: bool
    plan: Optional[str] = 'internal'
    logo_url: Optional[str] = ''


class OrgUpdateIn(Schema):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: Optional[dict] = None


class OrgUserOut(Schema):
    user_email: str
    user_full_name: str
    role: str
    is_admin: bool


class InviteIn(Schema):
    email: str
    role: str = 'editor'
