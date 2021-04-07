import pygame
import time

from tick_aware import TickAware

pygame.init()

class Clip(TickAware):
  def __init__(self, path_or_sound, volume=1, stereo=None):
    TickAware.__init__(self)
    if stereo is None:
      stereo = [1, 1]
    self._stereo = stereo
    self._volume = volume
    if isinstance(path_or_sound, pygame.mixer.Sound):
      self._sound = path_or_sound
    else:
      self._sound = pygame.mixer.Sound(path_or_sound)
    self._playing = False
    self._on_complete = lambda: None

  def play(self, on_complete=lambda:None):    
    left, right = self._stereo
    self._channel = self._sound.play()
    self._channel.set_volume(left * self.get_volume(), right * self.get_volume())
    self._on_complete = on_complete
    self._playing = True

  def get_volume(self):
    return self._volume

  def set_volume(self, volume):
    self._volume = volume
    self._sound.set_volume(volume)

  def tick(self, time_s, delta_s):
    if self._playing:
      if not self._channel.get_busy() or self._channel.get_sound() != self._sound:
        self._playing = False
        if self._on_complete != None:
          self._on_complete()


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
