from fastapi import FastAPI
from youtube_transcript_api import YouTubeTranscriptApi
import os
from groq import Groq
from config import GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client
app = FastAPI()

# Enpoint to get transcript and summarize it
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

# Endpoitnt for Sign up
@app.post("/signup")
def signup(email: str, password: str, full_name: str, username: str):
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            return {"message": "Signup failed", "error": "Authentication failed"}
            
        user_id = auth_response.user.id
        profile_data = {
            "id": user_id,
            "full_name": full_name,
            "username": username,
            "email": email,
            "tokens": 10000
        }
        
        try:
            profile_response = supabase.table("user_profiles").insert(profile_data).execute()
            return {"message": "Signup successful", "user_id": user_id}
        except Exception as e:
            # If profile creation fails, delete the auth user to maintain consistency
            supabase.auth.admin.delete_user(user_id)
            return {"message": "Profile creation failed", "error": str(e)}
            
    except Exception as e:
        return {"message": "Signup failed", "error": str(e)}

@app.post("/login")
def login(email: str, password: str):
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        autheticate_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        }) 
        
        if not autheticate_response.user:
            return {"message": "Login failed", "error": "Authentication failed"}
        
        user_id = autheticate_response.user.id
        return {"message": "Login successful", "user_id": user_id}

    except Exception as e:
        return {"message": "Login failed", "error": str(e)}
    
@app.get("/")
def read_root():
    return {"Youtube": "Transcript"}