"""方式 ②：Agentic search —— 一個會推理的 agent，自己決定怎麼找答案。
工具：list_docs（列檔）、grep_docs（關鍵字搜尋）、read_doc（讀整份文件）。
grep 只是它用的其中一個工具，不是 agentic search 本身。
回傳 {answer, steps}，steps 是它一步步的工具呼叫軌跡（給 UI 畫 workflow）。"""
import re
import json
from core import client, CHAT_MODEL, load_docs

_SENT = re.compile(r"[^。！？\n]+[。！？]?")

TOOLS = [
    {"type": "function", "function": {
        "name": "list_docs", "description": "列出所有可查的產品文件檔名。",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "grep_docs", "description": "用一個關鍵字在所有文件裡搜尋，回傳含該關鍵字的句子。",
        "parameters": {"type": "object", "properties": {"keyword": {"type": "string"}}, "required": ["keyword"]}}},
    {"type": "function", "function": {
        "name": "read_doc", "description": "讀取某一份文件的完整內容。",
        "parameters": {"type": "object", "properties": {"source": {"type": "string"}}, "required": ["source"]}}},
]

SYS = (
    "你是 KINYO 的產品客服 agent。你有工具可以列檔、用關鍵字 grep、讀整份文件。"
    "請自己一步步決定怎麼找答案：先想要查什麼 → grep 關鍵字 → 命中的句子不夠完整就讀整份文件 → 必要時再查一輪。"
    "蒐集到足夠資訊後，用繁體中文、口語、簡潔回答。只根據文件內容，找不到就說『資料中找不到』，不要編造。"
)


def _grep(keyword: str, limit: int = 8):
    out = []
    for source, text in load_docs().items():
        for sent in _SENT.findall(text):
            s = sent.strip()
            if keyword and keyword in s:
                out.append({"source": source, "text": s})
    return out[:limit]


def _run_tool(name, args):
    docs = load_docs()
    if name == "list_docs":
        return list(docs.keys())
    if name == "grep_docs":
        return _grep(args.get("keyword", ""))
    if name == "read_doc":
        return docs.get(args.get("source", ""), "(找不到此檔)")[:1600]
    return "unknown tool"


def answer(question: str, max_steps: int = 6):
    msgs = [{"role": "system", "content": SYS}, {"role": "user", "content": question}]
    steps = []
    for _ in range(max_steps):
        r = client.chat.completions.create(
            model=CHAT_MODEL, messages=msgs, tools=TOOLS, temperature=0)
        m = r.choices[0].message
        if not m.tool_calls:
            steps.append({"type": "answer", "content": m.content})
            return {"answer": m.content, "steps": steps}
        msgs.append({
            "role": "assistant", "content": m.content or "",
            "tool_calls": [{"id": tc.id, "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                           for tc in m.tool_calls],
        })
        for tc in m.tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            result = _run_tool(tc.function.name, args)
            steps.append({"type": "tool", "name": tc.function.name, "args": args, "result": result})
            msgs.append({"role": "tool", "tool_call_id": tc.id,
                         "content": json.dumps(result, ensure_ascii=False)[:2200]})
    fin = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=msgs + [{"role": "user", "content": "根據以上蒐集到的資訊，直接回答問題。"}],
        temperature=0)
    steps.append({"type": "answer", "content": fin.choices[0].message.content})
    return {"answer": fin.choices[0].message.content, "steps": steps}
