from sound import Clip
import os.path

class SpeechLines:
    WELCOME = "Ecotron initialized. Press the button on the Technic hub"
    ECOTRON_READY = "Ecotron Terrabiology Institute ready"

    CONVEYOR_CALIBRATION_STARTED = "Conveyor calibration started"
    CONVEYOR_CALIBRATION_COMPLETE = "Conveyor calibration complete"

    PRESSURIZING_AIRLOCK = "Pressurizing airlock"
    DEPRESSURIZING_AIRLOCK = "Depressurizing airlock"

    WELCOME_COMMANDER = "Welcome to Terrabiology Institute, Commander"

    TENTACLE_PLANT_AGITATED = "Warning. Tentacle plant shows unusual activity"
    TENTACLE_PLANT_BREAKOUT = "Containment breached. Initiate emergency protocols"
    TENTACLE_PLANT_PEACE = "Peace restored"

    COLOR_MODE_CONSTANT = "Mode: Constant"
    COLOR_MODE_PULSE = "Mode: Pulse"
    COLOR_MODE_PLASMA = "Mode: Plasma"

clips_by_text = dict()

for line_code in [x for x in dir(SpeechLines) if not x.startswith("__")]:
    line_text = getattr(SpeechLines, line_code)
    file = f"./resources/speech/{line_code}.ogg"
    if os.path.exists(file):
        clips_by_text[line_text] = Clip(file)

def say(text):
    clips_by_text[text].play()

