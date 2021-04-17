from sound import Clip
import os.path

class SpeechLines:
    WELCOME = "Ecotron initialized. Press the button on the Technic hub"
    ECOTRON_READY = "Ecotron Terrabiology Institute ready"

    CONVEYOR_CALIBRATION_STARTED = "Conveyor calibration started"
    CONVEYOR_CALIBRATION_COMPLETE = "Conveyor calibration complete"
    
    
clips_by_text = dict()

for line_code in [x for x in dir(SpeechLines) if not x.startswith("__")]:
    line_text = getattr(SpeechLines, line_code)
    file = f"./resources/speech/{line_code}.ogg"
    if os.path.exists(file):
        clips_by_text[line_text] = Clip(file)

def say(text):
    clips_by_text[text].play()

