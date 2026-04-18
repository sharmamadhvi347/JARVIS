from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

JARVIS_PERSONALITY = (
    'You are JARVIS, a highly intelligent AI assistant. '
    'You are witty and precise. Always address the user as Madam. '
    'Keep responses concise — no more than 3 sentences unless asked for more.'
)

def ask_jarvis(user_input):
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': JARVIS_PERSONALITY},
            {'role': 'user', 'content': user_input}
        ]
    )
    return response.choices[0].message.content

print('JARVIS brain online. Type your message.')
print('Type quit to exit')

while True:
    user_text = input('You: ')
    if user_text.lower() == 'quit':
        break
    reply = ask_jarvis(user_text)
    print(f'JARVIS: {reply}')
    print()