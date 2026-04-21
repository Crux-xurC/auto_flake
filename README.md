
# auto_flake

`auto_flake` is an interactive CLI assistant designed to bridge the gap between traditional package managers and Nix Flakes. It helps you migrate your local environment (starting with **AUR/Arch Linux**) into a reproducible `flake.nix` development shell.

## 🚀 Key Features

- **Phased Migration**: Guided workflow from discovery to analysis and injection.
- **Dynamic Plugin Discovery**: Automatically detects scanners and selection UIs based on file naming conventions.
- **Dependency Analysis**: Beyond just naming, it uses `ldd` and `nix-locate` to map binary dependencies to Nixpkgs.
- **Safe Injection**: Uses marker-based generation to update your `flake.nix` without touching your manual configurations.
- **Traceability**: Generates a `history.md` "receipt" for every migration session, keeping track of where each package came from.

---

---

### ⚠️ Note for Users & Contributors
This is my first time publishing an open-source application. While it works for my personal Arch Linux / Nix setup, please be aware:
- **Use at your own risk**: Always back up your `flake.nix` before running the tool.
- **WIP Logic**: The dependency analysis logic is still in an early/experimental stage.
- **Feedback**: If you find bugs or have suggestions, feel free to open an Issue, but please be constructive and patient. We all start somewhere! ❄️

---

## 📂 Repository Layout

```text
auto_flake/
├── main.py                 # CLI entrypoint and phase orchestration
├── info/
│   ├── flake.tmpl          # Default Nix template (customizable)
│   └── project_data.json   # Persistent state across sessions
└── modules/
    ├── scanners/
    │   ├── aur_list_scanner.py     # AUR discovery via 'pacman -Qm'
    │   └── aur_analyzer.py         # Binary/Shared-lib dependency mapper
    ├── generators/
    │   ├── default_generator.py    # Template loader
    │   ├── replace_generator.py    # Marker-based Nix code injector
    │   └── history_logger.py       # Session history generator
    └── utils/
        ├── plugin_loader.py        # Dynamic module importer
        ├── nix_resolver.py         # nix-locate integration helper
        ├── status_checker.py       # Environment/Phase validator
        ├── data_manager.py         # JSON state handler
        ├── list_bulk.py            # Fast selection UI (Index-based)
        └── list_sequentially.py    # Careful selection UI (Y/N-based)
```

---

## 🛠 Requirements

- **Python 3.10+**
- **Arch Linux** (for the default AUR scanner)
- **nix-index** (Optional but highly recommended)
  - Used for `nix-locate` to find packages by shared libraries.
  - Run `nix-run nixpkgs#nix-index -- nix-index` to initialize.

---

## 🚦 Quick Start

1. **Clone and Run**:
   ```bash
   git clone https://github.com/Crux-xurC/auto_flake.git
   cd auto_flake
   python main.py
   ```

2. **Follow the Prompts**:
   - **Target**: Set your target directory (e.g., `~/dev/xmonad-flake`).
   - **Scanner**: Select `aur` as your manager.
   - **Select**: Choose a selection method (`Bulk` or `Sequentially`).
   - **Apply**: Confirm the analysis and watch your `flake.nix` get updated.

---

## 🧩 Extending auto_flake

You can easily add support for other distributions or package managers.

### 1. Add a New Scanner
Create `modules/scanners/<name>_list_scanner.py`:
- Implement `scan()`: Returns a list of strings (package names).

### 2. Add a New Analyzer
Create `modules/scanners/<name>_analyzer.py`:
- Implement `analyze(package_list)`: Returns a list of dictionaries with mapping data.

### 3. Add a New UI
Create `modules/utils/list_<mode>.py`:
- Implement `select(candidates)`: Returns a filtered list of confirmed packages.
- Define `choice_method = "Description text"` for the CLI menu.

---

## 📝 Managed Markers

`auto_flake` respects your manual edits. It only modifies content between these lines in your `flake.nix`:

```nix
# <<NIX_AUTO_GEN_START>>
# (auto_flake will inject packages here)
# <<NIX_AUTO_GEN_END>>
```

---

## ⚖️ License

This project is currently provided "as is". Please consider adding an MIT or Apache 2.0 license before public release.
