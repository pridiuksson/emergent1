from fastapi import FastAPI, HTTPException, Body, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import uvicorn
import os
import logging
from pathlib import Path
import requests
from typing import List, Optional
from pydantic import BaseModel
import random

# /backend 
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class PlaylistRequest(BaseModel):
    theme: str
    count: Optional[int] = 10

class Song(BaseModel):
    title: str
    artist: str
    videoId: str
    thumbnail: str

# YouTube API Constants
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
YOUTUBE_API_URL = 'https://www.googleapis.com/youtube/v3/search'

@app.get("/")
async def root():
    return {"message": "Mixtape Generator API"}

# Sample 90s songs to use when no API key is provided - updated with verified embeddable videos
SAMPLE_90S_SONGS = [
    {"title": "Smells Like Teen Spirit", "artist": "Nirvana", "videoId": "hTWKbfoikeg", "thumbnail": "https://i.ytimg.com/vi/hTWKbfoikeg/hqdefault.jpg"},
    {"title": "Waterfalls", "artist": "TLC", "videoId": "8WEtxJ4-sh4", "thumbnail": "https://i.ytimg.com/vi/8WEtxJ4-sh4/hqdefault.jpg"},
    {"title": "Vogue", "artist": "Madonna", "videoId": "GuJQSAiODqI", "thumbnail": "https://i.ytimg.com/vi/GuJQSAiODqI/hqdefault.jpg"},
    {"title": "...Baby One More Time", "artist": "Britney Spears", "videoId": "C-u5WLJ9Yk4", "thumbnail": "https://i.ytimg.com/vi/C-u5WLJ9Yk4/hqdefault.jpg"},
    {"title": "No Scrubs", "artist": "TLC", "videoId": "FrLequ6dUdM", "thumbnail": "https://i.ytimg.com/vi/FrLequ6dUdM/hqdefault.jpg"},
    {"title": "Wannabe", "artist": "Spice Girls", "videoId": "gJLIiF15wjQ", "thumbnail": "https://i.ytimg.com/vi/gJLIiF15wjQ/hqdefault.jpg"},
    {"title": "I Want It That Way", "artist": "Backstreet Boys", "videoId": "4fndeDfaWCg", "thumbnail": "https://i.ytimg.com/vi/4fndeDfaWCg/hqdefault.jpg"},
    {"title": "Gangsta's Paradise", "artist": "Coolio", "videoId": "fPO76Jlnz6c", "thumbnail": "https://i.ytimg.com/vi/fPO76Jlnz6c/hqdefault.jpg"},
    {"title": "Wonderwall", "artist": "Oasis", "videoId": "bx1Bh8ZvH84", "thumbnail": "https://i.ytimg.com/vi/bx1Bh8ZvH84/hqdefault.jpg"},
    {"title": "Ms. Jackson", "artist": "OutKast", "videoId": "MYxAiK6VnXw", "thumbnail": "https://i.ytimg.com/vi/MYxAiK6VnXw/hqdefault.jpg"},
    {"title": "U Can't Touch This", "artist": "MC Hammer", "videoId": "otCpCn0l4Wo", "thumbnail": "https://i.ytimg.com/vi/otCpCn0l4Wo/hqdefault.jpg"},
    {"title": "Don't Speak", "artist": "No Doubt", "videoId": "TR3Vdo5etCQ", "thumbnail": "https://i.ytimg.com/vi/TR3Vdo5etCQ/hqdefault.jpg"},
    {"title": "Black Hole Sun", "artist": "Soundgarden", "videoId": "3mbBbFH9fAg", "thumbnail": "https://i.ytimg.com/vi/3mbBbFH9fAg/hqdefault.jpg"},
    {"title": "Barbie Girl", "artist": "Aqua", "videoId": "ZyhrYis509A", "thumbnail": "https://i.ytimg.com/vi/ZyhrYis509A/hqdefault.jpg"},
    {"title": "All Star", "artist": "Smash Mouth", "videoId": "L_jWHffIx5E", "thumbnail": "https://i.ytimg.com/vi/L_jWHffIx5E/hqdefault.jpg"},
    {"title": "Zombie", "artist": "The Cranberries", "videoId": "6Ejga4kJUts", "thumbnail": "https://i.ytimg.com/vi/6Ejga4kJUts/hqdefault.jpg"},
    {"title": "Bitter Sweet Symphony", "artist": "The Verve", "videoId": "1lyu1KKwC74", "thumbnail": "https://i.ytimg.com/vi/1lyu1KKwC74/hqdefault.jpg"},
    {"title": "Virtual Insanity", "artist": "Jamiroquai", "videoId": "4JkIs37a2JE", "thumbnail": "https://i.ytimg.com/vi/4JkIs37a2JE/hqdefault.jpg"},
    {"title": "Sabotage", "artist": "Beastie Boys", "videoId": "z5rRZdiu1UE", "thumbnail": "https://i.ytimg.com/vi/z5rRZdiu1UE/hqdefault.jpg"},
    {"title": "Californication", "artist": "Red Hot Chili Peppers", "videoId": "YlUKcNNmywk", "thumbnail": "https://i.ytimg.com/vi/YlUKcNNmywk/hqdefault.jpg"}
]

@app.post("/api/generate-playlist")
async def generate_playlist(request: PlaylistRequest):
    theme = request.theme.lower()
    count = min(request.count, 15)  # Limit to 15 songs
    
    if not YOUTUBE_API_KEY:
        # No API key, use sample data
        random.shuffle(SAMPLE_90S_SONGS)
        return {"playlist": SAMPLE_90S_SONGS[:count], "message": "Using sample 90s playlist (YouTube API key not configured)"}
    
    try:
        # Use YouTube API to search for videos
        params = {
            'part': 'snippet',
            'q': f'90s music {theme}',
            'type': 'video',
            'videoEmbeddable': 'true',
            'maxResults': 50,  # Get more results to filter
            'key': YOUTUBE_API_KEY
        }
        
        response = requests.get(YOUTUBE_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Process the results
        playlist = []
        for item in data.get('items', [])[:count]:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            thumbnail = item['snippet']['thumbnails']['medium']['url']
            
            playlist.append({
                "title": title,
                "artist": channel,
                "videoId": video_id,
                "thumbnail": thumbnail
            })
        
        return {"playlist": playlist, "message": "Successfully generated playlist"}
    
    except Exception as e:
        logger.error(f"Error in YouTube API: {str(e)}")
        # Fallback to sample data
        random.shuffle(SAMPLE_90S_SONGS)
        return {"playlist": SAMPLE_90S_SONGS[:count], "message": f"Using sample 90s playlist (API error: {str(e)})"}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
