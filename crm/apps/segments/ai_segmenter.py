import json
import logging
from openai import APIError, RateLimitError
from apps.core.ai_client import get_ai_client, get_model

logger = logging.getLogger(__name__)


class SegmenterError(Exception):
    """Raised when the AI segmenter cannot produce a valid filter tree."""


AI_SEGMENTER_SYSTEM_PROMPT = """
You convert plain-English customer filter descriptions into a structured JSON filter tree.

OUTPUT RULES:
- Respond ONLY with valid JSON. No explanation, no markdown, no preamble.
- The root object must have "operator" (AND or OR) and "conditions" (array).
- Each condition is either a leaf {field, op, value} or a nested group {operator, conditions}.
- Use only these fields: total_spend, total_orders, last_order_at, rfm_recency_score,
  rfm_frequency_score, rfm_monetary_score, rfm_composite, rfm_tier, churn_risk_score,
  city, gender, channel_preference, tags, created_at
- For date fields use days_ago_lte / days_ago_gte with integer values.
- For city/gender/channel_preference with multiple values, use op="in" and value=["a","b"].
- If the input is ambiguous, make a reasonable assumption and proceed.

Example input: "high value customers from Mumbai who haven't bought in 3 months"
Example output:
{"operator":"AND","conditions":[
  {"field":"total_spend","op":"gte","value":10000},
  {"field":"city","op":"eq","value":"Mumbai"},
  {"field":"last_order_at","op":"days_ago_gte","value":90}
]}
"""


def nl_to_filter_tree(description: str) -> dict:
    client = get_ai_client()
    try:
        resp = client.chat.completions.create(
            model=get_model(),
            max_tokens=512,
            messages=[
                {'role': 'system', 'content': AI_SEGMENTER_SYSTEM_PROMPT},
                {'role': 'user', 'content': description},
            ],
        )
        text = resp.choices[0].message.content.strip()
        # Strip markdown fences if present
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            if text.endswith('```'):
                text = text.rsplit('```', 1)[0]
        return json.loads(text)
    except (APIError, RateLimitError) as e:
        logger.warning("AI segmenter failed: %s", e)
        # Surface the failure instead of silently returning an empty tree, which
        # the evaluator treats as "match everyone" — a dangerous default for a
        # campaign audience. Callers decide how to present this to the user.
        raise SegmenterError("The AI segmenter is temporarily unavailable. Please try again.") from e
    except json.JSONDecodeError as e:
        logger.warning("AI segmenter returned invalid JSON: %s", e)
        raise SegmenterError("The AI segmenter returned an unparseable response. Please rephrase and retry.") from e
