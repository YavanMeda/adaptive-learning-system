import time

from openai import APIConnectionError, APIError, APITimeoutError, OpenAI, RateLimitError
import tiktoken

import config


EMBEDDING_ENCODING = tiktoken.get_encoding("cl100k_base")


def _get_client():
    if not config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=config.OPENAI_API_KEY)


def _truncate_for_embedding(text):
    tokens = EMBEDDING_ENCODING.encode(text)
    if len(tokens) <= 8191:
        return text, len(tokens)
    truncated_tokens = tokens[:8000]
    return EMBEDDING_ENCODING.decode(truncated_tokens), len(truncated_tokens)


def embed_text(text):
    """
    Embed a single text string using OpenAI's embedding API.
    """
    client = _get_client()
    prepared_text, token_count = _truncate_for_embedding(text)
    print(f"[EMBED] chars={len(prepared_text)} tokens={token_count}")

    last_error = None
    for attempt in range(2):
        try:
            response = client.embeddings.create(
                model=config.EMBEDDING_MODEL,
                input=prepared_text,
            )
            return response.data[0].embedding
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
            last_error = exc
            if attempt == 1:
                break
            time.sleep(2)
    raise RuntimeError(f"Embedding request failed after retry: {last_error}") from last_error

