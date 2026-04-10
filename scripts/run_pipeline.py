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
import textwrap
import numpy as np
from datetime import datetime
from pathlib import Path
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
    "fairy_tale_story":  {"weight": 25, "emoji": "🧚"},
    "brain_boost":       {"weight": 15, "emoji": "🧠"},
    "motivational":      {"weight": 15, "emoji": "💪"},
    "learning":          {"weight": 20, "emoji": "📚"},
    "good_habits":       {"weight": 15, "emoji": "🌈"},
    "adventure_story":   {"weight": 10, "emoji": "🗺️"},
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
    prompt = "Generate 40 YouTube video topic ideas for a kids animation channel (ages 3-10). Mix: fairy tales, brain puzzles, motivational stories, learning, good habits, adventures. Return ONLY a JSON array of strings."
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
    "fairy_tale_story": "magical fairy tale with lovable animals, moral lesson, heartwarming ending",
    "brain_boost": "fun brain puzzles, riddles, memory games with a friendly guide character",
    "motivational": "inspiring story about overcoming fear/failure, leaving kids feeling powerful",
    "learning": "educational video about ONE topic (animals, space, numbers, colors, science)",
    "good_habits": "fun story teaching ONE good habit (brushing teeth, kindness, sleeping on time)",
    "adventure_story": "exciting adventure with brave young heroes, teamwork, twist ending",
}

def generate_script(api_key: str, topic: str, video_type: str) -> dict:
    logger.info(f"📖 Generating script: {topic} ({video_type})")
    context = CATEGORY_SYSTEM.get(video_type, "kids educational story")
    prompt = f"""You are a master children's storyteller. Create a 5-minute animated video script.
Type: {context}
Topic: {topic}
Channel: {CHANNEL_NAME} | Ages: 3-10
Return ONLY valid JSON: {{"title":"title","hook":"hook","moral":"moral","characters":[{{"name":"Name","type":"hero","color":"#FF6B9D"}}],"scenes":[{{"scene_number":1,"title":"Scene","duration_seconds":22,"sky_type":"day","bg_color":"#1a0a3e","accent":"#FFD700","narration":"text","character_dialogue":"text","emotion":"happy","sound":"sparkle"}}],"outro_narration":"text","seo_keywords":["k1","k2"]}}
Create 12-14 scenes. Return ONLY JSON."""
    response = ai_call(api_key, prompt, max_retries=3)
    script = parse_json_response(response)
    if not script or "scenes" not in script:
        logger.warning("Using fallback script")
        script = _fallback_script(topic, video_type)
    logger.info(f"✅ Script ready: {script.get('title', topic)}")
    return script

def generate_seo_metadata(api_key: str, script: dict, video_type: str) -> dict:
    logger.info("🔍 Generating SEO metadata...")
    title = script.get("title", "")
    moral = script.get("moral", "")
    keywords = script.get("seo_keywords", [])
    desc = f"""✨ {title}
🌟 Welcome to {CHANNEL_NAME}! New animated story EVERY DAY!
🎯 YOUR CHILD WILL LEARN:
• {moral or "Important life values"}
• Creative thinking and imagination
• Kindness, bravery, and friendship

Perfect for ages 3-10. #KidsStories #ChildrenAnimation"""
    tags = list(set(keywords[:5] + ["kids stories", "children animation", "cartoon for kids", "kids channel"]))[:25]
    return {"title": title[:60], "description": desc, "tags": tags, "category_id": "27"}

def _fallback_script(topic: str, video_type: str) -> dict:
    return {
        "title": f"{topic} | Fun Story for Kids",
        "hook": "Get ready for an amazing adventure!",
        "moral": "Be kind, brave, and believe in yourself!",
        "characters": [{"name": "Luna", "type": "hero", "color": "#FF6B9D"}],
        "scenes": [{"scene_number": i, "title": f"Part {i}", "duration_seconds": 23, "sky_type": "magical", "bg_color": "#1a0a3e", "accent": "#FFD700", "narration": f"Story about {topic}", "character_dialogue": "Let's go!", "emotion": "excited", "sound": "sparkle"} for i in range(1, 13)],
        "outro_narration": "Subscribe for a new story EVERY day!",
        "seo_keywords": ["kids stories", "cartoon for kids"]
    }

from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
import moviepy.editor as mp

W, H = 1920, 1080

def get_font(size, bold=True):
    for p in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def create_video(script: dict, video_type: str) -> str:
    logger.info("🎬 Creating animated video...")
    scenes = script.get("scenes", [])
    if not scenes:
        logger.error("No scenes in script!")
        return ""
    os.makedirs("videos_queue", exist_ok=True)
    video_path = f"videos_queue/{video_type}_{int(time.time())}.mp4"
    clips = []
    for i, scene in enumerate(scenes):
        logger.info(f"  Scene {i+1}/{len(scenes)}")
        duration = scene.get("duration_seconds", 22)
        img = Image.new('RGB', (W, H), color=(30, 10, 60))
        draw = ImageDraw.Draw(img)
        draw.text((W//2, H//2), scene.get("title",""), fill=(255,255,255), font=get_font(60), anchor="mm")
        try:
            clip = mp.ImageClip(np.array(img)).set_duration(duration)
            clips.append(clip)
        except: pass
    if not clips:
        logger.error("No clips created!")
        return ""
    try:
        final = mp.concatenate_videoclips(clips, method="compose")
        final.write_videofile(video_path, fps=24, verbose=False, logger=None)
        final.close()
        for c in clips: c.close()
        logger.info(f"✅ Video: {video_path}")
        return video_path
    except Exception as e:
        logger.error(f"Video failed: {e}")
        return ""

def create_thumbnail(title: str, video_type: str) -> str:
    img = Image.new('RGB', (1280, 720), color=(30, 10, 60))
    draw = ImageDraw.Draw(img)
    draw.text((640, 360), title, fill=(255,255,255), font=get_font(60), anchor="mm")
    thumb_path = f"thumbnails_out/thumb_{int(time.time())}.png"
    os.makedirs("thumbnails_out", exist_ok=True)
    img.save(thumb_path)
    return thumb_path

def get_youtube_client():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        if not os.path.exists("token.pickle"):
            logger.error("❌ No token.pickle")
            return None
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
        return build("youtube", "v3", credentials=creds)
    except Exception as e:
        logger.error(f"YouTube auth failed: {e}")
        return None

def upload_to_youtube(youtube, video_path: str, title: str, description: str, tags: list, thumb_path: str, category_id: str = "27") -> dict:
    try:
        logger.info(f"📤 Uploading: {title}")
        request = youtube.videos().insert(
            part="snippet,status",
            body={"snippet": {"title": title, "description": description, "tags": tags[:20], "categoryId": category_id}, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": True}},
            media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
        video_id = response.get("id")
        logger.info(f"✅ Uploaded! Video ID: {video_id}")
        return {"success": True, "video_id": video_id}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return {"success": False, "error": str(e)}

def main():
    logger.info("=" * 50)
    logger.info("🎬 KIDS CHANNEL AUTOMATION")
    logger.info(f"   Channel: {CHANNEL_NAME}")
    logger.info("=" * 50)
    if not GROQ_API_KEY:
        logger.error("❌ GROQ_API_KEY not set!")
        sys.exit(1)
    api_key = setup_groq()
    topics = load_topics()
    video_type = pick_video_type()
    topic = get_next_topic(api_key, video_type, topics)
    logger.info(f"📌 {video_type}: {topic}")
    script = generate_script(api_key, topic, video_type)
    metadata = generate_seo_metadata(api_key, script, video_type)
    video_path = create_video(script, video_type)
    if not video_path:
        logger.error("❌ Video creation failed!")
        sys.exit(1)
    thumb_path = create_thumbnail(metadata["title"], video_type)
    yt = get_youtube_client()
    if not yt:
        logger.error("❌ YouTube not authenticated!")
        sys.exit(1)
    result = upload_to_youtube(yt, video_path, metadata["title"], metadata["description"], metadata["tags"], thumb_path, metadata["category_id"])
    if result.get("success"):
        mark_topic_done(topic, topics)
        logger.info("🎉 PIPELINE COMPLETE!")
    else:
        logger.error(f"Upload failed: {result.get('error')}")

if __name__ == "__main__":
    main()
