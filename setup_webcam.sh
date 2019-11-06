#!/usr/bin/env bash
sudo modprobe -r uvcvideo && sudo modprobe uvcvideo quirks=128
sudo modprobe v4l2loopback video_nr=1
v4l2-ctl --list-devices