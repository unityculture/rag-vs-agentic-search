"""方式 ①：PGVector RAG —— 問題向量化，到 pgvector 找語意最相近的 chunk。"""
from core import embed, chat_answer
from db import get_conn


def embed_query(question: str):
    """單獨把問題向量化（給 UI 分步呈現用）。"""
    return embed([question])[0]


def search(qvec, k: int = 4):
    """用既有的查詢向量到 pgvector 找最相近的 chunk（含相似度）。"""
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT source, chunk_index, content,
                   1 - (embedding <=> %s::vector) AS score
            FROM chunks
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (qvec, qvec, k),
        ).fetchall()
    return [
        {"source": r[0], "chunk_index": r[1], "content": r[2], "score": float(r[3])}
        for r in rows
    ]


def retrieve(question: str, k: int = 4):
    return search(embed_query(question), k)


def answer(question: str, k: int = 4):
    hits = retrieve(question, k)
    if not hits:
        return {"answer": "資料庫沒有資料，請先執行 ingest。", "hits": []}
    ans = chat_answer(question, [h["content"] for h in hits])
    return {"answer": ans, "hits": hits}
