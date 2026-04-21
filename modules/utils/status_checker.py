# modules/utils/status_checker.py
import os
import sys

class StatusChecker:
    """
    Validates the target environment and determines the migration phase.
    (English comments for GitHub visibility)
    """

    def __init__(self, data_manager):
        self.dm = data_manager

    def set_target_directory(self, path):
        """
        Validates the given path, ensures directories exist, and saves to info.json.
        """
        # 1. user input（~/ -> /home/user/ ）
        expanded_path = os.path.expanduser(path)

        # 2.get absolute path
        abs_path = os.path.abspath(os.path.expanduser(path))
        
        # Ensure the target directory exists
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
            print(f"[*] Created target directory: {abs_path}")
        
        # Ensure the 'info' directory exists inside the target
        info_dir = os.path.join(abs_path, "info")
        if not os.path.exists(info_dir):
            os.makedirs(info_dir)

        self.dm.data["status"]["target_path"] = abs_path
        self.dm.save()
        return abs_path

    def get_flake_status(self, target_path):
        """
        Determines the status of flake.nix in the target directory.
        Returns: 'missing', 'no_marker', or 'valid'
        """
        flake_path = os.path.join(target_path, "flake.nix")
        if not os.path.exists(flake_path):
            return "missing"
        
        try:
            with open(flake_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "<<NIX_AUTO_GEN_START>>" not in content:
                    return "no_marker"
            return "valid"
        except IOError:
            return "error"

    def check_and_greet(self):
        """
        Greets the user and returns the current phase.
        """
        phase = self.dm.data.get("phase", "idle")

        print("\n--- auto_flake: Nix Migration Assistant ---")
        
        if phase == "initial":
            print("[*] Welcome! This looks like a new project setup.")
        else:
            print(f"[*] Current Progress: {phase.capitalize()}")
        
        return phase
