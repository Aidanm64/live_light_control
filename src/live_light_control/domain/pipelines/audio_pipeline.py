import threading
import gi
import time
import logging
import gstreamer.utils as utils
from reactivex.subject import Subject

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib, GstAudio  # noqa: E402

logger = logging.getLogger(__name__)
Gst.init(None)


class AudioPipeline:
    def __init__(self, source, spectrum_observer=Subject(), sample_observer=Subject()):
        self.source = source
        self._spectrum_source = spectrum_observer
        self._sample_source = sample_observer
        #command = f"{source.command} ! audioconvert ! tee name=t t. ! queue ! spectrum interval=1000000000 bands=10 post-messages=true message-phase=true ! fakesink sync=true t. ! queue ! appsink name=audio-sink caps=audio/x-raw,format=F32LE sync=true"
        command = f"{source.command} ! audioconvert ! appsink name=audio-sink caps=audio/x-raw,format=F32LE"
        self.loop = GLib.MainLoop()
        self.pipeline = Gst.parse_launch(command)
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.bus_message_cb)

        audio_sink = self.pipeline.get_by_name("audio-sink")
        audio_sink.set_property("emit-signals", True)
        audio_sink.connect("new-sample", self.on_audio_sample)
        self.source.link(self.pipeline)

        self._thread = threading.Thread(target=self.run)

    def start(self):
        self._thread.start()

    def stop(self):
        self.shutdown()
        self._thread.join()

    def shutdown(self):
        self.pipeline.set_state(Gst.State.NULL)
        self.loop.quit()
        self._spectrum_source.on_completed()
        self._sample_source.on_completed()

    def bus_message_cb(self, bus, message):
        if message.type == Gst.MessageType.EOS:
            logger.info("eos")
            self.shutdown()
        elif message.type == Gst.MessageType.ERROR:
            error = message.parse_error()
            self.shutdown()

        message_structure = message.get_structure()
        if message_structure:
            message_name = message_structure.get_name()
            if (message_name == "spectrum"):
                self._spectrum_source.on_next(message_structure)

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        self.loop.run()

    def on_audio_sample(self, sink):
        sample = sink.emit("pull-sample")
        buffer = sample.get_buffer()
        data = buffer.extract_dup(0, buffer.get_size())
        self._sample_source.on_next(sample)
        #caps_format = sample.get_caps().get_structure(0)
        #print(caps_format.to_string())
        #frmt_str = caps_format.get_value("format")
        #audio_format = GstAudio.AudioFormat.from_string(frmt_str)

        return 0

    @property
    def sample_source(self):
        return self._sample_source

    @property
    def spectrum_source(self):
        return self._spectrum_source
