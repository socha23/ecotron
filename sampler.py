import pygame
import numpy as np
import scipy.signal
from sound import Clip
import math

pygame.init()
mixer_settings = pygame.mixer.get_init()

SAMPLE_RATE = mixer_settings[0]
BITRATE = -mixer_settings[1]
SAMPLE_MAX_VAL = 2**(BITRATE - 1) - 1

def compute_intensity(clip, frame_length_s):
    result = []
    samples = clip.samples()
    samples_mono = np.maximum(samples[:,0], samples[:,1])    
    samples_count = samples_mono.shape[0]

    samples_per_frame = int(SAMPLE_RATE * frame_length_s)
    
    for i in range(math.ceil(clip.duration_s() / frame_length_s)):
        frame_samples = samples_mono[i * samples_per_frame : (i + 1) * samples_per_frame]
        result.append(np.max(np.abs(frame_samples)) / SAMPLE_MAX_VAL)

    print(result)


#    s_mono = s[:,0]

#    print("before resampling")
    
    #print(s_mono.shape)
    #print(s_mono[0:50])

    #frame_count = s_mono.shape[0] / SAMPLE_RATE / frame_length_s
    #resampled = scipy.signal.resample(s_mono, int(frame_count))

    #print("after resampling")
    #print(resampled.shape)
    #print(resampled)


if __name__ == '__main__':
    compute_intensity(Clip("./resources/elevator_ding2.ogg"), 0.01)