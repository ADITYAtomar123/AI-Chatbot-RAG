import os
from PIL import Image
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def load_image(image_file):
    return Image.open(image_file)

def analyze_image(image_file, prompt):

    image = Image.open(image_file)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            prompt,
            image
        ]
    )

    return response.text