
# modules/scanners/other-pkg-manager_list_scanner.py

import subprocess

def scan():
    try:
        # Get local packages not in sync databases
#        result = subprocess.check_output(["comamand"], text=True)
        return [line.split()[0] for line in result.strip().split('\n')]
    except subprocess.CalledProcessError:
#        print("[!] Error: Could not execute pacman. Are you on [distorybution]"?")
        return []
