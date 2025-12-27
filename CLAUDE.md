# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python 3 command-line tool that generates WiX v6.0 installer projects for Windows applications. The entire application is contained in a single file: `wix_creator.py`.

## Essential Commands

```bash
# Run the tool
python3 wix_creator.py [PUBLISH_DIR] [-o OUTPUT_DIR]

# Build generated installer
dotnet build ./Installer/ProjectName.wixproj

# Alternative build (if dotnet not available)
wix build -ext WixToolset.UI.wixext -ext WixToolset.Util.wixext ./Installer/ProjectName.wxs
```

## Architecture

The application follows a simple single-file architecture with these key patterns:

1. **Configuration Management**: Settings are persisted in JSON files (`{ProductName}.json` and `last_project.json`)
2. **XML Generation**: Creates WiX XML files using Python's built-in XML libraries
3. **Interactive CLI**: Uses argparse for command-line options and prompts for configuration
4. **Directory Processing**: Recursively scans publish directories to include all application files

## Key Components in wix_creator.py

- **Main entry point**: `main()` function handles CLI arguments and orchestrates the workflow
- **Configuration**: `collect_project_details()` manages interactive prompts and settings
- **XML Generation**: `generate_wix_xml()` creates the WiX source file
- **Project Generation**: `generate_wixproj()` creates the MSBuild project file
- **File Discovery**: `add_directory_structure()` recursively processes application files

## Dependencies

- Python 3 (standard library only - no pip packages)
- WiX Toolset v6.0+ (for building installers)
- .NET 6.0+ (for dotnet build workflow)

## Development Notes

- No unit tests or formal testing framework
- No linting configuration - follow standard Python conventions
- Single-file design makes it easy to understand and modify
- Generates GUIDs for WiX components using Python's uuid module
- Supports both per-user and per-machine installations
- Automatically generates RTF license files when needed