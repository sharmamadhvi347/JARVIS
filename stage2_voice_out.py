from groq import Groq
import edge_tts
import asyncio
import os
import playsound
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

JARVIS_PERSONALITY = (
    'You are JARVIS, a highly intelligent AI assistant. '
    'You are witty and precise. Always address the user as Sir or Madam. '
    'Keep responses to 2 sentences max unless asked for more.'
)

async def speak_async(text):
    communicate = edge_tts.Communicate(text, voice="en-GB-RyanNeural")
    await communicate.save("jarvis_reply.mp3")

def speak(text):
    print(f'JARVIS: {text}')
    asyncio.run(speak_async(text))
    playsound.playsound("jarvis_reply.mp3")
    os.remove("jarvis_reply.mp3")

def ask_jarvis(user_input):
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': JARVIS_PERSONALITY},
            {'role': 'user',   'content': user_input}
        ]
    )
    return response.choices[0].message.content

speak('JARVIS online. All systems nominal.')

while True:
    user_text = input('You: ')
    if user_text.lower() == 'quit':
        speak('Shutting down. Goodbye, Sir.')
        break
    reply = ask_jarvis(user_text)
    speak(reply)