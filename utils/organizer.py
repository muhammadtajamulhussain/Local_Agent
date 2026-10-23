import os
import shutil

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

def organize_scanned_files(target_dir, scanned_files):
    """Quietly moves scanned files into their structured category folders."""
    for file_info in scanned_files:
        filename = file_info["filename"]
        ext = file_info["extension"]
        file_path = file_info["path"]

        subfolder = EXTENSION_MAPPING.get(ext, "Others")
        dest_folder = os.path.join(target_dir, subfolder)
        os.makedirs(dest_folder, exist_ok=True)
        
        dest_path = os.path.join(dest_folder, filename)
        shutil.move(file_path, dest_path)