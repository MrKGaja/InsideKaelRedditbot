import requests
import time
import os
import xml.etree.ElementTree as ET

# ─────────────────────────────────────────────
# CONFIGURATION
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
        r = requests.post(url, data=payload, timeout=10)
        print(f"Telegram response: {r.status_code}")
    except Exception as e:
        print(f"Telegram error: {e}")

# ─────────────────────────────────────────────
# FETCH NEW POSTS VIA RSS
# ─────────────────────────────────────────────

def fetch_rss(subreddit):
    url = f"https://www.reddit.com/r/{subreddit}/new/.rss"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; ECOSBot/1.0)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"r/{subreddit} status: {response.status_code}")
        if response.status_code != 200:
            return []
        root = ET.fromstring(response.content)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", namespace)
        posts = []
        for entry in entries:
            post_id = entry.find("atom:id", namespace).text
            title = entry.find("atom:title", namespace).text or ""
            content_el = entry.find("atom:content", namespace)
            content = content_el.text if content_el is not None else ""
            link_el = entry.find("atom:link", namespace)
            link = link_el.attrib.get("href", "") if link_el is not None else ""
            posts.append({
                "id": post_id,
                "title": title,
                "content": content,
                "link": link
            })
        return posts
    except Exception as e:
        print(f"RSS error for r/{subreddit}: {e}")
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
            posts = fetch_rss(subreddit)
            print(f"r/{subreddit}: {len(posts)} posts fetched")

            for post in posts:
                post_id = post["id"]

                if post_id in seen_ids:
                    continue
                seen_ids.add(post_id)

                combined = (post["title"] + " " + post["content"]).lower()

                for keyword in KEYWORDS:
                    if keyword.lower() in combined:
                        message = (
                            f"🎯 *ECOS Match!*\n\n"
                            f"*Subreddit:* r/{subreddit}\n"
                            f"*Title:* {post['title']}\n\n"
                            f"*Matched:* `{keyword}`\n\n"
                            f"*Link:* {post['link']}\n\n"
                            f"👉 Respond as Koushik. Be genuine first. Share ECOS only if it feels right."
                        )
                        print(f"✅ Match in r/{subreddit}: {post['title']}")
                        send_telegram(message)
                        break

            time.sleep(3)

        print("⏳ Sleeping 5 minutes before next check...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()