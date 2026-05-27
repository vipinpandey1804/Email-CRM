"""
AI features API — SSE streaming endpoints for all four agents.

Each POST endpoint authenticates via Bearer JWT, creates an AIJob record,
then streams Server-Sent Events (text/event-stream) as the LLM produces tokens.

Because Django Ninja's schema serialisation doesn't apply to StreamingHttpResponse,
these endpoints are defined as standard async Django views and wired into urls.py
directly (not via the Ninja router). A thin Ninja router is still exported for
any future non-streaming endpoints.
"""

import json
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from ninja import Router

from apps.accounts.auth import JWTAuth
from apps.organizations_app.models import OrganizationUserProfile
from .models import AIJob
from .agents.subject_line import SubjectLineAgent
from .agents.copy_optimizer import CopyOptimizerAgent
from .agents.spam_checker import SpamCheckerAgent
from .agents.cta_optimizer import CTAOptimizerAgent

logger = logging.getLogger(__name__)

# Thin Ninja router (future non-streaming endpoints)
router = Router()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AGENT_MAP = {
    'subject_lines': SubjectLineAgent,
    'copy_optimize': CopyOptimizerAgent,
    'spam_check': SpamCheckerAgent,
    'cta_suggest': CTAOptimizerAgent,
}


async def _resolve_user(request):
    """Validate Bearer token and return User or None."""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    token = auth_header[7:]
    from apps.accounts.auth import JWTAuth as _JWTAuth
    auth = _JWTAuth()
    # JWTAuth.authenticate is sync — wrap it
    from asgiref.sync import sync_to_async
    return await sync_to_async(auth.authenticate)(request, token)


async def _get_org_for_user(user):
    from asgiref.sync import sync_to_async

    def _fetch(u):
        profile = (
            OrganizationUserProfile.objects
            .select_related('org_user__organization')
            .filter(org_user__user=u)
            .first()
        )
        return profile.org_user.organization if profile else None

    return await sync_to_async(_fetch)(user)


async def _get_api_key(org):
    from asgiref.sync import sync_to_async

    def _fetch(o):
        try:
            return o.organizationprofile.openai_api_key or ''
        except Exception:
            return ''

    return await sync_to_async(_fetch)(org)


async def _sse_stream(request, job_type: str):
    """Core SSE handler — shared by all four agent endpoints."""
    # 1. Auth
    user = await _resolve_user(request)
    if not user:
        return JsonResponse({'detail': 'Unauthorized'}, status=401)

    # 2. Parse body
    try:
        input_data = json.loads(request.body)
    except Exception:
        return JsonResponse({'detail': 'Invalid JSON'}, status=400)

    # 3. Org + API key
    org = await _get_org_for_user(user)
    api_key = await _get_api_key(org) if org else ''

    # 4. Create job record
    from asgiref.sync import sync_to_async
    create_job = sync_to_async(AIJob.objects.create)
    job = await create_job(
        organization=org,
        job_type=job_type,
        status='running',
        input_data=input_data,
        created_by=user,
    )

    # 5. Pick agent
    agent_cls = _AGENT_MAP[job_type]
    agent = agent_cls(api_key=api_key)

    # 6. Streaming generator
    async def event_generator():
        collected: list[str] = []
        try:
            async for chunk in agent.astream(input_data):
                collected.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"

            full_output = ''.join(collected)
            update_job = sync_to_async(
                lambda: AIJob.objects.filter(pk=job.pk).update(
                    status='done',
                    output_data={'result': full_output},
                    completed_at=timezone.now(),
                )
            )
            await update_job()
            yield f"data: {json.dumps({'done': True, 'job_id': str(job.pk)})}\n\n"

        except Exception as exc:
            logger.exception('AI job %s failed', job.pk)
            fail_job = sync_to_async(
                lambda: AIJob.objects.filter(pk=job.pk).update(
                    status='failed',
                    output_data={'error': str(exc)},
                    completed_at=timezone.now(),
                )
            )
            await fail_job()
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    response = StreamingHttpResponse(
        event_generator(),
        content_type='text/event-stream',
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


# ---------------------------------------------------------------------------
# Public async views (registered in urls.py)
# ---------------------------------------------------------------------------

@csrf_exempt
async def stream_subject_lines(request):
    """POST /ai/subject-lines/stream — stream subject line suggestions."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    return await _sse_stream(request, 'subject_lines')


@csrf_exempt
async def stream_copy_optimizer(request):
    """POST /ai/copy-optimizer/stream — stream optimised copy."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    return await _sse_stream(request, 'copy_optimize')


@csrf_exempt
async def stream_spam_checker(request):
    """POST /ai/spam-checker/stream — stream spam analysis."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    return await _sse_stream(request, 'spam_check')


@csrf_exempt
async def stream_cta_optimizer(request):
    """POST /ai/cta-optimizer/stream — stream CTA suggestions."""
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    return await _sse_stream(request, 'cta_suggest')
