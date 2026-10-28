"""core/safe_mover.py

The single choke point for every file move in the agent.
Dry-run, collision handling and undo logging all live here, so no other
module ever calls shutil.move directly.

This module never prints. It returns results and lets the caller decide
how to show them, so the same code works for a menu, a CLI, or tests.
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from core.journal import Journal


class UndoResult(NamedTuple):
    current: str    # where the file is now
    restored: str   # where it goes (or went) back to
    status: str     # "restored", "restored_renamed" or "missing"


def unique_destination(dst: Path) -> Path:
    """Return dst, or 'name (1).ext', 'name (2).ext', ... if dst already exists."""
    if not dst.exists():
        return dst
    n = 1
    while True:
        candidate = dst.with_name(f"{dst.stem} ({n}){dst.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def move_file(
    src: str | Path,
    dst: str | Path,
    dry_run: bool = True,
    journal: Journal | None = None,
    run_id: str | None = None,
) -> Path:
    """Move src to dst safely and return the final destination path.

    - dry_run=True (default): computes the result, touches nothing.
    - If dst is an existing folder, src is moved inside it.
    - If the destination name is taken, a numbered name is used instead.
      Nothing is ever overwritten.
    - Missing parent folders are created (only when dry_run=False).
    - If a journal and run_id are given, the move is logged BEFORE it
      happens, so a crash can never leave an untracked move behind.
    """
    if (journal is None) != (run_id is None):
        raise ValueError("Pass both journal and run_id, or neither.")

    src, dst = Path(src), Path(dst)

    if not src.exists():
        raise FileNotFoundError(f"Source does not exist: {src}")

    if dst.is_dir():
        dst = dst / src.name

    # Moving a file onto itself is a no-op, not a collision.
    if dst.exists() and src.resolve() == dst.resolve():
        return src

    final = unique_destination(dst)

    # A folder can't be moved into itself.
    if src.is_dir() and src.resolve() in final.resolve().parents:
        raise ValueError(f"Cannot move a folder into itself: {src} -> {final}")

    if not dry_run:
        if journal is not None:
            journal.record(run_id, src.absolute(), final.absolute())
        final.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(final))

    return final


def undo_run(journal: Journal, run_id: str, dry_run: bool = True) -> list[UndoResult]:
    """Reverse every move of a run, newest first.

    An undo is just a move in the opposite direction, so it reuses
    move_file and gets the same protections: if something now sits at the
    original path, the file is restored under a numbered name instead of
    overwriting it. Files that are no longer where the journal says are
    reported as "missing" and skipped. Undo moves are not journaled.
    """
    results: list[UndoResult] = []
    for src, dst in reversed(journal.moves(run_id)):
        if not Path(dst).exists():
            results.append(UndoResult(dst, src, "missing"))
            continue
        restored = move_file(dst, src, dry_run=dry_run)
        status = "restored" if Path(restored) == Path(src) else "restored_renamed"
        results.append(UndoResult(dst, str(restored), status))

    if not dry_run:
        journal.mark_undone(run_id)
    return results