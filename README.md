# rpi_yf-s201_mqtt
Simple MQTT publishing from water flow sensor yf-s201 on RPI. (C) 2020 Lubomir Kamensky lubomir.kamensky@gmail.com

Dependencies
------------
* Eclipse Paho for Python - http://www.eclipse.org/paho/clients/python/

Example use
-----------
python3 rpi_yf-s201_mqtt.py --configuration studna.ini

Example use pm2 usage
---------------------
pm2 start /usr/bin/python3 --name "rpi_yf-s201_mqtt" -- /home/pi/rpi_yf-s201_mqtt/rpi_yf-s201_mqtt.py --configuration studna.ini

pm2 save
