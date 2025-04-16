import os
from groq import Groq
from config import GROQ_API_KEY

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You're an expert assistant that summarizes text. You'll be given a transcript of a video and you'll summarize it. Get the key points of the video and return them in a proper format (Introduction, body conclusion). Use bullets and examples if you need to. ",
        }
    ],
    model="llama-3.3-70b-versatile",
)

print(chat_completion.choices[0].message.content)