import random


FAILURE_REASONS = {
    'invalid_number': 0.04,
    'network_timeout': 0.05,
    'inbox_full': 0.03,
    'rate_limited': 0.03,
}


def sample_failure(channel: str, batch_size: int = 1) -> tuple[bool, str | None]:
    multiplier = 1.33 if batch_size > 500 else 1.0
    for reason, prob in FAILURE_REASONS.items():
        if reason == 'inbox_full' and channel == 'sms':
            continue
        if reason == 'invalid_number' and channel == 'email':
            continue
        if random.random() < prob * multiplier:
            return True, reason
    return False, None
