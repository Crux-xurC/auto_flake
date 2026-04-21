# modules/utils/list_sequentially.py

def select(candidates):
    """
    Prompts the user to confirm each package one by one.
    """
    selected = []
    print("\n--- Sequential Selection Mode ---")
    for pkg in candidates:
        ans = input(f"Migrate '{pkg}' to Flake? [y/N]: ").lower()
        if ans == 'y':
            selected.append(pkg)
    return selected
