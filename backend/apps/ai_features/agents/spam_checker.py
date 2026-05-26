from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm

SYSTEM_PROMPT = """You are an email deliverability expert. Analyze the provided email content for spam triggers.
Your response MUST follow this exact format:
SPAM SCORE: [0-100]/100
RISK LEVEL: [Low/Medium/High]
FLAGGED WORDS: [comma-separated list or 'None']
ISSUES:
- [issue 1]
- [issue 2]
FIXES:
- [fix 1]
- [fix 2]"""


class SpamCheckerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        subject = input_data.get('subject', '')
        preview_text = input_data.get('preview_text', '')
        body = input_data.get('body', '')

        user_content = f"""Subject line: {subject}
Preview text: {preview_text}
Email body: {body[:2000]}

Analyze for spam triggers and provide deliverability report:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
