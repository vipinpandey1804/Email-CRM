from ninja import Schema
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CampaignCreateIn(Schema):
    name: str
    subject_line: str = ''
    preview_text: str = ''
    from_name: str = ''
    from_email: str = ''
    reply_to: str = ''
    tags: List[str] = []
    template_id: Optional[UUID] = None


class CampaignUpdateIn(Schema):
    name: Optional[str] = None
    subject_line: Optional[str] = None
    preview_text: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    reply_to: Optional[str] = None
    tags: Optional[List[str]] = None
    template_id: Optional[UUID] = None


class CampaignOut(Schema):
    id: UUID
    name: str
    subject_line: str
    preview_text: str
    from_name: str
    from_email: str
    reply_to: str
    tags: List[str]
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    created_at: datetime


class ScheduleIn(Schema):
    scheduled_at: datetime


class RecipientIn(Schema):
    email: str
    name: str = ''


class RecipientsAddIn(Schema):
    recipients: List[RecipientIn]


class RecipientOut(Schema):
    id: UUID
    email: str
    name: str
    status: str
    sent_at: Optional[datetime] = None
    error_message: str
