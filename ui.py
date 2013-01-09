from time import sleep
try:
  from Adafruit_I2C import Adafruit_I2C
  from Adafruit_MCP230xx import Adafruit_MCP230XX
  from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
except ImportError:
  # This is just to allow the UI to be tested on Linux
  class Adafruit_CharLCDPlate(object):
    def __init__(self, busnum):
        pass

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class FakeCharLCDPlate(object):

    RED = "red"
    UP = "q"
    DOWN = "a"
    SELECT = "s"

    def __init__(self):
        self._getch = _GetchUnix()
        pass

    def clear(self):
        print "--LCD Cleared--"

    def message(self, msg):
        print msg

    def backlight(self, bl):
        print "Backlight %s" % str(bl)

    def fakeonly_getch(self):
        self._ch = self._getch()

    def buttonPressed(self, button):
        return self._ch == button



class TimelapseUi(object):

    def __init__(self):
        self._lcd = Adafruit_CharLCDPlate(busnum = 0)
        #self._lcd = FakeCharLCDPlate()

        self._lcd.backlight(self._lcd.ON)

    def update(self, text):
        self._lcd.clear()
        self._lcd.message(text)
        print(text)

    def show_config(self, configs, current):
        config = configs[current]
        self.update("Timelapse\nT: %s ISO: %d" % (config[0], config[1]))

    def show_status(self, shot, configs, current):
        config = configs[current]
        self.update("Shot %d\nT: %s ISO: %d" % (shot, config[0], config[1]))

    def show_error(self, text):
        self.update(text[0:16] + "\n" + text[16:])
        while not self._lcd.buttonPressed(self._lcd.SELECT):
            self.backlight_on()
            sleep(1)
            self.backlight_off()
            sleep(1)
        self.backlight_off()

    def backlight_on(self):
        self._lcd.backlight(self._lcd.ON)

    def backlight_off(self):
        self._lcd.backlight(self._lcd.OFF)


    def main(self, configs, current, network_status):
        self.backlight_on()
        self.update(network_status)
        while not self._lcd.buttonPressed(self._lcd.SELECT):
            pass

        ready = False
        while not ready:
            self.show_config(configs, current)

            while True:
                if (type(self._lcd) == type(FakeCharLCDPlate())):
                    self._lcd.fakeonly_getch()

                if self._lcd.buttonPressed(self._lcd.UP):
                    current -= 1
                    if current < 0:
                        current = 0
                    break
                if self._lcd.buttonPressed(self._lcd.DOWN):
                    current += 1
                    if current >= len(configs):
                        current = len(configs) - 1
                    break
                if self._lcd.buttonPressed(self._lcd.SELECT):
                    ready = True
                    break
        return current 



