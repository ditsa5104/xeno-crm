import hmac
import hashlib
from django.conf import settings


def hmac_sign(body: bytes, secret: str | None = None) -> str:
    secret = secret or settings.CHANNEL_STUB_SECRET
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def hmac_verify(body: bytes, signature: str, secret: str | None = None) -> bool:
    expected = hmac_sign(body, secret)
    return hmac.compare_digest(expected, signature or '')
