#!/usr/bin/env python3
"""
WiX Creator - A tool to create WiX v4.x installer projects

This script generates a WiX v4.x installer project from a specified Publish directory.
(Works with WiX v6.0.0 and later)
It prompts for common UI options and supports subdirectories.
"""
__author__ = "Leland Green"
__version__ = "1.0.2"
__license__ = "MIT"
__date__ = "2025-06-06"

import os
import sys
import argparse
import uuid
import datetime
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import time

UTIL_NS = "http://wixtoolset.org/schemas/v4/wxs/util"
UI_NS = "http://wixtoolset.org/schemas/v4/wxs/ui"

ET.register_namespace('util', UTIL_NS)
ET.register_namespace('ui', UI_NS)
ET.register_namespace('', "http://wixtoolset.org/schemas/v4/wxs")


def generate_license_rtf(company_name, product_name, output_dir):
    """
    Generate a standard commercial license in RTF format.

    Args:
        company_name (str): The name of the company
        product_name (str): The name of the product
        output_dir (str): Directory to save the license file

    Returns:
        str: Path to the generated license file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate license filename
    license_filename = f"{product_name}_License.rtf"
    license_path = os.path.join(output_dir, license_filename)

    # Get current date for the license
    current_date = time.strftime("%B %d, %Y")

    # RTF header
    rtf_header = r"{\rtf1\ansi\ansicpg1252\deff0\nouicompat\deflang1033{\fonttbl{\f0\fnil\fcharset0 Calibri;}{\f1\fnil\fcharset0 Arial;}}\viewkind4\uc1\pard\sa200\sl276\slmult1"

    # License content with company name and product name
    license_content = f"""
\\f1\\fs28\\b SOFTWARE LICENSE AGREEMENT\\par
\\fs24\\b0 
\\b IMPORTANT - READ CAREFULLY:\\b0  This License Agreement ("Agreement") is a legal agreement between you (either an individual or a single entity) and {company_name} for the software product {product_name} ("SOFTWARE"). By installing, copying, or otherwise using the SOFTWARE, you agree to be bound by the terms of this Agreement. If you do not agree to the terms of this Agreement, do not install or use the SOFTWARE.\\par

\\b 1. GRANT OF LICENSE\\b0 \\par
{company_name} grants you the following rights provided that you comply with all terms and conditions of this Agreement:\\par
a) Installation and Use: You may install and use an unlimited number of copies of the SOFTWARE on your devices for your commercial purposes.\\par
b) Reproduction and Distribution: You may reproduce and distribute an unlimited number of copies of the SOFTWARE; provided that each copy shall be a true and complete copy, including all copyright and trademark notices, and shall be accompanied by a copy of this Agreement.\\par

\\b 2. DESCRIPTION OF OTHER RIGHTS AND LIMITATIONS\\b0 \\par
a) Maintenance of Copyright Notices: You must not remove or alter any copyright notices on any and all copies of the SOFTWARE.\\par
b) Distribution: You may not distribute registered copies of the SOFTWARE to third parties.\\par
c) Prohibition on Reverse Engineering, Decompilation, and Disassembly: You may not reverse engineer, decompile, or disassemble the SOFTWARE, except and only to the extent that such activity is expressly permitted by applicable law notwithstanding this limitation.\\par
d) Rental: You may not rent, lease, or lend the SOFTWARE.\\par
e) Support Services: {company_name} may provide you with support services related to the SOFTWARE ("Support Services"). Any supplemental software code provided to you as part of the Support Services shall be considered part of the SOFTWARE and subject to the terms and conditions of this Agreement.\\par
f) Compliance with Applicable Laws: You must comply with all applicable laws regarding use of the SOFTWARE.\\par

\\b 3. TERMINATION\\b0 \\par
Without prejudice to any other rights, {company_name} may terminate this Agreement if you fail to comply with the terms and conditions of this Agreement. In such event, you must destroy all copies of the SOFTWARE in your possession.\\par

\\b 4. COPYRIGHT\\b0 \\par
All title, including but not limited to copyrights, in and to the SOFTWARE and any copies thereof are owned by {company_name} or its suppliers. All title and intellectual property rights in and to the content which may be accessed through use of the SOFTWARE is the property of the respective content owner and may be protected by applicable copyright or other intellectual property laws and treaties. This Agreement grants you no rights to use such content. All rights not expressly granted are reserved by {company_name}.\\par

\\b 5. NO WARRANTIES\\b0 \\par
{company_name} expressly disclaims any warranty for the SOFTWARE. The SOFTWARE is provided 'As Is' without any express or implied warranty of any kind, including but not limited to any warranties of merchantability, noninfringement, or fitness of a particular purpose. {company_name} does not warrant or assume responsibility for the accuracy or completeness of any information, text, graphics, links or other items contained within the SOFTWARE. {company_name} makes no warranties respecting any harm that may be caused by the transmission of a computer virus, worm, time bomb, logic bomb, or other such computer program. {company_name} further expressly disclaims any warranty or representation to Authorized Users or to any third party.\\par

\\b 6. LIMITATION OF LIABILITY\\b0 \\par
In no event shall {company_name} be liable for any damages (including, without limitation, lost profits, business interruption, or lost information) rising out of 'Authorized Users' use of or inability to use the SOFTWARE, even if {company_name} has been advised of the possibility of such damages. In no event will {company_name} be liable for loss of data or for indirect, special, incidental, consequential (including lost profit), or other damages based in contract, tort or otherwise. {company_name} shall have no liability with respect to the content of the SOFTWARE or any part thereof, including but not limited to errors or omissions contained therein, libel, infringements of rights of publicity, privacy, trademark rights, business interruption, personal injury, loss of privacy, moral rights or the disclosure of confidential information.\\par

\\b 7. INTERNATIONAL USE\\b0 \\par
You agree to comply with all applicable international laws, including the export and import regulations of other countries, regarding the use of the SOFTWARE.\\par

\\b 8. GOVERNING LAW\\b0 \\par
This Agreement shall be governed by the laws of the jurisdiction in which {company_name} is registered, excluding its conflict of law provisions. You hereby consent to the exclusive jurisdiction and venue of the courts in the country where {company_name} is registered.\\par

\\b 9. ENTIRE AGREEMENT\\b0 \\par
This Agreement constitutes the entire agreement between you and {company_name} relating to the SOFTWARE and supersedes all prior or contemporaneous understandings regarding such subject matter. No amendment to or modification of this Agreement will be binding unless in writing and signed by {company_name}.\\par

This license is effective as of {current_date}.\\par
{company_name}
"""

    # Combine RTF header and content
    rtf_content = rtf_header + license_content + "}"

    # Write to file
    try:
        with open(license_path, 'w', encoding='utf-8') as f:
            f.write(rtf_content)
        print(f"License file generated at: {license_path}")
        return license_path
    except Exception as e:
        print(f"Error generating license file: {e}")
        return None


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
        default_generate_license = defaults.get('generate_license', True)
        generate_license_default = "y" if default_generate_license else "n"
        generate_license_prompt = f"Generate standard commercial license? (y/n) [{generate_license_default}]: "
        generate_license_input = input(generate_license_prompt).lower()

        if generate_license_input:
            options['generate_license'] = generate_license_input == "y"
        else:
            options['generate_license'] = default_generate_license

        if options['generate_license']:
            # We'll generate the license file later when we have the output directory
            options['license_file'] = ""
        else:
            # Ask for an existing license file
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
    """Create WiX v4.x project files."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create main .wxs file
    create_wxs_file(output_dir, options, file_structure)

    # Create .wixproj file
    create_wixproj_file(output_dir, options)

    # Create README file with build instructions
    create_readme_file(output_dir)

    print(f"WiX v4.x installer project created in {output_dir}")


def create_wxs_file(output_dir, options, file_structure):
    """Create the main .wxs file for the WiX project."""
    wxs_path = os.path.join(output_dir, f"{options['product_name']}.wxs")

    # Create the root element with namespaces in the correct order
    wix = ET.Element(
        "Wix",
        {"xmlns": "http://wixtoolset.org/schemas/v4/wxs",
         "xmlns:ui": UI_NS}
    )

    # Create the package element
    package = ET.SubElement(wix, "Package",
                           Name=options['product_name'],
                           Manufacturer=options['manufacturer'],
                           Version=options['product_version'],
                           UpgradeCode=options['upgrade_code'])

    # WixUICostingPopupOptOut variable is not needed in the reference file

    # Add MediaTemplate element for packaging files
    ET.SubElement(package, "MediaTemplate", EmbedCab="yes")

    # Add WIXUI_INSTALLDIR property and set it to INSTALLDIR
    ET.SubElement(package, "Property", Id="WIXUI_INSTALLDIR", Value="INSTALLDIR")

    # Reference the standard WixUI_Minimal dialog set
    ET.SubElement(package, "ui:WixUI", Id="WixUI_Minimal")

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

        # Using standard WixUI_Mondo dialog set, no need for custom dialog

    # Create main component group
    components = ET.SubElement(package, "ComponentGroup", Id="ProductComponents")

    # Create a Feature element that references the ComponentGroup
    feature = ET.SubElement(package, "Feature",
                           Id="ProductFeature",
                           Title=options['product_name'],
                           Level="1")
    ET.SubElement(feature, "ComponentGroupRef", Id="ProductComponents")

    # Create directory structure - will be populated with subdirectories later
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

    # Create a dictionary to store directory elements by path and collect subdirectory names
    directory_elements = {}
    directory_elements[''] = product_dir  # Root directory
    subdirectories = set()  # To collect unique subdirectory names

    # First pass: identify all subdirectories
    for dir_path, files in file_structure.items():
        if dir_path:
            parts = dir_path.split(os.sep)
            current_path = ''

            for part in parts:
                if current_path:
                    current_path = os.path.join(current_path, part)
                else:
                    current_path = part

                # Store the directory path and sanitized name
                sanitized_part = ''.join(c if c.isalnum() or c == '_' or c == '.' else '_' for c in part)
                # Handle special cases for directory IDs with hyphens
                if '-' in part:
                    sanitized_part = part.replace('-', '_')

                subdirectories.add((current_path, sanitized_part, part))

    # Create a mapping of directory paths to directory IDs
    dir_id_map = {'': 'INSTALLDIR'}  # Root directory is INSTALLDIR

    # Create directory IDs for all subdirectories
    for dir_path, sanitized_part, part in subdirectories:
        dir_id = f"Dir_{sanitized_part}"
        dir_id_map[dir_path] = dir_id

    # Second pass: add files to directories
    for dir_path, files in file_structure.items():
        # Get the directory ID for this path
        if dir_path == '':
            dir_id = 'INSTALLDIR'
        else:
            # Get the last part of the path
            parts = dir_path.split(os.sep)
            last_part = parts[-1]

            # Sanitize the part name
            sanitized_part = ''.join(c if c.isalnum() or c == '_' or c == '.' else '_' for c in last_part)
            # Handle special cases for directory IDs with hyphens
            if '-' in last_part:
                sanitized_part = last_part.replace('-', '_')

            dir_id = f"Dir_{sanitized_part}"

        for file_info in files:
            component_id = f"Component_{component_id_counter}"
            component_id_counter += 1

            is_main_exe_component = False
            current_file_id_str = f"File_{file_id_counter}" # This is the ID for the current file

            if file_info['name'].endswith('.exe') and main_exe_id is None:
                main_exe_id = current_file_id_str # Assign the correct file_id
                is_main_exe_component = True

            # Generate a GUID for the main EXE component, others can use "*"
            component_guid = str(uuid.uuid4()) if is_main_exe_component else "*"

            scope_attributes = {}
            if options.get('shortcut_all_users', False) : # Apply to all components for consistency
                scope_attributes["Scope"] = "perMachine"

            component = ET.SubElement(components, "Component",
                                     Id=component_id,
                                     Directory=dir_id,
                                     Guid=component_guid,
                                     **scope_attributes)

            # file_id is now current_file_id_str, declared earlier
            file_id_counter += 1 # Increment for the next file

            file_attributes = {
                "Id": current_file_id_str, # Use the correct ID
                "Source": file_info['path'],
                "Name": file_info['name']
            }
            if is_main_exe_component:
                # The main executable's File element is marked as KeyPath="yes".
                # This is crucial because its component has a stable GUID and might be referenced
                # by other features (like shortcuts). The KeyPath tells Windows Installer
                # what file/registry key is the "key" for this component's installation status.
                # A stable GUID is important for upgrades and patching.
                file_attributes["KeyPath"] = "yes"

            file_element = ET.SubElement(component, "File", **file_attributes)

            # Add shortcut for executable files
            if file_info['name'].endswith('.exe'):
                # Store the first executable as the main one (already done above)
                # if main_exe_id is None:
                #    main_exe_id = file_id

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

    # Add icon if provided
    if options.get('icon_file'):
        # Check if the icon file exists
        icon_path = options['icon_file']

        # If the path is relative, try to resolve it
        if not os.path.isabs(icon_path):
            # Try different case variations for the filename
            icon_dir = os.path.dirname(icon_path) or '.'
            icon_filename = os.path.basename(icon_path)

            # Check if directory exists
            if os.path.exists(icon_dir):
                # Get actual files in the directory with correct case
                for filename in os.listdir(icon_dir):
                    if filename.lower() == icon_filename.lower():
                        # Found the file with correct case
                        icon_path = os.path.join(icon_dir, filename)
                        break

        # Only add the icon if the file exists
        if os.path.exists(icon_path):
            ET.SubElement(package, "Icon",
                         Id="ProductIcon",
                         SourceFile=icon_path)
            ET.SubElement(package, "Property",
                         Id="ARPPRODUCTICON",
                         Value="ProductIcon")
        else:
            print(f"Warning: Icon file '{icon_path}' not found. Icon will not be included in the installer.")

    # Conditional Feature Components (Shortcuts, PATH)
    # These features are placed in separate components to allow conditional installation
    # based on user selections in the InstallOptionsDialog.
    # Each component uses a <Condition> element that checks a WiX property (e.g., INSTALLDESKTOPSHORTCUT).
    # This property is set by the corresponding checkbox in the UI.
    # Components that don't install files directly (like these, which manage shortcuts or registry entries)
    # must have a KeyPath defined, typically a RegistryValue, to ensure they are correctly installed/uninstalled.

    # Create Desktop Shortcut Component
    if options.get('add_desktop_shortcut') and main_exe_id:
        desktop_shortcut_comp = ET.SubElement(components, "Component",
                                              Id="DesktopShortcutComponent",
                                              Directory="DesktopFolder", # Standard directory for desktop shortcuts
                                              Guid=str(uuid.uuid4())) # Unique GUID for this component
        # Create the shortcut itself, targeting the main executable
        ET.SubElement(desktop_shortcut_comp, "Shortcut",
                      Id="DesktopShortcut",
                      Name=options['product_name'],
                      Target=f"[#{main_exe_id}]", # Points to the File Id of the main EXE
                      WorkingDirectory="INSTALLDIR",
                      IconIndex="0")
        # KeyPath for the component: A registry value is created to mark the installation state.
        # This is necessary because the component doesn't install a file directly into DesktopFolder.
        ET.SubElement(desktop_shortcut_comp, "RegistryValue",
                      Root="HKCU", # Per-user registry key
                      Key=f"Software\\{options['manufacturer']}\\{options['product_name']}",
                      Name="DesktopShortcutInstalled",
                      Type="integer",
                      Value="1",
                      KeyPath="yes")

    # Create Start Menu Shortcut Component
    if options.get('add_start_menu_shortcut') and main_exe_id:
        # Determine the directory for the start menu shortcut (custom folder or general program menu)
        start_menu_shortcut_dir = "ShortcutFolder" if options.get('shortcut_folder_name') else "ProgramMenuFolder"
        start_menu_shortcut_comp = ET.SubElement(components, "Component",
                                                 Id="StartMenuShortcutComponent",
                                                 Directory=start_menu_shortcut_dir,
                                                 Guid=str(uuid.uuid4())) # Unique GUID
        # Create the shortcut
        ET.SubElement(start_menu_shortcut_comp, "Shortcut",
                      Id="StartMenuShortcut",
                      Name=options['product_name'],
                      Target=f"[#{main_exe_id}]", # Points to the main EXE
                      WorkingDirectory="INSTALLDIR",
                      IconIndex="0")
        # KeyPath for the component, using a registry value
        ET.SubElement(start_menu_shortcut_comp, "RegistryValue",
                      Root="HKCU", # Per-user registry key
                      Key=f"Software\\{options['manufacturer']}\\{options['product_name']}",
                      Name="StartMenuShortcutInstalled",
                      Type="integer",
                      Value="1",
                      KeyPath="yes")

    # Create Environment Path Component
    if options.get('add_to_path'):
        env_path_comp = ET.SubElement(components, "Component",
                                      Id="EnvironmentPathComponent",
                                      Directory="INSTALLDIR",  # The component is associated with INSTALLDIR
                                      Guid=str(uuid.uuid4())) # Unique GUID
        # The Environment element modifies the system PATH
        ET.SubElement(env_path_comp, "Environment",
                      Id="EnvironmentPath",
                      Name="PATH", # Modifying the PATH variable
                      Value="[INSTALLDIR]", # Adding the installation directory
                      Permanent="no", # Do not make permanent, will be removed on uninstall
                      Part="last", # Append to the PATH
                      Action="set", # Set the environment variable
                      System="yes") # Modify the system PATH (requires elevation)
        # KeyPath for the component. Since Environment elements are declarative,
        # a RegistryValue is used to ensure the component is properly managed.
        ET.SubElement(env_path_comp, "RegistryValue",
                      Root="HKLM", # HKEY_LOCAL_MACHINE for system PATH modification
                      Key=f"SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                      Name=f"Path_{options['product_name']}", # Unique name for registry value
                      Type="string",
                      Value="[INSTALLDIR]",
                      KeyPath="yes")

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

    # Add subdirectories to the product_dir element
    # Create a set to track unique directory names
    unique_dirs = set()

    # Collect unique directory names from file paths
    for dir_path, files in file_structure.items():
        if dir_path:
            # Get the first level directory
            parts = dir_path.split(os.sep)
            first_part = parts[0]

            # Sanitize the part name
            sanitized_part = ''.join(c if c.isalnum() or c == '_' or c == '.' else '_' for c in first_part)
            # Handle special cases for directory IDs with hyphens
            if '-' in first_part:
                sanitized_part = first_part.replace('-', '_')

            unique_dirs.add((sanitized_part, first_part))

    # Add each unique directory to the product_dir element
    for sanitized_part, part in sorted(unique_dirs):
        dir_id = f"Dir_{sanitized_part}"
        ET.SubElement(product_dir, "Directory", Id=dir_id, Name=part)

    # Write the XML to file with proper formatting
    rough_string = ET.tostring(wix, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    # Write to a temporary file first to avoid permission issues
    temp_wxs_path = wxs_path + ".tmp"
    try:
        with open(temp_wxs_path, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))

        # If the target file exists, try to remove it
        if os.path.exists(wxs_path):
            try:
                os.remove(wxs_path)
            except PermissionError:
                print(f"Warning: Could not overwrite {wxs_path}. The file may be in use.")
                print(f"The new file has been saved as {temp_wxs_path}")
                return

        # Rename the temporary file to the target file
        os.rename(temp_wxs_path, wxs_path)
    except Exception as e:
        print(f"Error writing to {wxs_path}: {e}")
        if os.path.exists(temp_wxs_path):
            print(f"The file has been saved as {temp_wxs_path}")
        return


def create_wixproj_file(output_dir, options):
    """Create the .wixproj file for the WiX project."""
    wixproj_path = os.path.join(output_dir, f"{options['product_name']}.wixproj")

    # Use the WiX SDK style project so "wix build" works correctly
    project = ET.Element(
        "Project",
        {"Sdk": "WixToolset.Sdk/6.0.0"},
    )

    # Minimal property group
    property_group = ET.SubElement(project, "PropertyGroup")
    ET.SubElement(property_group, "OutputName").text = options['product_name']
    ET.SubElement(property_group, "OutputType").text = "Package"
    # Use a fixed output path so wix build does not require $(Configuration)
    ET.SubElement(property_group, "OutputPath").text = "bin\\"

    # Compile item for main wxs file
    item_group = ET.SubElement(project, "ItemGroup")
    ET.SubElement(item_group, "Compile", Include=f"{options['product_name']}.wxs")

    # Always include UI extension
    extensions_group = ET.SubElement(project, "ItemGroup")
    ET.SubElement(extensions_group, "WixExtension", Include="WixToolset.UI.wixext")
    ET.SubElement(extensions_group, "PackageReference", Include="WixToolset.UI.wixext", Version="4.0.0")

    # Write the XML to file with proper formatting
    rough_string = ET.tostring(project, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    # Write to a temporary file first to avoid permission issues
    temp_wixproj_path = wixproj_path + ".tmp"
    try:
        with open(temp_wixproj_path, 'w', encoding='utf-8') as f:
            f.write(reparsed.toprettyxml(indent="  "))

        # If the target file exists, try to remove it
        if os.path.exists(wixproj_path):
            try:
                os.remove(wixproj_path)
            except PermissionError:
                print(f"Warning: Could not overwrite {wixproj_path}. The file may be in use.")
                print(f"The new file has been saved as {temp_wixproj_path}")
                return

        # Rename the temporary file to the target file
        os.rename(temp_wixproj_path, wixproj_path)
    except Exception as e:
        print(f"Error writing to {wixproj_path}: {e}")
        if os.path.exists(temp_wixproj_path):
            print(f"The file has been saved as {temp_wixproj_path}")
        return


def create_readme_file(output_dir):
    """Create a README file with build instructions."""
    readme_path = os.path.join(output_dir, "README.md")

    readme_content = """# WiX v4.x Installer Project

This directory contains a WiX v4.x installer project generated by wix_creator.py.

## Prerequisites

- WiX Toolset v4.x or later (https://wixtoolset.org/)
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

    # Write to a temporary file first to avoid permission issues
    temp_readme_path = readme_path + ".tmp"
    try:
        with open(temp_readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        # If the target file exists, try to remove it
        if os.path.exists(readme_path):
            try:
                os.remove(readme_path)
            except PermissionError:
                print(f"Warning: Could not overwrite {readme_path}. The file may be in use.")
                print(f"The new file has been saved as {temp_readme_path}")
                return

        # Rename the temporary file to the target file
        os.rename(temp_readme_path, readme_path)
    except Exception as e:
        print(f"Error writing to {readme_path}: {e}")
        if os.path.exists(temp_readme_path):
            print(f"The file has been saved as {temp_readme_path}")
        return

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Create a WiX v6.0.0 installer project.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
If PUBLISH_DIR is not provided, the script attempts to load settings from 'last_project.json'.

Examples:
  %(prog)s    # Load settings from last_project.json and prompt for confirmation
  %(prog)s ..\\MyApp\\bin\\Release\\net8.0\\publish
  %(prog)s c:\\path\\to\\published\\app -o MyInstallerProject
  %(prog)s D:\\Documents\\Code\\GitHub\\.Net\\MeshForge\\bin\\Release\\net8.0-windows\\win-x64\\publish -o Installer
        """)
    parser.add_argument('publish_dir', nargs='?',
                        help='Directory containing files to be included in the installer')
    parser.add_argument('--output-dir', '-o', default='Installer',
                        help='Output directory for the installer project (default: Installer)')
    return parser.parse_args()


def main():
    """Main function."""
    print (f"WiX v4.x Installer Project Creator - wix_creator.py v{__version__}")
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

    # Generate license file if requested
    if options.get('generate_license', False):
        license_path = generate_license_rtf(options['manufacturer'], options['product_name'], output_dir)
        if license_path:
            options['license_file'] = license_path

    # Create WiX project
    create_wix_project(publish_dir, output_dir, options, file_structure)


if __name__ == "__main__":
    main()
