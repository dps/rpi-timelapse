rpi-timelapse
=============

A timelapse camera controller for Raspberry Pi and Canon EOS 350d (should work with any camera supported by `gphoto2` with minor tweaks), with an optional UI and controls on the Adafruit LCD Pi plate.

Demo video
----------

<iframe width="960" height="720" src="http://www.youtube.com/embed/AZbK4acS5Mc" frameborder="0" allowfullscreen></iframe>

Installation
------------

rpi-timelapse uses `gphoto2` and `imagemagick`.  To install these dependencies on your pi:

```
$ sudo apt-get install gphoto2
$ sudo apt-get install imagemagick
```

Run
---

python tl.py

Run on boot
-----------

Follow the instructions at <http://learn.adafruit.com/drive-a-16x2-lcd-directly-with-a-raspberry-pi/init-script> using `timelapse` file from this repo instead of `lcd`.


Convert the resulting JPEGs to a timelapse movie
------------------------------------------------

```
ffmpeg -r 18 -q:v 2 -start_number XXXX -i /tmp/timelapse/IMG_%d.JPG output.mp4
```