# jarvis.py — Complete Phase 1 JARVIS FINAL
# Groq AI + faster-whisper + sounddevice + edge-tts + playsound

from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
from groq import Groq
import edge_tts
import asyncio
import playsound
import tempfile
import os
from config import GROQ_API_KEY

# ── Setup ────────────────────────────────────────────────
print('Initialising JARVIS systems...')

# Groq AI client
client = Groq(api_key=GROQ_API_KEY)

# faster-whisper for everything — wake word + command transcription
print('Loading voice recognition...')
whisper_model = WhisperModel('base', device='cpu', compute_type='int8')
print('Voice recognition ready.')

# Conversation memory
conversation_history = []

JARVIS_PERSONALITY = (
    'You are JARVIS, a highly intelligent AI assistant. '
    'You are witty, efficient and always address the user as Sir or Madam. '
    'Keep responses concise — 1 to 3 sentences unless asked to elaborate.'
)

# ── Functions ────────────────────────────────────────────
async def speak_async(text):
    communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
    await communicate.save("jarvis_reply.mp3")

def speak(text):
    print(f'JARVIS: {text}')
    asyncio.run(speak_async(text))
    playsound.playsound("jarvis_reply.mp3")
    os.remove("jarvis_reply.mp3")

def record_audio(duration=4, sample_rate=16000):
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
    segments, _ = whisper_model.transcribe(temp_path)
    text = ' '.join([s.text for s in segments]).strip()
    os.remove(temp_path)
    return text

def wait_for_wake_word():
    print('Listening...')
    while True:
        try:
            audio, sr_rate = record_audio(duration=4)
            text = transcribe(audio, sr_rate).lower()
            print(f'Heard: {text}')
            if 'jarvis' in text:
                return True
        except KeyboardInterrupt:
            return False

def ask_groq(user_input):
    messages = [{'role': 'system', 'content': JARVIS_PERSONALITY}]
    messages.extend(conversation_history[-6:])
    messages.append({'role': 'user', 'content': user_input})
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=messages
    )
    reply = response.choices[0].message.content
    conversation_history.append({'role': 'user', 'content': user_input})
    conversation_history.append({'role': 'assistant', 'content': reply})
    return reply

# ── Main Loop ────────────────────────────────────────────
speak('JARVIS online. All systems nominal. Say Hey JARVIS to begin.')
print('Waiting for wake word...')

try:
    while True:
        detected = wait_for_wake_word()
        if not detected:
            break

        speak('Yes, Sir?')

        print('Recording your command...')
        audio, sr_rate = record_audio(duration=6)
        command = transcribe(audio, sr_rate)

        if not command:
            speak('I did not catch that, Sir. Please try again.')
            continue

        print(f'You said: {command}')

        if any(w in command.lower() for w in ['shutdown', 'turn off', 'goodbye', 'exit']):
            speak('Shutting down all systems. Goodbye, Sir.')
            break

        try:
            reply = ask_groq(command)
            speak(reply)
        except Exception as e:
            print(f'Groq error: {e}')
            speak('I encountered an error, Sir. Please try again.')

except KeyboardInterrupt:
    speak('Manual shutdown. Goodbye.')
finally:
    print('JARVIS offline.')