# jarvis.py — Phase 2 JARVIS with UI
from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
from groq import Groq
import edge_tts
import asyncio
import playsound
import tempfile
import os
import subprocess
import webbrowser
import pyautogui
import threading
import time
from ui import set_state, start_ui
from config import GROQ_API_KEY

# ── Start UI ─────────────────────────────────────────────
ui_thread = threading.Thread(target=start_ui, daemon=True)
ui_thread.start()
time.sleep(1)

# ── Setup ────────────────────────────────────────────────
print('Initialising JARVIS systems...')

client = Groq(api_key=GROQ_API_KEY)

print('Loading voice recognition...')
whisper_model = WhisperModel('tiny', device='cpu', compute_type='int8')
print('JARVIS ready.')

conversation_history = []

JARVIS_PERSONALITY = (
    'You are JARVIS, a highly intelligent personal AI assistant installed on a Windows computer. '
    'You are witty, efficient and always address the user as Sir. '
    'Keep responses concise — 1 to 2 sentences unless asked to elaborate. '
    'When the user asks to open an app, search something, or control the PC, '
    'respond naturally and confirm what you are doing.'
)

APPS = {
    'edge':          r'C:\Program Files (x86)\Microsoft\Copilot\Application\148.0.3967.70\msedge.exe',
    'browser':       r'C:\Program Files (x86)\Microsoft\Copilot\Application\148.0.3967.70\msedge.exe',
    'spotify':       r'C:\Users\victus\AppData\Local\Microsoft\WindowsApps\Spotify.exe',
    'vs code':       r'C:\Users\victus\AppData\Local\Programs\Microsoft VS Code\Code.exe',
    'vscode':        r'C:\Users\victus\AppData\Local\Programs\Microsoft VS Code\Code.exe',
    'notepad':       'notepad.exe',
    'calculator':    'calc.exe',
    'file explorer': 'explorer.exe',
    'task manager':  'taskmgr.exe',
    'word':          r'C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE',
    'excel':         r'C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE',
}

# ── PC Control ───────────────────────────────────────────
def open_app(app_name):
    app_name = app_name.lower()
    for key in APPS:
        if key in app_name:
            try:
                subprocess.Popen(APPS[key])
                return f'Opening {key}, Sir.'
            except:
                return f'Could not find {key}, Sir.'
    return None

def search_web(query):
    webbrowser.open(f'https://www.google.com/search?q={query}')
    return f'Searching Google for {query}, Sir.'

def search_youtube(query):
    webbrowser.open(f'https://www.youtube.com/results?search_query={query}')
    return f'Searching YouTube for {query}, Sir.'

def take_screenshot():
    path = r'C:\Users\victus\OneDrive\Desktop\screenshot.png'
    pyautogui.screenshot(path)
    return 'Screenshot saved to your Desktop, Sir.'

def control_volume(action):
    if 'up' in action or 'increase' in action:
        for _ in range(5):
            pyautogui.press('volumeup')
        return 'Volume increased, Sir.'
    elif 'down' in action or 'decrease' in action or 'lower' in action:
        for _ in range(5):
            pyautogui.press('volumedown')
        return 'Volume decreased, Sir.'
    elif 'mute' in action:
        pyautogui.press('volumemute')
        return 'Volume muted, Sir.'

def handle_command(command):
    command_lower = command.lower()
    if 'open' in command_lower:
        result = open_app(command_lower)
        if result:
            return result
    if 'youtube' in command_lower:
        query = command_lower.replace('search youtube for', '').replace('youtube', '').strip()
        return search_youtube(query)
    if 'search' in command_lower or 'google' in command_lower:
        query = command_lower.replace('search google for', '').replace('search for', '').replace('google', '').strip()
        return search_web(query)
    if 'screenshot' in command_lower:
        return take_screenshot()
    if 'volume' in command_lower:
        return control_volume(command_lower)
    return None

# ── Voice ────────────────────────────────────────────────
async def speak_async(text):
    communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
    await communicate.save("jarvis_reply.mp3")

def speak(text):
    set_state("speaking")
    print(f'JARVIS: {text}')
    asyncio.run(speak_async(text))
    playsound.playsound("jarvis_reply.mp3")
    os.remove("jarvis_reply.mp3")

def record_audio(duration=3, sample_rate=16000):
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
    segments, _ = whisper_model.transcribe(
        temp_path,
        language='en',
        condition_on_previous_text=False,
        no_speech_threshold=0.6,
        log_prob_threshold=-1.0
    )
    text = ' '.join([s.text for s in segments]).strip()
    os.remove(temp_path)
    return text

def wait_for_wake_word():
    set_state("sleeping")
    while True:
        try:
            audio, sr_rate = record_audio(duration=3)
            text = transcribe(audio, sr_rate).lower().strip()
            if len(text) > 2:
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
speak('JARVIS online. Say Hey JARVIS to begin.')

try:
    while True:
        detected = wait_for_wake_word()
        if not detected:
            break

        set_state("listening")
        speak('Yes, Sir?')

        audio, sr_rate = record_audio(duration=5)
        command = transcribe(audio, sr_rate)

        if not command or len(command) < 3:
            speak('I did not catch that, Sir.')
            continue

        print(f'You said: {command}')

        if any(w in command.lower() for w in ['okay jarvis stop', 'stop jarvis', 'goodbye jarvis', 'shutdown']):
            speak('Shutting down. Goodbye, Sir.')
            break

        set_state("thinking")
        local_reply = handle_command(command)

        if local_reply:
            speak(local_reply)
        else:
            try:
                reply = ask_groq(command)
                speak(reply)
            except Exception as e:
                print(f'Groq error: {e}')
                speak('I encountered an error, Sir.')

except KeyboardInterrupt:
    speak('Manual shutdown. Goodbye.')
finally:
    print('JARVIS offline.')