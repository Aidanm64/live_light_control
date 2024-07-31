
import numpy as np
from live_light_control.domain.analysis.audio_analyzer import AudioAnalyzer
import librosa
import reactivex as rx
from reactivex import operators as ops


class SpectralFeatures:
    def __init__(self, rms, centroid, flatness):
        self.rms = rms
        self.centroid = centroid
        self.flatness = flatness


class SpectralAnalyzer(AudioAnalyzer):
    def __init__(self, *args, **kwargs):
        self._processing = False
        super().__init__(*args, **kwargs)

    def analyze(self, data):
        self._processing = True

        S, phase = librosa.magphase(librosa.stft(data))

        features = SpectralFeatures(
            rms=librosa.feature.rms(y=S).mean(),
            centroid=librosa.feature.spectral_centroid(y=S).mean(),
            flatness=librosa.feature.spectral_flatness(y=S).mean()
        )

        self._processing = False
        return features

    def is_busy(self):
        return self._processing


def get_spectral_features(spectral_analyzer=SpectralAnalyzer()):
    def _find_key(source):
        def subscribe(observer, scheduler=None):
            def on_next(data):
                try:
                    features = spectral_analyzer.analyze(data)
                    observer.on_next(features)
                except Exception as e:
                    observer.on_error(e)
            return source.pipe(ops.filter(lambda samples: len(samples) > 0)).subscribe(on_next,
                observer.on_error,
                observer.on_completed)
        return rx.create(subscribe)
    return _find_key
