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

            msg = resp.choices[0].message

            # Detect tool calls by presence rather than finish_reason: some models
            # (e.g. DeepSeek) attach tool_calls while reporting finish_reason='stop',
            # which would otherwise be misread as a final answer.
            if msg.tool_calls:
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
                    if name in ('create_segment_draft', 'create_campaign_draft', 'launch_campaign'):
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

        # Tool budget exhausted: make one final call WITHOUT tools so the model is
        # forced to synthesise a text answer from the data it has already gathered,
        # instead of dead-ending with a placeholder message.
        try:
            final = client.chat.completions.create(
                model=model,
                max_tokens=1024,
                messages=(
                    [{'role': 'system', 'content': system}]
                    + current
                    + [{
                        'role': 'user',
                        'content': (
                            'Summarise your findings and answer my original request now '
                            'using the information already gathered. Do not call any more tools.'
                        ),
                    }]
                ),
            )
            text = final.choices[0].message.content or ''
        except (APIError, RateLimitError) as e:
            logger.exception("Copilot final summarisation call failed")
            text = ''

        return {
            'response_text': text or "I gathered some data but couldn't finish composing a response. Please try rephrasing your request.",
            'tool_calls_made': calls_made,
            'created_objects': created,
        }
