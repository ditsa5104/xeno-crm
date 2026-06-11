import asyncio
import random
from datetime import datetime, timezone
from .failure_model import sample_failure
from .callback_client import fire_callback
from .metrics_store import metrics_store


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


OPEN_RATES = {'email': 0.25, 'whatsapp': 0.50, 'rcs': 0.45, 'sms': 0.15}
DELIVERY_RATES = {'email': 0.95}  # default 0.85 elsewhere


async def _send_event(callback_url, message_id, event_type, channel, secret, metadata=None):
    payload = {
        'message_id': message_id,
        'event_type': event_type,
        'channel': channel,
        'occurred_at': _now_iso(),
        'metadata': metadata or {},
    }
    metrics_store.record_event(event_type, channel)
    await fire_callback(callback_url, payload, secret)


async def simulate_message_lifecycle(
    stub_message_id: str,
    message_id: str,
    channel: str,
    callback_url: str,
    secret: str,
    batch_size: int = 1,
    message_body: str = '',
):
    delay_bonus = random.uniform(0.5, 3.0) if batch_size > 500 else 0.0

    # Sent
    await asyncio.sleep(random.uniform(0.1, 2.0) + delay_bonus)
    await _send_event(callback_url, message_id, 'sent', channel, secret, {'stub_message_id': stub_message_id})

    # Failed?
    failed, reason = sample_failure(channel, batch_size)
    if failed:
        metrics_store.record_failure(reason)
        await _send_event(callback_url, message_id, 'failed', channel, secret, {'reason': reason})
        return

    # Delivered
    await asyncio.sleep(random.uniform(1.0, 10.0) + delay_bonus)
    await _send_event(callback_url, message_id, 'delivered', channel, secret)

    # Opened
    open_rate = OPEN_RATES.get(channel, 0.40)
    if random.random() >= open_rate:
        return
    await asyncio.sleep(random.uniform(10.0, 120.0))
    await _send_event(callback_url, message_id, 'opened', channel, secret)

    # Read (whatsapp/rcs only)
    if channel in ('whatsapp', 'rcs') and random.random() < 0.60:
        await asyncio.sleep(random.uniform(5.0, 30.0))
        await _send_event(callback_url, message_id, 'read', channel, secret)

    # Clicked
    if 'http' in (message_body or '') and random.random() < 0.20:
        await asyncio.sleep(random.uniform(5.0, 60.0))
        await _send_event(callback_url, message_id, 'clicked', channel, secret)
    elif 'http' not in (message_body or '') and random.random() < 0.10:
        await asyncio.sleep(random.uniform(5.0, 60.0))
        await _send_event(callback_url, message_id, 'clicked', channel, secret)
