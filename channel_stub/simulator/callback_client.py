import asyncio
import hashlib
import hmac
import json
import logging
import httpx

logger = logging.getLogger(__name__)


async def fire_callback(url: str, payload: dict, secret: str, attempt: int = 0, max_attempts: int = 3) -> bool:
    body = json.dumps(payload, default=str)
    sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                url,
                content=body,
                headers={
                    'Content-Type': 'application/json',
                    'X-Xeno-Signature': sig,
                },
            )
            if resp.status_code < 300:
                return True
            logger.warning("Callback %s returned %s", url, resp.status_code)
    except httpx.RequestError as e:
        logger.warning("Callback request failed: %s", e)

    if attempt < max_attempts - 1:
        await asyncio.sleep(2 ** attempt)
        return await fire_callback(url, payload, secret, attempt + 1, max_attempts)
    return False
