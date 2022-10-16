#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]
  then echo -e "\033[0;31m./install.sh requires root privileges"
  exit
fi

echo -e "\033[0;32mInstalling dependencies..."
pacman -Sy evtest python-pyqt5 --noconfirm
pip install pyinstaller
echo -e "\033[0;32mDependencies installed. Creating executable..."
pyinstaller main.spec
cp dist/main /usr/bin/predator-sense-no-launch
touch /usr/bin/predator-sense
echo "#!/usr/bin/env bash" > /usr/bin/predator-sense
echo "pkexec env DISPLAY=\$DISPLAY XAUTHORITY=\$XAUTHORITY /usr/bin/predator-sense-no-launch" >> /usr/bin/predator-sense
chmod +x /usr/bin/predator-sense
touch /usr/share/applications/predator-sense.desktop
echo "[Desktop Entry]" > /usr/share/applications/predator-sense.desktop
echo "Encoding=UTF-8" >> /usr/share/applications/predator-sense.desktop
echo "Version=1.0" >> /usr/share/applications/predator-sense.desktop
echo "Type=Application" >> /usr/share/applications/predator-sense.desktop
echo "Terminal=false" >> /usr/share/applications/predator-sense.desktop
echo "Exec=/usr/bin/predator-sense" >> /usr/share/applications/predator-sense.desktop
echo "Name=PredatorSense" >> /usr/share/applications/predator-sense.desktop
echo "Icon=$HOME/Pictures/predator.png" >> /usr/share/applications/predator-sense.desktop
cp predator.png $HOME/Pictures
echo -e "\033[0;32mInstalling custom fonts..."
mkdir -p /usr/local/share/fonts/s
cp fonts/* /usr/local/share/fonts/s
echo -e "\033[0;32mPredatorSense was successfully installed\033[0m.\nUse \033[0;33mpredator-sense\033[0m to launch the app."
