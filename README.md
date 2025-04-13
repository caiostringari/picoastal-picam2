# Introduction

This project aims to provide the information needed to build an ARGUS-like
coastal monitoring system based on the Raspberry Pi computer board.

This is a new version of [picoastal](https://github.com/caiostringari/picoastal).

Main changes are:
 - Code now uses `picamera2`.
 - Support for FLIR cameras has been dropped in this version. In 2020, the Raspberry Pi foundation released the [High Quality Camera](https://www.raspberrypi.org/products/raspberry-pi-high-quality-camera/) for the Pi. This camera allows to use any type of lens which is perfect for our project. This camera costs around 75 USD and is much easier to use and program than other cameras. Everything is also open-source.

# Table of Contents

[TOC]

# 1. Hardware

## 1.1. Computer Board

This project has been developed using a Raspberry Pi Model 5 B with 4Gb of memory.

The components of the system are:

- [Raspberry Pi board](https://www.raspberrypi.com/products/raspberry-pi-5/)
- [16Gb+ SD card](https://www.raspberrypi.org/documentation/installation/sd-cards.md)
- External storage. In this case a 32Gb USB stick.
- Keyboard / Mouse
- [Optional] [Raspberry Pi display case](https://www.canakit.com/raspberry-pi-4-lcd-display-case-pi4.html)
- [Optional] 4G modem for email notifications.
- [Optional] Battery bank
- [Optional] Solar panel

Assembly should be straight forward but if in doubt, follow the tutorials from
the Raspberry Pi Foundation.


# 2. Software

## 2.1. Operating System (OS)

We will be using [Raspberry Pi OS](https://www.raspberrypi.org/software/) which usually comes pre-installed with the board.

Before doing anything, it is a good idea to update your system:

```bash
sudo apt update
sudo apt dist-upgrade
```

## 2.2 Camera Software

The code has been updated to use [`picamera2`](https://github.com/raspberrypi/picamera2). We need to first install it:

```bash
sudo apt install python3-picamera2 --no-install-recommends
```

Note that it's not recommended to install in an isolated environment using `pip`.

We will also need `ffmpeg`:

```
sudo apt install x264 ffmpeg
```

Install python libraries with `pip` system-wide.

```
sudo pip install natsort loguru --break-system-packages
```

# 2.3 Picoastal Code

To get the code do:

```bash
cd ~
git clone https://github.com/caiostringari/picoastal-picam2.git
```


# 3. Image Capture Configuration File


A configuration file is required to drive the camera. It tells the camera when to capture data, frame rates, etc. An example is:

```json
{
    "data": {
        "output": "/mnt/data/",
        "format": "jpeg",
        "hours": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    },
    "capture": {
        "duration": 20,
        "framerate": 10,
        "resolution": [1920, 1080],
        "quality": "MEDIUM"
    },
    "stream": {
        "duration": 20,
        "framerate": 30,
        "resolution": [640, 480]
    },
    "post_processing": {
        "extract_frames": true,
        "only_last_frame": false,
        "notify": false,
        "average": false,
        "deviation": false
    }
}
```

**JSON Options:**

Explanation of the configuration parameters above:

Streaming and Capturing:

- ```output```: The location to where to write the frames. Sub-folders will be created based on the hour of the capture cycle.
- ```framerate```: The capture frequency rate in frames per second.
- ```duration```: Capture cycle duration in seconds.
- ```resolution```: Image size for capturing or streaming.
- ```quality```: Image quality (bitrate). Options are `LOW`, `MEDIUM`, `HIGH`.
- ```hours```: Capture hours. If outside these hours, the camera does not grab any frames.

Post-processing:

- ```notify```: will send an e-mail (see below).
- ```average```: will create an average image.
- ```deviation```: will create the deviation image.


# 4. Capturing Frames


## 4.1. Displaying the Camera Stream

This is useful to point the camera in the right direction, to set the focus, and
aperture.

To launch the stream do:

```bash
cd ~/picoastal-picam2
python3 src/rpi/stream.py -i src/rpi/config_rpi.json > stream.log &
```

For information on creating desktop icons for easy access, see [Desktop Icon Setup](doc/desktop_icon.md).

## 4.2. Single Capture Cycle

The main capture program is [capture.py](src/rpi/capture.py). To run a single capture cycle, do:

```bash
cd ~/picoastal-picam2/
python3 src/rpi/capture.py -i config_rpi.json > capture.log &
```

## 4.3. Scheduling Capture Cycles

The recommend way to schedule jobs is using ```cron```.

First we need to create a ```bash``` script that will call all the commands we
need within a single capture cycle. A script [example](src/rpi/cycle_rpi.sh) has been provided in the repository. The script handles:

- Creating log directories
- Running the capture process
- Generating statistical images (average, variance, brightest/darkest frames)
- Creating rectified images
- Generating timestacks
- Sending email notifications

To examine or modify the script, check the [cycle_rpi.sh](src/rpi/cycle_rpi.sh) file.

To add a new job to cron, do:

```bash
crontab -e
```

If this is your first time using ```crontab```, you will be asked to chose a
text editor. I recommend using ```nano```. Add this line to the end of the file:

```
0 * * * * bash /home/pi/picoastal-picam2/src/rpi/cycle_rpi.sh
```

To save and exit use ```ctrl+o``` + ```ctrl+x```.

## 4.4. Controlling the System Remotely

The best way to control the camera is by using [Raspberrypi Connect](https://www.raspberrypi.com/software/connect/). It allows for both `SSH` and Remote Desktop access. 

# 5. Additional Features

This project includes several additional features and utilities that have been organized into separate documentation files:

- [Camera Calibration](doc/camera_calibration.md) - Information on calibrating the camera using ChArUco boards
- [Post-processing](doc/post_processing.md) - Tools for generating average, variance, brightest/darkest, rectified images, and timestacks
- [Experimental Features](doc/experimental_features.md) - Advanced features like Optical Flow and Machine Learning based analysis
- [Email Notifications](doc/email_notifications.md) - Set up email notifications for camera status updates and image delivery

# 6. Troubleshooting

Here are some common issues you might encounter and their solutions:

## Camera Not Working
- Check that the camera is properly connected to the Raspberry Pi
- Ensure the camera is enabled in the Raspberry Pi configuration (`sudo raspi-config`)
- Verify that the picamera2 library is properly installed

## Storage Issues
- Check available space with `df -h`
- Ensure the external storage is properly mounted
- Consider setting up automatic cleanup of old images

## Cron Jobs Not Running
- Check cron logs with `crontab -l`
- Ensure the paths in your scripts are absolute rather than relative
- Verify the script has execute permissions (`chmod +x your_script.sh`)

# 7. Known issues

...

# 8. Future improvements

I am open to suggestions. Keep in mind that I work in this project during my spare time and do no have access to much hardware, specially surveying gear.

# 9. Contributing

If you'd like to contribute to this project, please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

Please include clear documentation for any new features you implement.

# 10. Disclaimer

There is no warranty for the program, to the extent permitted by applicable law except when otherwise stated in writing the copyright holders and/or other parties provide the program "as is" without warranty of any kind, either expressed or implied, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose. the entire risk as to the quality and performance of the program is with you. should the program prove defective, you assume the cost of all necessary servicing, repair or correction.

