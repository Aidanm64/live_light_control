
from PyDMXControl.profiles.default import Fixture


class Spotlight(Fixture):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._register_channel('base')
        self._register_channel('red')
        self._register_channel_aliases('red', 'r')
        self._register_channel('green')
        self._register_channel_aliases('green', 'g')
        self._register_channel('blue')
        self._register_channel_aliases('blue', 'b')
        self._register_channel('effects')
        self.dim(255, channel="base")
        self.dim(0, channel='effects')
