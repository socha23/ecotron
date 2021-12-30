import pygame
import pygame.sndarray
import numpy as np
import scipy.signal
import math
import time
from value_source import ValueSource
from tick_aware import TickAware

pygame.mixer.pre_init(22050, -16, 2, 2048)
pygame.init()
mixer_settings = pygame.mixer.get_init()

SAMPLE_RATE = mixer_settings[0]
BITRATE = -mixer_settings[1]
SAMPLE_MAX_VAL = 2**(BITRATE - 1) - 1

_master_volume = 1

active_clips = set()

class Clip(TickAware):
  def __init__(self, path_or_sound, volume=1, stereo=None):
    TickAware.__init__(self)
    if stereo is None:
      stereo = [1, 1]
    self._stereo = stereo
    self._volume = volume
    self._path = None
    if isinstance(path_or_sound, pygame.mixer.Sound):
      self._sound = path_or_sound
    else:
      self._path = path_or_sound
      self._sound = pygame.mixer.Sound(path_or_sound)
    self._playing = False
    self._on_complete = lambda: None
    self._intensity = None

  def loop(self, fadein=0):
      return self.play(loops=-1, fadein=fadein)

  def play(self, on_complete=lambda:None, loops=0, fadein=0, volume=None, stereo=None):
    global _master_volume

    if volume == None:
        volume = self._volume
    volume *= _master_volume
    if stereo == None:
        stereo = self._stereo

    self._channel = self._sound.play(loops=loops, fade_ms=int(fadein * 1000))
    if self._channel != None:
      self.update_channel_volume(volume, stereo)
      self._on_complete = on_complete
      self._playing = True
      active_clips.add(self)

  def fadeout(self, time_s):
      if self._playing:
          self._sound.fadeout(int(time_s * 1000))

  def duration_s(self):
    return self._sound.get_length()

  def stop(self):
    self._sound.stop()

  def update_channel_volume(self, volume, stereo):
      left, right = stereo
      if self._channel != None:
        self._channel.set_volume(left * volume, right * volume)

  def _init_intensity(self):
    INTENSITY_SAMPLE_RATE = 100 # Hz
    if self._intensity == None:
      self._intensity = Intensity(self.samples(), INTENSITY_SAMPLE_RATE)

  def intensity_source(self):
    self._init_intensity()
    return IntensityValueSource(self._intensity)


  def tick(self, time_s, delta_s):
    if self._playing:
      if self._channel == None or not self._channel.get_busy() or self._channel.get_sound() != self._sound:
        self._playing = False
        active_clips.remove(self)
        if self._on_complete != None:
          self._on_complete()

  def samples(self):
    return pygame.sndarray.array(self._sound)




##################################################################################################################################################################################################

class Intensity:
  def __init__(self, samples, intensity_sample_rate):
    self._sample_rate = intensity_sample_rate
    self._intensity_samples = []
    self._precompute_samples(samples)

  def _precompute_samples(self, samples):
    samples_mono = np.maximum(samples[:,0], samples[:,1])
    samples_count = samples_mono.shape[0]

    samples_per_frame = int(SAMPLE_RATE / self._sample_rate)

    for i in range(int(samples_count / samples_per_frame)):
        frame_samples = samples_mono[i * samples_per_frame : (i + 1) * samples_per_frame]
        self._intensity_samples.append(np.max(np.abs(frame_samples)) / SAMPLE_MAX_VAL)

  def is_finished_at(self, time_s):
    idx = int(time_s * self._sample_rate)
    return idx >= len(self._intensity_samples)

  def at(self, time_s):
    idx = int(time_s * self._sample_rate)
    if idx >= len(self._intensity_samples):
      return 0
    else:
      return self._intensity_samples[idx]


class IntensityValueSource(ValueSource):
  DELAY = 0

  def __init__(self, intensity):
    ValueSource.__init__(self)
    self._intensity = intensity
    self._start_time = self.current_time()

  def value(self):
      t = self.current_time() - self._start_time
      if t < IntensityValueSource.DELAY:
          return 0
      else:
          return self._intensity.at(t - IntensityValueSource.DELAY)

  def is_finished(self):
      return self._intensity.is_finished_at(self.current_time() - self._start_time)



def play_mp3(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()


def play(path, volume=1, stereo=None):
    sound = Clip(path, volume, stereo)
    sound.play()
    return sound


def max_channels():
    return pygame.mixer.get_num_channels()


def wait_until_end():
    while pygame.mixer.get_busy():
      time.sleep(0.2)

def set_master_volume(volume):
  global _master_volume
  _master_volume = volume
  #for clip in active_clips:
  #  clip.update_channel_volume()
