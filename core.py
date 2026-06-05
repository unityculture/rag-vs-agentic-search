"""共用工具：讀 PDF、切 chunk、呼叫 OpenAI embedding / chat。"""
import os
import glob
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "gpt-4o-mini")
PDF_DIR = os.path.join(os.path.dirname(__file__), "data", "pdfs")

client = OpenAI()


def extract_pdf(path: str) -> str:
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


@lru_cache(maxsize=1)
def load_docs() -> dict:
    """{檔名: 全文}。供 grep 模式使用，3 份小檔直接讀。"""
    docs = {}
    for f in sorted(glob.glob(os.path.join(PDF_DIR, "*.pdf"))):
        docs[os.path.basename(f)] = extract_pdf(f)
    return docs


def chunk_text(text: str, size: int = 280, overlap: int = 40) -> list[str]:
    """以字元為單位切 chunk，盡量在標點處斷句，並保留重疊。"""
    text = " ".join(text.split())
    chunks, i, n = [], 0, len(text)
    while i < n:
        end = min(i + size, n)
        # 往回找最近的標點當斷點，讓 chunk 更完整
        if end < n:
            cut = max(text.rfind(p, i + overlap, end) for p in "。！？；\n.")
            if cut > i + overlap:
                end = cut + 1
        chunks.append(text[i:end].strip())
        if end >= n:
            break
        i = max(end - overlap, i + 1)
    return [c for c in chunks if c]


def embed(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def chat_answer(question: str, contexts: list[str]) -> str:
    joined = "\n\n".join(f"[來源片段 {i+1}]\n{c}" for i, c in enumerate(contexts))
    sys = (
        "你是 KINYO 的產品客服助理。只能根據提供的『來源片段』回答問題，"
        "用繁體中文、口語、簡潔。如果片段裡找不到答案，就直說『資料中找不到』，不要編造。"
    )
    user = f"問題：{question}\n\n可用的來源片段：\n{joined}\n\n請根據以上片段回答。"
    r = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": sys}, {"role": "user", "content": user}],
        temperature=0.2,
    )
    return r.choices[0].message.content.strip()
