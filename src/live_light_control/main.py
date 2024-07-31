
from live_light_control.domain.pipelines import AudioPipeline, FileSource
from live_light_control.domain.analysis import AudioAnalysisService
from live_light_control.infrastructure.rpi_room_controller import RPiRoomController
from live_light_control.domain.devices.controller import RoomController
from live_light_control.utils import map_range

import time
import logging
logging.getLogger('numba').setLevel(logging.WARNING)


def run():

    source = FileSource()
    pipeline = AudioPipeline(source)

    analysis = AudioAnalysisService(sample_source=pipeline.sample_source)
    controller = RoomController()

    controller.set_global_color("Green")
    controller.set_global_intensity(255)

    def key_to_room_color(key):
        print(key)
        if key[1] == "major":
            controller.set_global_color("Blue", ms=3000)
        elif key[1] == "minor":
            controller.set_global_color("Red", ms=3000)
        else:
            return

    def bpm_to_brigtness(bpm):
        print(bpm)
        intensity = int(map_range(bpm, 60, 300, 100, 255))
        controller.set_global_intensity(intensity, ms=2000)


    def print_spectral_features(features):
        print(f'rms: {features.rms}, centroid: {features.centroid}, flatness: {features.flatness}')

    analysis.key_source.subscribe(
        on_next=key_to_room_color,
        on_completed=lambda *args: None,
        on_error=lambda error: print(error))

    analysis.bpm_source.subscribe(
        on_next=bpm_to_brigtness,
        on_completed=lambda *args: None,
        on_error=lambda error: print(error))

    analysis.spectral_feature_source.subscribe(
        on_next=print_spectral_features,
        on_completed=lambda *args: None,
        on_error=lambda error: print(error))

    #def on_sample(sample):
    #    source.set_frequency(source.freq + 1)

    #pipeline.sample_source.subscribe(on_next=on_sample)

    pipeline.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    pipeline.stop()
