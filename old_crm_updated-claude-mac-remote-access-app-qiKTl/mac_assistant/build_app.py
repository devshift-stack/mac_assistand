#!/usr/bin/env python3
"""
Build script for Mac Remote Assistant
Creates a standalone .app bundle
"""

import os
import subprocess
import sys
import shutil
from pathlib import Path

APP_NAME = "Mac Remote Assistant"
VERSION = "2.0.0"
IDENTIFIER = "com.activi-dev.mac-remote-assistant"

def check_requirements():
    """Check if required tools are installed"""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller installed")

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Get the directory where this spec file is located
SPEC_DIR = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=[
        'anthropic',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'sqlite3',
        'threading',
        'subprocess',
        'json',
        'datetime',
        'pathlib',
        'mac_assistant',
        'mac_assistant.core',
        'mac_assistant.core_v2',
        'mac_assistant.ui',
        'mac_assistant.ui.main_window',
        'mac_assistant.database',
        'mac_assistant.database.activity_tracker',
        'mac_assistant.tasks',
        'mac_assistant.tasks.task_executor',
        'mac_assistant.tasks.task_parser',
        'mac_assistant.plugins',
        'mac_assistant.plugins.base_plugin',
        'mac_assistant.plugins.plugin_manager',
        'mac_assistant.plugins.mail_plugin',
        'mac_assistant.plugins.slack_plugin',
        'mac_assistant.plugins.viber_plugin',
        'mac_assistant.plugins.telegram_plugin',
        'mac_assistant.plugins.photos_plugin',
        'mac_assistant.utils',
        'mac_assistant.utils.ai_assistant',
        'mac_assistant.scripts',
        'mac_assistant.scripts.applescript_bridge',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)

app = BUNDLE(
    coll,
    name='{APP_NAME}.app',
    icon=None,
    bundle_identifier='{IDENTIFIER}',
    version='{VERSION}',
    info_plist={{
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': True,
        'CFBundleDocumentTypes': [],
        'NSRequiresAquaSystemAppearance': False,
        'NSAppleEventsUsageDescription': 'Mac Remote Assistant needs to control other apps to automate tasks.',
        'NSCalendarsUsageDescription': 'Mac Remote Assistant needs calendar access for scheduling.',
        'NSContactsUsageDescription': 'Mac Remote Assistant needs contacts access for messaging.',
        'NSPhotoLibraryUsageDescription': 'Mac Remote Assistant needs photo library access to manage photos.',
    }},
)
'''

    spec_path = Path(__file__).parent / f"{APP_NAME.replace(' ', '_')}.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)

    print(f"✓ Spec file created: {spec_path}")
    return spec_path

def build_app():
    """Build the application"""
    check_requirements()

    # Change to app directory
    app_dir = Path(__file__).parent
    os.chdir(app_dir)

    print(f"\n=== Building {APP_NAME} v{VERSION} ===\n")

    # Create spec file
    spec_path = create_spec_file()

    # Install dependencies
    print("\nInstalling dependencies...")
    req_file = app_dir / "requirements.txt"
    if req_file.exists():
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)
        print("✓ Dependencies installed")

    # Run PyInstaller
    print("\nBuilding app bundle...")
    result = subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Build failed:\n{result.stderr}")
        return False

    print("✓ Build completed")

    # Check output
    dist_dir = app_dir / "dist"
    app_path = dist_dir / f"{APP_NAME}.app"

    if app_path.exists():
        print(f"\n✓ App created: {app_path}")

        # Create ZIP for download
        zip_name = f"{APP_NAME.replace(' ', '_')}_v{VERSION}"
        zip_path = dist_dir / f"{zip_name}.zip"

        print(f"\nCreating download package...")
        shutil.make_archive(str(dist_dir / zip_name), 'zip', dist_dir, f"{APP_NAME}.app")
        print(f"✓ Download package: {zip_path}")

        return True
    else:
        print("❌ App bundle not found")
        return False

if __name__ == "__main__":
    success = build_app()
    sys.exit(0 if success else 1)
