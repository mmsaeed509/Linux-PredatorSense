## Predator Sense™ clone for ```PH315-51-78NP``` to control fan speed on Linux. This application is intended for "Acer Predator Helios 300", 2018 model.
![Predator Sense](demo.png)

## Disclaimer:
* This program uses ```ec_sys``` kernel module to function. Check using ```find /lib/modules/$(uname -r) -type f -name '*.ko*' | grep ec_sys```. If it isn't listed, you'll have to rebuild the kernel yourself manually. Arch Linux and Ubuntu do ship the kernel with this module available.
* Secure Boot is **not** supported.
* Using this application with other laptops may potentially damage them. Proceed at your discretion. Though it most likely works with other **Acer Predator Helios 300** models.
* It does **not** work with OpenBSD's root access command port, ```opendoas```. Use ```sudo``` instead when running through a terminal.

## Minimal usage (not recommended):
Dependencies are ```evtest``` and ***Python Qt5***.
All you need to do is run the main script as root:
```
# python main.py
```
***Warning: This will create ```__pycache__``` owned by "root". Use ```sudo rm -rf``` to delete if desired.***

## Full installation:
Dependencies:
* Ubuntu / Linux Mint:
```
sudo apt install python3-pip evtest python3-qtpy git
```
* Arch Linux:
```
sudo pacman -S python-pip evtest python-pyqt5 git
```
---
```
pip install pyinstaller
```
```
git clone https://github.com/mohsunb/PredatorSense.git && cd PredatorSense
```
```
~/.local/bin/pyinstaller main.spec
```
```
sudo ./configure.sh
```
---
## This is a fork of [PredatorNonSense by kphanipavan](https://github.com/kphanipavan/PredatorNonSense), customized for ```PH315-51```.

## Changes:
* Added custom font (TT Squares);
* Removed dysfunctional tabs (keyboard lighting settings, fan profiles, GPU overclock);
* Added dark theme;
* Added custom icon;
* Made the window not resizeable;
* General UI improvements;
* Refactored the code for easier maintenance;
* Dynamically disabled buttons to prevent unexpected behavior;
* Global fan state is now remembered across sessions;
