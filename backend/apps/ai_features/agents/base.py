from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel


def get_llm(api_key: str, model: str = 'gpt-4o', streaming: bool = True) -> BaseChatModel:
    """
    Factory that returns the configured LLM.
    Swap ChatOpenAI for ChatAnthropic / ChatGoogleGenerativeAI here for provider switching.
    """
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        streaming=streaming,
        temperature=0.7,
    )
