# modules/scanners/aur_list_scanner.py
import subprocess

def scan():
    """
    Fetches explicitly installed AUR packages via 'pacman -Qm'.
    Returns a list of strings (package names).
    """
    try:
        # Get local packages not in sync databases
        result = subprocess.check_output(["pacman", "-Qm"], text=True)
        return [line.split()[0] for line in result.strip().split('\n')]
    except subprocess.CalledProcessError:
        print("[!] Error: Could not execute pacman. Are you on Arch Linux?")
        return []
