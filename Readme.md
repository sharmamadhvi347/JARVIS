<div align="center">

<br/>

```
     ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║███████║██████╔╝██║   ██║██║███████╗
██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║
 ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
```

**Just A Rather Very Intelligent System**

*A GPU-accelerated, voice-controlled AI assistant — built from scratch, for fun.*

<br/>

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CUDA](https://img.shields.io/badge/CUDA-13.1-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.6_cu124-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

<br/>

> *"Sometimes you gotta run before you can walk."* — Tony Stark

<br/>

</div>

---

## 🧠 What is JARVIS?

JARVIS is a **fully local, GPU-accelerated, voice-first AI assistant** running entirely on a Windows machine. It wakes on a custom wake word, transcribes your speech using Whisper on an NVIDIA GPU, routes commands through a custom intent engine, thinks with a 70B parameter LLM, and responds in a natural neural voice — all while sitting silently in the background, consuming near-zero resources until called.

This is **not** a wrapper around a voice API. Every component was chosen deliberately, debugged manually, and tuned for performance on consumer hardware.

<br/>

---

## ⚡ The Full Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│   🎙️  YOU SPEAK                                                                │
│         │                                                                       │
│         ▼                                                                       │
│   ┌─────────────────────────────────┐                                          │
│   │   ENERGY GATE                   │                                          │
│   │   RMS < 0.01  →  skip           │  ← Kills hallucination on silence        │
│   │   RMS ≥ 0.01  →  transcribe     │                                          │
│   └──────────────┬──────────────────┘                                          │
│                  │                                                              │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   WAKE WORD DETECTION           │                                          │
│   │   faster-whisper  ·  CPU        │  ← 2s audio chunks, continuous loop     │
│   │   "hey jarvis" detected?        │                                          │
│   └──────────────┬──────────────────┘                                          │
│                  │  ✅ yes                                                      │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   COMMAND RECORDING             │                                          │
│   │   sounddevice  ·  16kHz mono    │  ← 10s window, WAV temp file            │
│   └──────────────┬──────────────────┘                                          │
│                  │                                                              │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   SPEECH TRANSCRIPTION   🟢 GPU │                                          │
│   │   faster-whisper medium         │  ← RTX 3050  ·  CUDA 13.1               │
│   │   float16  ·  ~0.8s latency     │    PyTorch 2.6 cu124                    │
│   └──────────────┬──────────────────┘    1.5GB VRAM  ·  2.5GB free            │
│                  │  "open spotify"                                              │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   INTENT ROUTER                 │                                          │
│   │   Local command?  →  execute    │  ← Zero-latency for PC tasks            │
│   │   Question?       →  LLM        │                                          │
│   └──────────────┬──────────────────┘                                          │
│                  │  complex query                                               │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   AI BRAIN                      │                                          │
│   │   Groq  ·  LLaMA 3.3 70B       │  ← 14,400 free req/day                  │
│   │   Conversation memory (6-turn)  │    <1s inference                        │
│   └──────────────┬──────────────────┘                                          │
│                  │  reply text                                                  │
│                  ▼                                                              │
│   ┌─────────────────────────────────┐                                          │
│   │   VOICE SYNTHESIS               │                                          │
│   │   edge-tts  ·  en-GB-RyanNeural │  ← Microsoft neural voice               │
│   │   playsound playback            │                                          │
│   └──────────────┬──────────────────┘                                          │
│                  │                                                              │
│                  ▼                                                              │
│   🔊  YOU HEAR JARVIS                                                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

<br/>

---

## 🚀 GPU Acceleration — The Technical Detail

The biggest engineering decision in this project was offloading Whisper inference to the GPU. Here is exactly what that means and why it matters.

### The Problem with CPU Transcription

Running Whisper on CPU forces you into a trade-off:
- **Small models** (tiny/base) — fast but poor accuracy, especially on non-native accents
- **Large models** (medium/large) — far better accuracy but 4-8 seconds per transcription on CPU

Neither is acceptable for a real-time assistant.

### The GPU Solution

```
CPU Path (before)                    GPU Path (after)
─────────────────                    ───────────────────────────────
Model:   base (145MB)                Model:   medium (1.5GB)
Device:  CPU                         Device:  NVIDIA RTX 3050
Precision: int8                      Precision: float16 (half precision)
Latency: 3–5 seconds                 Latency: ~0.8 seconds
Accuracy: struggles with accents     Accuracy: handles Indian English well
VRAM:    0MB                         VRAM:    ~1500MB of 4096MB
```

**float16 (half precision)** halves the memory footprint compared to float32 while preserving inference quality — this is the same technique used in production ML systems to fit larger models into constrained VRAM.

```python
# The line that unlocked everything
whisper_model = WhisperModel(
    'medium',
    device='cuda',           # NVIDIA GPU via CUDA
    compute_type='float16'   # Half precision — accuracy vs VRAM trade-off
)
```

### CUDA Stack

```
Application (Python 3.12)
        │
        ▼
faster-whisper 1.2.1
        │
        ▼
CTranslate2 (optimised inference engine)
        │
        ▼
PyTorch 2.6.0+cu124
        │
        ▼
CUDA 13.1
        │
        ▼
NVIDIA RTX 3050 — 4096MB GDDR6
```

<br/>

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.12 | Stable ML ecosystem support |
| Speech-to-text | faster-whisper | 1.2.1 | GPU-accelerated Whisper inference |
| GPU runtime | PyTorch + CUDA | 2.6 / 13.1 | RTX 3050 acceleration |
| Inference engine | CTranslate2 | 4.8.1 | Optimised transformer inference |
| AI brain | Groq API | — | LLaMA 3.3 70B, 14,400 req/day free |
| Voice synthesis | edge-tts | 7.2.8 | Microsoft neural TTS |
| Audio I/O | sounddevice + scipy | — | Microphone capture, WAV encoding |
| PC automation | pyautogui + subprocess | — | App launching, volume, screenshots |
| UI | customtkinter | 6.0.0 | Animated orb, 4 states, 30fps |

<br/>

---

## 🎨 The UI — Four States

A floating dark orb renders at 30fps and changes appearance based on system state. Zero web tech — pure Python canvas.

```
  ◉ SLEEPING        ◉ LISTENING       ◉ THINKING        ◉ SPEAKING
  Deep navy          Electric blue     Spinning gold     Green waves
  Slow dim pulse     Rotating dots     Amber rings       Sound ripples
  "I'm waiting"      "I hear you"      "Processing"      "Responding"
```

Built with `customtkinter` canvas — trigonometry, colour interpolation, and a 30ms animation loop. No libraries, no shortcuts.

<br/>

---

## 📁 Project Structure

```
jarvis/
│
├── 🧠 jarvis.py          # Core pipeline — wake, transcribe, route, respond
├── 🎨 ui.py              # Animated orb — 4 states, canvas, 30fps render loop
├── 🔑 config.py          # API keys — gitignored, never committed
├── 🚫 .gitignore         # config.py, __pycache__, *.mp3 excluded
└── 📖 README.md          # You are here
```

<br/>

---

## ⚙️ Setup & Installation

### Prerequisites

- Windows 10 / 11
- Python 3.12 (not 3.13 or 3.14 — PyTorch has no builds for those yet)
- NVIDIA GPU with CUDA support (CPU fallback available)
- Free Groq API key → [console.groq.com](https://console.groq.com)

### Install

```bash
# Core dependencies
pip install faster-whisper sounddevice scipy groq edge-tts playsound pyautogui customtkinter numpy

# GPU support — PyTorch with CUDA 12.4
pip install torch --index-url https://download.pytorch.org/whl/cu124

# Verify GPU is detected
python -c "import torch; print('GPU ready:', torch.cuda.is_available())"
```

### Configure

```python
# config.py — create this file, never commit it
GROQ_API_KEY = 'gsk_your_key_here'
```

### Run

```bash
python jarvis.py
```

First run downloads the Whisper medium model (~1.5GB). Stored permanently at `~/.cache/huggingface`. All subsequent runs are instant.

<br/>

---

## 🗣️ Usage

| Step | What to do |
|---|---|
| 1 | Run `python jarvis.py` — wait for "JARVIS online" |
| 2 | Say **"Hey JARVIS"** clearly |
| 3 | Wait for **"Yes, Madhvi?"** |
| 4 | Speak your command within 10 seconds |
| 5 | Say **"Okay stop"** to shut down |

### Supported Commands

```bash
# Apps
"Open Spotify"          "Open VS Code"         "Open Notepad"
"Open Edge"             "Open Calculator"      "Open File Explorer"

# Web
"Search YouTube for [anything]"
"Search Google for [anything]"

# System
"Volume up"             "Volume down"          "Mute volume"
"Take a screenshot"

# Conversation
"What is [anything]?"   "Tell me about [topic]"
"Write me [anything]"   "Explain [concept]"

# Shutdown
"Okay stop"             "Goodbye"              "Shutdown"
```

<br/>

---

## 🔧 Key Engineering Decisions

### Why faster-whisper over openai-whisper?
faster-whisper uses CTranslate2 under the hood — a highly optimised inference engine that runs Whisper 2-4x faster than the original implementation and supports GPU acceleration with float16 precision. The original openai-whisper has no native GPU compute type support.

### Why Groq over OpenAI / Gemini?
Groq uses custom LPU (Language Processing Unit) hardware — inference is 10x faster than GPU-based APIs. The free tier gives 14,400 requests/day with no credit card. Gemini's free tier exhausts in minutes of testing. OpenAI requires billing from day one.

### Why sounddevice over PyAudio?
PyAudio has no prebuilt wheel for Python 3.12+ on Windows — it requires Visual C++ build tools and manual compilation. sounddevice is a thin Python wrapper around PortAudio with prebuilt wheels for every platform and Python version. Zero friction.

### Why the energy threshold?
Whisper hallucinates. When given near-silence, it outputs random text — "thank you", "you", common phrases from training data. The energy gate `np.max(np.abs(audio)) < 0.01` checks RMS amplitude before sending audio to Whisper. If the recording is essentially silence, it skips transcription entirely. This eliminated 90% of false wake-word triggers.

<br/>

---

## 🗺️ Roadmap

- [x] Voice wake word detection
- [x] GPU-accelerated Whisper transcription
- [x] Groq LLM integration with conversation memory
- [x] PC control — apps, volume, screenshots, web search
- [x] Animated orb UI with 4 states
- [ ] Fully offline AI with Ollama (llama3 local inference)
- [ ] Piper TTS for offline voice synthesis
- [ ] Persistent memory across sessions
- [ ] Smart home device control
- [ ] Custom wake word training

<br/>

---

## 🧱 Problems I Actually Faced

Real projects break. Here is what broke, why, and how it was fixed.

| Problem | Root Cause | Fix |
|---|---|---|
| PyAudio install fails | No Python 3.12 wheel on Windows | Replaced with sounddevice |
| Picovoice requires company email | Enterprise-only free tier | Dropped entirely, used Whisper for wake word |
| Claude API credits exhausted | Paid from first request | Switched to Groq — 14,400 free/day |
| Gemini quota gone in minutes | 15 RPM free tier limit | Switched to Groq |
| google-generativeai deprecated | Package renamed | Replaced with google-genai, then dropped entirely |
| PyTorch not found for Python 3.14 | No wheels built yet | Downgraded to Python 3.12 |
| pyttsx3 speaks once then freezes | Windows COM threading bug | Replaced with edge-tts + playsound |
| Whisper hallucinates on silence | No speech detected but infers anyway | Added RMS energy gate pre-transcription |
| Wake word triggers on background noise | Whisper too sensitive at base size | Upgraded to medium on GPU — better no-speech threshold |

<br/>

---

## 💡 Why I Built This

I am a third-year CSE student at SRM Institute of Science and Technology. I am an Iron Man fan. I wanted a JARVIS. So I built one.

Not a tutorial. Not a YouTube clone-along. I decided what I wanted to build, figured out what I needed to learn, and built it. Every problem in the table above was a real wall that I hit, diagnosed, and pushed through.

This project is proof that the best way to learn is to build something you actually want to exist — something you will use, not just submit.

**Total cost to run: ₹0/month.**

<br/>

---

## 👩‍💻 Author

**Madhvi**


<br/>

---

<div align="center">

*Built with curiosity, caffeine, and a 4GB GPU.*

</div>