# Prototype Testing Guide

This guide is for a human tester validating the adaptive learning prototype implemented in this repository. It explains what the prototype does, how to set it up, how to run it, what to inspect, and which failure modes to watch for.

The prototype is intentionally narrow. It is testing one hypothesis:

1. A source text can be chunked and embedded.
2. A target concept can be expanded backward into prerequisites using RAG-grounded LLM calls.
3. The resulting prerequisite graph can be linearised into a plausible learning order.

Everything in this guide is aimed at testing that pipeline.

---

## What You Are Testing

You are not testing a web app, user accounts, mastery tracking, or assessments. You are testing whether the prototype produces:

- reasonable source chunks
- reasonable prerequisite nodes
- reasonable prerequisite edges
- acceptable deduplication behavior
- a coherent topological learning sequence

The most important question is not “did the script run?” but “does the graph make sense?”

---

## Repository Overview

The main files you will use are:

- [ingest.py](/workspace/ingest.py): loads a source text, chunks it, embeds each chunk, and stores the result in PostgreSQL
- [expand.py](/workspace/expand.py): starts from a target concept and recursively discovers prerequisite concepts
- [linearise.py](/workspace/linearise.py): performs topological sorting on the graph and prints a learning sequence
- [evaluate.py](/workspace/evaluate.py): exports a graph image, summary metrics, an evaluation record, and the expansion log
- [config.py](/workspace/config.py): core configuration constants
- [prompts/prerequisite.txt](/workspace/prompts/prerequisite.txt): prompt used for prerequisite discovery
- [prompts/dedup_confirm.txt](/workspace/prompts/dedup_confirm.txt): prompt used for borderline identity checks

Artifacts generated during testing will appear in `output/`.

---

## Prerequisites

Before running the prototype, make sure the following are available:

- Python 3.11+
- PostgreSQL with the `pgvector` extension available
- Graphviz installed on the system
- Valid OpenAI and Anthropic API keys

The repository already contains `requirements.txt`. Install dependencies with:

```bash
pip install -r requirements.txt
```

Your `.env` file should define:

```env
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
DATABASE_URL=postgresql://user:password@localhost:5432/adaptive_learning
```

---

## Recommended Test Corpus

Use a single educational text that is structured enough to contain definitional explanations and prerequisite assumptions. Good candidates:

- a textbook chapter
- a lecture note packet
- a tutorial-style markdown document

The best test corpus has:

- clear headings
- enough conceptual density to support prerequisite discovery
- a scope small enough that a tester can manually inspect the resulting graph

For the first test run, prefer a corpus in the range of roughly 20 to 80 pages of text-equivalent content.

---

## Suggested First Test Target

Choose a target concept that:

- definitely appears in the source text
- has multiple meaningful prerequisites
- is not so broad that the graph explodes immediately

Examples:

- `Gradient Descent`
- `Backpropagation`
- `Photosynthesis`
- `Bayes' Theorem`

Avoid first-run targets like:

- `Mathematics`
- `Biology`
- `Machine Learning`

Those are too broad to be good smoke-test targets.

---

## End-to-End Workflow

Run the prototype in this order:

1. Ingest the source corpus
2. Expand the graph from a target concept
3. Linearise the graph
4. Evaluate the graph
5. Manually inspect outputs

Commands:

```bash
python ingest.py --reset /path/to/source_text.md
python expand.py --reset "Gradient Descent" "An iterative optimisation algorithm that adjusts parameters in the direction of steepest decrease of a loss function"
python linearise.py
python evaluate.py
```

The `--reset` flags are recommended for clean test runs.

---

## Step 1: Test Ingestion

Run:

```bash
python ingest.py --reset /path/to/source_text.md
```

### What Success Looks Like

You should see:

- an `[INGEST] Complete.` message
- a nonzero chunk count
- a token count range that looks sensible
- a few sample chunks printed for inspection

### What to Inspect

Check the sample chunks and confirm:

- headings are sensible
- chunk bodies are readable and not obviously garbled
- chunks are not mostly tiny fragments
- chunks are not excessively large or semantically incoherent

### Red Flags

These are signs the chunking strategy is not working well:

- headings are mostly `Untitled` or generic fallback names when the source clearly has structure
- chunks begin or end mid-thought too often
- very large chunks contain multiple unrelated concepts
- almost all chunks are extremely short
- paragraphs from different sections are incorrectly merged

### Specific Ingestion Tests

Use these tests deliberately:

1. Test a markdown file with `#`, `##`, and `###` headings.
2. Test a numbered-outline document like `1.`, `1.1`, `1.1.1`.
3. Test a text file with no headings and confirm the paragraph fallback works.
4. Test re-running without `--reset` and confirm the script refuses to append duplicate corpus data.

Expected failure behavior for duplicate ingestion:

```text
[ERROR] The chunks table already contains N rows for corpus 'corpus_01'.
        Pass --reset to clear prior ingestion data before re-ingesting.
```

---

## Step 2: Test Expansion

Run:

```bash
python expand.py --reset "Gradient Descent" "An iterative optimisation algorithm that adjusts parameters in the direction of steepest decrease of a loss function"
```

### What Success Looks Like

You should see live DFS output, including:

- the current node being expanded
- new node creation events
- deduplication events
- optional cycle/back-edge flags
- a final node count and LLM call count

### What to Inspect

As the script runs, look for:

- prerequisite labels that are plausible and specific
- few or no obviously unrelated concepts
- deduplication merges that seem semantically justified
- manageable graph growth instead of immediate explosion

### Red Flags

These are the most important failure modes:

- prerequisites clearly come from general world knowledge rather than the source text
- prerequisites are too broad, like `Mathematics`
- prerequisites are too fine-grained, like notation trivia
- the same concept appears repeatedly under slightly different names
- many nodes have no meaningful relation to the target concept
- graph growth becomes runaway because each node expands into many vague sub-concepts

### Specific Expansion Tests

1. Run expansion on a target known to appear clearly in the source.
2. Re-run `expand.py` without `--reset` and confirm it refuses to append to an existing graph.
3. Use a second target concept from the same corpus and compare the resulting graph quality.
4. Inspect a few nodes in the database if needed and confirm `llm_response` is being saved.

Expected failure behavior for stale graph data:

```text
[ERROR] The nodes table is not empty (N rows found). Pass --reset to clear prior graph
        data before running a new expansion, or inspect the existing graph with
        linearise.py and evaluate.py.
```

---

## Step 3: Test Linearisation

Run:

```bash
python linearise.py
```

### What Success Looks Like

You should see a printed table with:

- sequence position
- label
- depth
- chunk count
- prerequisite count
- dependent count

### What to Inspect

Look through the ordering and ask:

- do foundational concepts tend to appear earlier?
- does the target concept appear later than its prerequisites?
- do obviously advanced concepts avoid showing up too early?

### Red Flags

- advanced concepts appear before fundamentals
- nodes with no prerequisites or chunk links dominate the top of the sequence
- the sort warns about a large number of orphaned nodes

Some imperfection is acceptable. The output should be directionally coherent, not necessarily pedagogically optimal.

---

## Step 4: Test Evaluation

Run:

```bash
python evaluate.py
```

### What Success Looks Like

The script should:

- save `output/dag.png`
- save `output/eval_record.json`
- save `output/expansion_log.json`
- print a summary statistics block

### What to Inspect

Inspect the following outputs:

- `output/dag.png`
- `output/eval_record.json`
- `output/expansion_log.json`

Check that:

- the graph image is readable
- the target node is visually distinguished
- back edges, if any, are clearly marked
- the evaluation record contains sensible counts and configuration values
- the expansion log is useful for reviewing dedup decisions

### Red Flags

- graph image generation fails because Graphviz is missing
- summary metrics are obviously inconsistent with the visible graph
- many nodes have no linked chunks
- expansion log is sparse or missing expected decisions

---

## Manual Quality Review Checklist

After the scripts run, manually inspect the graph and sequence using this checklist.

### Prerequisite Quality

For 10 sampled edges, ask:

- Is the source node truly a prerequisite of the target node?
- Is it immediate enough, or is it too far upstream?
- Is it grounded in the source text?

### Node Quality

For 10 sampled nodes, ask:

- Is the label concise and meaningful?
- Is the description specific and source-appropriate?
- Does the node feel like a teachable concept?

### Deduplication Quality

Review `output/expansion_log.json` and ask:

- Were obvious duplicates merged?
- Were distinct concepts incorrectly merged?
- Were near-duplicates split when they should have been merged?

### Chunk-Link Quality

For 10 sampled nodes, inspect linked chunks and ask:

- Do the `definitional` chunks actually define the concept?
- Do the `prerequisite-informing` chunks plausibly justify the dependency?

### Sequence Quality

Read the linearised order and ask:

- Could a learner plausibly move through this order?
- Do advanced concepts mostly appear after their foundations?

---

## Suggested Scoring Procedure

The prototype’s evaluation record contains fields you fill in manually. A simple review method is:

1. Evaluate depth-1 prerequisites for the target node.
2. Evaluate depth-2 prerequisites for a subset of children.
3. Count false merges and false splits from the expansion log.
4. Judge whether the linearised sequence is broadly coherent.

You can use this rough rubric:

- `precision_level_1`: fraction of returned depth-1 prerequisites that are correct
- `recall_level_1`: fraction of expected depth-1 prerequisites that were found
- `precision_level_2`: same idea at depth 2
- `recall_level_2`: same idea at depth 2
- `false_merge_count`: concepts merged that should have remained distinct
- `false_split_count`: concepts left separate that should have been merged
- `chunk_link_accuracy`: fraction of inspected chunk links that were useful and appropriate
- `sequence_coherence`: a subjective 0-1 score for whether the ordering mostly makes sense

Record notes in `output/eval_record.json` after inspection.

---

## Recommended Smoke Test Matrix

If you want a compact but useful test pass, run these:

1. Ingest a markdown corpus with headings.
2. Expand from one target concept with `--reset`.
3. Run `linearise.py`.
4. Run `evaluate.py`.
5. Re-run `expand.py` without `--reset` and confirm it fails correctly.
6. Re-run `ingest.py` without `--reset` and confirm it fails correctly.
7. Repeat the full run with a second target concept from the same corpus.

This is enough to validate the prototype’s basic operational behavior and get an initial read on graph quality.

---

## Common Operational Problems

### Database connection errors

Likely causes:

- `DATABASE_URL` is missing or incorrect
- PostgreSQL is not running
- `pgvector` is not installed in the target database

### Graphviz output failures

Likely cause:

- the Python package is installed but the Graphviz system binary is not

### OpenAI or Anthropic authentication failures

Likely causes:

- missing API keys
- malformed `.env`
- expired or invalid credentials

### Empty or poor graphs

Likely causes:

- the target concept is not well represented in the corpus
- chunking quality is poor
- the source corpus is too shallow or too broad
- the prompt is producing weak prerequisites

---

## When to Call a Test Run Successful

A test run is operationally successful if:

- all four scripts execute without crashing
- the outputs are generated where expected
- the graph is nontrivial
- the learning sequence is readable
- the manual review suggests the graph is at least directionally plausible

A test run is scientifically successful only if the graph quality is good enough to justify further iteration. That judgment depends on the manual review, not just on script completion.

---

## Minimal Tester Notes Template

You can use this template while testing:

```md
# Test Run Notes

## Corpus
- File:
- Domain:

## Target Concept
- Label:
- Description:

## Operational Outcome
- Ingest succeeded:
- Expand succeeded:
- Linearise succeeded:
- Evaluate succeeded:

## Graph Quality Notes
- Good:
- Bad:
- Suspected false merges:
- Suspected false splits:

## Sequence Notes
- Coherent aspects:
- Incoherent aspects:

## Next Changes Worth Trying
- 
```

