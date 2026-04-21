# modules/scanners/aur_analyzer.py
import subprocess
import os
import re

def analyze(package_list):
    analyzed_results = []

    for pkg_name in package_list:
        print(f"[*] Analyzing: {pkg_name}...")
        source_url = f"https://aur.archlinux.org/{pkg_name}.git"
        
        # 1. List files and find binaries(pacman -Ql)
        try:
            files = subprocess.check_output(["pacman", "-Ql", pkg_name], text=True).splitlines()
            binaries = [line.split()[1] for line in files if "/bin/" in line and os.path.isfile(line.split()[1])]
        except subprocess.CalledProcessError:
            print(f"[!] Package {pkg_name} not found in pacman database.")
            continue

        # 2.  Extract shared library dependencies(ldd)
        raw_depends = set()
        for bin_path in binaries:
            try:
                ldd_output = subprocess.check_output(["ldd", bin_path], text=True)
                libs = re.findall(r'\t(.*?) =>', ldd_output)
                for lib in libs:
                    raw_depends.add(lib.strip())
            except subprocess.CalledProcessError:
                continue

        # 3. Resolve corresponding Nix packag(nix-locate)
        # try to reslove from just pkg-name,or head that hitted
        
        nix_pkg_name = None
        if binaries:
            # let's try running commands "nix-locate" with binary-name
            target_bin = os.path.basename(binaries[0])
            nix_pkg_name = _resolve_nix_package(target_bin)

        analyzed_results.append({
            "name": pkg_name,
            "source": source_url,
            "depends": list(raw_depends),
            "package_name": nix_pkg_name, 
            "status": "analyzed"
        })

    return analyzed_results

def _resolve_nix_package(bin_name):
    """
    Uses nix-locate to find which Nix package provides the given binary.
    """
    try:
        # searching like " nix-locate -w -r "^/bin/pkg-name" "
        print(f"    [?] Searching nixpkgs for: {bin_name}")
        cmd = ["nix-locate", "--minimal", "--no-group", "--type", "x", "--whole-name", "--bin", f"/bin/{bin_name}"]
        output = subprocess.check_output(cmd, text=True).strip()
        
        if output:
            # Return the first successful match
            best_match = output.splitlines()[0].split(".")[0]
            print(f"    [+] Found: {best_match}")
            return best_match
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return None
