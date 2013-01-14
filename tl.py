#!/usr/bin/python

from datetime import datetime
from datetime import timedelta
import subprocess
import time

from wrappers import GPhoto
from wrappers import Identify
from wrappers import NetworkInfo


from ui import TimelapseUi

MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=30)
MIN_BRIGHTNESS = 20000
MAX_BRIGHTNESS = 30000

CONFIGS = [("1/1600", 200),
           ("1/1000", 200),
           ("1/800", 200),
           ("1/500", 200),
           ("1/320", 200),
           ("1/250", 200),
           ("1/200", 200),
           ("1/160", 200),
           ("1/100", 200),
           ("1/80", 200),
           ("1/60", 200),
           ("1/50", 200),
           ("1/40", 200),
           ("1/30", 200),
           ("1/20", 200),
           ("1/15", 200),
           ("1/13", 200),
           ("1/10", 200),
           ("1/6", 200),
           ("1/5", 200),
           ("1/4", 200),
           ("0.3", 200),
           ("0.5", 200),
           ("0.6", 200),
           ("0.8", 200),
           ("1", 200),
           ("1.6", 200),
           ("2.5", 200),
           ("3.2", 200),
           ("5", 200),
           ("8", 200),
           ("10", 200),
           ("13", 200),
           ("15", 200),
           ("20", 200),
           ("30", 200),
           ("30", 400),
           ("30", 800),
           ("30", 1600)]

def test_configs():
    camera = GPhoto(subprocess)

    for config in CONFIGS:
      camera.set_shutter_speed(secs=config[0])
      camera.set_iso(iso=str(config[1]))
      time.sleep(1)

def main():
    #print "Testing Configs"
    #test_configs()
    print "Timelapse"
    camera = GPhoto(subprocess)
    idy = Identify(subprocess)
    netinfo = NetworkInfo(subprocess)

    ui = TimelapseUi()

    current_config = 11
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None

    network_status = netinfo.network_status()
    current_config = ui.main(CONFIGS, current_config, network_status)

    try:
        while True:
            last_started = datetime.now()
            config = CONFIGS[current_config]
            print "Shot: %d Shutter: %s ISO: %d" % (shot, config[0], config[1])
            ui.backlight_on()
            ui.show_status(shot, CONFIGS, current_config)
            camera.set_shutter_speed(secs=config[0])
            camera.set_iso(iso=str(config[1]))
            ui.backlight_off()
            try:
              filename = camera.capture_image_and_download()
            except Exception, e:
              print "Error on capture." + str(e)
              print "Retrying..."
              # Occasionally, capture can fail but retries will be successful.
              continue
            prev_acquired = last_acquired
            brightness = float(idy.mean_brightness(filename))
            last_acquired = datetime.now()

            print "-> %s %s" % (filename, brightness)

            if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
                current_config = current_config + 1
            elif brightness > MAX_BRIGHTNESS and current_config > 0:
                current_config = current_config - 1
            else:
                if last_started and last_acquired and last_acquired - last_started < MIN_INTER_SHOT_DELAY_SECONDS:
                    print "Sleeping for %s" % str(MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))

                    time.sleep((MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started)).seconds)
            shot = shot + 1
    except Exception,e:
        ui.show_error(str(e))


if __name__ == "__main__":
    main()