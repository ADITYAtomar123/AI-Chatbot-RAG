import os

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GROQ API KEY
# ============================================================

api_key = os.getenv("GROQ_API_KEY")


if not api_key:

    raise ValueError(
        "GROQ_API_KEY not found. "
        "Please check your .env file."
    )


# ============================================================
# GROQ CLIENT
# ============================================================

client = Groq(
    api_key=api_key
)


# ============================================================
# GET AI RESPONSE
# ============================================================

def get_response(messages):

    system_prompt = {
        "role": "system",
        "content": """
You are a helpful AI assistant.

Rules:

1. Remember the previous conversation.
2. Give clear and accurate answers.
3. If PDF context is provided, use the PDF context
   to answer the user's question.
4. If the question is not related to the PDF,
   answer normally.
5. If the PDF context does not contain the answer,
   say:
   "I couldn't find this information in the uploaded PDF."
6. Use CSV data when CSV context is provided.
7. Use user memory when it is relevant.
8. Be concise and professional.
"""
    }

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                system_prompt
            ] + messages,

            temperature=0.5,

            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"❌ Groq API Error: {str(e)}"