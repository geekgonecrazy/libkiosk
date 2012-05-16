#!/bin/bash

USER=kioskuser
PASS=KioskPassword359

#Make sure script is run as root
if [ "$(id -u)" != "0" ]; then
        echo "This script must be run as root" 1>&2
        exit 1
fi

chmod +x start-kiosk
cp start-kiosk /usr/bin
useradd $USER -m
expect << EOF
spawn passwd $USER
expect "New Password:"
send "${PASS}\r"
expect "Retype New Password:"
send "${PASS}\r"
expect eof;
EOF

usermod -a -G users,nopasswdlogin $USER
openssl genrsa 1024 > key openssl req -new -x509 -nodes -sha1 -days 365 -key key > cert
chmod -R 755 .
chown -R root.users .
apt-get install -y gdm matchbox-window-manager

echo "[daemon]" >> /etc/gdm/custom.conf
echo "TimedLoginEnable=true" >> /etc/gdm/custom.conf
echo "TimedLogin=$USER" >> /etc/gdm/custom.conf
echo "TimedLoginDelay=0" >> /etc/gdm/custom.conf

mv xsession /home/$USER/.xsession
ln -s /home/$USER/.xsession /home/$USER/.xinitrc
chown -R  $USER.users /home/$USER/
touch log
chmod 777 log
mv $USER.desktop /usr/share/xsessions/

read -p "Please enter the address of the website this will be used Ex: [10.10.10.27]"
echo $REPLY >> $USER.config
chmod 755 $USER.config
chown $USER.users $USER.config