
from live_light_control.domain.pipelines.audio_pipeline import AudioPipeline
from live_light_control.domain.pipelines.sources import TestSource, FileSource
from live_light_control.domain.analysis.audio_analysis_service import AudioAnalysisService
from reactivex.subject import Subject
from reactivex import operators as ops
import reactivex as rx
import multiprocessing
import time
import logging


def test_audio_analysis():
    logging.getLogger('numba').setLevel(logging.WARNING)
    source = TestSource()
    spectrum_observer = Subject()
    sample_observer = Subject()
    p = AudioPipeline(source, spectrum_observer, sample_observer)

    def on_sample(sample):
        source.set_frequency(source.freq + 1)

    sample_observer.pipe(ops.buffer_with_count(1)).subscribe(on_next=on_sample)

    aa = AudioAnalysisService(sample_observer)

    aa.bpm_source.subscribe(on_next=lambda bpm: print(f"bpm: {bpm}"), on_completed=lambda *args: None, on_error=lambda error: print(error))
    aa.key_source.subscribe(on_next=lambda key: print(f"key: {key}"), on_completed=lambda *args: None, on_error=lambda error: print(error))
    p.start()

    time.sleep(20)

    p.stop()

    assert 0