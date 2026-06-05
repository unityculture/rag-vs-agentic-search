"""KINYO RAG demo — 同一份產品 PDF，兩種取得 context 的方式，逐步呈現 workflow。
  ① PGVector RAG（固定管線：向量化 → 相似度 → Top-K → LLM）
  ② Agentic search（agent 自己用 grep / read 工具一步步找）
執行：streamlit run app.py"""
import time
import streamlit as st
import core
import rag_agentic
from db import db_ready

st.set_page_config(page_title="KINYO RAG Demo", layout="wide")

EXAMPLES = [
    "多功能電烤盤的保固期是多久？哪些情況不保固？",
    "USB 循環扇可以整台水洗嗎？",
    "行動電源可以帶上飛機嗎？為什麼？",
    "電烤盤的不沾塗層刮傷了還能用嗎？",
    "行動電源可以邊充邊放嗎？",
    "循環扇風變小了可能是什麼原因？",
]

def _chip(label, sub="", accent="#0F1E3D", bg="#FFFFFF", fg="#1A1A1A", subfg="#6B7280"):
    s = f'<div style="font-size:11px;color:{subfg};font-weight:400;margin-top:3px;">{sub}</div>' if sub else ""
    return (f'<div style="background:{bg};border:1px solid #E2E4E8;border-left:4px solid {accent};'
            f'border-radius:10px;padding:10px 15px;font-weight:700;color:{fg};font-size:13px;line-height:1.2;'
            f'box-shadow:0 6px 14px -10px rgba(15,30,61,.4);">{label}{s}</div>')

_ARR = '<span style="color:#B6BEC8;font-size:17px;font-weight:800;padding:0 2px;">&rarr;</span>'


def _tag(t):
    return (f'<span style="font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.06em;'
            f'color:#F76B1C;background:#FDE7D6;padding:6px 12px;border-radius:999px;white-space:nowrap;'
            f'font-weight:700;">{t}</span>')


ARCH_HTML = f"""
<div style="background:#FAFAF8;border:1px solid #E2E4E8;border-radius:16px;padding:22px 24px;
            font-family:-apple-system,'Noto Sans TC',sans-serif;">
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin-bottom:18px;">
    {_tag('建置 · 一次性')}
    {_chip('📄 產品 PDF', '說明書 / 保固 / FAQ')}{_ARR}
    {_chip('✂️ ingest.py', '切 chunk + embedding')}{_ARR}
    {_chip('🗄️ pgvector', '向量庫', accent='#3B6FE0', bg='#EAF0FC')}
  </div>
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:9px;">
    {_tag('查詢 · 每次問')}
    {_chip('❓ 使用者問題')}{_ARR}
    <div style="display:flex;flex-direction:column;gap:9px;">
      {_chip('① PGVector', '向量檢索', accent='#F76B1C', bg='#FFF4EC')}
      {_chip('② Agentic search', 'grep / read 工具', accent='#2A9D8F', bg='#EAF6F3')}
    </div>
    {_ARR}
    {_chip('🤖 LLM', 'OpenAI', accent='#F76B1C', bg='#0F1E3D', fg='#F4F4F2', subfg='rgba(244,244,242,.7)')}{_ARR}
    {_chip('✅ 答案 + 來源')}
  </div>
</div>
"""

st.title("KINYO 產品問答 · RAG Demo")
st.caption("同一份產品說明書 PDF，比較兩種「取得 context」的方式。資料為 demo 用範例，非真實規格。")

# ---- 這個 demo 怎麼建的 ----
with st.expander("🛠 這個 demo 是怎麼建的？（建置很簡單，你們也能做）", expanded=True):
    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.html(ARCH_HTML)
    with c2:
        st.markdown("""
**做了什麼（約 8 個檔、半天可成）**
1. 自動產生 3 份中文產品說明書 PDF
2. `ingest.py`：切 chunk → OpenAI embedding → 寫進 pgvector
3. 兩條取資料的路：① 向量檢索 ② agent 用工具找
4. Streamlit 把流程畫出來

**跑起來只要 4 步**
```bash
docker compose up -d
uv run python ingest.py
uv run streamlit run app.py
# 開瀏覽器點問題
```
""")
    st.markdown("**給 LLM / agent 的關鍵 prompt：**")
    p1, p2 = st.columns(2)
    p1.code('系統：你是 KINYO 產品客服助理。\n只能根據提供的「來源片段」回答，\n找不到就說「資料中找不到」，不要編造。', language="text")
    p2.code('系統：你是 KINYO 產品客服 agent。\n你有工具：list_docs / grep_docs / read_doc。\n自己決定怎麼一步步找 → 夠了再回答。', language="text")
    st.caption("重點：整套 prototype 沒有魔法 —— 幾個檔案 + 幾段 prompt。你們接下來可以拿 README 自己跑一份。")

with st.sidebar:
    st.subheader("資料來源")
    for name in core.load_docs():
        st.write("📄", name)
    st.divider()
    ok = db_ready()
    st.write("PGVector 連線：", "🟢 已連線" if ok else "🔴 未連線")
    if not ok:
        st.caption("左欄需 DB：`docker compose up -d` + `uv run python ingest.py`。Agentic search 不需 DB。")
    st.caption("Embedding：text-embedding-3-small")

st.divider()
st.write("##### 點一個範例問題，或自己輸入：")
cols = st.columns(3)
if "q" not in st.session_state:
    st.session_state.q = ""
for i, ex in enumerate(EXAMPLES):
    if cols[i % 3].button(ex, use_container_width=True, key=f"ex{i}"):
        st.session_state.q = ex

q = st.text_input("問題", value=st.session_state.q, placeholder="例如：電烤盤的保固期多久？")
run = st.button("送出問題", type="primary")


def workflow_pgvector(q):
    st.markdown("### ① PGVector RAG")
    st.caption("固定管線：向量化 → 算相似度 → 取 Top-K → 餵 LLM")
    if not db_ready():
        st.warning("PGVector 未連線，請先啟動 DB（`docker compose up -d`）並 ingest。")
        return
    import rag_pgvector
    with st.status("① 把問題轉成向量（embedding）…", expanded=False) as s:
        qvec = rag_pgvector.embed_query(q)
        time.sleep(0.4)
        s.update(label=f"① 問題已向量化（{len(qvec)} 維）", state="complete")
    with st.status("② 在 pgvector 算與每個 chunk 的相似度…", expanded=True) as s:
        hits = rag_pgvector.search(qvec, 4)
        time.sleep(0.4)
        for h in hits:
            st.write(f"- **{h['source']}** · #{h['chunk_index']} · 相似度 `{h['score']:.3f}`")
        s.update(label="② 算出相似度，挑出最相近的片段", state="complete")
    with st.status("③ 把選中片段 + 問題組成 prompt → LLM…", expanded=False) as s:
        ans = core.chat_answer(q, [h["content"] for h in hits])
        time.sleep(0.3)
        s.update(label="③ LLM 根據片段生成答案", state="complete")
    st.success(ans)
    with st.expander("看選中的 chunk 全文"):
        for h in hits:
            st.markdown(f"**{h['source']}** · #{h['chunk_index']} · {h['score']:.3f}")
            st.write(h["content"])
            st.divider()


def workflow_agentic(q):
    st.markdown("### ② Agentic search")
    st.caption("Agent 自己決定怎麼找：list / grep / read，一步步推進。grep 只是它的工具之一。")
    with st.spinner("Agent 思考與搜尋中…"):
        r = rag_agentic.answer(q)
    for stp in r["steps"]:
        if stp["type"] != "tool":
            continue
        name, args, res = stp["name"], stp["args"], stp["result"]
        label = {
            "list_docs": "🗂 列出有哪些文件",
            "grep_docs": f"🔎 grep 關鍵字「{args.get('keyword','')}」",
            "read_doc": f"📄 讀取整份：{args.get('source','')}",
        }.get(name, name)
        with st.status(label, state="complete", expanded=True):
            if name == "grep_docs":
                if res:
                    for it in res:
                        st.write(f"- **{it['source']}**：{it['text']}")
                else:
                    st.write("（這個關鍵字沒命中，agent 會換方式）")
            elif name == "list_docs":
                st.write("、".join(res))
            elif name == "read_doc":
                st.write((res[:280] + "…") if isinstance(res, str) else res)
        time.sleep(0.35)
    st.success(r["answer"])


if run and q.strip():
    left, right = st.columns(2)
    with left:
        workflow_pgvector(q)
    with right:
        workflow_agentic(q)
elif run:
    st.info("請先輸入或選一個問題。")
