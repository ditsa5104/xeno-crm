import asyncio
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from settings import settings
from simulator.lifecycle import simulate_message_lifecycle

router = APIRouter()


class SendRequest(BaseModel):
    message_id: str
    recipient: str
    channel: str
    message_body: str
    callback_url: str
    batch_size: int = 1


@router.post('/send')
async def send_message(payload: SendRequest):
    stub_id = str(uuid.uuid4())
    asyncio.create_task(
        simulate_message_lifecycle(
            stub_message_id=stub_id,
            message_id=payload.message_id,
            channel=payload.channel,
            callback_url=payload.callback_url,
            secret=settings.CHANNEL_STUB_SECRET,
            batch_size=payload.batch_size,
            message_body=payload.message_body,
        )
    )
    return {'stub_message_id': stub_id, 'status': 'accepted'}
