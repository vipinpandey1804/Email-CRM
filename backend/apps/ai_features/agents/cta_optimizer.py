from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm

SYSTEM_PROMPT = """You are a conversion rate optimization expert for B2B enterprise emails.
Generate high-converting CTA button text variants.
Output exactly 4 CTA options, formatted as:
1. [CTA TEXT] — [Why it converts]
2. [CTA TEXT] — [Why it converts]
3. [CTA TEXT] — [Why it converts]
4. [CTA TEXT] — [Why it converts]
Keep CTA text under 5 words. Focus on enterprise action verbs."""


class CTAOptimizerAgent:
    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        campaign_goal = input_data.get('campaign_goal', 'schedule a demo')
        current_cta = input_data.get('current_cta', '')
        industry = input_data.get('industry', 'Technology')

        user_content = f"""Campaign goal: {campaign_goal}
Current CTA: {current_cta}
Industry: {industry}

Generate 4 high-converting CTA variants:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
