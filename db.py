import json
from collections import deque

import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import RealDictCursor

import config


CREATE_STATEMENTS = [
    "CREATE EXTENSION IF NOT EXISTS vector;",
    """
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
    """,
    """
    CREATE TABLE IF NOT EXISTS nodes (
        id               SERIAL PRIMARY KEY,
        label            TEXT NOT NULL,
        description      TEXT NOT NULL,
        embedding        VECTOR(1536),
        depth            INTEGER NOT NULL,
        is_target        BOOLEAN DEFAULT FALSE,
        is_depth_limited BOOLEAN DEFAULT FALSE,
        llm_response     JSONB,
        created_at       TIMESTAMP DEFAULT NOW()
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS edges (
        id              SERIAL PRIMARY KEY,
        source_id       INTEGER NOT NULL REFERENCES nodes(id),
        target_id       INTEGER NOT NULL REFERENCES nodes(id),
        is_back_edge    BOOLEAN DEFAULT FALSE,
        UNIQUE(source_id, target_id)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS node_chunks (
        id              SERIAL PRIMARY KEY,
        node_id         INTEGER NOT NULL REFERENCES nodes(id),
        chunk_id        INTEGER NOT NULL REFERENCES chunks(id),
        role            TEXT NOT NULL CHECK (
            role IN ('definitional', 'prerequisite-informing')
        ),
        UNIQUE(node_id, chunk_id, role)
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS expansion_log (
        id              SERIAL PRIMARY KEY,
        node_id         INTEGER NOT NULL REFERENCES nodes(id),
        event_type      TEXT NOT NULL,
        detail          JSONB,
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """,
]


def get_connection():
    """Return a psycopg2 connection using DATABASE_URL."""
    if not config.DATABASE_URL:
        raise ValueError("DATABASE_URL is not set.")
    conn = psycopg2.connect(config.DATABASE_URL, cursor_factory=RealDictCursor)
    register_vector(conn)
    return conn


def create_tables():
    """Execute all CREATE TABLE statements."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            for statement in CREATE_STATEMENTS:
                cur.execute(statement)


def insert_chunk(
    corpus_id,
    chapter_idx,
    section_idx,
    subsection_idx,
    heading,
    body,
    token_count,
    embedding,
):
    """Insert a chunk row and return the new chunk id."""
    sql = """
        INSERT INTO chunks (
            corpus_id, chapter_idx, section_idx, subsection_idx,
            heading, body, token_count, embedding
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    corpus_id,
                    chapter_idx,
                    section_idx,
                    subsection_idx,
                    heading,
                    body,
                    token_count,
                    embedding,
                ),
            )
            return cur.fetchone()["id"]


def insert_node(label, description, embedding, depth, is_target=False):
    """Insert a node row and return the new node id."""
    sql = """
        INSERT INTO nodes (label, description, embedding, depth, is_target)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (label, description, embedding, depth, is_target))
            return cur.fetchone()["id"]


def insert_edge(source_id, target_id, is_back_edge=False):
    """Insert an edge and return the new edge id or None if skipped."""
    sql = """
        INSERT INTO edges (source_id, target_id, is_back_edge)
        VALUES (%s, %s, %s)
        ON CONFLICT (source_id, target_id) DO NOTHING
        RETURNING id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (source_id, target_id, is_back_edge))
            row = cur.fetchone()
            return row["id"] if row else None


def insert_node_chunk(node_id, chunk_id, role):
    """Insert a node-chunk link. ON CONFLICT DO NOTHING."""
    sql = """
        INSERT INTO node_chunks (node_id, chunk_id, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (node_id, chunk_id, role) DO NOTHING
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (node_id, chunk_id, role))


def insert_expansion_log(node_id, event_type, detail_dict):
    """Insert an expansion log entry."""
    sql = """
        INSERT INTO expansion_log (node_id, event_type, detail)
        VALUES (%s, %s, %s::jsonb)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (node_id, event_type, json.dumps(detail_dict)))


def find_nearest_node(embedding, exclude_id=None):
    """Return the nearest node row and cosine similarity."""
    if exclude_id is None:
        sql = """
            SELECT *, 1 - (embedding <=> %s::vector) AS similarity
            FROM nodes
            ORDER BY embedding <=> %s::vector
            LIMIT 1
        """
        params = (embedding, embedding)
    else:
        sql = """
            SELECT *, 1 - (embedding <=> %s::vector) AS similarity
            FROM nodes
            WHERE id != %s
            ORDER BY embedding <=> %s::vector
            LIMIT 1
        """
        params = (embedding, exclude_id, embedding)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()
            if not row:
                return None, 0.0
            similarity = float(row.pop("similarity"))
            return row, similarity


def retrieve_top_k_chunks(embedding, k):
    """Return the k most similar chunks by cosine similarity."""
    sql = """
        SELECT *, 1 - (embedding <=> %s::vector) AS similarity
        FROM chunks
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (embedding, embedding, k))
            return list(cur.fetchall())


def get_all_nodes():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes ORDER BY id")
            return list(cur.fetchall())


def get_all_edges():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM edges ORDER BY id")
            return list(cur.fetchall())


def get_node_chunks(node_id):
    sql = """
        SELECT c.*, nc.role
        FROM node_chunks nc
        JOIN chunks c ON c.id = nc.chunk_id
        WHERE nc.node_id = %s
        ORDER BY c.id, nc.role
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (node_id,))
            return list(cur.fetchall())


def get_node_by_id(node_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE id = %s", (node_id,))
            return cur.fetchone()


def update_node_llm_response(node_id, response):
    sql = "UPDATE nodes SET llm_response = %s::jsonb WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (json.dumps(response), node_id))


def update_node_depth_limited(node_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE nodes SET is_depth_limited = TRUE WHERE id = %s",
                (node_id,),
            )


def is_ancestor(candidate_ancestor_id, node_id):
    """Determine whether candidate_ancestor_id is an ancestor of node_id."""
    if candidate_ancestor_id == node_id:
        return True

    visited = set()
    queue = deque([(node_id, 0)])

    with get_connection() as conn:
        with conn.cursor() as cur:
            while queue:
                current_id, depth = queue.popleft()
                if depth >= config.MAX_DEPTH or current_id in visited:
                    continue
                visited.add(current_id)
                cur.execute(
                    """
                    SELECT source_id
                    FROM edges
                    WHERE target_id = %s AND is_back_edge = FALSE
                    """,
                    (current_id,),
                )
                for row in cur.fetchall():
                    parent_id = row["source_id"]
                    if parent_id == candidate_ancestor_id:
                        return True
                    if parent_id not in visited:
                        queue.append((parent_id, depth + 1))
    return False


def count_rows(table_name):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS count FROM {table_name}")
            return cur.fetchone()["count"]


def count_chunks_for_corpus(corpus_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS count FROM chunks WHERE corpus_id = %s",
                (corpus_id,),
            )
            return cur.fetchone()["count"]


def truncate_graph_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE expansion_log, node_chunks, edges, nodes
                RESTART IDENTITY CASCADE
                """
            )


def truncate_all_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE expansion_log, node_chunks, edges, nodes, chunks
                RESTART IDENTITY CASCADE
                """
            )


def get_all_expansion_logs():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM expansion_log ORDER BY created_at, id")
            return list(cur.fetchall())
