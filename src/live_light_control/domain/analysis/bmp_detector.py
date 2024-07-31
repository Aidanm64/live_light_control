import librosa
from live_light_control.domain.analysis.audio_analyzer import AudioAnalyzer
import reactivex as rx
from reactivex import operators as ops

class BPMDetector(AudioAnalyzer):

    def analyze(self, samples):
        tempo, beats = librosa.beat.beat_track(y=samples, sr=self.sample_rate)
        #print("TEMPO: " + str(tempo))
        return tempo, beats


def detect_bpm(bpm_detector=BPMDetector()):
    def _bpm_detector(source):
        def subscribe(observer, scheduler=None):
            def on_next(samples):
                try:
                    bpm, beats = bpm_detector.analyze(samples=samples)
                    observer.on_next(bpm)
                except Exception as e:
                    observer.on_error(e)
            return source.pipe(ops.filter(lambda samples: len(samples) > 0)).subscribe(on_next,
                observer.on_error,
                observer.on_completed)
        return rx.create(subscribe)
    return _bpm_detector