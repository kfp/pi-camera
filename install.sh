#!/bin/bash

sudo apt install python3-picamera
sudo ln -s $(pwd)/camera.service /etc/systemd/system/camera.service
sudo ln -s $(pwd)/camera.py /usr/local/bin/camera.py
sudo systemctl enable camera
sudo systemctl start camera
