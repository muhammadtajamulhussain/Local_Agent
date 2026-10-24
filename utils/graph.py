import os
import ast
import networkx as nx
from pathlib import Path
from pyvis.network import Network
import webbrowser

# Central extension mapping dictionary
GRAPH_EXTENSION_MAPPING = {
    ".py": "Python",
    ".js": "JavaScript",
    ".html": "Html",
    ".css": "CSS",
    ".cpp": "C++",
    ".cs": "C#",
    ".jsx": "React"
}

# Central color mapping dictionary
NODE_COLOR_MAPPING = {
    ".py": "blue",
    ".js": "yellow",
    ".html": "orange",
    ".css": "purple",
    ".cpp": "green",
    ".cs": "red",
    ".jsx": "cyan"
}

def get_used_colors():
    """Returns a list of all currently assigned colors."""
    return list(NODE_COLOR_MAPPING.values())

def add_graph_rule(extension, language_name, color_name):
    """
    Dynamically adds a new extension, language name, and unique color.
    Returns (True, success_msg) or (False, error_msg) if the color is already taken.
    """
    ext = extension.strip().lower()
    if not ext.startswith("."):
        ext = "." + ext
        
    color = color_name.strip().lower()
    
    # Check for duplicate colors (case-insensitive)
    existing_colors = [c.lower() for c in NODE_COLOR_MAPPING.values()]
    if color in existing_colors:
        return False, f"The color '{color_name}' is already assigned to another extension!"
        
    GRAPH_EXTENSION_MAPPING[ext] = language_name
    NODE_COLOR_MAPPING[ext] = color
    return True, f"Successfully added {ext} -> {language_name} [{color}]"

def scan_project_files(target_dir):
    """
    Scans the target directory recursively using GRAPH_EXTENSION_MAPPING 
    to filter valid code files, skipping hidden folders and common libraries (lib, venv, node_modules).
    """
    target_dir = target_dir.strip('"\'')
    if not os.path.exists(target_dir):
        return []

    # Folders to completely ignore during the scan
    ignored_folders = {'.git', '__pycache__', 'venv', 'env', 'node_modules', 'lib', 'libs', 'dist', 'build'}

    valid_files = []

    for root, dirs, files in os.walk(target_dir):
        # Skip hidden folders and specified library/dependency folders
        dirs[:] = [d for d in dirs if not d.startswith('.') and d.lower() not in ignored_folders]

        for filename in files:
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext in GRAPH_EXTENSION_MAPPING:
                file_path = os.path.join(root, filename)
                valid_files.append(file_path)

    return valid_files

def build_code_graph(target_dir, valid_files):
    """
    Parses Python files using AST to extract import dependencies 
    and builds a NetworkX directed graph, attaching color attributes to nodes.
    """
    root = Path(target_dir)
    graph = nx.DiGraph()
    
    # Map module names to relative file paths for edge linking & assign colors
    module_map = {}
    for file_path in valid_files:
        path = Path(file_path)
        try:
            rel_path = path.relative_to(root)
        except ValueError:
            rel_path = path
            
        ext = path.suffix.lower()
        node_color = NODE_COLOR_MAPPING.get(ext, "gray")
        
        module_name = ".".join(rel_path.with_suffix("").parts)
        module_map[module_name] = str(rel_path)
        
        # Add node with file type, label, and color attribute
        graph.add_node(str(rel_path), label=str(rel_path), file_type=ext, color=node_color)

    # Second pass: Parse AST to find imports and build edges
    for file_path in valid_files:
        path = Path(file_path)
        try:
            rel_path = str(path.relative_to(root))
        except ValueError:
            rel_path = str(path)

        if path.suffix.lower() == '.py':
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                target_module = None
                
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        target_module = alias.name
                elif isinstance(node, ast.ImportFrom) and node.module:
                    target_module = node.module

                if target_module and target_module in module_map:
                    target_rel_path = module_map[target_module]
                    graph.add_edge(rel_path, target_rel_path, relationship="imports")

    return graph

def generate_interactive_graph(graph, output_filename="architecture_graph.html"):
    """
    Takes the NetworkX graph, generates an interactive HTML network file via PyVis,
    and embeds a live physics control panel directly inside the browser window.
    """
    net = Network(height="850px", width="100%", bgcolor="#1e1e1e", font_color="white", directed=True)
    net.from_nx(graph)
    
    # This adds the live configuration panel directly into the generated HTML page!
    net.show_buttons(filter_=['physics'])
    
    net.save_graph(output_filename)
    
    absolute_path = os.path.abspath(output_filename)
    webbrowser.open(f"file://{absolute_path}")
    
    return absolute_path