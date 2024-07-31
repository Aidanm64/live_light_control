import librosa

file_path = "/app/data/sample.wav"


y, sr = librosa.load(file_path)

tempo, beats = librosa.beat.beat_track(y=y)

print(tempo)
