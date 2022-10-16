# PredatorSense clone for ```PH-315-51-78NP``` to control fan speed on Linux.
![Predator Sense](demo.png)

## Disclaimer:
* Using this application with other laptops may potentially damage them. Proceed at your discretion. Though it most likely works with other **Acer Predator Helios 300** models.
## Usage: (Arch Linux)
```
git clone https://github.com/mohsunb/PredatorSense.git
```
```
cd PredatorSense
```
```
sudo chmod +x ./install.sh && sudo ./install.sh
```
```
predator-sense
```
... or use the desktop entry.

## This is a fork of [PredatorNonSense by kphanipavan](https://github.com/kphanipavan/PredatorNonSense), customized for ```PH315-51```.

## Current changes:
* Added custom font (TT Squares);
* Removed dysfunctional tabs (keyboard lighting settings, fan profiles, GPU overclock);
* Added dark theme;
* Added custom icon;
* Made the window not resizeable;
* General UI improvements;
* Refactored the code for easier maintenance;
* Dynamically disabled buttons to prevent unexpected behavior;

## Goals:
* Make it similar to the Windows version;
* Upload to AUR;
* Possibly rewrite it after understanding how it works properly;
