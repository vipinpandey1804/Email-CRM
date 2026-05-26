from ninja import Schema
from typing import Optional
from uuid import UUID
from datetime import datetime


class TemplateCreateIn(Schema):
    name: str
    category: str = 'promo'


class TemplateSaveIn(Schema):
    name: Optional[str] = None
    category: Optional[str] = None
    gjs_components: Optional[dict] = None
    gjs_styles: Optional[dict] = None
    mjml_source: Optional[str] = None
    html_output: Optional[str] = None
    thumbnail_url: Optional[str] = None


class TemplateOut(Schema):
    id: UUID
    name: str
    category: str
    thumbnail_url: str
    is_system: bool
    gjs_components: dict
    gjs_styles: dict
    mjml_source: str
    html_output: str
    updated_at: datetime
