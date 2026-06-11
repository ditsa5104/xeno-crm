import json
import logging
from openai import APIError, RateLimitError
from apps.core.ai_client import get_ai_client, get_model
from .prompts import COPILOT_CHAT_SYSTEM_PROMPT, COPILOT_AGENT_SYSTEM_PROMPT
from .tools import COPILOT_TOOLS, TOOL_IMPL

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 8


class CopilotAgent:
    def run(self, messages: list[dict], context: dict | None = None, mode: str = 'chat') -> dict:
        context = context or {}
        system = COPILOT_AGENT_SYSTEM_PROMPT if mode == 'agent' else COPILOT_CHAT_SYSTEM_PROMPT
        client = get_ai_client()
        model = get_model()

        current = list(messages)
        calls_made: list[str] = []
        created: dict = {}

        for _ in range(MAX_TOOL_ROUNDS):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    max_tokens=1024,
                    messages=[{'role': 'system', 'content': system}] + current,
                    tools=COPILOT_TOOLS,
                    tool_choice='auto',
                )
            except (APIError, RateLimitError) as e:
                logger.exception("Copilot AI call failed")
                return {
                    'response_text': f"AI service error: {e}. Please try again.",
                    'tool_calls_made': calls_made,
                    'created_objects': created,
                }

            choice = resp.choices[0]
            msg = choice.message

            if choice.finish_reason == 'tool_calls' and msg.tool_calls:
                current.append({
                    'role': 'assistant',
                    'content': msg.content or '',
                    'tool_calls': [
                        {
                            'id': tc.id,
                            'type': 'function',
                            'function': {'name': tc.function.name, 'arguments': tc.function.arguments},
                        }
                        for tc in msg.tool_calls
                    ],
                })
                for tc in msg.tool_calls:
                    name = tc.function.name
                    calls_made.append(name)
                    try:
                        args = json.loads(tc.function.arguments or '{}')
                    except json.JSONDecodeError:
                        args = {}
                    fn = TOOL_IMPL.get(name)
                    if not fn:
                        result = {'error': f'unknown tool {name}'}
                    else:
                        try:
                            result = fn(**args)
                        except Exception as e:
                            logger.exception("Tool %s failed", name)
                            result = {'error': str(e)}
                    if name in ('create_segment_draft', 'create_campaign_draft'):
                        created[name] = result
                    current.append({
                        'role': 'tool',
                        'tool_call_id': tc.id,
                        'content': json.dumps(result, default=str),
                    })
                continue

            return {
                'response_text': msg.content or '',
                'tool_calls_made': calls_made,
                'created_objects': created,
            }

        return {
            'response_text': "Stopped after maximum tool rounds.",
            'tool_calls_made': calls_made,
            'created_objects': created,
        }
