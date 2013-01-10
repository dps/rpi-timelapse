import subprocess
import time
import unittest

from wrappers import GPhoto
from wrappers import Identify
from wrappers import NetworkInfo

class FakePopen(object):

    def __init__(self, out, err, ret):
        self._out = out
        self._err = err
        self.returncode = ret

    def communicate(self):
        return self._out, self._err


class FakeSubprocess(object):

    PIPE = 'pipe'

    def __init__(self):
        self._fakes = {}
        self._invocations = []
        pass

    def set_Popen_for_cmd(self, cmd, popen):
        self._fakes[cmd] = popen

    def Popen(self, cmd, shell, stdout, stderr):
        self._invocations.append(cmd)
        if type(cmd) == type([]):
            cmd = cmd[0]
        if cmd in self._fakes.keys():
            return self._fakes[cmd]
        return FakePopen("out", "err", 0)

    def get_invocations(self):
        return self._invocations


class NetworkInfoTestCase(unittest.TestCase):

    def setUp(self):
        self._test_subprocess = FakeSubprocess()
        self._network_info = NetworkInfo(self._test_subprocess)

    def tearDown(self):
        pass

    def test_no_network(self):
        assert self._network_info.network_status() == 'No Network'
        assert 'iwconfig' in self._test_subprocess.get_invocations()
        assert 'ifconfig wlan0' in self._test_subprocess.get_invocations()
        assert 'ifconfig eth0' in self._test_subprocess.get_invocations()

    def test_ethernet(self):
        data = ''.join(file('testdata/ifceth0', 'r').readlines())
        popen = FakePopen(data, '', 0)
        self._test_subprocess.set_Popen_for_cmd('ifconfig eth0', popen)
        assert '10.1.10.15' in self._network_info.network_status()
        assert 'iwconfig' in self._test_subprocess.get_invocations()
        assert 'ifconfig wlan0' in self._test_subprocess.get_invocations()
        assert 'ifconfig eth0' in self._test_subprocess.get_invocations()

    def test_wlan(self):
        data = ''.join(file('testdata/ifceth0_nc', 'r').readlines())
        popen = FakePopen(data, '', 0)
        self._test_subprocess.set_Popen_for_cmd('ifconfig eth0', popen)
        data = ''.join(file('testdata/ifcwlan0', 'r').readlines())
        popen = FakePopen(data, '', 0)
        self._test_subprocess.set_Popen_for_cmd('ifconfig wlan0', popen)
        data = ''.join(file('testdata/iwc', 'r').readlines())
        popen = FakePopen(data, '', 0)
        self._test_subprocess.set_Popen_for_cmd('iwconfig', popen)

        assert '10.1.10.15' in self._network_info.network_status()
        assert '146csbr' in self._network_info.network_status()

        assert 'iwconfig' in self._test_subprocess.get_invocations()
        assert 'ifconfig wlan0' in self._test_subprocess.get_invocations()
        assert 'ifconfig eth0' in self._test_subprocess.get_invocations()

class IdentifyTestCase(unittest.TestCase):

    def setUp(self):
        self._test_subprocess = FakeSubprocess()
        self._identify = Identify(self._test_subprocess)

    def tearDown(self):
        pass

    def test_identify(self):
        popen = FakePopen('test.jpg JPEG 1728x1152 1728x1152+0+0 8-bit DirectClass 652KB 0.000u 0:00.009', '', 0)
        self._test_subprocess.set_Popen_for_cmd('identify test.jpg', popen)
        assert 'JPEG 1728x1152' in self._identify.summary('test.jpg')
        assert 'identify test.jpg' in self._test_subprocess.get_invocations()

    def test_brightness(self):
        self._identify.mean_brightness('test.jpg')
        assert 'identify -format "%[mean]" test.jpg' in self._test_subprocess.get_invocations()


class GPhotoTestCase(unittest.TestCase):

    def setUp(self):
        self._test_subprocess = FakeSubprocess()
        self._gphoto = GPhoto(self._test_subprocess)

    def tearDown(self):
        pass

    def test_set_shutter_speed(self):
        popen = FakePopen('Label: Shutter Speed\nType: MENU\nCurrent: 30\nChoice: 0 Bulb\nChoice: 4 2', '', 0)
        self._test_subprocess.set_Popen_for_cmd('gphoto2 --get-config /main/settings/shutterspeed', popen)

        self._gphoto.set_shutter_speed(secs="2")
        assert ['gphoto2 --get-config /main/settings/shutterspeed'] in self._test_subprocess.get_invocations()
        assert ['gphoto2 --set-config /main/settings/shutterspeed=4'] in self._test_subprocess.get_invocations()

    def test_get_camera_time(self):
        data = ''.join(file('testdata/datetime', 'r').readlines())
        popen = FakePopen(data, '', 0)
        self._test_subprocess.set_Popen_for_cmd('gphoto2 --get-config /main/status/datetime', popen)
        tim = self._gphoto.get_camera_date_time()
        assert time.strptime("2013-01-10 07:16:59", "%Y-%m-%d %H:%M:%S") == tim



if __name__ == '__main__':
    unittest.main()