# Desktop Icon (Optional)

It is useful to create desktop shortcuts so that you don't need to use the terminal every time.

## Stream Desktop Icon

```bash
cd ~/Desktop
nano stream.desktop
```

```
[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Exec=python3 /home/pi/picoastal/src/rpi/stream.py -i /home/pi/picoastal/src/rpi/config_rpi.json
Name=PiCoastal Stream
Comment=PiCoastal Stream
Icon=/home/pi/picoastal/doc/camera.png
```

To save and exit use ```ctrl+o``` + ```ctrl+x```.

## Capture Desktop Icon

```
[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Exec=python3 /home/pi/picoastal/src/rpi/capture.py -i /home/pi/picoastal/src/rpi/config_rpi.json.json
Name=PiCoastal Capture
Comment=PiCoastal Capture
Icon=/home/pi/picoastal/doc/camera.png
```