#!/usr/bin/env python3
"""
WiX Creator - A tool to create WiX v6.0.0 installer projects

This script generates a WiX v6.0.0 installer project from a specified Publish directory.
It prompts for common UI options and supports subdirectories.
"""

import os
import sys
import argparse
import uuid
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Create a WiX v6.0.0 installer project.')
    parser.add_argument('publish_dir', nargs='?', help='Directory containing files to be included in the installer')
    parser.add_argument('--output-dir', '-o', default='Installer',
                        help='Output directory for the installer project (default: Installer)')
    return parser.parse_args()


def save_settings(options):
    """Save settings to a JSON file named after the product name."""
    filename = f"{options['product_name']}.json"

    # Also save as last_project.json to remember the last used project
    last_project_file = "last_project.json"

    try:
        with open(filename, 'w') as f:
            json.dump(options, f, indent=4)

        # Save a copy as the last project
        with open(last_project_file, 'w') as f:
            json.dump(options, f, indent=4)

        print(f"Settings saved to {filename}")
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_settings(product_name=None):
    """
    Load settings from a JSON file.
    If product_name is provided, try to load that specific file.
    Otherwise, try to load the last project file.
    """
    options = {}

    if product_name:
        filename = f"{product_name}.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    options = json.load(f)
                print(f"Loaded settings from {filename}")
                return options
            except Exception as e:
                print(f"Error loading settings from {filename}: {e}")

    # Try to load the last project if no specific product name was provided or if loading failed
    last_project_file = "last_project.json"
    if os.path.exists(last_project_file):
        try:
            with open(last_project_file, 'r') as f:
                options = json.load(f)
            print(f"Loaded settings from last project")
            return options
        except Exception as e:
            print(f"Error loading last project settings: {e}")

    return options

def prompt_for_ui_options(defaults=None):
    """Prompt the user for common UI options."""
    if defaults is None:
        defaults = {}

    options = {}

    # Product information
    default_product_name = defaults.get('product_name', '')
    product_name_prompt = f"Product Name [{default_product_name}]: " if default_product_name else "Product Name: "
    options['product_name'] = input(product_name_prompt) or default_product_name

    # If we have a product name, try to load settings for it
    if options['product_name'] and not defaults:
        loaded_settings = load_settings(options['product_name'])
        if loaded_settings:
            return loaded_settings

    default_product_version = defaults.get('product_version', '')
    product_version_prompt = f"Product Version (e.g., 1.0.0) [{default_product_version}]: " if default_product_version else "Product Version (e.g., 1.0.0): "
    options['product_version'] = input(product_version_prompt) or default_product_version

    default_manufacturer = defaults.get('manufacturer', '')
    manufacturer_prompt = f"Manufacturer [{default_manufacturer}]: " if default_manufacturer else "Manufacturer: "
    options['manufacturer'] = input(manufacturer_prompt) or default_manufacturer

    # Generate a new product ID (UUID) if not provided in defaults
    options['product_id'] = defaults.get('product_id', str(uuid.uuid4()))

    # Upgrade code - this should remain the same across versions
    default_upgrade_code = defaults.get('upgrade_code', '')
    upgrade_code_prompt = f"Upgrade Code (leave blank to use existing) [{default_upgrade_code}]: " if default_upgrade_code else "Upgrade Code (leave blank to generate a new one): "
    upgrade_code_input = input(upgrade_code_prompt)
    options['upgrade_code'] = upgrade_code_input or default_upgrade_code or str(uuid.uuid4())

    # Installation options
    default_install_dir = defaults.get('install_dir_name', options['product_name'])
    install_dir_prompt = f"Installation Directory Name [{default_install_dir}]: "
    options['install_dir_name'] = input(install_dir_prompt) or default_install_dir

    # UI options
    default_ui_level = defaults.get('ui_level', 'full')
    ui_prompt = f"Include UI? (full/minimal/none) [{default_ui_level}]: "
    ui_options = input(ui_prompt).lower() or default_ui_level
    options['ui_level'] = ui_options

    if ui_options != "none":
        default_license = defaults.get('license_file', '')
        license_prompt = f"License File Path (optional) [{default_license}]: " if default_license else "License File Path (optional): "
        options['license_file'] = input(license_prompt) or default_license

        default_banner = defaults.get('banner_image', '')
        banner_prompt = f"Banner Image Path (optional) [{default_banner}]: " if default_banner else "Banner Image Path (optional): "
        options['banner_image'] = input(banner_prompt) or default_banner

        default_dialog = defaults.get('dialog_image', '')
        dialog_prompt = f"Dialog Image Path (optional) [{default_dialog}]: " if default_dialog else "Dialog Image Path (optional): "
        options['dialog_image'] = input(dialog_prompt) or default_dialog

        default_icon = defaults.get('icon_file', '')
        icon_prompt = f"Icon File Path (optional) [{default_icon}]: " if default_icon else "Icon File Path (optional): "
        options['icon_file'] = input(icon_prompt) or default_icon

    # Additional options
    default_desktop = defaults.get('add_desktop_shortcut', True)
    desktop_default = "y" if default_desktop else "n"
    desktop_prompt = f"Add Desktop Shortcut? (y/n) [{desktop_default}]: "
    desktop_input = input(desktop_prompt).lower()
    if desktop_input:
        options['add_desktop_shortcut'] = desktop_input != "n"
    else:
        options['add_desktop_shortcut'] = default_desktop

    default_start_menu = defaults.get('add_start_menu_shortcut', True)
    start_menu_default = "y" if default_start_menu else "n"
    start_menu_prompt = f"Add Start Menu Shortcut? (y/n) [{start_menu_default}]: "
    start_menu_input = input(start_menu_prompt).lower()
    if start_menu_input:
        options['add_start_menu_shortcut'] = start_menu_input != "n"
    else:
        options['add_start_menu_shortcut'] = default_start_menu

    # Shortcut folder name customization
    if options['add_start_menu_shortcut']:
        default_shortcut_folder = defaults.get('shortcut_folder_name', options['manufacturer'])
        shortcut_folder_prompt = f"Start Menu Shortcut Folder Name [{default_shortcut_folder}]: "
        options['shortcut_folder_name'] = input(shortcut_folder_prompt) or default_shortcut_folder

    # Shortcut scope (all users vs. current user)
    default_all_users = defaults.get('shortcut_all_users', False)
    all_users_default = "y" if default_all_users else "n"
    all_users_prompt = f"Create shortcuts for all users? (y/n) [{all_users_default}]: "
    all_users_input = input(all_users_prompt).lower()
    if all_users_input:
        options['shortcut_all_users'] = all_users_input == "y"
    else:
        options['shortcut_all_users'] = default_all_users

    # Run after setup option
    default_run_after = defaults.get('run_after_install', False)
    run_after_default = "y" if default_run_after else "n"
    run_after_prompt = f"Run program after installation? (y/n) [{run_after_default}]: "
    run_after_input = input(run_after_prompt).lower()
    if run_after_input:
        options['run_after_install'] = run_after_input == "y"
    else:
        options['run_after_install'] = default_run_after

    # Add to PATH option
    default_add_path = defaults.get('add_to_path', False)
    add_path_default = "y" if default_add_path else "n"
    add_path_prompt = f"Add application directory to PATH? (y/n) [{add_path_default}]: "
    add_path_input = input(add_path_prompt).lower()
    if add_path_input:
        options['add_to_path'] = add_path_input == "y"
    else:
        options['add_to_path'] = default_add_path

    # File associations
    default_file_assoc = defaults.get('file_associations', '')
    file_assoc_prompt = f"File extensions to associate (comma-separated, e.g., .txt,.doc) [{default_file_assoc}]: "
    file_assoc_input = input(file_assoc_prompt)
    options['file_associations'] = file_assoc_input or default_file_assoc

    return options


def scan_directory(directory):
    """
    Scan the directory and its subdirectories to collect file information.

    Returns:
        dict: A dictionary with directory paths as keys and lists of files as values
    """
    file_structure = {}

    for root, dirs, files in os.walk(directory):
        rel_path = os.path.relpath(root, directory)
        if rel_path == '.':
            rel_path = ''

        file_structure[rel_path] = []

        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_structure[rel_path].append({
                'name': file,
                'path': file_path,
                'size': file_size
            })

    return file_structure


def create_wix_project(publish_dir, output_dir, options, file_structure):
    """Create WiX v6.0.0 project files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create main .wxs file
    create_wxs_file(output_dir, options, file_structure)

    # Create .wixproj file
    create_wixproj_file(output_dir, options)

    # Create README file with build instructions
    create_readme_file(output_dir)

    print(f"WiX v6.0.0 installer project created in {output_dir}")


def create_wxs_file(output_dir, options, file_structure):
    """Create the main .wxs file for the WiX project."""
    wxs_path = os.path.join(output_dir, f"{options['product_name']}.wxs")

    # Create the root element
    wix = ET.Element("Wix", {
        "xmlns": "http://wixtoolset.org/schemas/v4/wxs",
        "xmlns:ui": "http://wixtoolset.org/schemas/v4/wxs/ui",
        "xmlns:util": "http://wixtoolset.org/schemas/v4/wxs/util"
    })

    # Create the package element
    package = ET.SubElement(wix, "Package", 
                           Name=options['product_name'],
                           Manufacturer=options['manufacturer'],
                           Version=options['product_version'],
                           UpgradeCode=options['upgrade_code'])

    # Add UI properties for installation options
    if options['ui_level'] in ['full', 'minimal']:
        # Property for desktop shortcut
        desktop_shortcut_default = "1" if options.get('add_desktop_shortcut', True) else "0"
        ET.SubElement(package, "Property", Id="INSTALLDESKTOPSHORTCUT", Value=desktop_shortcut_default)

        # Property for start menu shortcut
        start_menu_default = "1" if options.get('add_start_menu_shortcut', True) else "0"
        ET.SubElement(package, "Property", Id="INSTALLSTARTMENUSHORTCUT", Value=start_menu_default)

        # Property for running after installation
        run_after_default = "1" if options.get('run_after_install', False) else "0"
        ET.SubElement(package, "Property", Id="LAUNCHAPPONEXIT", Value=run_after_default)

        # Property for adding to PATH
        add_path_default = "1" if options.get('add_to_path', False) else "0"
        ET.SubElement(package, "Property", Id="ADDTOPATH", Value=add_path_default)

        # Add WIXUI_INSTALLDIR property for InstallDirDlg
        ET.SubElement(package, "Property", Id="WIXUI_INSTALLDIR", Value="INSTALLDIR")

        # Add UI reference as a direct child of the Package element
        ui_element = ET.SubElement(package, "UI")
        ET.SubElement(ui_element, "UIRef", Id="WixUI_InstallDir")

        # Add custom UI dialog for installation options
        ui_element = ET.SubElement(package, "UI")
        dialog = ET.SubElement(ui_element, "Dialog", 
                     Id="InstallOptionsDialog", 
                     Width="370", 
                     Height="270", 
                     Title="Installation Options")

        # Add checkboxes for options
        ET.SubElement(dialog, "Control", 
                     Id="DesktopShortcutCheckbox", 
                     Type="CheckBox", 
                     X="20", 
                     Y="60", 
                     Width="330", 
                     Height="17", 
                     Property="INSTALLDESKTOPSHORTCUT", 
                     CheckBoxValue="1", 
                     TabSkip="no",
                     Text="Create a shortcut on the desktop")

        ET.SubElement(dialog, "Control", 
                     Id="StartMenuShortcutCheckbox", 
                     Type="CheckBox", 
                     X="20", 
                     Y="80", 
                     Width="330", 
                     Height="17", 
                     Property="INSTALLSTARTMENUSHORTCUT", 
                     CheckBoxValue="1", 
                     Text="Create a shortcut in the Start Menu")

        ET.SubElement(dialog, "Control", 
                     Id="AddToPathCheckbox", 
                     Type="CheckBox", 
                     X="20", 
                     Y="100", 
                     Width="330", 
                     Height="17", 
                     Property="ADDTOPATH", 
                     CheckBoxValue="1", 
                     Text="Add application directory to PATH")

        ET.SubElement(dialog, "Control", 
                     Id="LaunchAppCheckbox", 
                     Type="CheckBox", 
                     X="20", 
                     Y="120", 
                     Width="330", 
                     Height="17", 
                     Property="LAUNCHAPPONEXIT", 
                     CheckBoxValue="1", 
                     Text="Launch application after installation")

        # Add navigation buttons
        ET.SubElement(dialog, "Control", 
                     Id="Back", 
                     Type="PushButton", 
                     X="180", 
                     Y="243", 
                     Width="56", 
                     Height="17", 
                     Text="Back")

        ET.SubElement(dialog, "Control", 
                     Id="Next", 
                     Type="PushButton", 
                     X="236", 
                     Y="243", 
                     Width="56", 
                     Height="17", 
                     Default="yes", 
                     Text="Next")

        ET.SubElement(dialog, "Control", 
                     Id="Cancel", 
                     Type="PushButton", 
                     X="304", 
                     Y="243", 
                     Width="56", 
                     Height="17", 
                     Cancel="yes", 
                     Text="Cancel")

        # Insert the dialog in the UI sequence
        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallOptionsDialog", 
                     Control="Back", 
                     Event="NewDialog", 
                     Value="LicenseAgreementDlg")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallOptionsDialog", 
                     Control="Next", 
                     Event="NewDialog", 
                     Value="InstallDirDlg")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="LicenseAgreementDlg", 
                     Control="Next", 
                     Event="NewDialog", 
                     Value="InstallOptionsDialog")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="Back", 
                     Event="NewDialog", 
                     Value="InstallOptionsDialog")

        # Add Cancel button event
        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallOptionsDialog", 
                     Control="Cancel", 
                     Event="SpawnDialog", 
                     Value="CancelDlg")

        # Add events for InstallDirDlg buttons to fix ICE17 errors
        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="Next", 
                     Event="SetTargetPath", 
                     Value="[WIXUI_INSTALLDIR]")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="Next", 
                     Event="DoAction", 
                     Value="ui:WixUIValidatePath",
                     Condition="NOT WIXUI_DONTVALIDATEPATH")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="Next", 
                     Event="SpawnDialog", 
                     Value="InvalidDirDlg",
                     Condition="WIXUI_INSTALLDIR_VALID<>\"1\"")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="Next", 
                     Event="NewDialog", 
                     Value="VerifyReadyDlg",
                     Condition="WIXUI_INSTALLDIR_VALID=\"1\"")

        ET.SubElement(ui_element, "Publish", 
                     Dialog="InstallDirDlg", 
                     Control="ChangeFolder", 
                     Event="SpawnDialog", 
                     Value="BrowseDlg")

    # Create main component group
    components = ET.SubElement(package, "ComponentGroup", Id="ProductComponents")

    # Create a Feature element that references the ComponentGroup
    feature = ET.SubElement(package, "Feature", 
                           Id="ProductFeature", 
                           Title=options['product_name'],
                           Level="1")
    ET.SubElement(feature, "ComponentGroupRef", Id="ProductComponents")

    # Create directory structure
    directories = ET.SubElement(package, "StandardDirectory", Id="ProgramFiles6432Folder")
    manufacturer_dir = ET.SubElement(directories, "Directory", 
                                    Id="ManufacturerFolder", 
                                    Name=options['manufacturer'])
    product_dir = ET.SubElement(manufacturer_dir, "Directory", 
                               Id="INSTALLDIR", 
                               Name=options['install_dir_name'])

    # Add standard directories
    ET.SubElement(package, "StandardDirectory", Id="DesktopFolder")
    program_menu = ET.SubElement(package, "StandardDirectory", Id="ProgramMenuFolder")

    # Create custom shortcut folder if specified
    if options.get('add_start_menu_shortcut') and options.get('shortcut_folder_name'):
        shortcut_folder = ET.SubElement(program_menu, "Directory", 
                                       Id="ShortcutFolder", 
                                       Name=options['shortcut_folder_name'])

        # Add a component to remove the shortcut folder on uninstall
        shortcut_folder_component = ET.SubElement(components, "Component", 
                                                Id="ShortcutFolderComponent", 
                                                Directory="ShortcutFolder",
                                                Guid=str(uuid.uuid4()))

        # Add registry key as KeyPath
        ET.SubElement(shortcut_folder_component, "RegistryValue",
                     Root="HKCU",
                     Key=f"Software\\{options['manufacturer']}\\{options['product_name']}",
                     Name="installed_shortcut_folder",
                     Type="integer",
                     Value="1",
                     KeyPath="yes")

        # Add RemoveFile entry for the shortcut folder
        ET.SubElement(shortcut_folder_component, "RemoveFolder",
                     Id="RemoveShortcutFolder",
                     On="uninstall")

    # Add files to the installer
    file_id_counter = 1
    component_id_counter = 1
    main_exe_id = None  # Store the ID of the main executable for later use

    for dir_path, files in file_structure.items():
        if dir_path:
            # Create subdirectory
            current_dir = product_dir
            for part in dir_path.split(os.sep):
                # Ensure directory ID only contains legal characters and starts with a letter or underscore
                # Legal characters are A-Z, a-z, digits, underscores, and periods
                # Replace any other characters with underscores
                sanitized_part = ''.join(c if c.isalnum() or c == '_' or c == '.' else '_' for c in part)
                dir_id = f"Dir_{sanitized_part}"
                current_dir = ET.SubElement(current_dir, "Directory", Id=dir_id, Name=part)
        else:
            current_dir = product_dir

        for file_info in files:
            component_id = f"Component_{component_id_counter}"
            component_id_counter += 1

            # Set appropriate scope for the component
            # Check if this component will have shortcuts (and thus registry keys as KeyPath)
            will_have_shortcuts = file_info['name'].endswith('.exe') and (options.get('add_desktop_shortcut', False) or options.get('add_start_menu_shortcut', False))

            # Generate a GUID for components that will have registry keys as KeyPath
            component_guid = str(uuid.uuid4()) if will_have_shortcuts else "*"

            if options.get('shortcut_all_users', False):
                component = ET.SubElement(components, "Component", 
                                         Id=component_id, 
                                         Directory=current_dir.get("Id"),
                                         Guid=component_guid,
                                         Scope="perMachine")
            else:
                component = ET.SubElement(components, "Component", 
                                         Id=component_id, 
                                         Directory=current_dir.get("Id"),
                                         Guid=component_guid)

            file_id = f"File_{file_id_counter}"
            file_id_counter += 1

            file_element = ET.SubElement(component, "File", 
                                        Id=file_id,
                                        Source=file_info['path'],
                                        Name=file_info['name'])

            # Add shortcut for executable files
            if file_info['name'].endswith('.exe'):
                # Store the first executable as the main one
                if main_exe_id is None:
                    main_exe_id = file_id

                # Add registry key as KeyPath for components with shortcuts
                if options.get('add_desktop_shortcut', False) or options.get('add_start_menu_shortcut', False):
                    # Add registry key as KeyPath
                    ET.SubElement(component, "RegistryValue",
                                 Root="HKCU",
                                 Key=f"Software\\{options['manufacturer']}\\{options['product_name']}",
                                 Name=f"installed_{file_id}",
                                 Type="integer",
                                 Value="1",
                                 KeyPath="yes")

                # Desktop shortcut - add based on options
                if options.get('add_desktop_shortcut', False):
                    ET.SubElement(component, "Shortcut",
                                 Id=f"DesktopShortcut_{file_id}",
                                 Directory="DesktopFolder",
                                 Name=options['product_name'],
                                 WorkingDirectory="INSTALLDIR",
                                 IconIndex="0",
                                 Advertise="no")

                # Start menu shortcut - add based on options
                # Determine the target directory for the shortcut
                shortcut_dir = "ShortcutFolder" if options.get('shortcut_folder_name') else "ProgramMenuFolder"

                if options.get('add_start_menu_shortcut', False):
                    ET.SubElement(component, "Shortcut",
                                 Id=f"StartMenuShortcut_{file_id}",
                                 Directory=shortcut_dir,
                                 Name=options['product_name'],
                                 WorkingDirectory="INSTALLDIR",
                                 IconIndex="0",
                                 Advertise="no")

                # Add file associations if specified
                if options.get('file_associations'):
                    for ext in options['file_associations'].split(','):
                        ext = ext.strip()
                        if ext:
                            # Create a unique ID for this extension
                            ext_id = ext.replace('.', '').upper()

                            # Add ProgId for this extension
                            prog_id = ET.SubElement(component, "ProgId", 
                                                  Id=f"{options['product_name']}{ext_id}",
                                                  Description=f"{options['product_name']} File",
                                                  Icon=file_id)

                            # Associate extension with ProgId
                            ET.SubElement(prog_id, "Extension", Id=ext_id, ContentType="application/octet-stream")

            # Add to PATH if specified
            if dir_path == '':  # Only add the main directory to PATH
                if options.get('add_to_path', False):
                    ET.SubElement(component, "Environment", 
                                 Id="PATH", 
                                 Name="PATH", 
                                 Value="[INSTALLDIR]", 
                                 Permanent="no", 
                                 Part="last", 
                                 Action="set", 
                                 System="yes")

    # Add icon if provided
    if options.get('icon_file'):
        ET.SubElement(package, "Icon", 
                     Id="ProductIcon", 
                     SourceFile=options['icon_file'])
        ET.SubElement(package, "Property", 
                     Id="ARPPRODUCTICON", 
                     Value="ProductIcon")

    # Add custom actions for UI mode
    if options['ui_level'] in ['full', 'minimal'] and main_exe_id and options.get('run_after_install', False):
        # Create properties to store paths
        ET.SubElement(package, "Property", 
                     Id="WixShellExecTarget", 
                     Value=f"[#[{main_exe_id}]]")

        # For UI mode, we'll use properties to control behavior
        # The actual shortcuts and environment variables will be added in the components loop
        # based on the file type and directory path

        # Add the custom action that will run the executable
        ET.SubElement(package, "CustomAction", 
                     Id="LaunchApplication", 
                     BinaryRef="WixCA", 
                     DllEntry="WixShellExec",
                     Impersonate="yes")

        # Add the InstallExecuteSequence element to schedule the custom action
        install_exec_seq = ET.SubElement(package, "InstallExecuteSequence")

        # Use the UI property to determine whether to run the application
        ET.SubElement(install_exec_seq, "Custom", 
                     Action="LaunchApplication", 
                     After="InstallFinalize",
                     Condition="NOT Installed AND LAUNCHAPPONEXIT=1")

    # For non-UI mode, add custom action if run_after_install is enabled
    elif main_exe_id and options.get('run_after_install', False):
        # Create a property to store the path to the executable
        ET.SubElement(package, "Property", 
                     Id="WixShellExecTarget", 
                     Value=f"[#[{main_exe_id}]]")

        # Add the custom action that will run the executable
        ET.SubElement(package, "CustomAction", 
                     Id="LaunchApplication", 
                     BinaryRef="WixCA", 
                     DllEntry="WixShellExec",
                     Impersonate="yes")

        # Add the InstallExecuteSequence element to schedule the custom action
        install_exec_seq = ET.SubElement(package, "InstallExecuteSequence")

        # Use the hardcoded setting if no UI
        ET.SubElement(install_exec_seq, "Custom", 
                     Action="LaunchApplication", 
                     After="InstallFinalize",
                     Condition="NOT Installed")

    # Write the XML to file with proper formatting
    rough_string = ET.tostring(wix, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(wxs_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))


def create_wixproj_file(output_dir, options):
    """Create the .wixproj file for the WiX project."""
    wixproj_path = os.path.join(output_dir, f"{options['product_name']}.wixproj")

    # Create the root element
    project = ET.Element("Project", 
                        DefaultTargets="Build",
                        xmlns="http://schemas.microsoft.com/developer/msbuild/2003",
                        ToolsVersion="4.0")

    # Add property group
    property_group = ET.SubElement(project, "PropertyGroup")
    ET.SubElement(property_group, "Configuration").text = "Debug"
    ET.SubElement(property_group, "Platform").text = "x86"
    ET.SubElement(property_group, "ProductVersion").text = options['product_version']
    ET.SubElement(property_group, "SchemaVersion").text = "2.0"
    ET.SubElement(property_group, "OutputName").text = options['product_name']
    ET.SubElement(property_group, "OutputType").text = "Package"

    # Add item group for project references
    item_group = ET.SubElement(project, "ItemGroup")
    compile = ET.SubElement(item_group, "Compile", Include=f"{options['product_name']}.wxs")

    # Add item group for WiX extensions
    extensions_group = ET.SubElement(project, "ItemGroup")
    ET.SubElement(extensions_group, "WixExtension", Include="WixToolset.UI.wixext")
    ET.SubElement(extensions_group, "WixExtension", Include="WixToolset.Util.wixext")

    # Add import for WiX targets
    ET.SubElement(project, "Import", Project="$(WixTargetsPath)", Condition="Exists('$(WixTargetsPath)')")

    # Write the XML to file with proper formatting
    rough_string = ET.tostring(project, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    with open(wixproj_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))


def create_readme_file(output_dir):
    """Create a README file with build instructions."""
    readme_path = os.path.join(output_dir, "README.md")

    readme_content = """# WiX v6.0.0 Installer Project

This directory contains a WiX v6.0.0 installer project generated by wix_creator.py.

## Prerequisites

- WiX Toolset v6.0.0 or later (https://wixtoolset.org/)
- .NET 6.0 or later

## Building the Installer

### Option 1: Using dotnet build
1. Open a command prompt or PowerShell window.
2. Navigate to this directory.
3. Run the following command:

```
dotnet build
```

The installer (.msi file) will be created in the bin/Debug or bin/Release directory.

### Option 2: Using wix build directly
1. Open a command prompt or PowerShell window.
2. Navigate to this directory.
3. Run the following command:

```
wix build -ext WixToolset.UI.wixext -ext WixToolset.Util.wixext YourProductName.wxs
```

Replace `YourProductName` with the actual name of your product. This command includes the necessary UI and Util extensions required for the installer.

## Customizing the Installer

You can modify the .wxs file to customize the installer further. Refer to the WiX documentation at https://wixtoolset.org/docs/ for more information.
"""

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def main():
    """Main function."""
    args = parse_arguments()

    # Load defaults from last project if available
    defaults = {}
    if not args.publish_dir:
        # If no publish directory is provided, try to load the last project
        defaults = load_settings()
        if not defaults:
            print("No previous project found. Please provide a publish directory.")
            sys.exit(1)

        # Ask user if they want to use the last project
        last_project_name = defaults.get('product_name', 'Unknown')
        use_last = input(f"Use last project '{last_project_name}'? (y/n, default: y): ").lower() != 'n'

        if not use_last:
            print("Please run the script again with a publish directory.")
            sys.exit(0)

        # Use the publish directory from the last project if available
        if 'publish_dir' in defaults:
            args.publish_dir = defaults['publish_dir']
        else:
            print("No publish directory found in the last project. Please provide a publish directory.")
            sys.exit(1)

    # Validate publish directory
    publish_dir = os.path.abspath(args.publish_dir)
    if not os.path.isdir(publish_dir):
        print(f"Error: Publish directory '{publish_dir}' does not exist or is not a directory.")
        sys.exit(1)

    # Prepare output directory
    output_dir = os.path.abspath(args.output_dir)

    # Prompt for UI options with defaults
    options = prompt_for_ui_options(defaults)

    # Store the publish directory in the options for future use
    options['publish_dir'] = publish_dir

    # Save the settings
    save_settings(options)

    # Scan the publish directory
    print(f"Scanning directory: {publish_dir}")
    file_structure = scan_directory(publish_dir)

    # Create WiX project
    create_wix_project(publish_dir, output_dir, options, file_structure)


if __name__ == "__main__":
    main()
