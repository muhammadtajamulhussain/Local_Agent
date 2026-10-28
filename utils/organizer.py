import os

from core.safe_mover import move_file

EXTENSION_MAPPING = {
    ".py": os.path.join("Code", "python"),
    ".js": os.path.join("Code", "js"),
    ".html": os.path.join("Code", "web"),
    ".css": os.path.join("Code", "web"),
    ".cpp": os.path.join("Code", "cpp"),
    ".cs": os.path.join("Code", "csharp"),
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".zip": "Archives",
    ".rar": "Archives"
}

def add_custom_rule(extension, category_path):
    """Dynamically adds a new extension and target folder on the fly."""
    ext = extension.strip().lower()
    if not ext.startswith("."):
        ext = "." + ext
    EXTENSION_MAPPING[ext] = category_path

def organize_scanned_files(target_dir, scanned_files, dry_run=True, journal=None):
    """
    Moves scanned files into their category folders through the safe mover.

    With dry_run=True (the default) nothing is touched; the returned plan
    shows exactly what would happen. When applying for real, pass a Journal
    and the whole batch is recorded as one run that can be undone.
    Returns a list of (source, destination).
    """
    run_id = None
    if journal is not None and not dry_run:
        run_id = journal.new_run(f"organize {target_dir}")

    plan = []
    for file_info in scanned_files:
        subfolder = EXTENSION_MAPPING.get(file_info["extension"], "Others")
        dest_path = os.path.join(target_dir, subfolder, file_info["filename"])
        final = move_file(
            file_info["path"],
            dest_path,
            dry_run=dry_run,
            journal=journal if run_id else None,
            run_id=run_id,
        )
        plan.append((file_info["path"], str(final)))
    return plan