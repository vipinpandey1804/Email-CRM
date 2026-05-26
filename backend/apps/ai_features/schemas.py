from typing import Optional
from ninja import Schema


class SubjectLineRequest(Schema):
    campaign_name: str
    industry: str = 'Technology'
    tone: str = 'professional'
    existing_draft: str = ''
    campaign_id: Optional[str] = None


class CopyOptimizerRequest(Schema):
    copy: str
    tone: str = 'professional'
    brand_voice: str = 'innovative, reliable, enterprise-focused'
    campaign_id: Optional[str] = None


class SpamCheckerRequest(Schema):
    subject: str
    body: str
    preview_text: str = ''
    campaign_id: Optional[str] = None


class CTAOptimizerRequest(Schema):
    campaign_goal: str = 'schedule a demo'
    current_cta: str = ''
    industry: str = 'Technology'
    campaign_id: Optional[str] = None


class AIJobOut(Schema):
    id: str
    job_type: str
    status: str
    output_data: Optional[dict] = None
