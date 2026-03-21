import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURATION — only fill in Telegram details
# ─────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

# ─────────────────────────────────────────────
# SUBREDDITS TO MONITOR
# ─────────────────────────────────────────────

SUBREDDITS = [
    "emotionalintelligence",
    "INFJ",
    "selfimprovement",
    "therapy",
    "mentalhealth",
    "anxiety",
]

# ─────────────────────────────────────────────
# KEYWORDS TO WATCH FOR
# ─────────────────────────────────────────────

KEYWORDS = [
    "can't name what i'm feeling",
    "don't know what i feel",
    "can't explain my emotions",
    "going in circles",
    "something feels off",
    "numb but don't know why",
    "can't identify my emotion",
    "don't know why i feel this way",
    "can't figure out what i'm feeling",
    "feeling something but can't name it",
    "emotionally confused",
    "can't pinpoint",
    "stuck in my feelings",
    "can't get to the root",
    "don't know what's wrong with me",
    "something is wrong but i don't know",
]

# ─────────────────────────────────────────────
# SEND TELEGRAM ALERT
# ─────────────────────────────────────────────

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# ─────────────────────────────────────────────
# FETCH NEW POSTS FROM SUBREDDIT
# ─────────────────────────────────────────────

def fetch_new_posts(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=25"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = data["data"]["children"]
            return posts
        else:
            print(f"Status {response.status_code} for r/{subreddit}")
            return []
    except Exception as e:
        print(f"Error fetching r/{subreddit}: {e}")
        return []

# ─────────────────────────────────────────────
# MAIN BOT LOOP
# ─────────────────────────────────────────────

def run_bot():
    seen_ids = set()
    print("🟢 ECOS bot started...")
    send_telegram("🟢 ECOS bot is live. Watching Reddit for your people...")

    while True:
        for subreddit in SUBREDDITS:
            posts = fetch_new_posts(subreddit)

            for post in posts:
                post_data = post["data"]
                post_id = post_data["id"]

                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                title = post_data.get("title", "").lower()
                body = post_data.get("selftext", "").lower()
                combined = title + " " + body

                for keyword in KEYWORDS:
                    if keyword.lower() in combined:
                        link = f"https://reddit.com{post_data['permalink']}"
                        message = (
                            f"🎯 *ECOS Match!*\n\n"
                            f"*Subreddit:* r/{subreddit}\n"
                            f"*Title:* {post_data['title']}\n\n"
                            f"*Matched:* `{keyword}`\n\n"
                            f"*Link:* {link}\n\n"
                            f"👉 Respond as Koushik. Be genuine first. Share ECOS only if it feels right."
                        )
                        print(f"✅ Match in r/{subreddit}: {post_data['title']}")
                        send_telegram(message)
                        break

            time.sleep(2)  # be polite between subreddit requests

        print("⏳ Sleeping 5 minutes before next check...")
        time.sleep(300)  # check every 5 minutes

if __name__ == "__main__":
    run_bot()