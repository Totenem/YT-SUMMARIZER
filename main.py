from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from youtube_transcript_api import YouTubeTranscriptApi
import os
from groq import Groq
from config import GROQ_API_KEY, SUPABASE_URL, SUPABASE_KEY
from supabase import create_client, Client

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Enpoint to get transcript and summarize it
@app.get("/transcript/{video_id}")
def getTranscript(video_id: str, user_id: str):
    # Check if user exists
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        user_profile = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if not user_profile.data or len(user_profile.data) == 0:
            return {"message": "User not found", "error": "Authentication failed"}
        
        # Get transcript and summarize
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        the_text = " ".join([entry['text'] for entry in transcript])
        client = Groq(
            api_key=GROQ_API_KEY,
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
        
        return {
            "summary": chat_completion.choices[0].message.content
        }
    except Exception as e:
        return {"message": "Failed to process request", "error": str(e)}

# Endpoitnt for Sign up
@app.post("/signup")
def signup(email: str = Body(...), password: str = Body(...), full_name: str = Body(...), username: str = Body(...)):
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
            "email": email
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
def login(email: str = Body(...), password: str = Body(...)):
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