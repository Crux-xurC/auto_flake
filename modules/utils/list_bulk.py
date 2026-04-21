# modules/utils/list_bulk.py

choice_method = "Select multiple packages by index or 'all' (Fast bulk mode)"

def select(candidates):
    """
    Displays all packages and lets the user pick by index or 'all'.
    """
    print("\n--- Bulk Selection Mode ---")
    for i, pkg in enumerate(candidates):
        print(f"[{i}] {pkg}")
    
    ans = input("\nEnter indices separated by space, or 'all': ").strip()
    
    if ans.lower() == 'all':
        return candidates
    
    try:
        indices = [int(x) for x in ans.split()]
        return [candidates[i] for i in indices if 0 <= i < len(candidates)]
    except (ValueError, IndexError):
        print("[!] Invalid input. Returning empty list.")
        return []
