# Adaptive Learning Prototype

Prototype implementation of the construction plan in `prompts/prototype_construction_plan_v2.md`.

## Setup

1. Install dependencies from `requirements.txt`.
2. Ensure PostgreSQL with `pgvector` is available.
3. Fill `.env` with `DATABASE_URL`, `OPENAI_API_KEY`, and `ANTHROPIC_API_KEY`.

## CLI

```bash
python ingest.py --reset /path/to/source_text.md
python expand.py --reset "Gradient Descent" "An iterative optimisation algorithm that adjusts parameters in the direction of steepest decrease of a loss function"
python linearise.py
python evaluate.py
```

