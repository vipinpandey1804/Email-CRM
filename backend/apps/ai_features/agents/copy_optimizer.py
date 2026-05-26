from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm

SYSTEM_PROMPT = """You are an enterprise email copywriter for Maven Technosoft.
Rewrite the provided email copy to be more compelling, professional, and conversion-focused.
Maintain the original intent but improve: clarity, tone, CTA strength, and enterprise positioning.
Output only the improved copy — no explanations."""


class CopyOptimizerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        original_copy = input_data.get('copy', '')
        tone = input_data.get('tone', 'professional')
        brand_voice = input_data.get('brand_voice', 'innovative, reliable, enterprise-focused')

        user_content = f"""Original email copy:
{original_copy}

Target tone: {tone}
Brand voice: {brand_voice}

Rewrite this copy to be more compelling:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
