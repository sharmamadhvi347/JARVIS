from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os

model = WhisperModel('base', device='cpu', compute_type='int8')

def record_and_check(duration=3, sample_rate=16000):
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        temp_path = f.name
        wav.write(temp_path, sample_rate, audio)
    segments, _ = model.transcribe(temp_path)
    text = ' '.join([s.text for s in segments]).lower()
    os.remove(temp_path)
    return text

print('JARVIS sleeping. Say Hey JARVIS to wake me.')

while True:
    try:
        print('Listening...')
        text = record_and_check(duration=3)
        print(f'Heard: {text}')
        if 'jarvis' in text:
            print('Wake word detected! JARVIS is awake.')
    except KeyboardInterrupt:
        print('Stopping.')
        break