## wix_creator.py 
This script is designed to create a WiX installer for applications. It automates the process of generating a WiX XML file.

### Features
- **Generates a Wix XML** file based on the provided configuration.
- **Saves the XML** file to a specified output directory.
- **Creates a project file** for each Wix project. 
- **Automatically reloads settings** from a configuration file, based on `<ProjectName>`.
- **Automatic project wizard:** Guides you through essential WiX installer options with interactive prompts or loads defaults from prior builds.
- **Configuration management:** Saves and loads all installer settings (`<ProjectName>.json` &/or `last_project.json`) for reproducible, incremental editing across builds.
- **Directory scanning:** Recursively scans your application's output directory to automatically include all files and folder structure in the installer.
- **Customizable UI:** Prompts for standard WiX User Interface settings, such as EULA/license text (supports generating an RTF license file), banner and dialog images, install scope (per-machine/per-user), install location, and more.
- **Outputs all essential WiX project files:**
  - `.wxs` file (WiX XML definition for the installer)
  - `.wixproj` MSBuild project file to support `dotnet build`
  - `README.txt` (optional, with per-project setup instructions)
  - `<ProductName>_License.rtf` (license file for the installer UI)
- **Command-line operation:** Supports full CLI usage with options for:
  - Specifying configuration file (`--config`)
  - Defining output directory (`--output`)
  - Running with minimal prompts if a config file is available
- **Efficient rebuilds:** Retains and reloads previous project settings, supporting rapid rebuilds by recalling the last used options.
- **Full compatibility with WiX v6 (.NET integration):** Output projects are ready for building with WiX 6.0 and `dotnet build` workflow.
- **License/EULA support:** Prompts for and generates the required `.rtf` license file for the installer UI.
- **Custom actions and extensions:** Adds references to necessary WiX UI and Util extensions automatically to avoid build errors.
- **Multi-platform scripting:** Fully functional on Windows 10/11 with PowerShell automation for WiX installation if needed.
- **Help and usage hints:** Includes detailed in-script usage guidance and shell tips for efficient iterative builds.

## Requirements

- Python 3.7+ (for running `wix_creator.py`) [https://www.python.org/downloads/](https://www.python.org/downloads/)
- WiX
- [WiX Toolset v6.0.0.6149](https://wixtoolset.org/)
- [WixToolset.BuildTools](https://www.nuget.org/packages/WixToolset.BuildTools) NuGet package for .NET MSBuild-based builds
- _From **this** repository_, you only need the `wix_creator.py` script. 

## Quick Start
Install WiX (if needed). 
```powershell
dotnet tool install --global wix --version 6.0.1
```

Then, clone this repository or simply download the `wix_creator.py` script. That's all you need to get started.

To build the resulting installer, you will need the following:

### WixToolset.BuildTools
  To build using dotnet build, you need this installed in your project. You can install it with nuget or with:
```powershell
dotnet add package WixToolset.BuildTools --version 4.* .\MeshForge.csproj
```

### WiX Toolset v6 

Use your preferred method to install WiX Toolset v6.0.0.6149, which is required for building the installer. Here are some options:

**1. Using Winget** (Windows 10/11)  
```powershell
winget install --id WiX.Toolset --version 6.0.0.6149
```

**2. Using Chocolatey**  
```powershell
choco install wix.toolset --version=6.0.0.6149 -y
```

**3. Manual download and silent install**  
```powershell
$version = '6.0.0.6149'
$url     = "https://github.com/wixtoolset/wix/releases/download/v$version/wix-$version.exe"
$installer = Join-Path $env:TEMP "wix-$version.exe"
Invoke-WebRequest -Uri $url -OutFile $installer
Start-Process -FilePath $installer -ArgumentList '/quiet','/norestart' -Wait
Remove-Item $installer
```

## Usage

If you run the script without parameters, it will automatically look for a `last_project.json` file in the same directory. If found, the values are used as defaults for othe prompt. This is useful when you want to change something from the previous build. You can also specify a different output directory using the `-o` or `--output` option.

If you run the script with at least one parameter, it will prompt for the project name. If it finds `<Project name>.json`, it loads that and uses the defaults for everything, meaning you're finished. (And can't change settings this run.)

***Shell Pro Tip:*** 

* Hit `↑` to recall your `python wix_creator.py ...` command and press `<Enter>`.
* Hit `↑` to recall your previous project name and press `<Enter>`
* Proceed to build the installer. 😊 

### Run the script:
```powershell
python wix_creator.py --config config.json --output output_directory
```

### Or: 
From a project directory, copy the script to current directory and run:
```powershell
python wix_creator.py D:\Documents\Code\GitHub\.Net\MeshForge\bin\Release\net8.0-windows\win-x64\publish -o Installer
```

This creates the Wix project in the `.\Installer` folder.

It does this magic by looking for "last_project.json" in the current directory, which is created by the script when it runs. This file is always identical to the last generated "<Product Name>.json" file, so you can use it to quickly rerun the script without needing to specify all parameters again.

Then build the installer using the generated project file:
```powershell
dotnet build .\Installer\MeshForge.wixproj
```

You can also use `wix build` if you prefer:
```powershell
wix build -ext WixToolset.UI.wixext -ext WixToolset.Util.wixext  .\Installer\MeshForge.wxs
```

Both commands automatically include the required UI and Util extensions when using the project file and avoid preprocessor variable errors.
