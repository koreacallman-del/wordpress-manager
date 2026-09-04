#!/usr/bin/env python3
"""
log.db 조회.
  python3 scripts/query_log.py --topic <이름> --last 10
  python3 scripts/query_log.py --search "표지"
  python3 scripts/query_log.py --usage            # 세션별 토큰 합계
"""
import argparse, os, sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "log.db")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", dest="client")
    ap.add_argument("--search")
    ap.add_argument("--last", type=int, default=20)
    ap.add_argument("--usage", action="store_true")
    a = ap.parse_args()
    if not os.path.exists(DB):
        print("log.db 없음 (아직 기록된 작업이 없음)")
        return
    conn = sqlite3.connect(DB)
    if a.usage:
        rows = conn.execute("SELECT ts, session_id, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens, turns FROM usage ORDER BY ts DESC LIMIT ?", (a.last,)).fetchall()
        print("ts | session | in | out | cache_read | cache_write | turns")
        tin = tout = 0
        for r in rows:
            print(" | ".join(str(x) for x in r))
            tin += r[2] or 0; tout += r[3] or 0
        print(f"합계 input={tin:,} output={tout:,}")
        return
    q = "SELECT ts, event, tool, agent, client, summary FROM events WHERE event != 'PostToolUse' OR tool IN ('Task','Agent','Write','Edit','Bash','WebSearch')"
    params = []
    if a.client:
        q += " AND client = ?"; params.append(a.client)
    if a.search:
        q += " AND (summary LIKE ? OR payload LIKE ?)"; params += [f"%{a.search}%", f"%{a.search}%"]
    q += " ORDER BY ts DESC LIMIT ?"; params.append(a.last)
    for r in conn.execute(q, params):
        ts, ev, tool, agent, client, summ = r
        tag = agent or tool or ev
        print(f"{ts} [{tag}] {client or '-'} :: {summ}")

if __name__ == "__main__":
    main()
