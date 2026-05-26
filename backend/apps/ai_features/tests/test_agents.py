import pytest
from unittest.mock import AsyncMock, patch, MagicMock


async def aiter(items):
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_subject_line_agent_streams_chunks():
    mock_llm = MagicMock()
    mock_chunks = [
        MagicMock(content='1. Transform Your Enterprise\n'),
        MagicMock(content='2. Modernize Operations Today\n'),
        MagicMock(content='3. Unlock Business Insights\n'),
    ]
    mock_llm.astream = MagicMock(return_value=aiter(mock_chunks))

    with patch('apps.ai_features.agents.subject_line.get_llm', return_value=mock_llm):
        from apps.ai_features.agents.subject_line import SubjectLineAgent
        agent = SubjectLineAgent(api_key='test-key')
        chunks = []
        async for chunk in agent.astream({'campaign_name': 'Cloud Launch', 'industry': 'Technology'}):
            chunks.append(chunk)

    assert len(chunks) == 3
    assert 'Transform' in chunks[0]


@pytest.mark.asyncio
async def test_spam_checker_agent_streams():
    mock_llm = MagicMock()
    mock_chunks = [MagicMock(content='SPAM SCORE: 12/100\nRISK LEVEL: Low\n')]
    mock_llm.astream = MagicMock(return_value=aiter(mock_chunks))

    with patch('apps.ai_features.agents.spam_checker.get_llm', return_value=mock_llm):
        from apps.ai_features.agents.spam_checker import SpamCheckerAgent
        agent = SpamCheckerAgent(api_key='test-key')
        chunks = []
        async for chunk in agent.astream({'subject': 'Hello World', 'body': 'Professional content here'}):
            chunks.append(chunk)

    assert len(chunks) == 1
    assert 'SPAM SCORE' in chunks[0]


@pytest.mark.asyncio
async def test_subject_line_agent_skips_empty_chunks():
    mock_llm = MagicMock()
    mock_chunks = [
        MagicMock(content=''),       # empty — should be skipped
        MagicMock(content='Line 1'),
    ]
    mock_llm.astream = MagicMock(return_value=aiter(mock_chunks))

    with patch('apps.ai_features.agents.subject_line.get_llm', return_value=mock_llm):
        from apps.ai_features.agents.subject_line import SubjectLineAgent
        agent = SubjectLineAgent(api_key='test-key')
        chunks = []
        async for chunk in agent.astream({'campaign_name': 'Test'}):
            chunks.append(chunk)

    assert chunks == ['Line 1']
