import argparse
import random
import re
from dataclasses import dataclass
from pathlib import Path

import tiktoken

import config
from db import count_chunks_for_corpus, create_tables, insert_chunk, truncate_all_tables
from embeddings import embed_text


TOKEN_ENCODING = tiktoken.get_encoding("cl100k_base")
MARKDOWN_RE = re.compile(r"^(#{1,4})\s+(.+)$")
NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+){0,2})\s+(.+)$")


@dataclass
class ChunkCandidate:
    chapter_idx: int
    section_idx: int
    subsection_idx: int | None
    heading: str
    body: str
    token_count: int


def count_tokens(text):
    return len(TOKEN_ENCODING.encode(text))


def split_into_sentences(paragraph):
    parts = re.split(r"(?<=[.!?])\s+", paragraph.strip())
    return [part for part in parts if part]


def split_by_token_count(text, max_tokens):
    tokens = TOKEN_ENCODING.encode(text)
    slices = []
    for start in range(0, len(tokens), max_tokens):
        slices.append(TOKEN_ENCODING.decode(tokens[start : start + max_tokens]).strip())
    return [slice_text for slice_text in slices if slice_text]


def split_oversized_body(body, heading, chapter_idx, section_idx, subsection_idx):
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]
    emitted = []
    current_parts = []
    current_tokens = 0

    def flush_current():
        nonlocal current_parts, current_tokens
        if not current_parts:
            return
        chunk_body = "\n\n".join(current_parts).strip()
        emitted.append(chunk_body)
        current_parts = []
        current_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = count_tokens(paragraph)
        paragraph_units = [paragraph]

        if paragraph_tokens > config.MAX_CHUNK_TOKENS:
            paragraph_units = []
            for sentence in split_into_sentences(paragraph):
                if count_tokens(sentence) > config.MAX_CHUNK_TOKENS:
                    paragraph_units.extend(
                        split_by_token_count(sentence, config.MAX_CHUNK_TOKENS)
                    )
                else:
                    paragraph_units.append(sentence)

        for unit in paragraph_units:
            unit_tokens = count_tokens(unit)
            candidate_body = "\n\n".join(current_parts + [unit]).strip()
            candidate_tokens = count_tokens(candidate_body) if current_parts else unit_tokens
            if current_parts and candidate_tokens > config.MAX_CHUNK_TOKENS:
                flush_current()
            current_parts.append(unit)
            current_tokens = count_tokens("\n\n".join(current_parts))
            if current_tokens >= config.MAX_CHUNK_TOKENS:
                flush_current()

    flush_current()

    results = []
    for index, chunk_body in enumerate(emitted):
        chunk_heading = heading if index == 0 else f"{heading} (continued)"
        results.append(
            ChunkCandidate(
                chapter_idx=chapter_idx,
                section_idx=section_idx,
                subsection_idx=subsection_idx,
                heading=chunk_heading,
                body=chunk_body,
                token_count=count_tokens(chunk_body),
            )
        )
    return results


def detect_heading(lines, index):
    line = lines[index]
    stripped = line.strip()
    if not stripped:
        return None

    markdown_match = MARKDOWN_RE.match(stripped)
    if markdown_match:
        hashes, heading = markdown_match.groups()
        level = len(hashes)
        if level == 1:
            return "chapter", heading.strip()
        if level == 2:
            return "section", heading.strip()
        return "subsection", heading.strip()

    numbered_match = NUMBERED_RE.match(stripped)
    if numbered_match:
        number_str, heading = numbered_match.groups()
        dots = number_str.count(".")
        if dots == 0:
            return "chapter", heading.strip()
        if dots == 1:
            return "section", heading.strip()
        return "subsection", heading.strip()

    if stripped == stripped.upper() and len(stripped.split()) >= 3:
        prev_blank = index > 0 and not lines[index - 1].strip()
        next_blank = index < len(lines) - 1 and not lines[index + 1].strip()
        if prev_blank and next_blank:
            return "section", stripped
    return None


def file_has_headings(lines):
    return any(detect_heading(lines, index) for index in range(len(lines)))


def build_chunks_from_paragraphs(text):
    chunks = []
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for idx, paragraph in enumerate(paragraphs, start=1):
        token_count = count_tokens(paragraph)
        if token_count > config.MAX_CHUNK_TOKENS:
            chunks.extend(
                split_oversized_body(
                    paragraph,
                    f"Paragraph {idx}",
                    0,
                    idx,
                    None,
                )
            )
        else:
            chunks.append(
                ChunkCandidate(
                    chapter_idx=0,
                    section_idx=idx,
                    subsection_idx=None,
                    heading=f"Paragraph {idx}",
                    body=paragraph,
                    token_count=token_count,
                )
            )
    return chunks


def parse_structured_chunks(text):
    lines = text.splitlines()
    if not file_has_headings(lines):
        return build_chunks_from_paragraphs(text)

    emitted = []
    pending_body = ""

    current_chapter_idx = 0
    current_section_idx = 0
    current_subsection_idx = None
    current_heading = "Untitled"
    current_body_lines = []
    chapters_detected = 0
    sections_detected = 0
    subsections_detected = 0

    def emit_candidate(candidate):
        nonlocal pending_body
        body = candidate.body
        if pending_body:
            body = f"{pending_body}\n{body}".strip() if body else pending_body.strip()
            pending_body = ""
        token_count = count_tokens(body)

        if token_count > config.MAX_CHUNK_TOKENS:
            oversized_chunks = split_oversized_body(
                body,
                candidate.heading,
                candidate.chapter_idx,
                candidate.section_idx,
                candidate.subsection_idx,
            )
            emitted.extend(oversized_chunks)
            return

        merged_candidate = ChunkCandidate(
            chapter_idx=candidate.chapter_idx,
            section_idx=candidate.section_idx,
            subsection_idx=candidate.subsection_idx,
            heading=candidate.heading,
            body=body,
            token_count=token_count,
        )

        if merged_candidate.token_count < config.MIN_CHUNK_TOKENS:
            pending_body = (
                f"{pending_body}\n{merged_candidate.body}".strip()
                if pending_body
                else merged_candidate.body
            )
            return

        emitted.append(merged_candidate)

    def finalize_current():
        body = "\n".join(current_body_lines).strip()
        if not body:
            return
        emit_candidate(
            ChunkCandidate(
                chapter_idx=current_chapter_idx,
                section_idx=current_section_idx,
                subsection_idx=current_subsection_idx,
                heading=current_heading,
                body=body,
                token_count=count_tokens(body),
            )
        )

    for index, _line in enumerate(lines):
        heading_match = detect_heading(lines, index)
        if heading_match:
            kind, heading_text = heading_match
            finalize_current()
            current_body_lines = []
            current_heading = heading_text
            if kind == "chapter":
                current_chapter_idx += 1
                current_section_idx = 0
                current_subsection_idx = None
                chapters_detected += 1
            elif kind == "section":
                current_section_idx += 1
                current_subsection_idx = None
                sections_detected += 1
            else:
                current_subsection_idx = (
                    0 if current_subsection_idx is None else current_subsection_idx + 1
                )
                subsections_detected += 1
            continue
        current_body_lines.append(lines[index])

    finalize_current()

    if pending_body:
        emitted.append(
            ChunkCandidate(
                chapter_idx=current_chapter_idx,
                section_idx=current_section_idx,
                subsection_idx=current_subsection_idx,
                heading=current_heading,
                body=pending_body.strip(),
                token_count=count_tokens(pending_body.strip()),
            )
        )

    return emitted, chapters_detected, sections_detected, subsections_detected


def save_chunks(chunks):
    chunk_ids = []
    for chunk in chunks:
        embedding = embed_text(f"{chunk.heading}\n\n{chunk.body}")
        chunk_id = insert_chunk(
            corpus_id=config.CORPUS_ID,
            chapter_idx=chunk.chapter_idx,
            section_idx=chunk.section_idx,
            subsection_idx=chunk.subsection_idx,
            heading=chunk.heading,
            body=chunk.body,
            token_count=chunk.token_count,
            embedding=embedding,
        )
        chunk_ids.append(chunk_id)
    return chunk_ids


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("source_path")
    args = parser.parse_args()

    create_tables()

    if args.reset:
        truncate_all_tables()
    else:
        existing = count_chunks_for_corpus(config.CORPUS_ID)
        if existing:
            print(
                f"[ERROR] The chunks table already contains {existing} rows for corpus "
                f"'{config.CORPUS_ID}'."
            )
            print("        Pass --reset to clear prior ingestion data before re-ingesting.")
            raise SystemExit(1)

    source_path = Path(args.source_path)
    text = source_path.read_text(encoding="utf-8")

    parsed = parse_structured_chunks(text)
    if isinstance(parsed, tuple):
        chunks, chapters_detected, sections_detected, subsections_detected = parsed
    else:
        chunks = parsed
        chapters_detected = 0
        sections_detected = len(chunks)
        subsections_detected = 0

    if not chunks:
        print("[INGEST] No chunks created.")
        return

    save_chunks(chunks)
    token_counts = [chunk.token_count for chunk in chunks]

    print("[INGEST] Complete.")
    print(f"  Chunks created: {len(chunks)}")
    print(f"  Token count range: {min(token_counts)} — {max(token_counts)}")
    print(f"  Chapters detected: {chapters_detected}")
    print(f"  Sections detected: {sections_detected}")
    print(f"  Subsections detected: {subsections_detected}")

    sample_count = min(5, len(chunks))
    print("\n[INGEST] Sample chunks:")
    for chunk in random.sample(chunks, sample_count):
        preview = chunk.body[:100].replace("\n", " ")
        print(f"  - {chunk.heading} | {preview}... | tokens={chunk.token_count}")


if __name__ == "__main__":
    main()

