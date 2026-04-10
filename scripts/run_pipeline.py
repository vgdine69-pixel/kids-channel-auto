import requests

def setup_groq():
    """Configure Groq API."""
    return GROQ_API_KEY

def ai_call(api_key: str, prompt: str, max_retries: int = 3) -> str:
    """Call Groq API with retry logic."""
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
  def generate_seo_metadata(api_key: str, script: dict, video_type: str) -> dict:
    """Generate world-class SEO metadata."""
    logger.info("🔍 Generating SEO metadata...")
    title = script.get("title", "")
    moral = script.get("moral", "")
    keywords = script.get("seo_keywords", [])
    scenes = script.get("scenes", [])

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
         VIDEO_TYPES.get(video_type, {}).get("emoji", ""),
         CHANNEL_NAME, "kids fun", "kids cartoon", "english cartoon"] +
        [t.strip() for t in keywords if len(t.strip()) > 3]
    ))[:25]

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
                    "narration": f"In a magical land, an amazing story about {topic} was unfolding!",
                    "character_dialogue": "I can do this! Let's go on an adventure!",
                    "emotion": "excited", "sound": "sparkle"} for i in range(1, 13)],
        "outro_narration": "Wasn't that amazing? Subscribe for a new story EVERY day!",
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
    "magical":
...(truncated)...
