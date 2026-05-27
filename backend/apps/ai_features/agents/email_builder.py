from typing import AsyncIterator
from langchain_core.messages import HumanMessage, SystemMessage
from apps.ai_features.agents.base import get_llm

SYSTEM_PROMPT = """You are an expert email designer for Maven Technosoft, an enterprise
technology company (cloud, big data, AI, digital transformation).

Generate a COMPLETE, production-ready marketing email as MJML markup.

STRICT OUTPUT RULES — follow exactly:
- Output ONLY valid MJML. The response MUST start with <mjml> and end with </mjml>.
- Do NOT use markdown, code fences (```), or any explanation before or after the MJML.
- Build a full email: a branded header containing "Maven Technosoft", a hero heading,
  1-3 short body paragraphs, an optional bullet list or highlight, a clear call-to-action
  <mj-button>, and a footer with an unsubscribe line.
- Use <mj-section>, <mj-column>, <mj-text>, <mj-button> (and <mj-image> only with real
  https URLs or omit it). Style with mj-attributes / inline attributes; use a strong accent
  color for the header bar and the button.
- Keep copy concise, professional, and enterprise-focused.
- Use the personalization tokens {{first_name}} and {{company_name}} where natural.
- Ensure it is responsive and email-client safe."""


class EmailBuilderAgent:
    """Generates a full MJML email from a short brief."""

    def __init__(self, api_key: str):
        self.llm = get_llm(api_key)

    async def astream(self, input_data: dict) -> AsyncIterator[str]:
        title = input_data.get('title') or input_data.get('campaign_name', 'Email Campaign')
        goal = input_data.get('goal', 'drive engagement and conversions')
        industry = input_data.get('industry', 'Technology')
        tone = input_data.get('tone', 'professional')
        key_points = input_data.get('key_points', '')

        user_content = f"""Create a complete marketing email.

Title / theme: {title}
Primary goal: {goal}
Industry: {industry}
Tone: {tone}
Key points to include: {key_points or '(use sensible enterprise messaging)'}

Return the full MJML now, starting with <mjml>:"""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]

        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
