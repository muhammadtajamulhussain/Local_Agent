import os

def scan_directory(target_dir):
    """
    Scans the target directory and returns a list of dictionaries 
    containing file names, extensions, and full paths without moving anything.
    """
    target_dir = target_dir.strip('"\'')

    if not os.path.exists(target_dir):
        print(f"Error: The path '{target_dir}' does not exist.")
        return []

    scanned_files = []

    # Loop through items in the target folder
    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)

        # Skip if it's a folder, we only want to scan files
        if os.path.isdir(file_path):
            continue

        # Tuple unpacking for file name and extension
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Append file details to our list
        scanned_files.append({
            "filename": filename,
            "name": name,
            "extension": ext,
            "path": file_path
        })

    return scanned_files