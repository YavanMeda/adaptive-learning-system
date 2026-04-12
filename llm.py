import json
import time
from pathlib import Path

from anthropic import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    Anthropic,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    PermissionDeniedError,
    RateLimitError,
)

import config


def _get_client():
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set.")
    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _load_prompt_template(path):
    return Path(path).read_text(encoding="utf-8")


def _strip_code_fences(text):
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _extract_text_block(response):
    for block in response.content:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError("Anthropic response contained no text block.")


def _is_transient_error(exc):
    return isinstance(
        exc,
        (RateLimitError, InternalServerError, APIConnectionError, APITimeoutError, APIError),
    ) and not isinstance(exc, (AuthenticationError, BadRequestError, PermissionDeniedError))


def call_llm(system_prompt, user_prompt):
    """
    Send a message to the LLM and return the parsed JSON response.
    """
    client = _get_client()
    prompt_suffix = ""
    delay = config.LLM_RETRY_DELAY_SECONDS
    last_error = None

    for attempt in range(config.LLM_MAX_RETRIES):
        try:
            response = client.messages.create(
                model=config.LLM_MODEL,
                system=system_prompt,
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": f"{user_prompt}{prompt_suffix}",
                    }
                ],
            )
            usage = getattr(response, "usage", None)
            tokens_in = getattr(usage, "input_tokens", "?")
            tokens_out = getattr(usage, "output_tokens", "?")
            print(
                f"[LLM] model={config.LLM_MODEL} tokens_in={tokens_in} "
                f"tokens_out={tokens_out}"
            )

            text = _strip_code_fences(_extract_text_block(response))
            return json.loads(text)
        except json.JSONDecodeError as exc:
            last_error = exc
            if attempt == config.LLM_MAX_RETRIES - 1:
                raise ValueError("LLM response could not be parsed as JSON.") from exc
            prompt_suffix = (
                "\n\nYour previous response was not valid JSON. "
                "Respond ONLY with a JSON object, no other text."
            )
        except (AuthenticationError, BadRequestError, PermissionDeniedError):
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if not _is_transient_error(exc) or attempt == config.LLM_MAX_RETRIES - 1:
                raise RuntimeError("LLM call failed after retries.") from exc
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f"LLM call failed after retries: {last_error}") from last_error


def call_llm_confirm_identity(
    candidate_label,
    candidate_description,
    existing_label,
    existing_description,
):
    """
    Ask the LLM whether two concept descriptions refer to the same concept.
    """
    template = _load_prompt_template("prompts/dedup_confirm.txt")
    user_prompt = template.format(
        label_a=candidate_label,
        description_a=candidate_description,
        label_b=existing_label,
        description_b=existing_description,
    )
    response = call_llm(
        system_prompt="You are a concept identity resolution system. You respond only with valid JSON.",
        user_prompt=user_prompt,
    )
    return bool(response.get("same_concept", False))

