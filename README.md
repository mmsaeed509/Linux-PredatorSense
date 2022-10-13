## This is a fork of [PredatorNonSense by kphanipavan](https://github.com/kphanipavan/PredatorNonSense). It is a WIP and is intented to be customized for Acer Predator Helios 300 (2018), ```PH315-51```.

## Current changes:
* Added custom font;
* Removed unfunctional tabs (RGB, Keyboard settings);
* Added dark theme;
* Added custom icon;
* Made the window not resizeable;
* General UI improvements;

## Goals:
* Make it similar to the Windows version;
* Package it and upload to AUR;
* Possibly rewrite it after understanding how it works properly;

## Requirements (Arch Linux):
* ```python-pyqt5```
* ```evtest```

## Usage:
```
sudo python main.py
```

## Build:
To create an executable, you will need [pyinstaller](https://aur.archlinux.org/packages/pyinstaller).
```
cd PredatorSense
```
* Create the executable:
```
~/.local/bin/pyinstaller main.spec
```
* Run the executable:
```
sudo dist/main
```

## Alternatively, you can download the executable from [Releases](https://github.com/mohsunb/PredatorSense/releases)
