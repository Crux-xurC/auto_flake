from datetime import datetime

def generate(dictionary, template_content):
    """
    Analyzes the dictionary and injects formatted package strings into the flake template.
    Ensures that the injection is traceable by adding metadata as Nix comments.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Prepare the formatted string for injection
    packages_code = ""
    
    for item in dictionary:
        name = item.get("name", "unknown-app")
        nix_pkg = item.get("package_name")
        source = item.get("source", "N/A")
        deps = item.get("depends", [])
        
        # Metadata header for traceability within flake.nix
        packages_code += f"\n          # --- Added by auto_flake on {today} ---\n"
        packages_code += f"          # Original App: {name}\n"
        packages_code += f"          # Source: {source}\n"
        
        # Display detected shared libraries (limited to 5 for cleanliness)
        if deps:
            short_deps = ", ".join(deps[:5]) + ("..." if len(deps) > 5 else "")
            packages_code += f"          # Detected dependencies: {short_deps}\n"
        
        # Inject the resolved Nix package or a TODO comment if resolution failed
        if nix_pkg:
            packages_code += f"          {nix_pkg}\n"
        else:
            # Fallback for manual user intervention
            packages_code += f"          # {name} # [TODO: Could not resolve in nixpkgs. Please add manually.]\n"

    # 2. Marker-based Replacement Logic
    start_marker = "# <<NIX_AUTO_GEN_START>>"
    end_marker = "# <<NIX_AUTO_GEN_END>>"
    
    if start_marker in template_content and end_marker in template_content:
        # Split the content to isolate the section between markers
        parts = template_content.split(start_marker)
        pre_content = parts[0]
        # Isolating the part after the end marker
        post_content = parts[1].split(end_marker)[1]
        
        # Re-assemble the flake.nix with the new injected content
        new_content = f"{pre_content}{start_marker}{packages_code}\n          {end_marker}{post_content}"
        return new_content
    else:
        # If markers are missing, return original content to prevent file corruption
        return template_content
