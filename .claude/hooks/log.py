#!/usr/bin/env python3
"""
Claude Code 훅 → SQLite 기록.
사용: python3 .claude/hooks/log.py <EventName>   (stdin으로 훅 JSON이 들어온다)

기록되는 것:
- events  : 모든 훅 이벤트 원본(JSON) + 요약 필드
- usage   : Stop 이벤트 시 transcript를 읽어 세션 누적 토큰 기록

실패해도 Claude Code 동작을 막지 않는다 (항상 exit 0).
"""
import sys, os, json, sqlite3, datetime, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = os.path.join(ROOT, "log.db")

def init(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY,
      ts TEXT NOT NULL,
      session_id TEXT,
      event TEXT NOT NULL,
      tool TEXT,
      agent TEXT,
      client TEXT,
      summary TEXT,
      payload TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_events_client ON events(client);
    CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
    CREATE TABLE IF NOT EXISTS usage (
      id INTEGER PRIMARY KEY,
      ts TEXT NOT NULL,
      session_id TEXT,
      input_tokens INTEGER,
      output_tokens INTEGER,
      cache_read_tokens INTEGER,
      cache_write_tokens INTEGER,
      turns INTEGER
    );
    """)

def guess_client(text):
    """경로에 projects/<고객명>/ 이 있으면 고객명 추출."""
    if not text:
        return None
    m = re.search(r"content/([^/\s\"']+)/", text)
    if m and m.group(1) != "_template":
        return m.group(1)
    return None

def summarize(event, data):
    tool = data.get("tool_name")
    agent = None
    summary = ""
    ti = data.get("tool_input") or {}
    if event == "UserPromptSubmit":
        summary = (data.get("prompt") or "")[:300]
    elif event == "PostToolUse":
        if tool in ("Read", "Write", "Edit", "MultiEdit"):
            summary = ti.get("file_path") or ti.get("path") or ""
        elif tool == "Bash":
            summary = (ti.get("command") or "")[:300]
        elif tool in ("Task", "Agent"):
            agent = ti.get("subagent_type") or ti.get("agent") or ""
            summary = (ti.get("description") or ti.get("prompt") or "")[:300]
        elif tool in ("WebSearch", "WebFetch"):
            summary = ti.get("query") or ti.get("url") or ""
        else:
            summary = json.dumps(ti, ensure_ascii=False)[:300]
    elif event == "SubagentStop":
        agent = data.get("agent_type") or data.get("subagent_type") or ""
        summary = "subagent finished"
    elif event == "Stop":
        summary = "turn finished"
    return tool, agent, summary

def record_usage(conn, data):
    """transcript(JSONL)에서 usage 합산. 형식이 바뀌면 조용히 건너뛴다."""
    path = data.get("transcript_path")
    if not path or not os.path.exists(path):
        return
    inp = out = cr = cw = turns = 0
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue
            msg = obj.get("message") if isinstance(obj, dict) else None
            u = None
            if isinstance(msg, dict):
                u = msg.get("usage")
            if not u and isinstance(obj, dict):
                u = obj.get("usage")
            if isinstance(u, dict):
                turns += 1
                inp += int(u.get("input_tokens") or 0)
                out += int(u.get("output_tokens") or 0)
                cr += int(u.get("cache_read_input_tokens") or 0)
                cw += int(u.get("cache_creation_input_tokens") or 0)
    if turns == 0:
        return
    sid = data.get("session_id")
    # 같은 세션의 이전 기록은 덮어쓴다 (누적값이므로)
    conn.execute("DELETE FROM usage WHERE session_id = ?", (sid,))
    conn.execute(
        "INSERT INTO usage (ts, session_id, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, turns) VALUES (?,?,?,?,?,?,?)",
        (datetime.datetime.now().isoformat(timespec="seconds"), sid, inp, out, cr, cw, turns),
    )

def main():
    event = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    try:
        conn = sqlite3.connect(DB)
        init(conn)
        tool, agent, summary = summarize(event, data)
        client = guess_client(summary) or guess_client(data.get("cwd", "")) or guess_client(raw if 'raw' in locals() else "")
        conn.execute(
            "INSERT INTO events (ts, session_id, event, tool, agent, client, summary, payload) VALUES (?,?,?,?,?,?,?,?)",
            (
                datetime.datetime.now().isoformat(timespec="seconds"),
                data.get("session_id"),
                event, tool, agent, client, summary,
                json.dumps(data, ensure_ascii=False)[:20000],
            ),
        )
        if event == "Stop":
            record_usage(conn, data)
        conn.commit()
        conn.close()
    except Exception as e:
        sys.stderr.write(f"[log.py] {e}\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
