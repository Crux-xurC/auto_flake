# modules/generators/history_logger.py
from datetime import datetime
import os

def write_history(dictionary, target_path):
    """
    Logs the migration details into a Markdown table inside the TARGET directory.
    This ensures traceability and serves as a 'receipt' of the migration.
    """
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Direct the output to info/history.md relative to the target directory
    history_file = os.path.join(target_path, "info/history.md")
    
    # Ensure the 'info' directory exists before writing
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    file_exists = os.path.exists(history_file)
    
    with open(history_file, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("# auto_flake Migration History\n\n")
            f.write("This log tracks packages migrated from other managers to Nix Flakes.\n")
        
        f.write(f"\n## Session: {today}\n\n")
        f.write("| App Name | Detected Nix Pkg | Source | Key Dependencies |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        
        for item in dictionary:
            name = item.get("name", "Unknown")
            nix_pkg = item.get("package_name") or "*(Manual Resolve)*"
            source = item.get("source", "N/A")
            # Show first 3 deps to keep the table readable
            deps = ", ".join(item.get("depends", [])[:3])
            
            f.write(f"| {name} | {nix_pkg} | {source} | {deps} |\n")
