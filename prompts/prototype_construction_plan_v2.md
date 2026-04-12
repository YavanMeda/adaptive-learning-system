# Adaptive Learning System — Prototype Construction Plan v2

**Objective:** Validate the core hypothesis — that backward DFS from a target concept, grounded in source text chunks via RAG, produces a usable prerequisite DAG and a learnable sequence — before investing in the full architecture.

**Audience for this document:** An LLM or junior developer who will implement this as working Python code. Every ambiguous decision has been resolved. Where the v1 plan said "design a prompt" or "handle retries," this version provides the exact specification.

---

## What "Core Functionality" Means

The architecture's central bet is a three-step pipeline:

1. Chunk a source text and embed the chunks.
2. Starting from a user-specified target concept, recursively discover prerequisites by issuing one LLM call per concept, grounded in retrieved chunks.
3. Linearise the resulting DAG into a learning sequence.

Everything else — spaced repetition, mastery tracking, declarative/procedural ratios, cross-corpus alignment, assessment generation, instruction generation, user feedback loops, diagnostic entry points — is downstream of this pipeline and meaningless if the pipeline itself produces a poor graph. The prototype tests the pipeline.

---

## What the Prototype Excludes

The following components are deliberately omitted. Each omission is justified by the principle that no downstream feature can compensate for a broken DAG.

- **Multi-corpus support.** Test with one text. Cross-corpus deduplication is a separate risk with separate validation needs.
- **Declarative/procedural ratio.** Remove this from the combined LLM call. It is a classification task that does not affect graph structure and adds noise to the prompt.
- **Instruction generation service.** Not needed to evaluate the graph.
- **Assessment generation service.** Not needed to evaluate the graph.
- **Spaced repetition and mastery tracking.** Irrelevant without a validated graph.
- **User state layer.** No user sessions exist in the prototype.
- **Diagnostic entry point determination.** Presupposes a valid sequence.
- **User feedback mechanism.** The prototype operator *is* the evaluator; formal feedback storage is overhead.
- **Frontend.** All interaction is via CLI and inspection of stored data.
- **Docker containerisation.** Run locally.
- **Externally assumed prerequisite detection.** Useful but not load-bearing for the core test. Flag it manually during inspection.

---

## Project Structure

```
adaptive-learning-prototype/
├── config.py                  # All configuration constants
├── db.py                      # Database connection, table creation, all SQL operations
├── llm.py                     # LLM call wrapper (single function + retry logic)
├── embeddings.py              # Embedding function (single function)
├── ingest.py                  # CLI script: reads source text, chunks, embeds, stores
├── expand.py                  # CLI script: runs backward DFS from target concept
├── linearise.py               # CLI script: topological sort, prints sequence
├── evaluate.py                # CLI script: graph stats, visualisation, exports eval record
├── prompts/
│   ├── prerequisite.txt       # The prerequisite identification prompt template
│   └── dedup_confirm.txt      # The deduplication confirmation prompt template
├── requirements.txt
├── .env                       # API keys only (not checked into git)
└── README.md
```

Each CLI script is invoked independently from the command line. They share code through the module files (`config.py`, `db.py`, `llm.py`, `embeddings.py`). There is no framework, no FastAPI server, no class hierarchy. Each script runs, does its work, and exits.

---

## Technology Stack (Prototype)

| Layer | Technology | Specific Version / Package |
|---|---|---|
| Language | Python 3.11+ | — |
| Database | PostgreSQL 16 + pgvector 0.7+ | `psycopg2-binary` for Python driver |
| Embedding model | OpenAI `text-embedding-3-small` | `openai` Python package, 1536-dimensional vectors |
| LLM | Anthropic Claude Sonnet — pinned to `claude-sonnet-4-20250514` | `anthropic` Python package |
| Graph visualisation | Graphviz | `graphviz` Python package (requires system install of Graphviz) |
| Token counting | `tiktoken` | For chunk size enforcement |
| Environment variables | `python-dotenv` | Loads `.env` file |

### requirements.txt

> **Note on model pinning:** The LLM model string is hardcoded to `claude-sonnet-4-20250514` in `config.py` rather than resolved dynamically. This is intentional: the prototype's success criteria require results to be reproducible across at least two runs. Using a floating "latest" alias risks invoking different model weights across runs separated by days or weeks, making evaluation results non-comparable. Update the pinned string deliberately when upgrading, and re-run all evaluation criteria against the new string before treating prior results as a baseline.

```
psycopg2-binary>=2.9
openai>=1.0
anthropic>=0.30
tiktoken>=0.7
graphviz>=0.20
python-dotenv>=1.0
pgvector>=0.3
```

### .env

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://user:password@localhost:5432/adaptive_learning
```

---

## config.py — Complete Specification

```python
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
MAX_CHUNK_TOKENS = 1500          # Target maximum tokens per chunk
MIN_CHUNK_TOKENS = 200           # Chunks below this are merged with their successor
CORPUS_ID = "corpus_01"         # Hardcoded for single-corpus prototype

# --- DFS Expansion ---
MAX_DEPTH = 8                    # Maximum prerequisite chain depth
K_CHUNKS = 10                   # Number of candidate chunks retrieved per expansion call
PREREQUISITE_CAP = 8            # Maximum prerequisites the LLM may return per node

# --- Deduplication Thresholds ---
HIGH_THRESHOLD = 0.92           # Above this: auto-deduplicate, no LLM confirmation
BORDERLINE_THRESHOLD = 0.82     # Between BORDERLINE and HIGH: trigger LLM confirmation
                                 # Below BORDERLINE: create new node

# --- LLM Call Settings ---
LLM_MAX_RETRIES = 3             # Retry on transient API errors
LLM_RETRY_DELAY_SECONDS = 2    # Wait between retries (doubles each retry)
LLM_MAX_OUTPUT_TOKENS = 4096   # Maximum tokens in LLM response
LLM_TEMPERATURE = 0.0          # Deterministic output for reproducibility
```

---

## db.py — Database Operations (Complete Specification)

### Table Creation

Run this once at setup. The script should check whether tables exist before creating them (use `CREATE TABLE IF NOT EXISTS`).

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id              SERIAL PRIMARY KEY,
    corpus_id       TEXT NOT NULL,
    chapter_idx     INTEGER NOT NULL,
    section_idx     INTEGER NOT NULL,
    subsection_idx  INTEGER,
    heading         TEXT NOT NULL,
    body            TEXT NOT NULL,
    token_count     INTEGER NOT NULL,
    embedding       VECTOR(1536)
);

CREATE TABLE IF NOT EXISTS nodes (
    id              SERIAL PRIMARY KEY,
    label           TEXT NOT NULL,
    description     TEXT NOT NULL,
    embedding       VECTOR(1536),
    depth           INTEGER NOT NULL,
    is_target       BOOLEAN DEFAULT FALSE,
    is_depth_limited BOOLEAN DEFAULT FALSE,
    llm_response    JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS edges (
    id              SERIAL PRIMARY KEY,
    source_id       INTEGER NOT NULL REFERENCES nodes(id),
    target_id       INTEGER NOT NULL REFERENCES nodes(id),
    is_back_edge    BOOLEAN DEFAULT FALSE,
    UNIQUE(source_id, target_id)
);

CREATE TABLE IF NOT EXISTS node_chunks (
    id              SERIAL PRIMARY KEY,
    node_id         INTEGER NOT NULL REFERENCES nodes(id),
    chunk_id        INTEGER NOT NULL REFERENCES chunks(id),
    role            TEXT NOT NULL CHECK (role IN ('definitional', 'prerequisite-informing')),
    UNIQUE(node_id, chunk_id, role)
);

CREATE TABLE IF NOT EXISTS expansion_log (
    id              SERIAL PRIMARY KEY,
    node_id         INTEGER NOT NULL REFERENCES nodes(id),
    event_type      TEXT NOT NULL,
    detail          JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);
```

The `expansion_log` table records every deduplication decision for post-hoc audit. Every auto-merge, every LLM confirmation call, and every new-node creation is logged here with the similarity scores, the candidate labels, and the decision outcome.

### Required Python Functions in db.py

Each function executes SQL directly via `psycopg2`. No ORM.

```python
def get_connection():
    """Return a psycopg2 connection using DATABASE_URL. 
    Caller is responsible for closing."""

def create_tables():
    """Execute all CREATE TABLE statements above."""

def insert_chunk(corpus_id, chapter_idx, section_idx, subsection_idx, 
                 heading, body, token_count, embedding) -> int:
    """Insert a chunk row. Return the new chunk id.
    embedding is a Python list of floats."""

def insert_node(label, description, embedding, depth, is_target=False) -> int:
    """Insert a node row. Return the new node id."""

def insert_edge(source_id, target_id, is_back_edge=False) -> int:
    """Insert an edge. Use ON CONFLICT (source_id, target_id) DO NOTHING
    to silently skip duplicate edges. Return edge id or None if skipped."""

def insert_node_chunk(node_id, chunk_id, role):
    """Insert a node-chunk link. ON CONFLICT DO NOTHING."""

def insert_expansion_log(node_id, event_type, detail_dict):
    """Insert an expansion log entry. detail_dict is serialised to JSONB."""

def find_nearest_node(embedding, exclude_id=None):
    """Return (node_row, cosine_similarity) for the most similar existing node.

    When exclude_id is provided (not None), use:
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity FROM nodes
        WHERE id != %s ORDER BY embedding <=> %s::vector LIMIT 1
    When exclude_id is None, omit the WHERE clause entirely:
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity FROM nodes
        ORDER BY embedding <=> %s::vector LIMIT 1
    Do NOT use WHERE id != NULL — that condition is never true in SQL because
    NULL comparisons always evaluate to NULL, not FALSE. Branch on exclude_id
    in Python and build the appropriate query string before executing.
    If the nodes table is empty or only contains the excluded node, return (None, 0.0).
    The <=> operator computes cosine distance; similarity = 1 - distance."""

def retrieve_top_k_chunks(embedding, k):
    """Return the k most similar chunks by cosine similarity.
    Use: SELECT *, 1 - (embedding <=> %s::vector) AS similarity FROM chunks
         ORDER BY embedding <=> %s::vector LIMIT %s
    Return list of chunk row dicts with similarity score included."""

def get_all_nodes():
    """Return all node rows as list of dicts."""

def get_all_edges():
    """Return all edge rows as list of dicts."""

def get_node_chunks(node_id):
    """Return all chunk rows linked to a node, with role."""

def get_node_by_id(node_id):
    """Return a single node row dict."""

def update_node_llm_response(node_id: int, response: dict):
    """UPDATE nodes SET llm_response = %s::jsonb WHERE id = %s.
    response is a Python dict that will be serialised to JSON before binding."""

def update_node_depth_limited(node_id: int):
    """UPDATE nodes SET is_depth_limited = TRUE WHERE id = %s."""

def is_ancestor(candidate_ancestor_id: int, node_id: int) -> bool:
    """Determine whether candidate_ancestor_id is an ancestor of node_id
    in the current DAG (following non-back-edges upward from node_id).

    Implementation: BFS upward from node_id using:
        SELECT source_id FROM edges WHERE target_id = %s AND is_back_edge = FALSE
    Walk upward iteratively with a visited set to prevent loops.
    Return True if candidate_ancestor_id is encountered; False otherwise.
    Maximum walk depth: config.MAX_DEPTH (to bound computation at prototype scale)."""
```

**Critical implementation note on pgvector:** The `embedding` column stores vectors. When inserting, convert the Python list of floats to a string format pgvector accepts: `'[0.1, 0.2, ...]'`. Use `psycopg2`'s `register_vector` from `pgvector.psycopg2` or format manually. Install `pgvector` Python helper: add `pgvector>=0.3` to requirements.txt and use:

```python
from pgvector.psycopg2 import register_vector
conn = get_connection()
register_vector(conn)
# Now you can pass numpy arrays or lists directly as embedding parameters.
```

---

## llm.py — LLM Call Wrapper (Complete Specification)

### Primary Function

```python
import time
import json
from anthropic import Anthropic

def call_llm(system_prompt: str, user_prompt: str) -> dict:
    """
    Send a message to the LLM and return the parsed JSON response.
    
    Args:
        system_prompt: The system-level instruction.
        user_prompt: The user-level message containing the concept and chunks.
    
    Returns:
        Parsed JSON dict from the LLM response.
    
    Raises:
        ValueError: If the response cannot be parsed as JSON after retries.
        RuntimeError: If all retries are exhausted due to API errors.
    
    Behaviour:
        - Uses config.LLM_MODEL, config.LLM_TEMPERATURE, config.LLM_MAX_OUTPUT_TOKENS.
        - Retries up to config.LLM_MAX_RETRIES times on transient errors (rate limit, 
          server error, connection error). Non-transient errors (auth, invalid request)
          are raised immediately.
        - Delay between retries doubles each time, starting at config.LLM_RETRY_DELAY_SECONDS.
        - The response text is extracted from the first content block of type "text".
        - The response text is stripped of markdown code fences (```json ... ```) if present.
        - The stripped text is parsed as JSON. If parsing fails, the call is retried
          with an appended user message: "Your previous response was not valid JSON.
          Respond ONLY with a JSON object, no other text."
        - All calls (including retries) are printed to stdout with a prefix: 
          [LLM] model=... tokens_in=... tokens_out=... 
    """
```

### Deduplication Confirmation Function

```python
def call_llm_confirm_identity(candidate_label, candidate_description,
                               existing_label, existing_description) -> bool:
    """
    Ask the LLM whether two concept descriptions refer to the same concept.
    
    Returns True if same, False if different.
    
    Uses the dedup_confirm.txt prompt template.
    Parses a JSON response with a single key: {"same_concept": true/false}
    """
```

---

## embeddings.py — Embedding Function (Complete Specification)

```python
from openai import OpenAI

def embed_text(text: str) -> list[float]:
    """
    Embed a single text string using OpenAI's embedding API.
    
    Args:
        text: The string to embed. If it exceeds 8191 tokens (the model's limit),
              truncate to the first 8000 tokens before embedding.
    
    Returns:
        A list of floats with length config.EMBEDDING_DIMENSIONS (1536).
    
    Behaviour:
        - Uses config.OPENAI_API_KEY and config.EMBEDDING_MODEL.
        - Single retry on transient error with 2-second delay.
        - Prints to stdout: [EMBED] chars=... tokens=...
    """
```

**What to embed for a node:** Concatenate label and description with a separator: `f"{label}: {description}"`. This concatenation is performed by the caller, not inside `embed_text`.

---

## Phase 1 — Ingestion Pipeline (ingest.py)

### Input

The script accepts a single argument: the path to a source text file. The file must be UTF-8 encoded plain text (`.txt`) or Markdown (`.md`).

```bash
python ingest.py /path/to/source_text.md
```

An optional `--reset` flag truncates the ingestion data before ingesting, ensuring a clean run:

```bash
python ingest.py --reset /path/to/source_text.md
```

When `--reset` is passed, the script must execute the following before any other operation:

```sql
TRUNCATE expansion_log, node_chunks, edges, nodes, chunks RESTART IDENTITY CASCADE;
```

This full reset is intentional. Because `node_chunks.chunk_id` references `chunks.id`, truncating `chunks` alone would cascade into `node_chunks` and leave any existing `nodes`, `edges`, and `expansion_log` rows semantically inconsistent with the newly ingested corpus. The prototype therefore treats ingestion reset as a complete corpus-and-graph reset.

**Startup guard (no `--reset` flag):** If `--reset` is not passed and the `chunks` table already contains rows with the same `corpus_id` as `config.CORPUS_ID`, the script must abort immediately with the following message and exit code 1:

```
[ERROR] The chunks table already contains N rows for corpus '{CORPUS_ID}'.
        Pass --reset to clear prior ingestion data before re-ingesting.
```

Silent appending to a prior ingestion run is prohibited for the same reason it is prohibited in `expand.py`: mixed chunk sets from multiple ingestion runs will corrupt retrieval quality and make evaluation results non-reproducible. Every ingestion run must start from a clean corpus state, and in this prototype corpus state and graph state are reset together.

### Heading Detection

The chunker must identify structural headings to split on. Use the following regex-based heuristics in priority order:

1. **Markdown headings.** Lines matching `^#{1,4}\s+(.+)$`. The number of `#` characters determines the level: `#` = chapter, `##` = section, `###` = subsection, `####` = sub-subsection (treated as subsection).
2. **Numbered headings.** Lines matching `^\d+\.\s+(.+)$` (chapter), `^\d+\.\d+\s+(.+)$` (section), `^\d+\.\d+\.\d+\s+(.+)$` (subsection). These are common in textbooks without Markdown formatting.
3. **Uppercase headings.** Lines that are entirely uppercase, contain at least 3 words, and are preceded and followed by a blank line. Treat as section-level headings. This is a fallback heuristic.

If no headings are detected in the entire file, fall back to splitting on double newlines (paragraph-level chunks) and assign `chapter_idx=0`, `section_idx` = sequential counter, `subsection_idx=None` for all chunks.

### Chunking Algorithm (Step by Step)

```
1. Read the entire file into a string.
2. Split the string into lines.
3. Walk the lines sequentially, maintaining state:
   - current_chapter_idx (integer, starts at 0)
   - current_section_idx (integer, starts at 0, resets to 0 on new chapter)
   - current_subsection_idx (integer or None, starts at None, resets on new section)
   - current_heading (string)
   - current_body_lines (list of strings)

4. At each line:
   a. Test if the line matches a heading pattern.
   b. If it matches a chapter-level heading:
      - Finalise the current chunk (see step 5).
      - Increment current_chapter_idx.
      - Reset current_section_idx to 0, current_subsection_idx to None.
      - Set current_heading to the matched heading text.
      - Clear current_body_lines.
   c. If it matches a section-level heading:
      - Finalise the current chunk.
      - Increment current_section_idx.
      - Reset current_subsection_idx to None.
      - Set current_heading to the matched heading text.
      - Clear current_body_lines.
   d. If it matches a subsection-level heading:
      - Finalise the current chunk.
      - Increment current_subsection_idx (set to 0 if None, else increment).
      - Set current_heading to the matched heading text.
      - Clear current_body_lines.
   e. If it does not match any heading pattern:
      - Append the line to current_body_lines.

5. Finalise the current chunk:
   a. Join current_body_lines with newlines. Strip leading and trailing whitespace.
   b. If the result is empty, skip — do not create a chunk.
   c. Count tokens using tiktoken (use the "cl100k_base" encoding).
   d. If token_count > MAX_CHUNK_TOKENS:
      - Split the body at paragraph boundaries (double newline "\n\n").
      - Group consecutive paragraphs into sub-chunks, each <= MAX_CHUNK_TOKENS.
      - The first sub-chunk inherits the current heading.
      - Subsequent sub-chunks get the heading suffixed with " (continued)".
      - Each sub-chunk becomes a separate chunk with the same positional metadata.
      - If a single paragraph by itself exceeds MAX_CHUNK_TOKENS, split that
        paragraph further at sentence boundaries. If a single sentence still
        exceeds MAX_CHUNK_TOKENS, split it by token count into contiguous
        slices of at most MAX_CHUNK_TOKENS. The goal is that no emitted
        sub-chunk ever exceeds MAX_CHUNK_TOKENS, even for pathological input.
   e. If token_count < MIN_CHUNK_TOKENS:
      - Do not emit this chunk. Append its body to a `pending_body` accumulator
        (a string, initially empty, maintained across the entire line-by-line pass).
      - When the next chunk is finalised, prepend `pending_body` to that chunk's
        body (with a newline separator if both are non-empty), then clear
        `pending_body`. Apply the MIN_CHUNK_TOKENS check to the merged body.
        If the merged body is still below MIN_CHUNK_TOKENS, continue accumulating.
      - The merged chunk inherits the successor chunk's heading and positional
        metadata (chapter_idx, section_idx, subsection_idx). The sub-minimum
        predecessor's heading is discarded.
      - If the end of the file is reached and `pending_body` is non-empty, emit
        it as a standalone chunk using the last-seen heading and positional
        metadata, regardless of size.
      - This rule applies only during the top-level line-by-line parsing pass.
        Sub-chunks produced by the oversized-chunk splitting logic in step 5d are
        emitted as-is and are not subject to the MIN_CHUNK_TOKENS check; merging
        them across paragraph boundaries would defeat the purpose of the split.
   f. Otherwise, emit the chunk: store to database via insert_chunk().

6. After all lines are processed, finalise the last accumulated chunk.
```

### After Ingestion: Validation Output

After ingestion completes, print a summary:

```
[INGEST] Complete.
  Chunks created: 147
  Token count range: 203 — 1487
  Chapters detected: 12
  Sections detected: 47
  Subsections detected: 88
```

Then print 5 randomly sampled chunks (heading + first 100 characters of body + token count) for quick manual inspection.

---

## Phase 2 — Backward DFS Expansion (expand.py)

### Input

The script accepts two arguments: a target concept label and a target concept description.

```bash
python expand.py "Gradient Descent" "An iterative optimisation algorithm that adjusts parameters in the direction of steepest decrease of a loss function"
```

An optional `--reset` flag truncates all graph tables before beginning, ensuring a clean run:

```bash
python expand.py --reset "Gradient Descent" "An iterative optimisation algorithm ..."
```

When `--reset` is passed, the script must truncate the following tables in this order (respecting foreign key constraints) before any other operation:

```sql
TRUNCATE expansion_log, node_chunks, edges, nodes RESTART IDENTITY CASCADE;
```

**Startup guard (no `--reset` flag):** If `--reset` is not passed and the `nodes` table already contains rows, the script must abort immediately with the following message and exit code 1:

```
[ERROR] The nodes table is not empty (N rows found). Pass --reset to clear prior graph
        data before running a new expansion, or inspect the existing graph with
        linearise.py and evaluate.py.
```

Silent appending to a prior run is prohibited. Every expansion run must either start from a clean state (`--reset`) or be an explicit continuation — and continuation is not currently supported; the only valid non-reset invocation is on an empty database.

### Startup Sequence

1. Embed the target concept: `embed_text(f"{label}: {description}")`.
2. Insert the target node with `depth=0`, `is_target=True`.
3. Initialise `frontier = [target_node_id]` (a Python list used as a stack — `pop()` from the end for depth-first behaviour).
4. Initialise `visited = set()`.

### Prerequisite Identification Prompt Template (prompts/prerequisite.txt)

This is the exact prompt template. Placeholders are denoted by `{variable_name}`.

```
You are a prerequisite analysis system. You will be given a concept and a set of source text chunks. Your task is to identify the immediate prerequisites for understanding the given concept, based ONLY on what the provided source text chunks say or assume.

CRITICAL RULES:
- Identify ONLY prerequisites: concepts that MUST be understood BEFORE the given concept can be understood. A prerequisite is something the source text assumes the reader already knows when explaining this concept.
- Do NOT include related concepts, co-requisites, applications, or concepts that come AFTER this one.
- Do NOT use your general knowledge. If the source chunks do not mention or assume a concept, do not list it as a prerequisite.
- Each prerequisite should be at the granularity of a single teachable concept — something that could be explained in one focused lesson of 10-20 minutes. 
  - TOO COARSE: "Mathematics" or "Linear Algebra" (these are entire fields, not single concepts).
  - TOO FINE: "The notation x_i for indexed variables" (this is a notational convention, not a concept).
  - CORRECT GRANULARITY: "Matrix Multiplication", "Partial Derivatives", "Learning Rate".
- Return at most {prerequisite_cap} prerequisites. If you believe there are more, return only the {prerequisite_cap} most essential ones.
- For each prerequisite, cite which of the provided chunk IDs informed your decision.
- Separately, identify which chunk IDs are DEFINITIONAL for the given concept — chunks that define, explain, or teach the concept itself (not chunks that merely mention it in passing or apply it).

CONCEPT:
Label: {concept_label}
Description: {concept_description}

SOURCE CHUNKS:
{chunks_formatted}

Respond with ONLY a JSON object in this exact format, no other text:
{{
  "prerequisites": [
    {{
      "label": "Short concept name",
      "description": "One sentence explaining what this concept is, in the context of this source material",
      "informing_chunk_ids": [1, 4]
    }}
  ],
  "definitional_chunk_ids": [2, 5],
  "reasoning": "Brief explanation of why these prerequisites were selected"
}}
```

### How to Format Chunks for the Prompt

The `{chunks_formatted}` placeholder is replaced with a block of text constructed as follows:

```
For each chunk in the candidate_chunks list (returned by retrieve_top_k_chunks):

--- CHUNK {chunk.id} ---
Position: Chapter {chunk.chapter_idx}, Section {chunk.section_idx}{", Subsection " + str(chunk.subsection_idx) if chunk.subsection_idx is not None else ""}
Heading: {chunk.heading}
Content:
{chunk.body}
---

Separate each chunk block with a single blank line.
```

### How to Construct the LLM Call

```python
system_prompt = "You are a prerequisite analysis system. You respond only with valid JSON."

user_prompt = prerequisite_template.format(
    prerequisite_cap=config.PREREQUISITE_CAP,
    concept_label=current_node.label,
    concept_description=current_node.description,
    chunks_formatted=formatted_chunks_string
)

response = call_llm(system_prompt, user_prompt)
```

### How to Parse the LLM Response

```python
# response is already a parsed dict (call_llm handles JSON parsing)

prerequisites = response.get("prerequisites", [])
definitional_chunk_ids = response.get("definitional_chunk_ids", [])

# Enforce prerequisite cap
prerequisites = prerequisites[:config.PREREQUISITE_CAP]

# Validate chunk IDs — discard any chunk ID not in the candidate set
valid_chunk_ids = {c["id"] for c in candidate_chunks}
for prereq in prerequisites:
    prereq["informing_chunk_ids"] = [
        cid for cid in prereq.get("informing_chunk_ids", []) if cid in valid_chunk_ids
    ]
definitional_chunk_ids = [
    cid for cid in definitional_chunk_ids if cid in valid_chunk_ids
]
```

### Deduplication Confirmation Prompt Template (prompts/dedup_confirm.txt)

```
You are a concept identity resolution system. Determine whether the following two concept descriptions refer to the same underlying concept or to two distinct concepts.

CONCEPT A:
Label: {label_a}
Description: {description_a}

CONCEPT B:
Label: {label_b}
Description: {description_b}

Two concepts are the SAME if a learner who has mastered one would have fully mastered the other — they are different names or phrasings for the same knowledge. They are DIFFERENT if mastering one does not guarantee mastery of the other, even if they are closely related.

Respond with ONLY a JSON object, no other text:
{{"same_concept": true}} or {{"same_concept": false}}
```

### Expansion Loop (Complete, No Pseudocode)

```python
import json

def run_expansion(target_label: str, target_description: str):
    # 1. Create target node
    target_embedding = embed_text(f"{target_label}: {target_description}")
    target_id = insert_node(
        label=target_label,
        description=target_description,
        embedding=target_embedding,
        depth=0,
        is_target=True
    )
    
    frontier = [target_id]  # stack: pop from end
    visited = set()
    total_llm_calls = 0
    
    while frontier:
        current_id = frontier.pop()
        
        if current_id in visited:
            continue
        
        current = get_node_by_id(current_id)
        
        if current["depth"] >= config.MAX_DEPTH:
            # Mark as depth-limited, do not expand
            update_node_depth_limited(current_id)
            visited.add(current_id)
            insert_expansion_log(current_id, "depth_limited", {
                "depth": current["depth"]
            })
            print(f"[DFS] Depth limit reached: {current['label']} (depth {current['depth']})")
            continue
        
        visited.add(current_id)
        print(f"[DFS] Expanding: {current['label']} (depth {current['depth']}, "
              f"visited {len(visited)}, frontier {len(frontier)})")
        
        # 2. Retrieve candidate chunks
        candidate_chunks = retrieve_top_k_chunks(current["embedding"], k=config.K_CHUNKS)
        
        if not candidate_chunks:
            insert_expansion_log(current_id, "no_chunks_found", {})
            print(f"[DFS] WARNING: No chunks found for {current['label']}")
            continue
        
        # 3. Format chunks and issue LLM call
        chunks_formatted = format_chunks_for_prompt(candidate_chunks)
        
        prerequisite_template = load_prompt_template("prompts/prerequisite.txt")
        user_prompt = prerequisite_template.format(
            prerequisite_cap=config.PREREQUISITE_CAP,
            concept_label=current["label"],
            concept_description=current["description"],
            chunks_formatted=chunks_formatted
        )
        
        response = call_llm(
            system_prompt="You are a prerequisite analysis system. You respond only with valid JSON.",
            user_prompt=user_prompt
        )
        total_llm_calls += 1
        
        # Store full response on node
        # UPDATE nodes SET llm_response = %s WHERE id = %s
        update_node_llm_response(current_id, response)
        
        # 4. Parse response
        prerequisites = response.get("prerequisites", [])[:config.PREREQUISITE_CAP]
        definitional_chunk_ids = response.get("definitional_chunk_ids", [])
        
        valid_chunk_ids = {c["id"] for c in candidate_chunks}
        definitional_chunk_ids = [cid for cid in definitional_chunk_ids if cid in valid_chunk_ids]
        
        # 5. Store definitional chunk links for current node
        for chunk_id in definitional_chunk_ids:
            insert_node_chunk(current_id, chunk_id, "definitional")
        
        # 6. Process each prerequisite
        for prereq in prerequisites:
            prereq_label = prereq.get("label", "").strip()
            prereq_description = prereq.get("description", "").strip()
            
            if not prereq_label or not prereq_description:
                continue
            
            informing_chunk_ids = [
                cid for cid in prereq.get("informing_chunk_ids", []) 
                if cid in valid_chunk_ids
            ]
            
            prereq_embedding = embed_text(f"{prereq_label}: {prereq_description}")
            
            # 7. Deduplication check
            match, similarity = find_nearest_node(prereq_embedding, exclude_id=None)
            
            resolved_node_id = None
            
            if match is not None and similarity >= config.HIGH_THRESHOLD:
                # Auto-deduplicate
                resolved_node_id = match["id"]
                insert_expansion_log(current_id, "dedup_auto_merge", {
                    "candidate_label": prereq_label,
                    "matched_label": match["label"],
                    "similarity": similarity
                })
                print(f"  [DEDUP] Auto-merge: '{prereq_label}' -> '{match['label']}' "
                      f"(sim={similarity:.4f})")
            
            elif match is not None and similarity >= config.BORDERLINE_THRESHOLD:
                # LLM confirmation required
                is_same = call_llm_confirm_identity(
                    prereq_label, prereq_description,
                    match["label"], match["description"]
                )
                total_llm_calls += 1
                
                if is_same:
                    resolved_node_id = match["id"]
                    insert_expansion_log(current_id, "dedup_llm_merge", {
                        "candidate_label": prereq_label,
                        "matched_label": match["label"],
                        "similarity": similarity,
                        "llm_decision": "same"
                    })
                    print(f"  [DEDUP] LLM confirmed merge: '{prereq_label}' -> "
                          f"'{match['label']}' (sim={similarity:.4f})")
                else:
                    insert_expansion_log(current_id, "dedup_llm_split", {
                        "candidate_label": prereq_label,
                        "matched_label": match["label"],
                        "similarity": similarity,
                        "llm_decision": "different"
                    })
                    print(f"  [DEDUP] LLM rejected merge: '{prereq_label}' != "
                          f"'{match['label']}' (sim={similarity:.4f})")
            
            # If not resolved, create new node
            if resolved_node_id is None:
                new_id = insert_node(
                    label=prereq_label,
                    description=prereq_description,
                    embedding=prereq_embedding,
                    depth=current["depth"] + 1
                )
                resolved_node_id = new_id
                
                insert_expansion_log(current_id, "new_node", {
                    "label": prereq_label,
                    "nearest_similarity": similarity if match else None
                })
                print(f"  [NEW] Created node: '{prereq_label}' (depth {current['depth'] + 1})")
                
                # Add to frontier only if new (not already visited)
                if new_id not in visited:
                    frontier.append(new_id)
            
            # 8. Create prerequisite edge
            # source = prerequisite node, target = current node
            # Check for back edge: if resolved_node_id is an ancestor of current_id
            if is_ancestor(resolved_node_id, current_id):
                insert_edge(resolved_node_id, current_id, is_back_edge=True)
                insert_expansion_log(current_id, "back_edge", {
                    "from": resolved_node_id,
                    "to": current_id
                })
                print(f"  [CYCLE] Back edge detected and flagged: "
                      f"node {resolved_node_id} -> node {current_id}")
            else:
                insert_edge(resolved_node_id, current_id, is_back_edge=False)
            
            # 9. Store prerequisite-informing chunk links
            for chunk_id in informing_chunk_ids:
                insert_node_chunk(resolved_node_id, chunk_id, "prerequisite-informing")
    
    print(f"\n[DFS] Expansion complete.")
    print(f"  Nodes: {len(visited)}")
    print(f"  LLM calls: {total_llm_calls}")
```

### Ancestor Check Function (for Cycle Detection)

```python
def is_ancestor(candidate_ancestor_id: int, node_id: int) -> bool:
    """
    Determine whether candidate_ancestor_id is an ancestor of node_id
    in the current DAG (following prerequisite edges from node_id upward).
    
    Implementation: BFS/DFS upward from node_id through non-back-edges.
    
    SELECT source_id FROM edges WHERE target_id = %s AND is_back_edge = FALSE
    
    Walk upward recursively. If candidate_ancestor_id is encountered, return True.
    Use a visited set to prevent infinite loops (should not occur if back edges 
    are correctly flagged, but defensive programming).
    
    Maximum walk depth: config.MAX_DEPTH (to bound computation).
    """
```

### Helper: format_chunks_for_prompt

```python
def format_chunks_for_prompt(chunks: list[dict]) -> str:
    """
    Format a list of chunk dicts into the text block for the LLM prompt.
    
    Each chunk dict has keys: id, chapter_idx, section_idx, subsection_idx, 
    heading, body, similarity.
    
    Output format per chunk:
    
    --- CHUNK {id} ---
    Position: Chapter {chapter_idx}, Section {section_idx}[, Subsection {subsection_idx}]
    Heading: {heading}
    Content:
    {body}
    ---
    
    Chunks are separated by a single blank line.
    """
```

### Helper: load_prompt_template

```python
def load_prompt_template(path: str) -> str:
    """Read a text file and return its contents as a string."""
```

### Helper: update_node_llm_response

```python
def update_node_llm_response(node_id: int, response: dict):
    """UPDATE nodes SET llm_response = %s::jsonb WHERE id = %s"""
```

### Console Output During Expansion

The expansion loop prints to stdout in real time. A complete expansion run should look like this:

```
[DFS] Expanding: Gradient Descent (depth 0, visited 1, frontier 0)
  [NEW] Created node: 'Loss Function' (depth 1)
  [NEW] Created node: 'Partial Derivatives' (depth 1)
  [NEW] Created node: 'Learning Rate' (depth 1)
[DFS] Expanding: Learning Rate (depth 1, visited 2, frontier 2)
  [DEDUP] Auto-merge: 'Step Size' -> 'Learning Rate' (sim=0.9438)
  [NEW] Created node: 'Convergence' (depth 2)
[DFS] Expanding: Partial Derivatives (depth 1, visited 3, frontier 2)
  [NEW] Created node: 'Multivariable Functions' (depth 2)
  [DEDUP] LLM confirmed merge: 'Derivative' -> 'Partial Derivatives' (sim=0.8641)
...
[DFS] Expansion complete.
  Nodes: 43
  LLM calls: 48
```

---

## Phase 3 — Linearisation (linearise.py)

### Input

No arguments. Operates on the current database state.

```bash
python linearise.py
```

### Kahn's Algorithm (Complete)

```python
def linearise():
    nodes = get_all_nodes()
    edges = get_all_edges()
    
    # Exclude back edges from the sort
    edges = [e for e in edges if not e["is_back_edge"]]
    
    # Build adjacency and in-degree structures
    # in_degree[node_id] = number of incoming prerequisite edges (non-back)
    # dependents[node_id] = list of node_ids that depend on this node
    in_degree = {n["id"]: 0 for n in nodes}
    dependents = {n["id"]: [] for n in nodes}
    
    for e in edges:
        in_degree[e["target_id"]] += 1
        dependents[e["source_id"]].append(e["target_id"])
    
    # Tie-breaking score: earliest linked text position, ordered by chapter first
    # and then section. Lower value = earlier in the source text = higher priority.
    node_sort_key = {}
    for n in nodes:
        chunks = get_node_chunks(n["id"])
        if chunks:
            min_section = min(
                c["chapter_idx"] * 1000 + c["section_idx"] for c in chunks
            )
            node_sort_key[n["id"]] = min_section
        else:
            node_sort_key[n["id"]] = 999999  # no chunks = sort last
    
    # Initialise queue with all zero-in-degree nodes, sorted by tie-break key
    import heapq
    queue = []
    for n in nodes:
        if in_degree[n["id"]] == 0:
            heapq.heappush(queue, (node_sort_key[n["id"]], n["id"]))
    
    sequence = []
    
    while queue:
        _, node_id = heapq.heappop(queue)
        sequence.append(node_id)
        
        for dep_id in dependents[node_id]:
            in_degree[dep_id] -= 1
            if in_degree[dep_id] == 0:
                heapq.heappush(queue, (node_sort_key[dep_id], dep_id))
    
    if len(sequence) != len(nodes):
        orphaned = set(n["id"] for n in nodes) - set(sequence)
        print(f"[WARN] Topological sort incomplete. {len(orphaned)} nodes not reached.")
        print(f"  Orphaned node IDs: {orphaned}")
        # Append orphaned nodes at the end (sorted by sort key)
        for nid in sorted(orphaned, key=lambda x: node_sort_key[x]):
            sequence.append(nid)
    
    # Print the sequence
    print(f"\n{'Pos':<5} {'Label':<40} {'Depth':<6} {'Chunks':<7} "
          f"{'Prereqs':<8} {'Dependents':<10}")
    print("-" * 116)
    
    for pos, node_id in enumerate(sequence, 1):
        node = get_node_by_id(node_id)
        chunks = get_node_chunks(node_id)
        prereq_count = sum(1 for e in edges if e["target_id"] == node_id)
        dep_count = sum(1 for e in edges if e["source_id"] == node_id)
        
        print(f"{pos:<5} {node['label']:<40} {node['depth']:<6} "
              f"{len(chunks):<7} {prereq_count:<8} {dep_count:<10}")
    
    return sequence
```

---

## Phase 4 — Evaluation (evaluate.py)

### Input

No arguments. Operates on the current database state.

```bash
python evaluate.py
```

### What the Script Produces

The script outputs three things:

1. **A Graphviz DAG visualisation** saved to `output/dag.png`.
2. **A summary statistics block** printed to stdout.
3. **A JSON evaluation record** saved to `output/eval_record.json`.

### Graphviz DAG Visualisation

```python
from graphviz import Digraph

def generate_dag_visualisation():
    nodes = get_all_nodes()
    edges = get_all_edges()
    
    dot = Digraph(comment="Prerequisite DAG", format="png")
    dot.attr(rankdir="BT")  # Bottom-to-top: prerequisites at bottom, targets at top
    dot.attr("node", shape="box", style="rounded", fontsize="10", fontname="Helvetica")
    
    for n in nodes:
        label = n["label"]
        if n["is_target"]:
            dot.node(str(n["id"]), label, style="rounded,bold", color="red")
        elif n.get("is_depth_limited"):
            dot.node(str(n["id"]), label, style="rounded,dashed", color="gray")
        else:
            dot.node(str(n["id"]), label)
    
    for e in edges:
        if e["is_back_edge"]:
            dot.edge(str(e["source_id"]), str(e["target_id"]), 
                     style="dashed", color="red", label="back")
        else:
            dot.edge(str(e["source_id"]), str(e["target_id"]))
    
    dot.render("output/dag", cleanup=True)
    print("[EVAL] DAG visualisation saved to output/dag.png")
```

### Summary Statistics

```python
import os
import json
from datetime import datetime
from collections import Counter

def print_summary_statistics():
    nodes = get_all_nodes()
    edges = get_all_edges()
    non_back_edges = [e for e in edges if not e["is_back_edge"]]
    back_edges = [e for e in edges if e["is_back_edge"]]
    
    if not nodes:
        print("\n=== EVALUATION SUMMARY ===")
        print("No nodes found. Run expand.py before evaluate.py.")
        return
    
    depths = [n["depth"] for n in nodes]
    
    # Fan-out: number of prerequisites per node
    prereq_counts = {}
    for e in non_back_edges:
        prereq_counts[e["target_id"]] = prereq_counts.get(e["target_id"], 0) + 1
    
    # Nodes with no chunks linked
    nodes_without_chunks = sum(1 for n in nodes if len(get_node_chunks(n["id"])) == 0)
    
    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total nodes:              {len(nodes)}")
    print(f"Total edges:              {len(non_back_edges)}")
    print(f"Back edges (cycles):      {len(back_edges)}")
    print(f"Depth range:              {min(depths)} — {max(depths)}")
    print(f"Depth distribution:       {dict(sorted(Counter(depths).items()))}")
    print(f"Max fan-out:              {max(prereq_counts.values()) if prereq_counts else 0}")
    print(f"Avg fan-out:              {sum(prereq_counts.values()) / len(prereq_counts):.1f}" 
          if prereq_counts else "")
    print(f"Nodes without chunks:     {nodes_without_chunks}")
    print(f"Depth-limited nodes:      {sum(1 for n in nodes if n.get('is_depth_limited'))}")
```

### Evaluation Record (JSON)

```python
def export_eval_record():
    nodes = get_all_nodes()
    edges = get_all_edges()
    non_back_edges = [e for e in edges if not e["is_back_edge"]]
    depths = [n["depth"] for n in nodes]
    
    record = {
        "run_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "corpus": config.CORPUS_ID,
        "target_concept": next((n["label"] for n in nodes if n["is_target"]), "unknown"),
        "config": {
            "MAX_DEPTH": config.MAX_DEPTH,
            "K_CHUNKS": config.K_CHUNKS,
            "HIGH_THRESHOLD": config.HIGH_THRESHOLD,
            "BORDERLINE_THRESHOLD": config.BORDERLINE_THRESHOLD,
            "PREREQUISITE_CAP": config.PREREQUISITE_CAP,
            "LLM_MODEL": config.LLM_MODEL,
            "EMBEDDING_MODEL": config.EMBEDDING_MODEL,
            "MAX_CHUNK_TOKENS": config.MAX_CHUNK_TOKENS,
        },
        "node_count": len(nodes),
        "edge_count": len(non_back_edges),
        "back_edge_count": len(edges) - len(non_back_edges),
        "max_depth_reached": max(depths) if depths else None,
        "depth_distribution": dict(sorted(Counter(depths).items())) if depths else {},
        "depth_limited_nodes": sum(1 for n in nodes if n.get("is_depth_limited")),
        # These fields are populated manually after inspection:
        "precision_level_1": None,
        "recall_level_1": None,
        "precision_level_2": None,
        "recall_level_2": None,
        "spurious_node_count": None,
        "false_merge_count": None,
        "false_split_count": None,
        "chunk_link_accuracy": None,
        "sequence_coherence": None,
        "notes": ""
    }
    
    os.makedirs("output", exist_ok=True)
    with open("output/eval_record.json", "w") as f:
        json.dump(record, f, indent=2)
    
    print(f"[EVAL] Evaluation record saved to output/eval_record.json")
    print(f"       Fill in manual evaluation fields after inspection.")
```

### Expansion Log Dump

Additionally, the evaluation script should dump the full expansion log for deduplication review:

```python
def dump_expansion_log():
    """Query all rows from expansion_log ordered by created_at.
    Print as a formatted table and save to output/expansion_log.json."""
```

---

## Phase 5 — Iteration Targets

Based on evaluation results, the following are the expected areas requiring iteration. Address them in priority order.

### Priority 1 — Prompt Engineering

If precision or recall at depth 1 is below 0.7, the prerequisite identification prompt is the first thing to revise. Common failure modes:

- The LLM returns prerequisites from its general knowledge rather than from the provided chunks. Strengthen the grounding instruction. Consider adding a "cite which chunk informed this prerequisite" requirement and discarding prerequisites with no citation.
- The LLM returns prerequisites at inconsistent granularity. Add more examples to the granularity specification. Consider a two-pass approach: first identify prerequisites, then filter for granularity in a second call (this sacrifices the O(V) cost model but may be necessary).
- The LLM returns co-requisites or related concepts rather than strict prerequisites. Sharpen the definition of prerequisite in the prompt. A prerequisite is a concept that *must* be understood *before* the current concept can be understood; a related concept is not a prerequisite.

### Priority 2 — Chunking Strategy

If chunk linking quality is poor (fewer than 7 of 10 inspected nodes have adequate definitional chunks), revise the chunking strategy before re-running. Consider:

- Reducing chunk size to increase specificity.
- Adding chunk overlap at section boundaries.
- Embedding chunk headings separately from chunk bodies and retrieving on both.

### Priority 3 — Deduplication Thresholds

If false merge or false split rates are above 15%, adjust thresholds. If adjustment does not resolve the problem, consider replacing cosine similarity with a more discriminative identity check — for instance, always using an LLM confirmation call rather than relying on embedding similarity alone. This increases cost by one LLM call per candidate prerequisite per expansion step, but if deduplication is unreliable, the cost is justified.

### Priority 4 — Depth Limit

If the depth distribution shows the majority of nodes at MAX_DEPTH, increase the limit and re-run. If the graph still does not terminate naturally, the granularity may be too fine, causing each concept to generate further prerequisites indefinitely. This is a granularity problem, not a depth problem.

---

## Implementation Sequence

Build in this order. Do not skip ahead. Each step should be testable before proceeding to the next.

1. **config.py** — Copy the configuration block from this document. Verify it loads.
2. **db.py** — Implement all functions. Test by calling `create_tables()`, then `insert_chunk()` with a dummy row, then `retrieve_top_k_chunks()` on it. Verify pgvector cosine distance works.
3. **embeddings.py** — Implement `embed_text()`. Test by embedding two similar phrases and two unrelated phrases; verify cosine similarity (dot product of normalised vectors) is higher for the similar pair.
4. **llm.py** — Implement `call_llm()` and `call_llm_confirm_identity()`. Test `call_llm()` by sending a trivial JSON-response prompt and verifying the return is a parsed dict.
5. **prompts/** — Create both prompt template files with the exact text from this document.
6. **ingest.py** — Implement the chunker. Run on the chosen corpus. Inspect output with the validation gate.
7. **expand.py** — Implement the full expansion loop. Run on a single target concept. Watch the console output for obvious errors.
8. **linearise.py** — Implement Kahn's algorithm. Run and print the sequence.
9. **evaluate.py** — Implement visualisation, statistics, and record export. Run and inspect.
10. **Manually fill in evaluation fields** in the eval record. Compare against ground truth.

---

## Success Criteria

The prototype succeeds — and work on the full architecture is justified — if and only if:

- Prerequisite precision at depth 1–2 exceeds 0.75.
- Prerequisite recall at depth 1–2 exceeds 0.65.
- Deduplication false merge rate is below 15%.
- Deduplication false split rate is below 15%.
- Sequence coherence rate exceeds 0.70.
- The above results are reproducible across at least 2 runs with different target concepts from the same corpus.

If these criteria are not met after 3–4 iteration cycles on prompts, thresholds, and chunking, the approach has a fundamental limitation that should be understood before committing to the full architecture.

---

## Common Implementation Errors to Avoid

This section addresses mistakes a coding LLM is likely to make.

1. **Do not use an ORM.** Use `psycopg2` directly with raw SQL. SQLAlchemy, Peewee, and similar add complexity with no benefit at this scale.

2. **Do not use async.** The prototype is single-threaded and synchronous. `asyncio`, `aiohttp`, and similar are unnecessary. Use the synchronous `anthropic.Anthropic` client and the synchronous `openai.OpenAI` client.

3. **Do not create a class hierarchy.** There should be no `Node` class, no `Edge` class, no `Graph` class. Nodes and edges are database rows represented as Python dicts. Functions operate on dicts and IDs.

4. **Do not build a web server.** No Flask, no FastAPI, no endpoints. The prototype consists of CLI scripts only.

5. **Do not install LangChain, LlamaIndex, or similar frameworks.** All LLM calls go through the `anthropic` or `openai` client libraries directly.

6. **Do not use chromadb, pinecone, weaviate, or similar unless pgvector setup fails.** If pgvector setup is genuinely prohibitive, use an in-memory dict mapping node IDs to numpy arrays and compute cosine similarity with `numpy.dot` / `numpy.linalg.norm`. This is adequate for the prototype's scale (< 200 vectors).

7. **Do not parallelize the DFS loop.** Run it synchronously. Parallelism introduces race conditions in deduplication that are not worth debugging in a prototype.

8. **Handle the empty-database case.** `find_nearest_node` will be called when the node table contains only the target node. It must return `(None, 0.0)` rather than crashing. The expansion loop must handle this: if `match` is `None`, always create a new node.

9. **JSON parsing from the LLM.** The LLM may return JSON wrapped in markdown fences: ` ```json\n{...}\n``` `. Strip these before parsing. The LLM may also include a preamble like "Here is the JSON:" before the actual JSON. Use a regex to extract the first `{...}` block if `json.loads()` fails on the raw response.

10. **Embedding dimension mismatch.** `text-embedding-3-small` returns 1536-dimensional vectors. The `VECTOR(1536)` column type in pgvector must match exactly. If you switch to a different embedding model, update both `config.EMBEDDING_DIMENSIONS` and the SQL schema.

11. **The `frontier.pop()` call must pop from the end of the list** (default Python list behaviour), not from the front. Popping from the front (`pop(0)`) turns the DFS into BFS, which still produces a correct DAG but changes the expansion order and depth assignment. Use `.pop()` with no argument.

12. **Cost of `is_ancestor` check.** This function walks the graph upward from `node_id`. At prototype scale (< 200 nodes), a simple BFS with a visited set is sufficient. Do not use recursive CTEs or stored procedures — a Python-level BFS over edges fetched from the database is adequate.

13. **The `output/` directory must be created** before writing files to it. Use `os.makedirs("output", exist_ok=True)` at the start of any script that writes to `output/`.

14. **Do not rerun ingestion without clearing the chunks table first.** Add a `--reset` flag to `ingest.py` that truncates the `chunks` table before ingesting. Similarly, add `--reset` to `expand.py` that truncates `nodes`, `edges`, `node_chunks`, and `expansion_log`.

15. **Token counting.** Use `tiktoken` with the `cl100k_base` encoding for all token counts. This encoding is used by both OpenAI's embedding models and Claude's tokeniser is close enough for size estimation purposes. Do not count words or characters as a proxy for tokens.
