# modules/generators/default_generator.py
import os

# Get the absolute path of the directory where this file resides, 
# then go up to the project root to find 'info/flake.tmpl'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "info", "flake.tmpl")

def get_default_flake():
    """
    Reads the template file from the fixed absolute path and returns it as a string.
    Ensures the template can be found regardless of where main.py is called from.
    """
    if os.path.exists(TEMPLATE_PATH):
        try:
            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except IOError as e:
            print(f"[!] Error reading template file at {TEMPLATE_PATH}: {e}")
            return _get_fallback_template()
    else:
        # Detailed warning helps users debug installation issues
        print(f"[!] Warning: Template not found at {TEMPLATE_PATH}. Using internal fallback.")
        return _get_fallback_template()
def _get_fallback_template():
    """
    Provides a minimal flake.nix structure in case the external template is missing.
    """
    return '''{
  description = "Auto-generated flake by auto_flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # <<NIX_AUTO_INPUTS_START>>
    # <<NIX_AUTO_INPUTS_END>>
  };

  outputs = { self, nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          # <<NIX_AUTO_GEN_START>>
          # <<NIX_AUTO_GEN_END>>
        ];

        shellHook = \'\'
          echo "❄️ Welcome to your auto_flake environment!"
        \'\';
      };
    };
}
'''
