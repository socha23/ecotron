#!/usr/bin/python

import os

from speech import SpeechLines

for line_code in [x for x in dir(SpeechLines) if not x.startswith("__")]:
    line_text = getattr(SpeechLines, line_code)
    os.system(f"./speech/tts.sh \"{line_text}\" resources/speech/{line_code}.mp3")
    os.system(f"ffmpeg -y -i resources/speech/{line_code}.mp3 -c:a libvorbis -q:a 8 resources/speech/{line_code}.ogg")
    os.system(f"rm resources/speech/{line_code}.mp3")
print("Preparing speech lines complete")