# CodeMap for WiX Creator

Last Updated: 2025-08-04

## Table of Contents

| Section | Line |
|---------|------|
| Overview | 7 |
| Architecture | 15 |
| Key Features | 26 |
| File Structure | 35 |
| Class/Function Breakdown | 45 |
| Configuration Management | 265 |
| Command Line Interface | 288 |

## Overview

WiX Creator is a Python 3 command-line tool that generates WiX v6.0 installer projects for Windows applications. The entire application is self-contained in a single file (`wix_creator.py`) with no external dependencies beyond the Python standard library.

**Version**: 1.0.5  
**Author**: Leland Green  
**License**: MIT

## Architecture

The application follows a simple single-file architecture with these patterns:

1. **Single-file design**: All functionality contained in `wix_creator.py`
2. **Configuration persistence**: Settings stored in JSON files
3. **XML generation**: Uses Python's built-in XML libraries
4. **Interactive CLI**: Command-line interface with prompts
5. **Recursive directory processing**: Scans and includes all application files

## Key Features

- Generates WiX v6.0 compatible installer projects
- Interactive configuration with saved settings
- Support for UI customization (banner, dialog, icons)
- Desktop and Start Menu shortcuts
- Per-user and per-machine installations
- Environment PATH modification
- File associations
- RTF license generation

## File Structure

```
wix_creator/
├── wix_creator.py          # Main application file (1111 lines)
├── CLAUDE.md              # AI assistant instructions
├── ReadMe.md              # Project documentation
├── requirements.txt       # Python dependencies (empty - stdlib only)
└── Docs/
    └── CodeMap.md         # This file
```

## Class/Function Breakdown

### Main Entry Point
| Function | Line | Description |
|----------|------|-------------|
| `main()` | 1048-1110 | Entry point, handles CLI arguments and orchestrates workflow |

### License Generation
| Function | Line | Description |
|----------|------|-------------|
| `generate_license_rtf()` | 33-113 | Generates standard commercial license in RTF format |

### Argument Parsing
| Function | Line | Description |
|----------|------|-------------|
| `parse_arguments()` | 116-122 | Parses command line arguments (initial version) |
| `parse_arguments()` | 1027-1045 | Enhanced version with examples and help text |

### Configuration Management
| Function | Line | Description |
|----------|------|-------------|
| `save_settings()` | 125-143 | Saves project settings to JSON files |
| `load_settings()` | 144-174 | Loads settings from JSON files |
| `prompt_for_ui_options()` | 176-315 | Interactive prompts for configuration |

### Directory Processing
| Function | Line | Description |
|----------|------|-------------|
| `scan_directory()` | 318-343 | Recursively scans directory structure |

### WiX Project Generation
| Function | Line | Description |
|----------|------|-------------|
| `create_wix_project()` | 346-361 | Orchestrates project file creation |
| `create_wxs_file()` | 363-906 | Generates main WiX source XML file |
| `create_wixproj_file()` | 908-960 | Generates MSBuild project file |
| `create_readme_file()` | 962-1025 | Creates README with build instructions |

### Key Components in create_wxs_file()

| Component | Lines | Description |
|-----------|-------|-------------|
| Package setup | 365-388 | Creates root WiX elements and package configuration |
| UI configuration | 389-475 | Sets up UI elements, images, and properties |
| Directory structure | 486-525 | Defines installation directories |
| File processing | 526-677 | Adds files and identifies main executable |
| Icon handling | 679-711 | Processes and adds icon files |
| Shortcuts | 720-779 | Creates desktop and start menu shortcuts |
| PATH modification | 781-804 | Adds environment variable modifications |
| Custom actions | 806-854 | Sets up post-install actions |
| Directory creation | 856-878 | Creates subdirectory structure |
| XML output | 880-906 | Formats and writes XML file |

### XML Namespaces

| Namespace | URI | Variable |
|-----------|-----|----------|
| WiX (default) | http://wixtoolset.org/schemas/v4/wxs | N/A |
| Util | http://wixtoolset.org/schemas/v4/wxs/util | `UTIL_NS` |
| UI | http://wixtoolset.org/schemas/v4/wxs/ui | `UI_NS` |

## Configuration Management

The application manages configuration through JSON files:

1. **Product-specific settings**: `{ProductName}.json`
2. **Last project memory**: `last_project.json`

### Configuration Options

| Option | Type | Description |
|--------|------|-------------|
| `product_name` | string | Name of the product |
| `product_version` | string | Version number (e.g., "1.0.0") |
| `manufacturer` | string | Company/manufacturer name |
| `product_id` | UUID | Unique product identifier |
| `upgrade_code` | UUID | Consistent upgrade identifier |
| `install_dir_name` | string | Installation directory name |
| `ui_level` | string | UI type: "full", "minimal", "none" |
| `generate_license` | boolean | Auto-generate RTF license |
| `license_file` | string | Path to license file |
| `banner_image` | string | Path to banner image (493x58) |
| `dialog_image` | string | Path to dialog image (493x312) |
| `icon_file` | string | Path to icon file |
| `add_desktop_shortcut` | boolean | Create desktop shortcut |
| `add_start_menu_shortcut` | boolean | Create start menu shortcut |
| `shortcut_folder_name` | string | Start menu folder name |
| `shortcut_all_users` | boolean | Create shortcuts for all users |
| `run_after_install` | boolean | Run program after installation |
| `add_to_path` | boolean | Add to system PATH |
| `file_associations` | string | Comma-separated file extensions |

## Command Line Interface

### Usage
```bash
python3 wix_creator.py [PUBLISH_DIR] [-o OUTPUT_DIR]
```

### Arguments
- `PUBLISH_DIR` (optional): Directory containing files to include in installer
- `-o, --output-dir`: Output directory for installer project (default: "Installer")

### Examples
```bash
# Load settings from last project
python3 wix_creator.py

# Create new project
python3 wix_creator.py ../MyApp/bin/Release/net8.0/publish

# Specify output directory
python3 wix_creator.py ./publish -o MyInstaller
```

## Recent Changes (2025)

Based on git history, recent updates include:

- **v1.0.5**: Corrected dialog image handling
- **v1.0.4**: Fixed shortcut target references
- **v1.0.3**: Fixed license display and icon issues
- **v1.0.2**: Added RTF license generation
- Multiple fixes for WiX v4 compatibility
- Namespace handling improvements
- UI element structure corrections