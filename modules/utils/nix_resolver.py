# modules/utils/nix_resolver.py
import subprocess
import os

def resolve_package_by_lib(lib_name):
    """
    Uses 'nix-locate' to find which Nix package provides the given library.
    Requires 'nix-index' to be installed and database updated.
    """
    # 1. Check if nix-locate is available
    if subprocess.call(["type", "nix-locate"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True) != 0:
        # We don't print a warning every time, just return None. 
        # The main logic or status_checker can show a one-time global warning.
        return None

    try:
        # Search for the library in the lib directory of nixpkgs
        # Added --no-group to simplify output
        result = subprocess.check_output(
            ["nix-locate", "--minimal", "--no-group", "--type", "x", "--path", f"/lib/{lib_name}"],
            text=True,
            stderr=subprocess.DEVNULL # Ignore database-not-found warnings in stderr
        ).strip().splitlines()
        
        if result:
            # Return the first matching package name (e.g., openssl.out -> openssl)
            return result[0].split('.')[0]
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
        
    return None

def is_database_ready():
    """Checks if nix-index database exists."""
    # Common path for nix-index database
    db_path = os.path.expanduser("~/.cache/nix-index/files.0.sqlite")
    return os.path.exists(db_path)
