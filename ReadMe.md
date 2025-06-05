## wix_creator.py 
This script is designed to create a WiX installer for applications. It automates the process of generating a WiX XML file.

### Features
- Generates a Wix XML file based on the provided configuration.
- Saves the XML file to a specified output directory.
- Creates a project file for each Wix project. 
- It automatically reloads settings from a configuration file, based on "Product Name".

## Requirements:
_From **this** repository_, you only need the `wix_creator.py` script. 

To build the resulting installer, you will need the following:

### WixToolset.BuildTools
  You need this installed in every project you want to use this with. You can install it using the following command:
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

### Run the script:
```powershell
python wix_creator.py --config config.json --output output_directory
```

### Or: 
From a project directory, relative to the script:
```powershell
python ..\..\wix_creator\wix_creator.py D:\Documents\Code\GitHub\.Net\MeshForge\bin\Release\net8.0-windows\win-x64\publish -o Installer
```
If you run the script from the project directory, it will automatically look for a `<Product Name>.json` file in the same directory. Then, if you run it without parameters, it will use your previous input as all defaults. This is useful for repeat builds of the same project. You can also specify a different output directory using the `-o` or `--output` option. 

It does this magic by looking for "last_project.json" in the current directory, which is created by the script when it runs. This file is always identical to the last generated "<Product Name>.json" file, so you can use it to quickly rerun the script without needing to specify all parameters again.

Then build the installer using the generated WiX XML file:
```powershell
wix build -ext WixToolset.UI.wixext -ext WixToolset.Util.wixext .\Installer\MeshForge.wxs
```

This command includes the necessary UI and Util extensions required for the installer. Without these extensions, you may encounter errors related to unhandled extension elements or illegal identifiers with namespace prefixes.
