"""把 data/pdfs/ 的 PDF 切 chunk、算 embedding、寫進 pgvector。
用法：先 `docker compose up -d` 再 `uv run python ingest.py`。"""
import glob
import os
from core import PDF_DIR, extract_pdf, chunk_text, embed
from db import get_conn, init_schema


def main():
    pdfs = sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf")))
    if not pdfs:
        print("找不到 PDF，請先跑 `uv run python gen_samples.py`")
        return
    conn = get_conn()
    init_schema(conn)
    conn.execute("TRUNCATE chunks RESTART IDENTITY")
    total = 0
    for path in pdfs:
        name = os.path.basename(path)
        chunks = chunk_text(extract_pdf(path))
        vecs = embed(chunks)
        with conn.cursor() as cur:
            for i, (c, v) in enumerate(zip(chunks, vecs)):
                cur.execute(
                    "INSERT INTO chunks (source, chunk_index, content, embedding) VALUES (%s,%s,%s,%s)",
                    (name, i, c, v),
                )
        conn.commit()
        total += len(chunks)
        print(f"  {name}: 切成 {len(chunks)} 個 chunk、embedding、寫入完成")
    print(f"完成：{len(pdfs)} 份 PDF，共 {total} 個 chunk 已進 pgvector。")
    conn.close()


if __name__ == "__main__":
    main()
