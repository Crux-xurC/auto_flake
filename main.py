import sys
import os
from modules.utils.data_manager import DataManager
from modules.utils.status_checker import StatusChecker
from modules.utils import plugin_loader
from modules.generators import default_generator, replace_generator, history_logger


def safe_input(prompt):
    """
    Captures user input and exits the program immediately if 'q' is entered.
    """
    user_input = input(prompt).strip()
    if user_input.lower() == 'q':
        print("\n[*] Quitting auto_flake. Goodbye!")
        sys.exit(0)
    return user_input

def setup_environment(checker, dm):
    """
    Orchestrates the initial directory setup and flake.nix validation.
    Uses StatusChecker for path resolution and default_generator for templating.
    """
    print(f"[*] Current working directory: {os.getcwd()}")
    print("[*] (Enter 'q' at any prompt to quit)")
    
    # 1. Ask for destination
    user_path = safe_input("[?] Enter target directory (Press Enter for current): ")
    
    # 2. Path validation & target-specific 'info/' directory creation
    # This also saves dm.data["status"]["target_path"] internally.
    target_path = checker.set_target_directory(user_path if user_path else ".")
    
    # 3. Check for flake.nix existence and markers
    f_status = checker.get_flake_status(target_path)
    flake_file = os.path.join(target_path, "flake.nix")

    if f_status == "missing":
        ans = safe_input(f"\n[?] 'flake.nix' not found in {target_path}. Create from template? [y/N]: ")
        if ans.lower() == 'y':
            # Uses the logic from your shared default_generator.py
            tmpl = default_generator.get_default_flake()
            with open(flake_file, "w", encoding="utf-8") as f:
                f.write(tmpl)
            dm.update_phase("idle")
            print("[+] Initialized new flake.nix from template.")
            
    elif f_status == "no_marker":
        print(f"\n[!] Warning: {flake_file} exists but lacks requiredMarkers (<<NIX_AUTO_GEN_START>>).")
        ans = safe_input("Overwrite it with the auto_flake template to enable injection? [y/N]: ").lower()
        if ans == 'y':
            tmpl = default_generator.get_default_flake()
            with open(flake_file, "w", encoding="utf-8") as f:
                f.write(tmpl)
            dm.update_phase("idle")
            print("[*] Overwritten with template. Ready for injection.")
        else:
            print("[!] Markers missing. Automated injection will be disabled.")

    return target_path

def select_manager(dm, managers):
    """
    Step 2: Which package manager?
    Identifies the source of packages (e.g., aur, pacman, brew).
    The selection determines which scanner and analyzer modules will be loaded.
    """
    if dm.data["selection"].get("manager"):
        return dm.data["selection"]["manager"]

    print("\n[Available Package Managers]")
    for i, manager in enumerate(managers):
        print(f"[{i}] {manager}")
    
    try:
        m_input = safe_input("\nSelect manager index: ")
        m_idx = int(m_input)
        selected_manager = managers[m_idx]
        dm.data["selection"]["manager"] = selected_manager
        dm.save()
        return selected_manager
    except (ValueError, IndexError):
        print("[!] Invalid manager selection.")
        return None

def select_ui_method(uis):
    """
    Step 3: How to select packages?
    Loads interaction plugins from modules/utils/list_*.py.
    Allows users to choose between Bulk, Sequential, or future 'Search' methods.
    """
    print("\n[Available Selection Methods]")
    ui_mods = []
    for i, ui_name in enumerate(uis):
        mod = plugin_loader.load_module(f"modules.utils.{ui_name}")
        # Each UI plugin should provide a 'choice_method' description string
        desc = getattr(mod, "choice_method", "No description provided")
        method_label = ui_name.replace('list_', '')
        print(f"[{i}] {method_label.capitalize()} : {desc}")
        ui_mods.append(mod)
    
    try:
        u_input = safe_input("\nSelect UI method index: ")
        u_idx = int(u_input)
        return ui_mods[u_idx]
    except (ValueError, IndexError):
        print("[!] Invalid UI selection.")
        return None


def run_selection_phase(dm, managers, uis):
    """
    Step 2 & 3: Selection and Scanning.
    Uses managers and uis lists synced by plugin_loader.
    """
    # 1. Select Package Manager (if not already selected)    
    print("\n[Available Package Managers]")
    for i, m in enumerate(managers):
        print(f"[{i}] {m}")
    
    try:
        m_idx = int(safe_input("\nSelect manager index: "))
        dm.data["selection"]["manager"] = managers[m_idx]
        dm.save()
    except (ValueError, IndexError):
        print("[!] Invalid selection.")
        return False 

    mgr_name = dm.data["selection"]["manager"]

    # 2. Select UI Method (Selection Style)
    print("\n[Available Selection Methods]")
    ui_mods = []
    for i, ui_name in enumerate(uis):
        mod = plugin_loader.load_module(f"modules.utils.{ui_name}")
        # Fetch description from the UI module
        desc = getattr(mod, "choice_method", "No description provided")
        method_label = ui_name.replace('list_', '').capitalize()
        print(f"[{i}] {method_label} : {desc}")
        ui_mods.append(mod)
    
    try:
        u_idx = int(safe_input("\nSelect UI method index: "))
        target_ui = ui_mods[u_idx]
    except (ValueError, IndexError):
        print("[!] Invalid selection.")
        return False

    # 3. Dynamic Scan Execution
    print(f"\n[*] Scanning packages via {mgr_name}...")
    try:
        # Dynamically load the scanner based on convention
        module_path = f"modules.scanners.{mgr_name}_list_scanner"
        scanner_mod = plugin_loader.load_module(module_path)
        
        # Consistent API call: .scan()
        available_packages = scanner_mod.scan()
        
        if not available_packages:
            print(f"[!] No packages found for {mgr_name}. Try another manager.")
            dm.data["selection"]["manager"] = None # Reset for retry
            return False

        # Use the selected UI method to pick packages
        selected_packages = target_ui.select(available_packages)
        
        if selected_packages:
            dm.data["selection"]["raw_list"] = selected_packages
            dm.update_phase("selected")
            print(f"[+] Successfully selected {len(selected_packages)} packages.")
            return True
        else:
            print("[!] No packages selected.")
            return False

    except Exception as e:
        print(f"[!] Scanning error in '{mgr_name}': {e}")
        return False

def run_analysis_phase(dm):
    """
    Step 4: Dependency Analysis.
    Loads the analyzer module corresponding to the selected manager (e.g., aur_analyzer.py).
    It resolves binaries and maps them to Nixpkgs using ldd and nix-locate.
    """
    print("\n[*] Starting Analysis Phase...")
    selected_list = dm.data["selection"].get("raw_list", [])
    mgr_name = dm.data["selection"].get("manager")

    if not selected_list:
        print("[!] No packages selected to analyze. Returning to idle.")
        dm.update_phase("idle")
        return False

    try:
        # Loading convention: modules/scanners/{mgr_name}_analyzer.py
        module_path = f"modules.scanners.{mgr_name}_analyzer"
        analyzer_mod = plugin_loader.load_module(module_path)
        
        # Validation: Check if the required 'analyze' function exists
        if not hasattr(analyzer_mod, "analyze"):
            print(f"[!] Plugin Error: '{module_path}' is missing the 'analyze()' function.")
            return False

        # Execute analysis (the logic you shared)
        # Returns: list of dicts [{'name':..., 'package_name':..., 'source':...}]
        results = analyzer_mod.analyze(selected_list)
        
        if results:
            # Update the centralized JSON dictionary
            dm.data["dictionary"] = results
            dm.update_phase("analyzed")
            print(f"[+] Analysis complete. {len(results)} packages mapped to Nix.")
            return True
        else:
            print("[!] Analysis resulted in an empty list.")
            dm.update_phase("idle")
            return False

    except Exception as e:
        print(f"[!] Analysis phase failed with error: {e}")
        return False



def run_generation_phase(dm, target_path):
    """
    Step 5: File Generation & Injection.
    Finalizes the process by updating flake.nix and logging to history.md.
    """
    print("\n[*] Finalizing: Injecting data into flake.nix...")
    flake_file = os.path.join(target_path, "flake.nix")
    
    if not dm.data.get("dictionary"):
        print("[!] No data found in dictionary. Skipping generation.")
        return False

    try:
        # Read the current content (template or existing flake)
        with open(flake_file, "r", encoding="utf-8") as f:
            current_content = f.read()
        
        # Inject analyzed results via markers
        new_content = replace_generator.generate(dm.data["dictionary"], current_content)
        
        with open(flake_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        # --- History Logging ---
        # Using the shared write_history(dictionary, target_path) logic
        history_logger.write_history(dm.data["dictionary"], target_path)
        
        dm.update_phase("generated")
        print(f"\n[+SUCCESS] {flake_file} updated!")
        print(f"[+] Migration details logged to: {os.path.join(target_path, 'info/history.md')}")
        return True

    except Exception as e:
        print(f"[!] Generation phase failed: {e}")
        return False    
    
def main():
    """
    Main orchestrator for the auto_flake workflow.
    Ensures a continuous flow from selection to generation.
    """
    dm = DataManager()
    checker = StatusChecker(dm)
    target_path = setup_environment(checker, dm)

    keep_running = True

    while keep_running:

        current_phase = dm.data.get("phase", "idle")
        managers, uis = plugin_loader.sync_plugins(dm)

        # 1. Selection Phase
        if current_phase in ["initial", "idle"]:
            checker.check_and_greet()
            if run_selection_phase(dm, managers, uis):
                current_phase = "selected" 
            else:
                continue

        # 2. Analysis Phase
        if current_phase == "selected":
            if run_analysis_phase(dm):
                current_phase = "analyzed"
            else:
                dm.update_phase("idle")
                continue

        # 3. Generation Phase
        if current_phase == "analyzed":
            if run_generation_phase(dm, target_path):
                current_phase = "generated"
            else:
                continue

        # 4. Success / Exit
        if current_phase == "generated":
            print("\n[🎉] All migration steps completed successfully!")

        elif current_phase is None:
            dm.update_phase("idle")
            continue
        elif current_phase not in ["initial", "idle", "selected", "analyzed", "generated"]:
            print(f"[!] Unknown state: {current_phase}. Emergency exit.")
            keep_running = False     

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Process interrupted by user. Exiting.")
        sys.exit(0)
