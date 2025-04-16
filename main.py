from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
import os
from groq import Groq
from config import GROQ_API_KEY
app = FastAPI()

# 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

@app.get("/transcript/{video_id}")
def getTranscript(video_id: str):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    
    the_text = " ".join([entry['text'] for entry in transcript])
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "You'll be given a transcript of a video and you'll summarize it. Get the key points of the video and return them in a proper format (Introduction, body conclusion). Use bullets and examples if you need to. Transcript: " + the_text + " ",
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

# @app.get("/summary/{the_text}")
# def getSummary(the_text: str):
#     client = Groq(
#         api_key=os.environ.get("GROQ_API_KEY"),
#     )

#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You're an expert assistant that summarizes text. You'll be given a transcript of a video and you'll summarize it. Get the key points of the video and return them in a proper format (Introduction, body conclusion). Use bullets and examples if you need to. ",
#             }
#         ],
#         model="llama-3.3-70b-versatile",
#     )
#     return chat_completion.choices[0].message.content
    
    
@app.get("/")
def read_root():
    return {"Youtube": "Transcript"}