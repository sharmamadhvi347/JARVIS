from groq import Groq
import edge_tts
import pygame
import asyncio
import os
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

JARVIS_PERSONALITY = (
    'You are JARVIS, a highly intelligent AI assistant. '
    'You are witty and precise. Always address the user asMadam. '
    'Keep responses to 2 sentences max unless asked for more.'
)

async def speak_async(text):
    communicate = edge_tts.Communicate(text, voice="en-US-GuyNeural")
    await communicate.save("jarvis_reply.mp3")

def speak(text):
    print(f'JARVIS: {text}')
    asyncio.run(speak_async(text))
    pygame.mixer.init()
    pygame.mixer.music.load("jarvis_reply.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()
    pygame.mixer.quit()
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