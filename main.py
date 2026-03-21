import requests
import time
import os
import xml.etree.ElementTree as ET

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

SUBREDDITS = ["emotionalintelligence","INFJ","selfimprovement","therapy","mentalhealth","anxiety"]

KEYWORDS = [
    # Can't name the feeling
    "can't name what i'm feeling",
    "don't know what i feel",
    "can't explain my emotions",
    "can't identify my emotion",
    "can't figure out what i'm feeling",
    "feeling something but can't name it",
    "don't know why i feel this way",
    "emotionally confused",
    "can't pinpoint",
    "something feels off",
    "don't know what's wrong with me",

    # Going in circles
    "going in circles",
    "stuck in my feelings",
    "can't get to the root",
    "keep looping",
    "same patterns",
    "can't move forward",

    # Unheard and unseen
    "feeling unheard",
    "no one notices",
    "no one asks how i'm doing",
    "no one checks on me",
    "i'm always the one who",
    "no one bothers",
    "left feeling misunderstood",
    "deeply rejected",

    # Pretending
    "i pretend i'm okay",
    "pretend to be happy",
    "pretend nothing is wrong",
    "i'm not really okay",
    "i'm barely surviving",
    "i'm falling apart",
    "slowly dying inside",

    # Carrying too much
    "carry everyone's emotions",
    "everyone's therapist",
    "tired of being strong",
    "tired of everything",
    "tired of carrying",
    "i just want someone to",
    "numb but don't know why",

    # Lost and confused
    "something is wrong but i don't know",
    "i don't feel like myself",
    "feel empty but don't know why",
    "feel lost but can't explain",
    "can't get out of my head",
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def fetch_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ECOSBot/1.0)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"r/{subreddit} status: {response.status_code}")
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        posts = []
        for entry in entries:
            posts.append({
                "id": entry.find("atom:id", ns).text,
                "title": (entry.find("atom:title", ns).text or ""),
                "content": (entry.find("atom:content", ns).text or "" if entry.find("atom:content", ns) is not None else ""),
                "link": (entry.find("atom:link", ns).attrib.get("href","") if entry.find("atom:link", ns) is not None else "")
            })
        return posts
    except Exception as e:
        print(f"RSS error for r/{subreddit}: {e}")
        return []

def run_bot():
    seen_ids = set()
    print("🟢 ECOS bot started...")
    send_telegram("🟢 ECOS bot is live. Watching Reddit for your people...")
    while True:
        for subreddit in SUBREDDITS:
            posts = fetch_rss(subreddit)
            print(f"r/{subreddit}: {len(posts)} posts fetched")
            for post in posts:
                if post["id"] in seen_ids:
                    continue
                seen_ids.add(post["id"])
                combined = (post["title"] + " " + post["content"]).lower()
                for keyword in KEYWORDS:
                    if keyword.lower() in combined:
                        send_telegram(f"🎯 *ECOS Match!*\n\n*Subreddit:* r/{subreddit}\n*Title:* {post['title']}\n\n*Matched:* `{keyword}`\n\n*Link:* {post['link']}\n\n👉 Respond as Koushik. Be genuine first. Share ECOS only if it feels right.")
                        print(f"✅ Match: {post['title']}")
                        break
            time.sleep(3)
        send_telegram("👀 Checked all subreddits. No matches yet. Checking again in 5 mins...")
        print("⏳ Sleeping 5 minutes...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()
