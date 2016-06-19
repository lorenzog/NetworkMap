import os
import logging
import sys


from parsers import guess_dumpfile_type_and_os as guess

# hat tip: http://stackoverflow.com/a/7483862/204634
logger = logging.getLogger('netgrapher')
logger.addHandler(logging.StreamHandler(sys.stdout))


SAMPLES_DIR = os.path.join(
    os.path.dirname(
        os.getcwd()),
    'samples')


arp_dir = os.path.join(SAMPLES_DIR, 'arp')
tr_dir = os.path.join(SAMPLES_DIR, 'traceroute')
route_dir = os.path.join(SAMPLES_DIR, 'route')


class TestArp(object):
    def test_guess_linux(self):
        dumpfile = os.path.join(arp_dir, 'linux_arp.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'arp'
        assert _o == 'linux'

    def test_guess_windows(self):
        dumpfile = os.path.join(arp_dir, 'windows_7_arp.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'arp'
        assert _o == 'windows'

    def test_guess_obsd(self):
        dumpfile = os.path.join(arp_dir, 'openbsd_arp.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'arp'
        assert _o == 'openbsd'


class TestTraceroute(object):
    def test_guess_linux(self):
        dumpfile = os.path.join(tr_dir, 'linux_traceroute.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'traceroute'
        assert _o == 'linux'


class TestRoute(object):
    def test_guess_linux(self):
        dumpfile = os.path.join(route_dir, 'linux_route.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'route'
        assert _o == 'linux'

    def test_guess_windows(self):
        dumpfile = os.path.join(route_dir, 'windows_7_route_print.txt')
        _t, _o = guess(dumpfile)
        assert _t == 'route'
        assert _o == 'windows'
