# Pyrolysis Furnace Intelligence v2.3.0

This release adds a Windows desktop distribution of the furnace engineering workbench.

## Windows installer

Download:

`Pyrolysis-Furnace-Intelligence-Setup-v2.3.0.exe`

The installer:

- installs the application for the current Windows user;
- does not require a separate Python installation;
- adds a Start Menu shortcut;
- can optionally create a desktop shortcut;
- includes the Combustion, Heat Transfer and Process modules;
- can be removed from Windows Installed Apps.

The desktop shell runs the existing public Dash engineering model locally on the user's computer and displays it in a native application window. No external plant connection is created.

## Model scope

The engineering scope and model boundaries are unchanged from the public repository. The software is an educational/portfolio engineering workbench, not a plant digital twin, BMS, APC replacement or safety system.

## Windows security note

The installer is built automatically from this public repository by GitHub Actions. Code signing is not yet configured, so Windows SmartScreen may identify the publisher as unknown.
