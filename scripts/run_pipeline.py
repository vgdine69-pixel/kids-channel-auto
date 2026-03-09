"""
run_pipeline.py - Main pipeline that runs on GitHub's FREE cloud servers
Full flow: AI Script → Animation Video → Thumbnail → YouTube Upload
Uses only FREE APIs:
  - Google Gemini (free tier - no credit card)
  - YouTube Data API (free 10,000 units/day)
  - gTTS (completely free TTS)
  - PIL + MoviePy (open source, free)
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

# ─── LOGGING ──────────────────────────────────────────────────────────────────
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

# ─── FREE APIS ────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
CHANNEL_NAME = os.environ.get("CHANNEL_NAME", "Wonder Kids World")
VIDEO_TYPE_INPUT = os.environ.get("VIDEO_TYPE", "auto")

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1: FREE AI CONTENT GENERATOR (Google Gemini)
# ═══════════════════════════════════════════════════════════════════════════════

import google.generativeai as genai
def setup_gemini():
    """Configure free Gemini API."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client

def ai_call(client, prompt: str, max_retries: int = 3) -> str:
    """Call Gemini with retry logic."""
    for attempt in range(max_retries):
        try:
                        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                        return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini attempt {attempt+1} failed: {e}")
            time.sleep(5 * (attempt + 1))
        return ""

def parse_json_response(text: str) -> dict:
    """Safely parse JSON from AI response."""
    import re
    # Remove markdown code blocks
    text = re.sub(r"```json\s*|\s*```", "", text).strip()
    # Find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except Exception:
            pass
    # Try array
    start = text.find("[")
    end = text.rfind("]") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except Exception:
            pass
    return {}

# ─── VIDEO TYPE CONFIG ─────────────────────────────────────────────────────────
VIDEO_TYPES = {
    "fairy_tale_story":  {"weight": 25, "emoji": "🧚", "playlist": "Magical Fairy Tales 🧚"},
    "brain_boost":       {"weight": 15, "emoji": "🧠", "playlist": "Brain Games 🧠"},
    "motivational":      {"weight": 15, "emoji": "💪", "playlist": "Inspiring Stories 💪"},
    "learning":          {"weight": 20, "emoji": "📚", "playlist": "Learn With Fun 📚"},
    "good_habits":       {"weight": 15, "emoji": "🌈", "playlist": "Good Habits 🌈"},
    "adventure_story":   {"weight": 10, "emoji": "🗺️", "playlist": "Epic Adventures 🗺️"},
}

def pick_video_type() -> str:
    if VIDEO_TYPE_INPUT != "auto" and VIDEO_TYPE_INPUT in VIDEO_TYPES:
        return VIDEO_TYPE_INPUT
    types = list(VIDEO_TYPES.keys())
    weights = [VIDEO_TYPES[t]["weight"] for t in types]
    return random.choices(types, weights=weights, k=1)[0]

# ─── TOPICS QUEUE ─────────────────────────────────────────────────────────────
def load_topics() -> dict:
    if os.path.exists("data/topics.json"):
        with open("data/topics.json") as f:
            return json.load(f)
    return {"pending": [], "completed": []}

def save_topics(data: dict):
    with open("data/topics.json", "w") as f:
        json.dump(data, f, indent=2)

def get_next_topic(model, video_type: str, topics: dict) -> str:
    if topics["pending"]:
        return topics["pending"][0]
    logger.info("💡 Generating new topics with AI...")
    prompt = f"""Generate 40 YouTube video topic ideas for a kids animation channel (ages 3-10).
Mix: fairy tales, brain puzzles, motivational stories, learning, good habits, adventures.
Be specific and searchable. Return ONLY a JSON array of strings.
Example: ["The Brave Little Lion", "5 Tricky Riddles for Kids", ...]"""
    response = ai_call(model, prompt)
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

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2: AI SCRIPT GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

CATEGORY_SYSTEM = {
    "fairy_tale_story": "magical fairy tale with lovable animals, moral lesson, heartwarming ending",
    "brain_boost": "fun brain puzzles, riddles, memory games with a friendly guide character",
    "motivational": "inspiring story about overcoming fear/failure, leaving kids feeling powerful",
    "learning": "educational video about ONE topic (animals, space, numbers, colors, science)",
    "good_habits": "fun story teaching ONE good habit (brushing teeth, kindness, sleeping on time)",
    "adventure_story": "exciting adventure with brave young heroes, teamwork, twist ending",
}

def generate_script(model, topic: str, video_type: str) -> dict:
    """Generate complete 5-minute kids video script."""
    logger.info(f"📖 Generating script: {topic} ({video_type})")
    context = CATEGORY_SYSTEM.get(video_type, "kids educational story")

    prompt = f"""You are a master children's storyteller. Create a 5-minute animated video script.
Type: {context}
Topic: {topic}
Channel: {CHANNEL_NAME} | Ages: 3-10

Return ONLY valid JSON (no markdown):
{{
  "title": "Catchy SEO title under 60 chars",
  "hook": "Opening 2 sentences to grab attention immediately",
  "moral": "Main lesson of this video",
  "characters": [
    {{"name": "Character name", "type": "hero|villain|helper|narrator|animal", "color": "#FF6B9D"}}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "title": "Scene title 3-4 words",
      "duration_seconds": 22,
      "sky_type": "day|night|sunset|magical|space|forest",
      "bg_color": "#1a0a3e",
      "accent": "#FFD700",
      "narration": "Narrator text 2-3 engaging sentences",
      "character_dialogue": "Main character says something",
      "emotion": "happy|excited|sad|scared|brave|curious|triumph",
      "sound": "sparkle|magic|whoosh|giggle|chime|none"
    }}
  ],
  "outro_narration": "Subscribe/like CTA + moral recap",
  "seo_keywords": ["keyword1","keyword2","keyword3","keyword4","keyword5"]
}}

Create 12-14 scenes totaling 280-300 seconds. Return ONLY the JSON object."""

    response = ai_call(model, prompt, max_retries=3)
    script = parse_json_response(response)

    if not script or "scenes" not in script:
        logger.warning("Using fallback script")
        script = _fallback_script(topic, video_type)

    logger.info(f"✅ Script ready: {script.get('title', topic)}")
    return script

def generate_seo_metadata(model, script: dict, video_type: str) -> dict:
    """Generate world-class SEO metadata."""
    logger.info("🔍 Generating SEO metadata...")
    title = script.get("title", "")
    moral = script.get("moral", "")
    keywords = script.get("seo_keywords", [])
    scenes = script.get("scenes", [])

    # Build chapters
    chapters = "00:00 🎬 Introduction\n"
    t = 25
    for s in scenes[:10]:
        m, sec = t // 60, t % 60
        chapters += f"{m:02d}:{sec:02d} {s.get('title','Scene')}\n"
        t += s.get("duration_seconds", 22)
    chapters += f"0{t//60}:{t%60:02d} 💌 Subscribe for More!\n"

    kw_str = ", ".join(keywords)
    desc = f"""✨ {title}

🌟 Welcome to {CHANNEL_NAME}! New animated story EVERY DAY!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR CHILD WILL LEARN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• {moral or "Important life values through fun stories"}
• Creative thinking and imagination
• New vocabulary and English language skills
• Kindness, bravery, and friendship
• That learning can be FUN!

━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ CHAPTERS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
{chapters}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
💌 JOIN OUR FAMILY:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔔 SUBSCRIBE for a NEW story EVERY DAY!
👍 LIKE if your child smiled!
💬 COMMENT your child's favorite part!
📤 SHARE with other parents!

Perfect for ages 3-10. 100% safe, ad-appropriate content.
{kw_str}, kids stories, children animation, bedtime stories,
moral stories for kids, cartoon for kids, animated stories,
educational videos for kids, stories in english, kids channel

#KidsStories #ChildrenAnimation #KidsEducation #AnimatedStories #BedtimeStories
#MoralStories #KidsChannel #CartoonForKids #StoriesForKids #KidsLearning
#KidsVideos #AnimatedCartoon #StoryTime #KidsFun #LearnWithFun"""

    tags = list(set(
        keywords[:5] +
        ["kids stories", "children animation", "bedtime stories", "moral stories for kids",
         "cartoon for kids", "animated stories", "kids education", "stories for kids",
         "english stories for kids", "kids channel", "learning videos for kids",
         "animated fairy tales", "kids cartoon", "kids learning", "educational kids"]
    ))[:20]

    return {
        "title": title[:60],
        "description": desc,
        "tags": tags,
        "category_id": "27",
    }

def _fallback_script(topic: str, video_type: str) -> dict:
    return {
        "title": f"{topic} | Fun Story for Kids",
        "hook": "Get ready for an amazing adventure! Something magical is about to happen!",
        "moral": "Be kind, brave, and always believe in yourself!",
        "characters": [{"name": "Luna", "type": "hero", "color": "#FF6B9D"},
                       {"name": "Narrator", "type": "narrator", "color": "#4ECDC4"}],
        "scenes": [{"scene_number": i, "title": f"Part {i}", "duration_seconds": 23,
                    "sky_type": "magical", "bg_color": "#1a0a3e", "accent": "#FFD700",
                    "narration": f"In a magical land, an amazing story about {topic} was unfolding! Our brave hero was ready for anything.",
                    "character_dialogue": "I can do this! Let's go on an adventure!",
                    "emotion": "excited", "sound": "sparkle"} for i in range(1, 13)],
        "outro_narration": "Wasn't that amazing? Subscribe for a new story EVERY day! Hit the like button and the bell!",
        "seo_keywords": ["kids stories", "children animation", topic, "bedtime stories", "cartoon for kids"]
    }

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 3: ANIMATED VIDEO CREATOR
# ═══════════════════════════════════════════════════════════════════════════════

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from gtts import gTTS
import moviepy.editor as mp

W, H = 1920, 1080

SKY_COLORS = {
    "day":       {"top": (100, 180, 255), "bot": (200, 235, 255), "gnd": (60, 140, 50)},
    "night":     {"top": (8, 4, 35),      "bot": (25, 15, 70),    "gnd": (15, 40, 15)},
    "sunset":    {"top": (255, 100, 50),  "bot": (255, 190, 80),  "gnd": (90, 50, 25)},
    "magical":   {"top": (50, 0, 100),    "bot": (130, 25, 180),  "gnd": (35, 0, 70)},
    "space":     {"top": (2, 2, 18),      "bot": (8, 4, 35),      "gnd": (12, 8, 25)},
    "forest":    {"top": (40, 90, 40),    "bot": (70, 140, 55),   "gnd": (30, 70, 25)},
    "underwater":{"top": (0, 50, 130),    "bot": (0, 100, 180),   "gnd": (0, 70, 90)},
}

EMOTION_COLORS = {
    "happy": (255, 230, 50), "excited": (255, 150, 0), "sad": (100, 150, 255),
    "scared": (180, 50, 200), "brave": (255, 80, 80), "curious": (0, 220, 180),
    "triumph": (255, 200, 0), "calm": (150, 220, 255),
}

def get_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_gradient_sky(draw, sky_type, frame=0):
    pal = SKY_COLORS.get(sky_type, SKY_COLORS["day"])
    sky_h = int(H * 0.72)
    top, bot, gnd = pal["top"], pal["bot"], pal["gnd"]
    shift = math.sin(frame / 90.0) * 4
    for y in range(sky_h):
        ratio = y / sky_h
        r = int(top[0] + (bot[0]-top[0]) * ratio + shift)
        g = int(top[1] + (bot[1]-top[1]) * ratio + shift * 0.5)
        b = int(top[2] + (bot[2]-top[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b))))
    for y in range(sky_h, H):
        ratio = (y-sky_h) / (H-sky_h)
        r = int(gnd[0] * (1 - ratio*0.4))
        g = int(gnd[1] * (1 - ratio*0.3))
        b = int(gnd[2] * (1 - ratio*0.4))
        draw.line([(0, y), (W, y)], fill=(max(0,r), max(0,g), max(0,b)))

def draw_clouds(draw, frame):
    random.seed(42)
    for i in range(5):
        cx = (random.randint(100, W-100) + frame * (i+1) // 4) % W
        cy = random.randint(50, 180)
        cr = random.randint(70, 130)
        for ox, or_ in [(0, 1.0), (-cr//2, 0.75), (cr//2, 0.75)]:
            draw.ellipse([(cx+ox-cr*or_, cy-cr//2*or_), (cx+ox+cr*or_, cy+cr//2*or_)],
                         fill=(255, 255, 255))

def draw_stars(draw, frame):
    random.seed(7)
    for i in range(70):
        sx = random.randint(0, W)
        sy = random.randint(0, int(H*0.7))
        bright = int(150 + 105 * abs(math.sin((frame/20.0 + i) * 0.8)))
        draw.ellipse([(sx-2, sy-2), (sx+2, sy+2)], fill=(bright, bright, bright))

def draw_sparkles(draw, frame):
    random.seed(frame // 6)
    for _ in range(15):
        px = random.randint(50, W-50)
        py = random.randint(50, H-120)
        pr = random.randint(3, 8)
        c = random.choice([(255,255,100), (255,180,255), (100,255,255), (255,210,100)])
        draw.ellipse([(px-pr, py-pr), (px+pr, py+pr)], fill=c)
        draw.line([(px-pr*2, py), (px+pr*2, py)], fill=c, width=1)
        draw.line([(px, py-pr*2), (px, py+pr*2)], fill=c, width=1)

def draw_trees(draw, sky_type):
    if sky_type in ["space", "underwater"]:
        return
    tc = (25, 100, 25) if sky_type in ["day","forest","sunset"] else (12,40,12)
    gy = int(H*0.72)
    for tx in [80, 200, 340, W-340, W-200, W-80]:
        th = random.randint(100, 200) if False else 150
        draw.rectangle([(tx-7, gy), (tx+7, gy+35)], fill=(90, 55, 18))
        draw.polygon([(tx, gy-th), (tx-60, gy), (tx+60, gy)], fill=tc)
        draw.polygon([(tx, gy-th*3//4), (tx-48, gy-th//4+18), (tx+48, gy-th//4+18)], fill=tc)

def draw_character(draw, cx, cy, char_type, color_hex, emotion, mouth_open, bounce=0):
    cy = int(cy + math.sin(bounce * 0.15) * 8)
    try:
        color = hex_to_rgb(color_hex)
    except Exception:
        color = (255, 107, 157)
    dark = tuple(int(c*0.7) for c in color)
    S = 170

    if char_type == "hero" or char_type == "child":
        skin = (255, 210, 165)
        # Body
        draw.ellipse([(cx-S//2, cy), (cx+S//2, cy+S*2//3)], fill=color, outline=dark, width=2)
        # Head
        draw.ellipse([(cx-S//2+6, cy-S+6), (cx+S//2-6, cy-6)], fill=skin, outline=dark, width=2)
        # Hair
        draw.arc([(cx-S//2+6, cy-S+6), (cx+S//2-6, cy-S//2)], 180, 360, fill=(80,40,20), width=S//8)
        # Eyes
        _draw_eyes(draw, cx, cy-S*2//3, S//10, emotion)
        # Mouth
        _draw_mouth(draw, cx, cy-S//2+S//8, mouth_open)
        # Cheeks
        draw.ellipse([(cx-S//3, cy-S//3), (cx-S//8, cy-S//8)], fill=(255,150,150,100))
        draw.ellipse([(cx+S//8, cy-S//3), (cx+S//3, cy-S//8)], fill=(255,150,150,100))
        # Legs
        draw.rounded_rectangle([(cx-S//4-4, cy+S*2//3), (cx-4, cy+S)], radius=8, fill=skin)
        draw.rounded_rectangle([(cx+4, cy+S*2//3), (cx+S//4+4, cy+S)], radius=8, fill=skin)

    elif char_type == "animal":
        # Cute round animal (bunny-style)
        # Ears
        for ex in [cx-S//3, cx+S//3]:
            draw.ellipse([(ex-S//7, cy-S-S//3), (ex+S//7, cy-S//4)], fill=color, outline=dark, width=2)
            draw.ellipse([(ex-S//11, cy-S-S//5), (ex+S//11, cy-S//3+5)], fill=(255,200,200))
        # Body
        draw.ellipse([(cx-S//2, cy), (cx+S//2, cy+S*2//3)], fill=color, outline=dark, width=2)
        # Head
        draw.ellipse([(cx-S//2, cy-S), (cx+S//2, cy)], fill=color, outline=dark, width=2)
        # Nose
        draw.ellipse([(cx-S//10, cy-S//2+S//10), (cx+S//10, cy-S//3)], fill=(255,150,150))
        # Eyes
        _draw_eyes(draw, cx, cy-S*3//4, S//10, emotion)
        # Mouth
        _draw_mouth(draw, cx, cy-S//3, mouth_open)
        # Cheeks
        draw.ellipse([(cx-S//3, cy-S//4), (cx-S//8, cy)], fill=(255,180,180,80))
        draw.ellipse([(cx+S//8, cy-S//4), (cx+S//3, cy)], fill=(255,180,180,80))
        # Tail
        draw.ellipse([(cx+S//3, cy+S//3), (cx+S//2+4, cy+S//2+4)], fill=(255,255,255))

    elif char_type == "villain":
        # Spiky villain character
        draw.polygon([(cx, cy-S*4//3), (cx-S//3, cy-S), (cx+S//3, cy-S)], fill=dark)
        draw.ellipse([(cx-S//2, cy-S-5), (cx+S//2, cy+S//5)], fill=dark, outline=color, width=3)
        draw.ellipse([(cx-S//2, cy-S), (cx+S//2, cy)], fill=color, outline=dark, width=2)
        _draw_eyes(draw, cx, cy-S*3//4, S//10, "scared")  # Villain has shifty eyes
        _draw_mouth(draw, cx, cy-S//3, mouth_open, villain=True)
        draw.ellipse([(cx-S//2, cy+S//5), (cx+S//2, cy+S)], fill=color, outline=dark, width=2)

    else:  # narrator/wizard
        # Wise character with robe
        draw.polygon([(cx-S//2, cy), (cx+S//2, cy), (cx+S*2//3, cy+S), (cx-S*2//3, cy+S)], fill=color)
        # Stars on robe
        for sx, sy in [(cx-S//4, cy+S//3), (cx+S//5, cy+S//2)]:
            _draw_star(draw, sx, sy, S//12, (255,220,50))
        # Hat
        draw.polygon([(cx, cy-S*3//2), (cx-S//3, cy-S), (cx+S//3, cy-S)], fill=dark)
        draw.ellipse([(cx-S//2, cy-S-10), (cx+S//2, cy-S+10)], fill=dark)
        # Head
        draw.ellipse([(cx-S//3, cy-S+5), (cx+S//3, cy-5)], fill=(255,210,165))
        _draw_eyes(draw, cx, cy-S*3//4, S//12, emotion)
        _draw_mouth(draw, cx, cy-S//2+S//8, mouth_open)

def _draw_eyes(draw, cx, cy, er, emotion):
    for side in [-1, 1]:
        ex = cx + side * (er * 2)
        if emotion in ["happy"]:
            draw.arc([(ex-er, cy-er), (ex+er, cy+er//2)], 200, 340, fill=(40,20,10), width=3)
            draw.ellipse([(ex-er//3, cy-er//3), (ex, cy)], fill=(255,255,255))
        elif emotion in ["excited", "triumph"]:
            draw.ellipse([(ex-er, cy-er), (ex+er, cy+er)], fill=(40,20,10))
            draw.ellipse([(ex-er//3, cy-er//3), (ex+er//3, cy+er//3)], fill=(255,255,255))
        elif emotion == "sad":
            draw.arc([(ex-er, cy-er//3), (ex+er, cy+er*2)], 200, 340, fill=(40,20,10), width=3)
        elif emotion in ["scared", "curious"]:
            draw.ellipse([(ex-er, cy-er), (ex+er, cy+er)], fill=(255,255,255), outline=(40,20,10), width=2)
            draw.ellipse([(ex-er//3, cy-er//3), (ex+er//3, cy+er//3)], fill=(40,20,10))
        elif emotion in ["brave", "determined"]:
            draw.line([(ex-er, cy-er), (ex+er, cy-er//2)], fill=(40,20,10), width=3)
            draw.arc([(ex-er, cy-er//2), (ex+er, cy+er)], 180, 360, fill=(40,20,10), width=3)
        else:
            draw.ellipse([(ex-er, cy-er), (ex+er, cy+er)], fill=(40,20,10))
            draw.ellipse([(ex-er//3, cy-er//3), (ex, cy)], fill=(255,255,255))

def _draw_mouth(draw, cx, cy, mouth_open, villain=False):
    w, h = 30, 18
    if villain:
        draw.arc([(cx-w, cy-h), (cx+w, cy+h)], 180, 360, fill=(40,20,10), width=3)
        return
    if mouth_open > 0.5:
        draw.ellipse([(cx-w, cy-h), (cx+w, cy+h)], fill=(40,20,10))
        draw.ellipse([(cx-w+4, cy-h+4), (cx+w-4, cy+h-4)], fill=(200,60,60))
    elif mouth_open > 0:
        draw.arc([(cx-w, cy-h), (cx+w, cy+h)], 0, 180, fill=(40,20,10), width=3)
        draw.ellipse([(cx-w//2, cy-h//2), (cx+w//2, cy)], fill=(200,60,60))
    else:
        draw.arc([(cx-w, cy-h//2), (cx+w, cy+h)], 0, 180, fill=(40,20,10), width=3)

def _draw_star(draw, cx, cy, r, color):
    pts = []
    for i in range(10):
        a = math.pi * i / 5 - math.pi / 2
        ri = r if i % 2 == 0 else r // 2
        pts.extend([cx + ri*math.cos(a), cy + ri*math.sin(a)])
    draw.polygon(pts, fill=color)

def render_frame(scene, chars, frame, total_frames, narration_progress, lip_open, bounce):
    img = Image.new("RGB", (W, H), (0,0,0))
    draw = ImageDraw.Draw(img)
    sky = scene.get("sky_type", "day")
    emotion = scene.get("emotion", "happy")
    accent = scene.get("accent", "#FFD700")

    draw_gradient_sky(draw, sky, frame)
    if sky in ["night", "magical", "space"]:
        draw_stars(draw, frame)
    if sky in ["day", "sunset", "forest"]:
        draw_clouds(draw, frame)
    draw_trees(draw, sky)
    if sky == "magical" or emotion in ["triumph", "excited"]:
        draw_sparkles(draw, frame)

    # Draw characters
    positions = [(W//2, H//2-80)] if len(chars) == 1 else \
                [(W//3, H//2-60), (W*2//3, H//2-60)] if len(chars) == 2 else \
                [(W//4, H//2-60), (W//2, H//2-80), (W*3//4, H//2-60)]

    for i, char in enumerate(chars[:3]):
        cx, cy = positions[min(i, len(positions)-1)]
        draw_character(draw, cx, cy,
                      char.get("type", "hero"),
                      char.get("color", "#FF6B9D"),
                      emotion,
                      lip_open if i == 0 else 0,
                      bounce + i * 0.5)

    # Subtitle box
    narration = scene.get("narration", "")
    if narration and narration_progress > 0:
        _draw_subtitle(draw, narration, accent, narration_progress)

    # Scene title (first 1.5s)
    progress = frame / max(total_frames, 1)
    if frame < 45:
        _draw_scene_title(draw, scene.get("title", ""), min(1.0, frame / 25.0))

    # Watermark
    _draw_watermark(draw)

    return img

def _draw_subtitle(draw, text, accent_hex, progress):
    try:
        ac = hex_to_rgb(accent_hex)
    except Exception:
        ac = (255, 200, 0)
    font = get_font(38)
    words = text.split()
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if draw.textbbox((0,0), " ".join(cur), font=font)[2] > W-120 and len(cur) > 1:
            lines.append(" ".join(cur[:-1]))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))

    total_chars = sum(len(l) for l in lines)
    show = int(total_chars * min(1.0, progress))

    bh = len(lines) * 52 + 20
    y = H - bh - 20
    draw.rounded_rectangle([(55, y-10), (W-55, y+bh)], radius=14, fill=(0,0,0,185))
    draw.rectangle([(55, y-10), (66, y+bh)], fill=ac)

    char_count = 0
    for i, line in enumerate(lines):
        shown = ""
        for ch in line:
            if char_count < show:
                shown += ch; char_count += 1
            else:
                break
        char_count += 1
        draw.text((78+2, y+i*52+2), shown, font=font, fill=(0,0,0,200))
        draw.text((78, y+i*52), shown, font=font, fill=(255,255,240))

def _draw_scene_title(draw, title, alpha):
    font = get_font(48, bold=True)
    c = int(alpha * 255)
    draw.text((W//2, 50), title, font=font, fill=(255,240,80,c), anchor="mm")

def _draw_watermark(draw):
    font = get_font(24, bold=False)
    draw.rounded_rectangle([(W-280, H-44), (W-20, H-12)], radius=6, fill=(0,0,0,120))
    draw.text((W-270, H-40), f"● {CHANNEL_NAME}", font=font, fill=(200,200,200))

def generate_tts(text, filename, lang="en", tld="com") -> float:
    """Generate free TTS audio. Returns duration estimate."""
    try:
        tts = gTTS(text=text, lang=lang, tld=tld, slow=False)
        tts.save(filename)
        return max(3.0, len(text.split()) / 2.6)
    except Exception as e:
        logger.warning(f"TTS failed: {e}")
        return len(text.split()) / 2.6

def create_video(script: dict, video_type: str) -> str:
    """Create complete animated video. Returns path."""
    import time as time_mod
    title = script.get("title", "Kids Story")
    scenes = script.get("scenes", [])
    characters = script.get("characters", [])
    fps = 24

    ts = int(time_mod.time())
    output = f"videos_queue/video_{ts}.mp4"
    logger.info(f"🎬 Creating video: {title} ({len(scenes)} scenes)")

    clips = []
    temp_files = []

    # INTRO CLIP (5s)
    intro_clip = _create_intro_clip(script, characters, fps, temp_files)
    if intro_clip:
        clips.append(intro_clip)

    # SCENE CLIPS
    for i, scene in enumerate(scenes):
        narration = scene.get("narration", "")
        dialogue = scene.get("character_dialogue", "")
        full_text = f"{narration} {dialogue}".strip()

        audio_path = f"temp/audio_{i:03d}.mp3"
        temp_files.append(audio_path)
        dur = generate_tts(full_text, audio_path)
        duration = max(scene.get("duration_seconds", 22), dur + 0.6)
        total_frames = int(duration * fps)

        frames = []
        bounce = 0.0
        for f in range(total_frames):
            progress = f / total_frames
            bounce += 1
            lip = 0.8 if (f % 8) < 4 and progress > 0.05 else 0.0
            sub_prog = min(1.0, f / (fps * 2.5))
            frame_img = render_frame(scene, characters, f, total_frames, sub_prog, lip, bounce)
            frames.append(np.array(frame_img))

        try:
            clip = mp.ImageSequenceClip(frames, fps=fps)
            audio_clip = mp.AudioFileClip(audio_path)
            clip = clip.set_audio(audio_clip).set_duration(max(duration, audio_clip.duration + 0.4))
            clips.append(clip)
            logger.info(f"  ✅ Scene {i+1}/{len(scenes)} done ({duration:.1f}s)")
        except Exception as e:
            logger.warning(f"  Scene {i+1} error: {e}")

    # OUTRO CLIP (8s)
    outro_clip = _create_outro_clip(script, fps, temp_files)
    if outro_clip:
        clips.append(outro_clip)

    if not clips:
        logger.error("No clips!")
        return ""

    logger.info(f"🎞️ Assembling {len(clips)} clips...")
    try:
        final = mp.concatenate_videoclips(clips, method="compose")
        final.write_videofile(output, fps=fps, codec="libx264", audio_codec="aac",
                              bitrate="3500k", verbose=False, logger=None)
        final.close()
    except Exception as e:
        logger.error(f"Render error: {e}")
        return ""

    for f in temp_files:
        try:
            os.remove(f)
        except Exception:
            pass

    logger.info(f"✅ Video: {output}")
    return output

def _create_intro_clip(script, characters, fps, temp_files):
    title = script.get("title", "Kids Story")
    hook = script.get("hook", "")
    dur = 5.0
    frames = []
    for f in range(int(dur * fps)):
        p = f / (dur * fps)
        img = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(img)
        for y in range(H):
            r = int(20 + 50 * y/H + math.sin(f/20)*8)
            g = int(5 + 20 * y/H)
            b = int(80 + 60 * y/H + math.sin(f/15+1)*8)
            draw.line([(0,y),(W,y)], fill=(min(255,max(0,r)), min(255,g), min(255,max(0,b))))
        draw_stars(draw, f)
        draw_sparkles(draw, f)
        font_ch = get_font(64, bold=True)
        font_t = get_font(72, bold=True)
        a = min(1.0, p * 2.5)
        # Channel name
        cn = CHANNEL_NAME.upper()
        bbox = draw.textbbox((0,0), cn, font=font_ch)
        cx = (W - (bbox[2]-bbox[0])) // 2
        draw.text((cx, H//2-110), cn, font=font_ch,
                  fill=(int(255*a), int(200*a), int(50*a)))
        # Title
        a2 = min(1.0, max(0, (p-0.25)*2.5))
        words = title.split()
        lines, cur = [], []
        for w in words:
            cur.append(w)
            if draw.textbbox((0,0)," ".join(cur),font=font_t)[2] > W-200 and len(cur)>1:
                lines.append(" ".join(cur[:-1])); cur=[w]
        if cur: lines.append(" ".join(cur))
        yt = H//2
        for line in lines[:2]:
            bbox = draw.textbbox((0,0), line, font=font_t)
            lx = (W-(bbox[2]-bbox[0]))//2
            draw.text((lx+2, yt+2), line, font=font_t, fill=(0,0,0,180))
            draw.text((lx, yt), line, font=font_t, fill=(int(255*a2),int(255*a2),int(255*a2)))
            yt += 90
        frames.append(np.array(img))
    clip = mp.ImageSequenceClip(frames, fps=fps)
    if hook:
        af = "temp/intro.mp3"
        temp_files.append(af)
        d = generate_tts(hook, af)
        try:
            audio = mp.AudioFileClip(af)
            clip = clip.set_audio(audio).set_duration(max(dur, audio.duration+0.4))
        except Exception:
            pass
    return clip

def _create_outro_clip(script, fps, temp_files):
    narration = script.get("outro_narration", f"Subscribe to {CHANNEL_NAME} for a new story EVERY day! Hit like and the bell!")
    dur = 8.0
    frames = []
    for f in range(int(dur*fps)):
        p = f / (dur*fps)
        img = Image.new("RGB", (W, H))
        draw = ImageDraw.Draw(img)
        for y in range(H):
            draw.line([(0,y),(W,y)], fill=(max(0,int(20+25*y/H)), max(0,int(8+12*y/H)), max(0,int(80+40*y/H))))
        draw_stars(draw, f)
        draw_sparkles(draw, f)
        scale = 1.0 + 0.04 * math.sin(f*0.2)
        bw = int(380*scale); bh = int(75*scale)
        bx = (W-bw)//2; by = H//2-30
        draw.rounded_rectangle([(bx,by),(bx+bw,by+bh)], radius=18, fill=(220,30,30))
        font_b = get_font(42, bold=True)
        sub_text = "SUBSCRIBE NOW!"
        sb = draw.textbbox((0,0), sub_text, font=font_b)
        draw.text(((W-(sb[2]-sb[0]))//2, by+16), sub_text, font=font_b, fill=(255,255,255))
        # Channel name
        font_ch = get_font(50, bold=True)
        cn = CHANNEL_NAME
        cb = draw.textbbox((0,0), cn, font=font_ch)
        draw.text(((W-(cb[2]-cb[0]))//2, H//2-120), cn, font=font_ch, fill=(255,200,50))
        # Bell emoji text
        font_em = get_font(36)
        draw.text((W//2, by+bh+30), "🔔 Click the BELL for daily stories!", font=font_em,
                  fill=(255,220,100), anchor="mm")
        frames.append(np.array(img))
    clip = mp.ImageSequenceClip(frames, fps=fps)
    af = "temp/outro.mp3"
    temp_files.append(af)
    generate_tts(narration, af)
    try:
        audio = mp.AudioFileClip(af)
        clip = clip.set_audio(audio).set_duration(max(dur, audio.duration+0.4))
    except Exception:
        pass
    return clip

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 4: 3D THUMBNAIL GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

TW, TH = 1280, 720

THUMB_PALETTES = {
    "fairy_tale_story": {"bg_top":(60,0,120),"bg_bot":(200,80,255),"glow":(255,150,255),"text":(255,255,100),"shadow":(120,0,180)},
    "brain_boost":      {"bg_top":(0,20,80), "bg_bot":(0,100,200), "glow":(0,200,255), "text":(255,255,255),"shadow":(0,50,140)},
    "motivational":     {"bg_top":(140,50,0),"bg_bot":(255,140,0),"glow":(255,210,80),"text":(255,255,255),"shadow":(130,40,0)},
    "learning":         {"bg_top":(0,60,0),  "bg_bot":(50,180,70),"glow":(120,255,80),"text":(255,255,255),"shadow":(0,70,10)},
    "good_habits":      {"bg_top":(0,70,140),"bg_bot":(80,190,255),"glow":(180,230,255),"text":(255,255,100),"shadow":(0,50,110)},
    "adventure_story":  {"bg_top":(80,20,0),"bg_bot":(200,80,0),"glow":(255,140,40),"text":(255,255,255),"shadow":(90,25,0)},
}

def create_thumbnail(title: str, video_type: str) -> str:
    pal = THUMB_PALETTES.get(video_type, THUMB_PALETTES["fairy_tale_story"])
    img = Image.new("RGB", (TW, TH))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background
    top, bot = pal["bg_top"], pal["bg_bot"]
    for y in range(TH):
        ratio = y / TH
        r = int(top[0]+(bot[0]-top[0])*ratio)
        g = int(top[1]+(bot[1]-top[1])*ratio)
        b = int(top[2]+(bot[2]-top[2])*ratio)
        draw.line([(0,y),(TW,y)], fill=(r,g,b))

    # Sparkles
    random.seed(77)
    for _ in range(30):
        px,py = random.randint(20,TW-20), random.randint(20,TH-20)
        pr = random.randint(3,9)
        c = random.choice([(255,255,120),(255,180,255),(120,255,255),(255,210,80)])
        draw.ellipse([(px-pr,py-pr),(px+pr,py+pr)], fill=c)
        draw.line([(px-pr*2,py),(px+pr*2,py)], fill=c, width=1)
        draw.line([(px,py-pr*2),(px,py+pr*2)], fill=c, width=1)

    # Glowing border
    glow = pal["glow"]
    for i in range(0, 24, 4):
        draw.rectangle([(i,i),(TW-i,TH-i)], outline=(*glow, int(180*(1-i/24))), width=3)

    # Main 3D text
    words = title.upper().split()
    lines, cur = [], []
    font_main = get_font(120, bold=True)
    for w in words:
        cur.append(w)
        test = " ".join(cur)
        if draw.textbbox((0,0),test,font=font_main)[2] > TW*0.85 and len(cur)>1:
            lines.append(" ".join(cur[:-1])); cur=[w]
    if cur: lines.append(" ".join(cur))

    total_h = len(lines) * 130
    y_start = (TH - total_h) // 2 - 20

    shadow = pal["shadow"]
    text_color = pal["text"]

    for line in lines[:3]:
        bbox = draw.textbbox((0,0), line, font=font_main)
        lx = (TW-(bbox[2]-bbox[0]))//2
        # 3D depth layers
        for d in range(7, 0, -1):
            f = d/7
            sc = (int(shadow[0]*f), int(shadow[1]*f), int(shadow[2]*f))
            draw.text((lx+d, y_start+d), line, font=font_main, fill=sc)
        # Glow
        for gd in [8, 5, 3]:
            draw.text((lx, y_start), line, font=font_main, fill=(*glow, 60))
        # White highlight
        draw.text((lx-1, y_start-1), line, font=font_main, fill=(255,255,255,70))
        # Main text
        draw.text((lx, y_start), line, font=font_main, fill=text_color)
        y_start += 130

    # Channel name badge
    font_ch = get_font(34, bold=True)
    ch_text = f"  {CHANNEL_NAME}  "
    bbox = draw.textbbox((0,0), ch_text, font=font_ch)
    tw = bbox[2]-bbox[0]
    bx = (TW-tw)//2
    draw.rounded_rectangle([(bx-8, TH-58),(bx+tw+8, TH-12)], radius=8, fill=(0,0,0,180))
    draw.text((bx, TH-54), ch_text, font=font_ch, fill=pal["glow"])

    # "NEW!" badge
    draw.ellipse([(TW-120, 10),(TW-10, 100)], fill=pal.get("badge",(255,220,0)) if "badge" in pal else (255,220,0),
                 outline=(255,255,255), width=3)
    font_badge = get_font(26, bold=True)
    draw.text((TW-65, 55), "NEW!", font=font_badge, fill=(20,20,20), anchor="mm")

    # Vignette
    for i in range(60):
        alpha = int(180 * (i/60)**2)
        draw.rectangle([(i,i),(TW-i,TH-i)], outline=(0,0,0,alpha), width=2)

    img = ImageEnhance.Color(img).enhance(1.3)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    img = img.filter(ImageFilter.SHARPEN)

    import time as t
    path = f"thumbnails_out/thumb_{int(t.time())}.jpg"
    img.save(path, "JPEG", quality=96)
    logger.info(f"🖼️ Thumbnail: {path}")
    return path

# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 5: YOUTUBE UPLOADER (FREE API)
# ═══════════════════════════════════════════════════════════════════════════════

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

YT_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

def get_youtube_client():
    """Get authenticated YouTube API client."""
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
        return build("youtube", "v3", credentials=creds)

    if creds and creds.valid:
        return build("youtube", "v3", credentials=creds)

    logger.error("❌ YouTube auth token missing or expired! Run auth_setup.py locally first.")
    return None

def upload_to_youtube(yt, video_path, title, description, tags, thumbnail_path=None, category_id="27") -> dict:
    """Upload video to YouTube using free API."""
    try:
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags[:500],
                "categoryId": category_id,
            },
            "status": {"privacyStatus": "public"},
        }
        media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True,
                                chunksize=1024*1024*10)
        request = yt.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"   Upload: {int(status.progress()*100)}%")

        video_id = response["id"]

        # Set thumbnail
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                yt.thumbnails().set(videoId=video_id,
                                    media_body=MediaFileUpload(thumbnail_path)).execute()
                logger.info("🖼️ Thumbnail set!")
            except Exception as e:
                logger.warning(f"Thumbnail failed: {e}")

        # Pin first comment
        try:
            yt.commentThreads().insert(
                part="snippet",
                body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {
                    "textOriginal": f"🌟 Which character was your favorite? Tell us below! 👇\n🔔 Subscribe for a new story EVERY DAY! ✨"
                }}}}
            ).execute()
        except Exception:
            pass

        logger.info(f"✅ UPLOADED! https://youtube.com/watch?v={video_id}")
        return {"success": True, "video_id": video_id}

    except HttpError as e:
        logger.error(f"❌ Upload error: {e}")
        return {"success": False, "error": str(e)}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    logger.info("=" * 65)
    logger.info("🎬 KIDS CHANNEL AUTOMATION - FREE CLOUD PIPELINE")
    logger.info(f"   Channel: {CHANNEL_NAME}")
    logger.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    logger.info("=" * 65)

    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY secret not set!")
        sys.exit(1)

    # Setup
    model = setup_gemini()
    topics = load_topics()

    # 1. Pick type & topic
    video_type = pick_video_type()
    topic = get_next_topic(model, video_type, topics)
    logger.info(f"📌 {video_type}: {topic}")

    # 2. Generate script
    script = generate_script(model, topic, video_type)

    # 3. Generate SEO metadata
    metadata = generate_seo_metadata(model, script, video_type)
    logger.info(f"📊 Title: {metadata['title']}")

    # 4. Create video
    video_path = create_video(script, video_type)
    if not video_path:
        logger.error("❌ Video creation failed!")
        sys.exit(1)

    # 5. Create thumbnail
    thumb_path = create_thumbnail(metadata["title"], video_type)

    # 6. Upload to YouTube
    yt = get_youtube_client()
    if not yt:
        logger.error("❌ YouTube not authenticated!")
        sys.exit(1)

    result = upload_to_youtube(
        yt, video_path,
        metadata["title"],
        metadata["description"],
        metadata["tags"],
        thumb_path,
        metadata["category_id"]
    )

    if result.get("success"):
        mark_topic_done(topic, topics)
        logger.info("🎉 PIPELINE COMPLETE!")
    else:
        logger.error(f"Upload failed: {result.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
