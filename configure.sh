#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]
	then echo -e "\033[0;31m./configure.sh script requires root privileges"
	exit
fi

FILE=dist/main

if [ -f "$FILE" ]; then
	echo -e "\033[0;32mPreparing the executable..."
	cp dist/main /usr/bin/predator-sense-no-launch
	touch /usr/bin/predator-sense
	printf "#!/usr/bin/env bash\npkexec env DISPLAY=\$DISPLAY XAUTHORITY=\$XAUTHORITY /usr/bin/predator-sense-no-launch" > /usr/bin/predator-sense
	chmod +x /usr/bin/predator-sense
	sleep 1
	echo -e "\033[0;32mCreating desktop entry..."
	touch /usr/share/applications/predator-sense.desktop
	printf "[Desktop Entry]\nEncoding=UTF-8\nVersion=1.0\nType=Application\nTerminal=false\nExec=/usr/bin/predator-sense\nName=Predator Sense™\nComment=Application to control fan speed for Acer Predator Helios 300\nIcon=/usr/share/icons/predator-sense" > /usr/share/applications/predator-sense.desktop
	cp app_icon.ico /usr/share/icons/predator-sense
	sleep 1
	echo -e "\033[0;32mInstalling custom fonts..."
	mkdir -p /usr/local/share/fonts/s
	cp fonts/* /usr/local/share/fonts/s
	sleep 1
	echo -e "\033[0;32mPredatorSense was successfully installed\033[0m.\nUse \033[0;33mpredator-sense\033[0m or the desktop entry to launch the app."
else
	echo -e "\033[0;31mWrong command order.\nRefer to README.md"
	exit
fi
