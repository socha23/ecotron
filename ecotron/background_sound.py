from .properties import DEFAULT_ECOTRON_PROPERTIES
from sound import Clip
from .widget import Widget

CLIP_BACKGROUND = Clip("./resources/background_factory.ogg", volume=0.6)

class BackgroundSound(Widget):

    def __init__(self):
        super().__init__()
        self.bind_to_property(DEFAULT_ECOTRON_PROPERTIES.background_sound_on)

    def when_initialize(self, property_value):
        if property_value:
            CLIP_BACKGROUND.loop(fadein=1)

    def when_turn_on(self):
        CLIP_BACKGROUND.loop(fadein=1)

    def when_turn_off(self):
        CLIP_BACKGROUND.fadeout(1)
