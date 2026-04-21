{
  description = "A development environment managed by auto_flake";

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

        shellHook = ''
          echo "❄️ Welcome to your custom Nix environment!"
        '';
      };
    };
}