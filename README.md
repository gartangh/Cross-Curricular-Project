# Inventory management by drones

The goal of this project is to provide commercially available drones with a functional on-board controller and to use a control board that is responsible for drone control and localization.
Beside that, the controller is responsible for communication with a central control point.
The drone is capable of flying autonomous and smoothly on a route, send from the control point.

Click [here](https://github.ugent.be/pages/gartangh/VOP_Voorraadbeheer) to visit the website!

## Getting Started

### Hardware

* 1 Raspberry Pi 3 B (with a power supply, a 16 GB microSD card and an Ethernet cable)
* 1 Raspberry Pi Zero W (with a LiPo SHIM, a 3.7 V, 500 mAh LiPo battery and a 16 GB microSD card)
* 1 Pozyx tag (with a Micro-USB to Micro-USB OTG cable)
* 4 Pozyx anchors (with power supply)
* 1 Parrot AR.Drone 2.0

![The image of the setup could not be loaded.](https://github.ugent.be/gartangh/VOP_Voorraadbeheer/blob/master/Report/images/Setup_Software.png)

### Prerequisites

* Clone this project wherever you like - Source Code
* Install [Unity](https://store.unity.com/) - Visualization
* Download [NOOBS](https://www.raspberrypi.org/downloads/noobs/) - System image for Raspberry Pi 3 B and Raspberry Pi Zero W
* Install [Putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) - SSH Client (Optional)
* Install [WinSCP](https://winscp.net/eng/download.php) - (S)FTP Client (Windows)

### Setting up the Raspberry Pi 3 B

Copy the NOOBS system image to a formatted microSD card.
Copy Setup/wpa_supplicant.conf and Setup/ssh to the microSD card.
Change the network in wpa_supplicant.conf (on the microSD card) to the network of the drone (ardrone2-XXXXXX).
Plug the microSD card in the Raspberry Pi.
Power on the Raspberry Pi and let it install the system image.
Connect to the Raspberry Pi via Putty or terminal and WinSCP.

#### Add the necessary files

Copy all files from Code\Drone_Control in a directory of your choosing with WinSCP.

The rest of the commands can be send via Putty or terminal.

#### Set up node.js

```
sudo apt-get remove nodered -y
sudo apt-get remove nodejs nodejs-legacy -y
wget https://nodejs.org/dist/v6.10.0/node-v6.10.0-linux-armv6l.tar.xz
tar xvf node-v6.10.0-linux-armv6l.tar.xz
cd node-v6.10.0-linux-armv6l
sudo cp -R bin/* /usr/bin/
sudo cp -R lib/* /usr/lib/
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential
```

#### Install packages

```
sudo npm install ar-drone
sudo npm install ardrone-autonomy
sudo pip install pypozyx
sudo pip install paho-mqtt
```

#### Reboot

```
sudo reboot
```

#### Run the program

```
node server.js
python2 client.py
```

### Setting up the Raspberry Pi Zero W:

Copy the NOOBS system image to a formatted micro SD card.
Copy Setup/wpa_supplicant.conf and Setup/ssh to the micro SD card.
Change the network in wpa_supplicant.conf (on the microSD card) to the network you would like to use.
Plug the SD card in the Raspberry Pi.
Power on the Raspberry Pi and let it install the system image.
Connect to the Raspberry Pi via Putty or terminal and WinSCP.

#### Update everything

```
sudo apt-get update
sudo apt-get upgrade
sudo reboot
```

#### Add the necessary files

Copy all files from Code\Localization in a directory of your choosing with WinSCP.

The rest of the commands can be send via Putty or terminal.

#### Install packages

```
sudo pip install pypozyx
sudo pip install paho-mqtt
sudo pip install pyserial
```

#### Reboot

```
sudo reboot
```

#### Run the program

```
python2 pozyx-tag.py 
```

## More information

More information about all sorts of topics can be found in the [wiki](https://github.ugent.be/gartangh/VOP_Voorraadbeheer/wiki).

## Authors

* Xavier Claerhoudt
* Bram De Smet
* Robbe De Vilder
* Garben Tanghe

## Supervisors

* Prof. D. Colle
* Prof. E. De Poorter
* Prof. M. Pickavet
* Ir. J. Rossey
* Ir. P. Stroobant
* Ir. J. Vanhie-Van Gerwen
