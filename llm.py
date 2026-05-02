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
from openai import (
    APIConnectionError as OpenAIAPIConnectionError,
    APIError as OpenAIAPIError,
    APITimeoutError as OpenAIAPITimeoutError,
    AuthenticationError as OpenAIAuthenticationError,
    BadRequestError as OpenAIBadRequestError,
    InternalServerError as OpenAIInternalServerError,
    OpenAI,
    PermissionDeniedError as OpenAIPermissionDeniedError,
    RateLimitError as OpenAIRateLimitError,
)

import config


def _get_anthropic_client():
    if not config.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not set.")
    return Anthropic(api_key=config.ANTHROPIC_API_KEY)


def _get_openai_client():
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _uses_openai(model_name):
    prefixes = ("gpt-", "o", "chatgpt-")
    return model_name.startswith(prefixes)


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


def _extract_openai_text(response):
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    output = getattr(response, "output", None) or []
    parts = []
    for item in output:
        for content in getattr(item, "content", []) or []:
            if getattr(content, "type", None) == "output_text":
                parts.append(content.text)

    if parts:
        return "\n".join(parts).strip()

    raise ValueError("OpenAI response contained no output text.")


def _is_anthropic_transient_error(exc):
    return isinstance(
        exc,
        (RateLimitError, InternalServerError, APIConnectionError, APITimeoutError, APIError),
    ) and not isinstance(exc, (AuthenticationError, BadRequestError, PermissionDeniedError))


def _is_openai_transient_error(exc):
    return isinstance(
        exc,
        (
            OpenAIRateLimitError,
            OpenAIInternalServerError,
            OpenAIAPIConnectionError,
            OpenAIAPITimeoutError,
            OpenAIAPIError,
        ),
    ) and not isinstance(
        exc,
        (
            OpenAIAuthenticationError,
            OpenAIBadRequestError,
            OpenAIPermissionDeniedError,
        ),
    )


def _call_anthropic_llm(system_prompt, user_prompt):
    client = _get_anthropic_client()
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
                f"[LLM] provider=anthropic model={config.LLM_MODEL} "
                f"tokens_in={tokens_in} tokens_out={tokens_out}"
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
            if not _is_anthropic_transient_error(exc) or attempt == config.LLM_MAX_RETRIES - 1:
                raise RuntimeError("LLM call failed after retries.") from exc
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f"LLM call failed after retries: {last_error}") from last_error


def _call_openai_llm(system_prompt, user_prompt):
    client = _get_openai_client()
    prompt_suffix = ""
    delay = config.LLM_RETRY_DELAY_SECONDS
    last_error = None

    for attempt in range(config.LLM_MAX_RETRIES):
        try:
            response = client.responses.create(
                model=config.LLM_MODEL,
                instructions=system_prompt,
                input=f"{user_prompt}{prompt_suffix}",
                max_output_tokens=config.LLM_MAX_OUTPUT_TOKENS,
                text={"format": {"type": "json_object"}},
            )
            usage = getattr(response, "usage", None)
            tokens_in = getattr(usage, "input_tokens", "?")
            tokens_out = getattr(usage, "output_tokens", "?")
            print(
                f"[LLM] provider=openai model={config.LLM_MODEL} "
                f"tokens_in={tokens_in} tokens_out={tokens_out}"
            )

            text = _strip_code_fences(_extract_openai_text(response))
            return json.loads(text)
        except json.JSONDecodeError as exc:
            last_error = exc
            if attempt == config.LLM_MAX_RETRIES - 1:
                raise ValueError("LLM response could not be parsed as JSON.") from exc
            prompt_suffix = (
                "\n\nYour previous response was not valid JSON. "
                "Respond ONLY with a JSON object, no other text."
            )
        except (
            OpenAIAuthenticationError,
            OpenAIBadRequestError,
            OpenAIPermissionDeniedError,
        ):
            raise
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if not _is_openai_transient_error(exc) or attempt == config.LLM_MAX_RETRIES - 1:
                raise RuntimeError("LLM call failed after retries.") from exc
            time.sleep(delay)
            delay *= 2

    raise RuntimeError(f"LLM call failed after retries: {last_error}") from last_error


def call_llm(system_prompt, user_prompt):
    """
    Send a message to the LLM and return the parsed JSON response.
    """
    if _uses_openai(config.LLM_MODEL):
        return _call_openai_llm(system_prompt, user_prompt)
    return _call_anthropic_llm(system_prompt, user_prompt)


def call_llm_confirm_identity(
    candidate_label,
    candidate_description,
    existing_label,
    existing_description,
):
    """
    Ask the LLM whether two concept descriptions refer to the same concept.
    """
    template = _load_prompt_template("prompts/dedup_confirm_v2.txt")
    # Support both legacy and v2 prompt templates by supplying optional
    # source/graph context placeholders with safe empty defaults.
    user_prompt = template.format(
        label_a=candidate_label,
        description_a=candidate_description,
        label_b=existing_label,
        description_b=existing_description,
        source_context_a="",
        graph_context_a="",
        source_context_b="",
        graph_context_b="",
    )
    response = call_llm(
        system_prompt="You are a concept identity resolution system. You respond only with valid JSON.",
        user_prompt=user_prompt,
    )

    # Legacy schema: {"same_concept": true/false}
    if "same_concept" in response:
        return bool(response.get("same_concept", False))

    # v2 schema: {"relation_type": "...", "merge": true/false, ...}
    if "merge" in response:
        return bool(response.get("merge", False))

    # Defensive fallback for partially compliant outputs.
    return str(response.get("relation_type", "")).strip().lower() == "same_concept"
