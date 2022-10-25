#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]
  then echo -e "\033[0;31m./install.sh requires root privileges"
  exit
fi

echo -e "\033[0;32mInstalling dependencies...\033[0m"
pacman -Sy evtest python-pyqt5 --noconfirm
pip install pyinstaller
echo -e "\033[0;32mDependencies installed. Creating executable..."
pyinstaller main.spec
cp dist/main /usr/bin/predator-sense-no-launch
touch /usr/bin/predator-sense
printf "#!/usr/bin/env bash\npkexec env DISPLAY=\$DISPLAY XAUTHORITY=\$XAUTHORITY /usr/bin/predator-sense-no-launch" > /usr/bin/predator-sense
chmod +x /usr/bin/predator-sense
touch /usr/share/applications/predator-sense.desktop
printf "[Desktop Entry]\nEncoding=UTF-8\nVersion=1.0\nType=Application\nTerminal=false\nExec=/usr/bin/predator-sense\nName=PredatorSense\nComment=Application to control fan speed for Acer Predator Helios 300\nIcon=$HOME/Pictures/predator.png" > /usr/share/applications/predator-sense.desktop
cp predator.png $HOME/Pictures
echo -e "\033[0;32mInstalling custom fonts..."
mkdir -p /usr/local/share/fonts/s
cp fonts/* /usr/local/share/fonts/s
echo -e "\033[0;32mPredatorSense was successfully installed\033[0m.\nUse \033[0;33mpredator-sense\033[0m to launch the app."
