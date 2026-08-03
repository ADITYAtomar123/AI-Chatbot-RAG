import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response(messages):

    system_prompt = {
        "role": "system",
        "content": """
You are a helpful AI assistant.

Rules:
1. Remember previous conversation.
2. If PDF context is provided, answer ONLY from PDF.
3. If answer is not found in PDF, clearly say:
'I couldn't find this information in the uploaded PDF.'
4. Be concise and professional.
"""
    }

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[system_prompt] + messages,
        temperature=0.5,
        max_tokens=1024
    )

    return response.choices[0].message.content