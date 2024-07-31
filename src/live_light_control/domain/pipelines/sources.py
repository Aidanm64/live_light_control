
class Source:
    @property
    def name(self):
        return ""

    @property
    def command(self):
        return ""

    def link(self, pipeline):
        pass


class TestSource(Source):
    def __init__(self, wave=0, freq=440):
        self.wave = wave
        self.freq = freq

    @property
    def name(self):
        return "audio_test_src"

    @property
    def command(self):
        return f"audiotestsrc name={self.name} wave={self.wave} freq={self.freq} is-live=true"

    def link(self, pipeline):
        self.audio_test_src = pipeline.get_by_name(self.name)

    def set_frequency(self, freq):
        self.freq = freq
        self.audio_test_src.set_property("freq", self.freq)


class FileSource(Source):

    def __init__(self, location="/app/data/sample.wav"):
        self.location = location

    @property
    def name(self):
        return "file_src"

    @property
    def command(self):
        return f"filesrc location={self.location} ! wavparse"


class AudioInterfaceSource(Source):

    def __init__(self, device="hw:1,0"):
        self.device = device

    @property
    def name(self):
        return "audio_src"

    @property
    def command(self):
        return f"alsasrc device={self.device} name={self.name}"