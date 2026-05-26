"""
Tests for the AI SSE streaming views in apps.ai_features.api.

We mock _resolve_user, _get_org_for_user, _get_api_key, and the agent's
astream method so no real DB or LLM calls happen.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from django.test import AsyncClient


async def aiter(items):
    for item in items:
        yield item


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_stream_subject_lines_returns_sse():
    """POST /ai/subject-lines/stream streams SSE chunks and a done event."""
    mock_user = MagicMock()
    mock_user.pk = 1
    mock_org = MagicMock()
    mock_org.pk = 1

    mock_chunks = [
        MagicMock(content='1. Transform Enterprise Now\n'),
        MagicMock(content='2. Unlock Cloud Potential\n'),
    ]

    mock_job = MagicMock()
    mock_job.pk = 'test-job-uuid'

    with (
        patch('apps.ai_features.api._resolve_user', new=AsyncMock(return_value=mock_user)),
        patch('apps.ai_features.api._get_org_for_user', new=AsyncMock(return_value=mock_org)),
        patch('apps.ai_features.api._get_api_key', new=AsyncMock(return_value='sk-test')),
        patch('apps.ai_features.api.AIJob.objects.create', return_value=mock_job),
        patch('apps.ai_features.api.AIJob.objects.filter') as mock_filter,
        patch('apps.ai_features.agents.subject_line.get_llm') as mock_get_llm,
    ):
        mock_llm = MagicMock()
        mock_llm.astream = MagicMock(return_value=aiter(mock_chunks))
        mock_get_llm.return_value = mock_llm
        mock_filter.return_value.update = MagicMock(return_value=1)

        client = AsyncClient()
        payload = json.dumps({'campaign_name': 'Q4 Push', 'industry': 'SaaS'})
        response = await client.post(
            '/ai/subject-lines/stream',
            data=payload,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer fake-token',
        )

    assert response.status_code == 200
    assert 'text/event-stream' in response['Content-Type']


@pytest.mark.asyncio
async def test_stream_subject_lines_returns_401_without_auth():
    """POST without valid auth returns 401."""
    with patch('apps.ai_features.api._resolve_user', new=AsyncMock(return_value=None)):
        client = AsyncClient()
        response = await client.post(
            '/ai/subject-lines/stream',
            data=json.dumps({'campaign_name': 'Test'}),
            content_type='application/json',
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_stream_subject_lines_rejects_get():
    """GET request returns 405."""
    client = AsyncClient()
    response = await client.get('/ai/subject-lines/stream')
    assert response.status_code == 405
