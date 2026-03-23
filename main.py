import requests
import time
import os
import xml.etree.ElementTree as ET

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

SUBREDDITS = ["emotionalintelligence","INFJ","selfimprovement","therapy","mentalhealth","anxiety", "hsp"]

KEYWORDS = [
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
    "going in circles",
    "stuck in my feelings",
    "can't get to the root",
    "keep looping",
    "same patterns",
    "can't move forward",
    "feeling unheard",
    "no one notices",
    "no one asks how i'm doing",
    "no one checks on me",
    "i'm always the one who",
    "no one bothers",
    "left feeling misunderstood",
    "deeply rejected",
    "i pretend i'm okay",
    "pretend to be happy",
    "pretend nothing is wrong",
    "i'm not really okay",
    "i'm barely surviving",
    "i'm falling apart",
    "slowly dying inside",
    "carry everyone's emotions",
    "everyone's therapist",
    "tired of being strong",
    "tired of everything",
    "tired of carrying",
    "i just want someone to",
    "numb but don't know why",
    "something is wrong but i don't know",
    "i don't feel like myself",
    "feel empty but don't know why",
    "feel lost but can't explain",
    "can't get out of my head",

    # Relationship loops
"can't stop thinking about",
"keep analyzing",
"can't detach",
"can't stop caring",
"how do i stop caring",
"can't move on",
"keep going back to",
"breadcrumbs",
"i want to detach",

# Carrying others
"i'm always the therapist",
"people treat me like their therapist",
"everyone comes to me",
"i'm tired of being the strong one",
"no one is there for me",
"i give so much",

# Self awareness but still stuck
"i know what i should do but",
"i know better but",
"i understand it but still",
"logically i know but",
"i've done the work but",
"even after therapy",
"even after healing",

# Low EQ / can't explain feelings
"low eq",
"low emotional intelligence",
"can't explain what i'm feeling",
"can't articulate my feelings",
"don't know what i'm feeling",
"struggle to identify my feelings",
"emotionally unavailable",
"don't understand my emotions",

# Relationship emotional patterns  
"i don't understand why i",
"i hurt someone and don't know why",
"she said i was being",
"he said i was being",
"i cried and didn't know why",
"feel like a child",

# HSP related
"highly sensitive",
"too sensitive",
"feel everything so deeply",
"overwhelmed by emotions",
"can't stop feeling",
]

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        print(f"Telegram status: {r.status_code}")
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
    print("ECOS bot started...")
    send_telegram("ECOS bot is live. Watching Reddit for your people...")
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
                        message = (
                            f"ECOS Match!\n\n"
                            f"Subreddit: r/{subreddit}\n"
                            f"Title: {post['title']}\n\n"
                            f"Matched: {keyword}\n\n"
                            f"Link: {post['link']}\n\n"
                            f"Respond as Koushik. Be genuine first. Share ECOS only if it feels right."
                        )
                        send_telegram(message)
                        print(f"Match sent: {post['title']}")
                        break
            time.sleep(3)
        send_telegram("Checked all subreddits. Sleeping 5 mins...")
        print("Sleeping 5 minutes...")
        time.sleep(300)

if __name__ == "__main__":
    run_bot()
