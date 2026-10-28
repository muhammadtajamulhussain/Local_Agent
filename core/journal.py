"""core/journal.py

Append-only undo journal stored as JSON Lines (one record per line).

Record types:
    {"type": "run",    "run": id, "label": ..., "ts": ...}   a batch of moves starts
    {"type": "move",   "run": id, "src": ..., "dst": ...}    one move (logged BEFORE it happens)
    {"type": "undone", "run": id, "ts": ...}                 the run was reversed

Why append-only: nothing is ever rewritten, so a crash can at worst leave
one half-written last line, which the reader skips. It is also O(1) per
move, however many files a run touches.

This module only stores and reads history. It never moves files; the
actual undo lives in safe_mover.py so it gets the same safety rules.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

DEFAULT_PATH = Path.home() / ".file_agent" / "undo_log.jsonl"


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


class Journal:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path else DEFAULT_PATH

    # ---------- writing ----------

    def _append(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

    def new_run(self, label: str = "") -> str:
        """Start a new batch of moves and return its id."""
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:4]
        self._append({"type": "run", "run": run_id, "label": label, "ts": _now()})
        return run_id

    def record(self, run_id: str, src, dst) -> None:
        """Log a move. Call this BEFORE performing it (write-ahead)."""
        self._append({"type": "move", "run": run_id, "src": str(src), "dst": str(dst)})

    def mark_undone(self, run_id: str) -> None:
        self._append({"type": "undone", "run": run_id, "ts": _now()})

    # ---------- reading ----------

    def _read(self):
        if not self.path.exists():
            return
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue  # half-written line left by a crash

    def runs(self) -> list[dict]:
        """All runs, oldest first: {id, label, ts, moves, undone}."""
        runs: dict[str, dict] = {}
        for rec in self._read():
            run_id, kind = rec.get("run"), rec.get("type")
            if kind == "run":
                runs[run_id] = {
                    "id": run_id,
                    "label": rec.get("label", ""),
                    "ts": rec.get("ts", ""),
                    "moves": 0,
                    "undone": False,
                }
            elif run_id in runs:
                if kind == "move":
                    runs[run_id]["moves"] += 1
                elif kind == "undone":
                    runs[run_id]["undone"] = True
        return list(runs.values())

    def moves(self, run_id: str) -> list[tuple[str, str]]:
        """The (src, dst) pairs of one run, in the order they happened."""
        return [
            (rec["src"], rec["dst"])
            for rec in self._read()
            if rec.get("type") == "move" and rec.get("run") == run_id
        ]

    def last_undoable_run(self) -> str | None:
        """Newest run that has moves and hasn't been undone yet."""
        for run in reversed(self.runs()):
            if run["moves"] > 0 and not run["undone"]:
                return run["id"]
        return None