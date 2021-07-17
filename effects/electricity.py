import glob
from sound import Clip
from director import Script
import value_source
import random

ELECTRICITY_ZAP_CLIPS = [Clip(path) for path in glob.glob("./resources/electric_zap_*.ogg")]

class ZapSource(value_source._Composite):
    def __init__(self, max_sources = 4):
        value_source._Composite.__init__(self)
        self._inner_sources = [value_source.AlwaysOff() for _ in range(max_sources)]

    
    def set_inner_source(self, idx, source):
        self._inner_sources[idx] = source

    def value(self):
        return max([s.value() for s in self._inner_sources])


def _run_zap(clip, channel, zap_source):
    clip.play()
    zap_source.set_inner_source(channel, clip.intensity_source())


def prolonged_zap_script(duration_s, channel, zap_source):
    s = Script()

    time_left = duration_s
    while time_left > 0:
        clip = random.choice(ELECTRICITY_ZAP_CLIPS)
        s.add_step(lambda clip=clip: _run_zap(clip, channel, zap_source))
        
        if time_left < clip.duration_s():
            s.add_sleep(time_left)
            s.add_step(clip.stop)
        else:
            s.add_sleep(clip.duration_s())

            
        time_left -= clip.duration_s()

    return s


def zap_script(neopixels, duration_s=10):
    zap_source = ZapSource()
    return (Script()
        .add_step(lambda: neopixels.set_source(zap_source))
        .add_parallel(
            prolonged_zap_script(duration_s, 0, zap_source),
            prolonged_zap_script(duration_s, 1, zap_source),
            prolonged_zap_script(duration_s, 2, zap_source)
        )
        .add_step(neopixels.off))
