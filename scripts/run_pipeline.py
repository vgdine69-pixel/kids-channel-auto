"""
run_pipeline.py - Main pipeline that runs on GitHub's FREE cloud servers
Uses Groq API for AI content generation
"""

import os
import sys
import json
import time
import logging
import pickle
import random
import math
import numpy as np
from datetime import datetime
import requests

os.makedirs("logs", exist_ok=True)
os.makedirs("thumbnails_out", exist_ok=True)
os.makedirs("videos_queue", exist_ok=True)
os.makedirs("temp", exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Pipeline")

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "Wonder Kids World")
VIDEO_TYPE_INPUT = os.environ.get("VIDEO_TYPE", "auto")

def setup_groq():
    return GROQ_API_KEY

def ai_call(api_key: str, prompt: str, max_retries: int = 3) -> str:
    if not api_key:
        logger.error("GROQ_API_KEY not set!")
        return ""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 2048}
    for attempt in range(max_retries):
        try:
            response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            if "429" in str(e): time.sleep(60)
            else: time.sleep(5 * (attempt + 1))
    return ""

def parse_json_response(text: str) -> dict:
    import re
    text = re.sub(r"```json\s*|\s*```", "", text).strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try: return json.loads(text[start:end])
        except: pass
    return {}

VIDEO_TYPES = {
    "fairy_tale_story": {"weight": 25, "emoji": "🧚"},
    "brain_boost": {"weight": 15, "emoji": "🧠"},
    "motivational": {"weight": 15, "emoji": "💪"},
    "learning": {"weight": 20, "emoji": "📚"},
    "good_habits": {"weight": 15, "emoji": "🌈"},
    "adventure_story": {"weight": 10, "emoji": "🗺️"},
}

def pick_video_type() -> str:
    if VIDEO_TYPE_INPUT != "auto" and VIDEO_TYPE_INPUT in VIDEO_TYPES:
        return VIDEO_TYPE_INPUT
    types = list(VIDEO_TYPES.keys())
    weights = [VIDEO_TYPES[t]["weight"] for t in types]
    return random.choices(types, weights=weights, k=1)[0]

def load_topics() -> dict:
    if os.path.exists("data/topics.json"):
        with open("data/topics.json") as f:
            return json.load(f)
    return {"pending": [], "completed": []}

def save_topics(data: dict):
    with open("data/topics.json", "w") as f:
        json.dump(data, f, indent=2)

def get_next_topic(api_key: str, video_type: str, topics: dict) -> str:
    if topics["pending"]:
        return topics["pending"][0]
    logger.info("💡 Generating new topics with AI...")
    prompt = "Generate 40 YouTube video topic ideas for a kids animation channel (ages 3-10). Return ONLY a JSON array of strings."
    response = ai_call(api_key, prompt)
    parsed = parse_json_response(response)
    if isinstance(parsed, list):
        topics["pending"] = parsed
        save_topics(topics)
        return topics["pending"][0] if topics["pending"] else "Amazing Kids Story"
    return "The Magical Adventure Story"

def mark_topic_done(topic: str, topics: dict):
    if topic in topics["pending"]:
        topics["pending"].remove(topic)
    if topic not in topics["completed"]:
        topics["completed"].append(topic)
    save_topics(topics)

CATEGORY_SYSTEM = {
    "fairy_tale_story": "magical fairy tale with lovable animals, moral lesson",
    "brain_boost": "fun brain puzzles, riddles with friendly guide",
    "motivational": "inspiring story about overcoming fear",
    "learning": "educational video about one topic",
    "good_habits": "fun story teaching one good habit",
    "adventure_story": "exciting adventure with brave heroes",
}

def generate_script(api_key: str, topic: str, video_type: str) -> dict:
    logger.info(f"📖 Generating script: {topic} ({video_type})")
    context = CATEGORY_SYSTEM.get(video_type, "kids educational story")
    prompt = f"""Create a 5-minute kids video script. Type: {context}. Topic: {topic}. Return ONLY JSON: {{"title":"title","moral":"moral","characters":[{{"name":"Name","type":"hero","color":"#FF6B9D"}}],"scenes":[{{"scene_number":1,"title":"Scene","duration_seconds":22,"sky_type":"day","bg_color":"#1a0a3e","accent":"#FFD700","narration":"text","character_dialogue":"text","emotion":"happy","sound":"sparkle"}}],"outro_narration":"text","seo_keywords":["k1"]}} Create 12-14 scenes."""
    response = ai_call(api_key, prompt, max_retries=3)
    script = parse_json_response(response)
    if not script or "scenes" not in script:
        script = {"title": f"{topic} | Fun Story", "moral": "Be kind", "characters": [{"name": "Luna", "type": "hero", "color": "#FF6B9D"}], "scenes": [{"scene_number": i, "title": f"Part {i}", "duration_seconds": 23, "sky_type": "magical", "bg_color": "#1a0a3e", "accent": "#FFD700", "narration": f"Story about {topic}", "character_dialogue": "Let's go!", "emotion": "excited", "sound": "sparkle"} for i in range(1, 13)], "outro_narration": "Subscribe!", "seo_keywords": ["kids"]}
    return script

def generate_seo_metadata(api_key: str, script: dict, video_type: str) -> dict:
    title = script.get("title", "")
    moral = script.get("moral", "")
    keywords = script.get("seo_keywords", [])
    desc = f"✨ {title}\n🌟 Welcome to {CHANNEL_NAME}!\n• {moral}\nPerfect for ages 3-10."
    tags = list(set(keywords[:5] + ["kids stories", "cartoon for kids"]))[:25]
    return {"title": title[:60], "description": desc, "tags": tags, "category_id": "27"}

from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp

W, H = 1920, 1080

def get_font(size):
    for p in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def create_video(script: dict, video_type: str) -> str:
    logger.info("🎬 Creating video...")
    scenes = script.get("scenes", [])
    if not scenes: return ""
    video_path = f"videos_queue/{video_type}_{int(time.time())}.mp4"
    clips = []
    for scene in scenes:
        img = Image.new('RGB', (W, H), color=(30, 10, 60))
        draw = ImageDraw.Draw(img)
        draw.text((W//2, H//2), scene.get("title",""), fill=(255,255,255), font=get_font(60), anchor="mm")
        try:
            clip = mp.ImageClip(np.array(img)).set_duration(scene.get("duration_seconds", 22))
            clips.append(clip)
        except: pass
    if not clips: return ""
    try:
        final = mp.concatenate_videoclips(clips, method="compose")
        final.write_videofile(video_path, fps=24, verbose=False, logger=None)
        final.close()
        for c in clips: c.close()
        return video_path
    except: return ""

def create_thumbnail(title: str, video_type: str) -> str:
    img = Image.new('RGB', (1280, 720), color=(30, 10, 60))
    draw = ImageDraw.Draw(img)
    draw.text((640, 360), title, fill=(255,255,255), font=get_font(60), anchor="mm")
    os.makedirs("thumbnails_out", exist_ok=True)
    img.save(f"thumbnails_out/thumb_{int(time.time())}.png")
    return f"thumbnails_out/thumb_{int(time.time())}.png"

def get_youtube_client():
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        import google.auth.exceptions
        
        creds = None
        client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
        
        # Load existing token
        if os.path.exists("token.pickle"):
            try:
                with open("token.pickle", "rb") as f:
                    creds = pickle.load(f)
                logger.info("✅ Loaded existing YouTube credentials")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load token.pickle: {e}")
        
        # If no credentials or they're invalid, try to refresh or create new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    logger.info("🔄 Refreshing expired YouTube token...")
                    creds.refresh(Request())
                    logger.info("✅ Token refreshed successfully")
                except Exception as e:
                    logger.error(f"❌ Token refresh failed: {e}")
                    creds = None
            
            # If still no valid credentials, we can't proceed
            if not creds or not creds.valid:
                if client_id and client_secret:
                    logger.error("❌ Token expired and can't be refreshed. Need new OAuth flow.")
                    logger.error("Run auth_setup.py locally to generate a fresh token.")
                else:
                    logger.error("❌ No YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET set")
                return None
        
        # Build YouTube client with cache disabled to avoid file_cache warning
        youtube = build("youtube", "v3", credentials=creds, cache_discovery=False)
        logger.info("✅ YouTube client created successfully")
        return youtube
        
    except Exception as e:
        logger.error(f"❌ Failed to create YouTube client: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def upload_to_youtube(youtube, video_path, title, description, tags, thumb_path, category_id="27"):
    try:
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
        
        logger.info(f"📤 Uploading video to YouTube: {title}")
        
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags[:20],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": True
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        retries = 0
        while response is None and retries < 5:
            try:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"⬆️ Upload progress: {int(status.progress() * 100)}%")
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    retries += 1
                    logger.warning(f"⚠️ Upload error (retry {retries}/5): {e}")
                    time.sleep(2 ** retries)
                else:
                    raise
        
        if response:
            video_id = response.get("id")
            logger.info(f"✅ Upload complete! Video ID: {video_id}")
            return {"success": True, "video_id": video_id}
        else:
            logger.error("❌ Upload failed after retries")
            return {"success": False}
            
    except HttpError as e:
        logger.error(f"❌ YouTube HTTP error: {e.resp.status} - {e.reason}")
        try:
            error_details = e.error_details if hasattr(e, 'error_details') else e._get_reason()
            logger.error(f"Details: {error_details}")
        except:
            pass
        return {"success": False}
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False}

def main():
    logger.info("🎬 KIDS CHANNEL AUTOMATION")
    logger.info(f"⏰ Started at: {datetime.now().isoformat()}")
    
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set!")
        sys.exit(1)
    
    # Check YouTube credentials
    if not os.environ.get("YOUTUBE_CLIENT_ID") or not os.environ.get("YOUTUBE_CLIENT_SECRET"):
        logger.warning("⚠️ YOUTUBE_CLIENT_ID or YOUTUBE_CLIENT_SECRET not set")
    
    if not os.path.exists("token.pickle"):
        logger.error("❌ token.pickle not found! Run auth_setup.py first to authenticate.")
        sys.exit(1)
    
    api_key = setup_groq()
    topics = load_topics()
    video_type = pick_video_type()
    logger.info(f"🎲 Selected video type: {video_type}")
    
    topic = get_next_topic(api_key, video_type, topics)
    logger.info(f"📋 Topic: {topic}")
    
    script = generate_script(api_key, topic, video_type)
    metadata = generate_seo_metadata(api_key, script, video_type)
    
    video_path = create_video(script, video_type)
    if not video_path:
        logger.error("❌ Video creation failed")
        sys.exit(1)
    logger.info(f"✅ Video created: {video_path}")
    
    yt = get_youtube_client()
    if not yt:
        logger.error("❌ Failed to create YouTube client. Cannot upload.")
        logger.error("💡 To fix this:")
        logger.error("   1. Run 'python auth_setup.py' locally to generate a new token.pickle")
        logger.error("   2. Upload the new token.pickle to GitHub Secrets as YOUTUBE_TOKEN_B64")
        sys.exit(1)
    
    result = upload_to_youtube(yt, video_path, metadata["title"], metadata["description"], metadata["tags"], "", metadata["category_id"])
    
    if result.get("success"):
        mark_topic_done(topic, topics)
        logger.info(f"🎉 DONE! Video uploaded: https://youtube.com/watch?v={result.get('video_id')}")
    else:
        logger.error("❌ Upload failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
