## wix_creator.py 
This script is designed to create a WiX installer for applications. It automates the process of generating a WiX XML file.

### Features
- Generates a Wix XML file based on the provided configuration.
- Saves the XML file to a specified output directory.
- Creates a project file for each Wix project. 
- It automatically reloads settings from a configuration file, based on "Product Name".

### Requirements:

#### WixToolset.BuildTools
You need this installed in every project you want to use this with. You can install it using the following command:
```powershell
dotnet add package WixToolset.BuildTools --version 4.* .\MeshForge.csproj
```

#### WiX Toolset v6 

Use your preferred method to install WiX Toolset v6.0.0.6149, which is required for building the installer. Here are some options:

**1. Using Winget** (Windows 10/11)  
    ```powershell
    winget install --id WiX.Toolset --version 6.0.0.6149
    ```

**2. Using Chocolatey**  
    ```powershell
    choco install wix.toolset --version=6.0.0.6149 -y
    ```

**3. Manual download & silent install**  
    ```powershell
    $version = '6.0.0.6149'
    $url     = "https://github.com/wixtoolset/wix/releases/download/v$version/wix-$version.exe"
    $installer = Join-Path $env:TEMP "wix-$version.exe"
    Invoke-WebRequest -Uri $url -OutFile $installer
    Start-Process -FilePath $installer -ArgumentList '/quiet','/norestart' -Wait
    Remove-Item $installer
    ```

### Run the script:
```powershell
python wix_creator.py --config config.json --output output_directory
```

### Or: 
From a project directory, relative to the script:
```powershell
python ..\..\wix_creator\wix_creator.py D:\Documents\Code\GitHub\.Net\MeshForge\bin\Release\net8.0-windows\win-x64\publish -o Installer
```

```powershell
wix build .\Installer\MeshForge.wxs
```