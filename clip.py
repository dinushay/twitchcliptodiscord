import requests
import time
import os
from datetime import datetime, timedelta, timezone

# =============================
# Configuration
# =============================

# Get your Client ID and OAuth tokens here:
# https://twitchtokengenerator.com
CLIENT_ID = "<your_client_id>"
ACCESS_TOKEN = "<your_initial_access_token>"
REFRESH_TOKEN = "<your_refresh_token>"

# Your Discord Webhook URL (create one in your Discord server settings)
WEBHOOK_URL = "<your_discord_webhook_url>"

# The Twitch broadcaster you want to monitor
# https://streamweasels.com/tools/convert-twitch-username-to-user-id
BROADCASTER_ID = "<twitch_broadcaster_id>"

# Interval in SECONDS
CHECK_INTERVAL = 60

# Message template (customizable)
# Available placeholders: {creator_name}, {url}, {title}, {broadcaster_name}, {id}
MESSAGE_TEMPLATE = "🎬 New clip created by: [{creator_name}]({url})"

# File to store the last seen clip ID
LAST_CLIP_FILE = "lastclip.txt"


# =============================
# Code
# =============================

def get_access_token():
    """
    Refresh the Twitch access token using the refresh token.
    Handles potential network errors.
    """
    global ACCESS_TOKEN
    url = "https://id.twitch.tv/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            ACCESS_TOKEN = data["access_token"]
            print("[INFO] Access token refreshed.")
            return True
        else:
            print(f"[ERROR] Could not refresh access token. Status: {resp.status_code}, Response: {resp.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error while refreshing token: {e}")
        return False


def get_last_clip():
    """
    Fetch the most recent clip created in the last interval.
    Handles potential network errors.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Client-Id": CLIENT_ID
    }

    started_at = (datetime.now(timezone.utc) - timedelta(seconds=CHECK_INTERVAL + 5)).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = (
        f"https://api.twitch.tv/helix/clips"
        f"?broadcaster_id={BROADCASTER_ID}"
        f"&first=1"
        f"&started_at={started_at}"
    )
    
    try:
        resp = requests.get(url, headers=headers)

        if resp.status_code == 401:
            print("[INFO] Token expired. Refreshing...")
            get_access_token()
            return get_last_clip() # Retry after refreshing

        if resp.status_code != 200:
            print(f"[ERROR] API error. Status: {resp.status_code}, Response: {resp.text}")
            return None

        data = resp.json().get("data", [])
        if not data:
            return None

        return data[0]

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error while fetching clips: {e}")
        return None


def read_last_saved_clip():
    if not os.path.exists(LAST_CLIP_FILE):
        return None
    with open(LAST_CLIP_FILE, "r") as f:
        return f.read().strip()


def save_last_clip(clip_id):
    with open(LAST_CLIP_FILE, "w") as f:
        f.write(clip_id)


def send_discord_message(clip):
    """
    Send a message to the Discord webhook.
    Handles potential network errors.
    """
    message_text = MESSAGE_TEMPLATE.format(
        creator_name=clip.get("creator_name", "Unknown"),
        url=clip.get("url", "#"),
        title=clip.get("title", "Untitled"),
        broadcaster_name=clip.get("broadcaster_name", "Unknown"),
        id=clip.get("id", "0")
    )

    message = {"content": message_text}
    
    try:
        resp = requests.post(WEBHOOK_URL, json=message)
        if resp.status_code == 204:
            print("[INFO] Message sent to Discord.")
        else:
            print(f"[ERROR] Discord webhook error. Status: {resp.status_code}, Response: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error while sending to Discord: {e}")


def main():
    print("[INFO] Starting Twitch clip monitor...")
    while True:
        clip = get_last_clip()
        if clip:
            last_saved = read_last_saved_clip()
            if clip["id"] != last_saved:
                print(f"[NEW] New clip found: {clip['id']}")
                send_discord_message(clip)
                save_last_clip(clip["id"]) # Save only after attempting to send
            else:
                # This state is less likely with the new time window logic, but kept for safety.
                print("[INFO] Clip already seen, no new clip.")
        else:
            print("[INFO] No new clips found in the last interval.")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
