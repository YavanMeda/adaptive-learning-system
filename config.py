import os

from dotenv import load_dotenv


load_dotenv()


# --- API Keys ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Model Configuration ---
LLM_MODEL = "claude-sonnet-4-20250514"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# --- Chunking ---
MAX_CHUNK_TOKENS = 1500
MIN_CHUNK_TOKENS = 200
CORPUS_ID = "corpus_01"

# --- DFS Expansion ---
MAX_DEPTH = 8
K_CHUNKS = 10
PREREQUISITE_CAP = 8

# --- Deduplication Thresholds ---
HIGH_THRESHOLD = 0.92
BORDERLINE_THRESHOLD = 0.82

# --- LLM Call Settings ---
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY_SECONDS = 2
LLM_MAX_OUTPUT_TOKENS = 4096
LLM_TEMPERATURE = 0.0

