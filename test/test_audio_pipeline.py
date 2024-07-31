from live_light_control.domain.pipelines.audio_pipeline import AudioPipeline
from live_light_control.domain.pipelines import TestSource, FileSource
from reactivex.subject import Subject
from reactivex.scheduler import ThreadPoolScheduler
from reactivex import operators as ops
import reactivex as rx
import multiprocessing
import time


def on_spectrum(spectrum_message):
    print("got spectrum")
    #magnitudes = spectrum_message.get_list("magnitude")
    #print([magnitudes[1].get_nth(i) for i in range(10)])
    #phases = spectrum_message.get_list("phase")
    #print([phases[1].get_nth(i) for i in range(10)])


def on_sample(sample):
    print(len(sample))
    print("got sample")

def combine_samples(samples):
    def subscribe(observer, dispose):
        try:
            large_sample = b''
            for sample in samples:
                buffer = sample.get_buffer()
                data = buffer.extract_dup(0, buffer.get_size())
                large_sample += data

            observer.on_next(large_sample)

        except TypeError:
            observer.on_error("Error doubling val:", samples)

    return rx.create(subscribe)


def test_audio_test_src():

    scheduler = ThreadPoolScheduler(multiprocessing.cpu_count())

    source = TestSource()
    spectrum_observer = Subject()
    sample_observer = Subject()
    p = AudioPipeline(source, spectrum_observer, sample_observer)

    spectrum_observer.pipe(ops.observe_on(scheduler)).subscribe(
        on_next=on_spectrum)

    sample_observer.pipe(ops.observe_on(scheduler), ops.buffer_with_count(9), ops.flat_map(combine_samples)).subscribe(
        on_next=on_sample)

    p.start()

    time.sleep(10)

    p.stop()

    assert 0
