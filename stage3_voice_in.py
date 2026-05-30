from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os

print('Loading Whisper model...')
model = WhisperModel('base', device='cpu', compute_type='int8')
print('Whisper ready.')

def record_audio(duration=5, sample_rate=16000):
    print(f'Listening for {duration} seconds...')
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    return audio, sample_rate

def transcribe(audio, sample_rate):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = f.name
        wav.write(temp_path, sample_rate, audio)
    segments, _ = model.transcribe(temp_path)
    text = ' '.join([s.text for s in segments])
    os.remove(temp_path)
    return text.strip()

print('Say something after this message...')
audio, sr = record_audio(duration=5)
text = transcribe(audio, sr)
print(f'You said: {text}')