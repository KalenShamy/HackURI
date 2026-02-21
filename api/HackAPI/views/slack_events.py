import hashlib
import hmac
import time

from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def verify_slack_signature(request) -> bool:
    """Verify the Slack request signature."""
    signing_secret = settings.SLACK_SIGNING_SECRET
    if not signing_secret:
        return False

    timestamp = request.META.get('HTTP_X_SLACK_REQUEST_TIMESTAMP', '')
    signature = request.META.get('HTTP_X_SLACK_SIGNATURE', '')

    if not timestamp or not signature:
        return False

    # Reject requests older than 5 minutes
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    sig_basestring = f'v0:{timestamp}:{request.body.decode()}'
    computed = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(computed, signature)


@api_view(['POST'])
@permission_classes([AllowAny])
def slack_events(request):
    """Handle Slack Events API callbacks (URL verification + events)."""
    # URL verification challenge
    if request.data.get('type') == 'url_verification':
        return Response({'challenge': request.data.get('challenge')})

    if not verify_slack_signature(request):
        return Response({'error': 'Invalid signature'}, status=403)

    event = request.data.get('event', {})
    event_type = event.get('type')

    # Handle slash commands or app_mention events here
    if event_type == 'app_mention':
        # TODO: implement slash-command style interactions
        pass

    return Response({'status': 'ok'})
