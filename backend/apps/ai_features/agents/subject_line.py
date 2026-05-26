from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm

SYSTEM_PROMPT = """You are an expert B2B email marketing specialist for Maven Technosoft,
a technology solutions company. Generate compelling subject lines for enterprise email campaigns.
Focus on: digital transformation, cloud computing, big data, enterprise solutions, TTHL technology.
Always produce exactly 5 subject lines, numbered 1-5, one per line.
Keep each under 60 characters. Focus on value, urgency, and enterprise relevance."""


class SubjectLineAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        campaign_name = input_data.get('campaign_name', '')
        industry = input_data.get('industry', 'Technology')
        tone = input_data.get('tone', 'professional')
        existing_draft = input_data.get('existing_draft', '')

        user_content = f"""Campaign: {campaign_name}
Industry: {industry}
Tone: {tone}
Existing draft (improve on this): {existing_draft}

Generate 5 high-converting subject lines:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
