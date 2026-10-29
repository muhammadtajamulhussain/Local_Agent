# agent/menu.py

import os
from utils.scanner import scan_directory
from utils.organizer import organize_scanned_files, add_custom_rule
from utils.graph import (
    scan_project_files, 
    build_code_graph, 
    add_graph_rule, 
    GRAPH_EXTENSION_MAPPING, 
    get_used_colors, 
    generate_interactive_graph
)
from core.journal import Journal
from core.safe_mover import undo_run

journal = Journal()

def handle_organization_flow():
    """Sub-menu for organizing files and handling custom extensions."""
    path = input("Enter target folder path to organize: ").strip('"\'')
    
    while True:
        print("\n[Organization Options]")
        print("1. Add a custom file extension")
        print("2. Organize files now")
        print("3. Back to main menu")
        
        sub_choice = input("Select an option (1-3): ").strip()
        
        if sub_choice == "1":
            ext = input("Enter file extension (e.g. md or .md): ").strip()
            category = input("Enter target folder name (e.g. Documents): ").strip()
            add_custom_rule(ext, category)
            print(f"Added successfully: {ext} -> {category}")
            
        elif sub_choice == "2":
            print("Scanning directory...")
            files = scan_directory(path)
            if not files:
                print("No files found or path does not exist.")
                break

            errors = []
            plan = organize_scanned_files(path, files, dry_run=True, errors=errors)
            print(f"\nPreview: {len(plan)} files will be moved:")
            for src, dst in plan[:20]:
                print(f"  {os.path.basename(src)} -> {os.path.relpath(dst, path)}")
            if len(plan) > 20:
                print(f"  ...and {len(plan) - 20} more")
            if errors:
                print(f"\n{len(errors)} files can't be moved and will be skipped:")
                for p, why in errors:
                    print(f"  {os.path.basename(p)}: {why}")

            if input("\nApply these changes? (y/n): ").strip().lower() == "y":
                errors = []
                organize_scanned_files(path, files, dry_run=False, journal=journal, errors=errors)
                print("Organization complete.")
                if errors:
                    print(f"{len(errors)} files were skipped:")
                    for p, why in errors:
                        print(f"  {os.path.basename(p)}: {why}")
            else:
                print("Cancelled. Nothing was changed.")
            break
            
        elif sub_choice == "3":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")


def handle_graph_flow():
    """Sub-menu for Code Graph & Architecture Mapping."""
    path = input("Enter target project directory path to map: ").strip('"\'')
    
    while True:
        print("\n[Code Graph & Architecture Options]")
        print("Current Supported Extensions & Mappings:")
        for ext, lang in GRAPH_EXTENSION_MAPPING.items():
            print(f"  {ext} -> {lang}")
            
        print("1. Add extension to show on graph")
        print("2. View the Graph (Launch Interactive Visualizer)")
        print("3. Back to main menu")
        
        sub_choice = input("Select an option (1-4): ").strip()
        
        if sub_choice == "1":
            ext = input("Enter file extension (e.g. .ts or ts): ").strip()
            lang_name = input(f"Enter language/component name for {ext}: ").strip()
            
            # Loop until a unique color is provided
            while True:
                print(f"\nCurrently taken colors: {get_used_colors()}")
                color_name = input("Enter a unique color for this extension: ").strip()
                
                success, message = add_graph_rule(ext, lang_name, color_name)
                if success:
                    print(message)
                    break
                else:
                    print(f"❌ {message} Please choose a different color.")
            
        elif sub_choice == "2":
            print("Scanning and filtering project files...")
            valid_files = scan_project_files(path)
            
            if valid_files:
                print(f"Found {len(valid_files)} valid code files. Building architecture graph...")
                graph = build_code_graph(path, valid_files)
                
                print(f"\n--- Graph Built Successfully! ---")
                print(f"Total Nodes: {graph.number_of_nodes()} | Total Edges (Imports): {graph.number_of_edges()}")
                print("\nLaunching interactive network with live settings panel in your browser...")
                
                html_path = generate_interactive_graph(graph)
                
                print(f"Interactive graph successfully opened from: {html_path}")
            else:
                print("No valid code files found or path does not exist.")
            break    
            
        elif sub_choice == "3":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3 or 4.")

def handle_undo_flow():
    """Undo the most recent organization run."""
    run_id = journal.last_undoable_run()
    if run_id is None:
        print("Nothing to undo.")
        return

    results = undo_run(journal, run_id, dry_run=True)
    print(f"\nUndo preview for run {run_id}: {len(results)} files")
    for r in results[:20]:
        print(f"  [{r.status}] {r.current} -> {r.restored}")
    if len(results) > 20:
        print(f"  ...and {len(results) - 20} more")

    if input("\nApply undo? (y/n): ").strip().lower() == "y":
        undo_run(journal, run_id, dry_run=False)
        print("Undo complete.")
    else:
        print("Cancelled. Nothing was changed.")

def run_agent():
    """Main control center loop."""
    print("========================================")
    print("      Welcome User - Local Agent        ")
    print("========================================")
    
    while True:
        print("\n[Main Menu]")
        print("1. Organization of files")
        print("2. Code Graph & Architecture Mapper")
        print("3. Undo Last organization")
        print("4. Exit")
        
        choice = input("Select an option (1-3): ").strip()
        
        if choice == "1":
            handle_organization_flow()
        elif choice == "2":
            handle_graph_flow()
        elif choice == "3":
            handle_undo_flow()
        elif choice == "4":
            print("Shutting down Agent. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3 or 4.")


if __name__ == "__main__":
    run_agent()