# agent/menu.py

from utils.scanner import scan_directory
from utils.organizer import organize_scanned_files, add_custom_rule

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
            if files:
                print(f"Found {len(files)} files. Organizing...")
                organize_scanned_files(path, files)
                print("Organization complete.")
            else:
                print("No files found or path does not exist.")
            break
            
        elif sub_choice == "3":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

def run_agent():
    """Main control center loop."""
    print("========================================")
    print("   Welcome User                         ")
    print("========================================")
    
    while True:
        print("\n1. Organization of files")
        print("2. Exit")
        
        choice = input("Select an option (1-2): ").strip()
        
        if choice == "1":
            handle_organization_flow()
        elif choice == "2":
            print("Shutting down Agent. Goodbye.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")