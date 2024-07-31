import numpy as np

from live_light_control.domain.analysis.bmp_detector import BPMDetector, detect_bpm
from live_light_control.domain.analysis.key_finder import KeyFinder, find_key
from reactivex.scheduler import ThreadPoolScheduler
from reactivex import operators as ops
import reactivex as rx

from live_light_control.domain.analysis.spectral_analyzer import SpectralAnalyzer, get_spectral_features


def combine_samples():
    def _combine_samples(source):
        def subscribe(observer, scheduler=None):
            def on_next(samples):
                combined_sample = b''
                for sample in samples:
                    buffer = sample.get_buffer()
                    data = buffer.extract_dup(0, buffer.get_size())
                    combined_sample += data
                arr = np.frombuffer(combined_sample)
                observer.on_next(arr)
            source.subscribe(on_next,
                observer.on_error,
                observer.on_completed)
        return rx.create(subscribe)
    return _combine_samples


class AudioAnalysisService:

    def __init__(self, sample_source, sample_rate=44100):
        self.sample_source = sample_source
        self._sample_rate = sample_rate
        self.scheduler = ThreadPoolScheduler()

        self.bpm_detector = BPMDetector(sample_rate=sample_rate)
        self.key_finder = KeyFinder(sample_rate=sample_rate)
        self.spectral_analyzer = SpectralAnalyzer(sample_rate=sample_rate)

        self.buffered_sample_source = self.sample_source.pipe(
            ops.subscribe_on(self.scheduler),
            ops.buffer_with_count(100),
            combine_samples())

        self._bpm_source = None
        self._key_source = None
        self._spectral_feature_source = None

    @property
    def bpm_source(self):
        if not self._bpm_source:
            self._bpm_source = self.buffered_sample_source.pipe(
                ops.subscribe_on(self.scheduler),
                detect_bpm(self.bpm_detector),
                ops.filter(lambda bpm: bpm > 0),
                ops.distinct_until_changed())
        return self._bpm_source

    @property
    def key_source(self):
        if not self._key_source:
            self._key_source = self.buffered_sample_source.pipe(
                ops.subscribe_on(self.scheduler),
                find_key(self.key_finder),
                ops.distinct_until_changed())

        return self._key_source

    @property
    def spectral_feature_source(self):
        if not self._spectral_feature_source:
            self._spectral_feature_source = self.buffered_sample_source.pipe(
                ops.subscribe_on(self.scheduler),
                get_spectral_features(self.spectral_analyzer),
                ops.distinct_until_changed())

        return self._spectral_feature_source