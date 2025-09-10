# twitchcliptodiscord
A script that continuously monitors a Twitch broadcaster for new clips and sends notifications to a Discord channel in real-time.

---

## Features
- ⏱️ Check for new clips every 60 seconds (configurable).
- 🎬 Detects only **new clips** (no duplicates).
- 💬 Customizable Discord message format.
- 🔄 Automatic refresh of Twitch access token when expired.
- 🗂️ Saves the last clip ID in a local file (`lastclip.txt`).

---

## Requirements
- Python 3.8+
- `requests` library

Install dependencies with:
```bash
pip install requests
````

---

## Setup

1. **Clone this repository**

   ```bash
   git clone https://github.com/dinushay/twitchcliptodiscord.git
   cd twitchcliptodiscord
   ```

2. **Get your Twitch tokens**
   Use [twitchtokengenerator.com](https://twitchtokengenerator.com) to generate:

   * `CLIENT_ID`
   * `ACCESS_TOKEN`
   * `REFRESH_TOKEN`

3. **Set up a Discord Webhook**

   * In your Discord server, go to **Server Settings → Integrations → Webhooks**
   * Create a webhook and copy its URL.

4. **Edit the script configuration**
   Open `clip_monitor.py` and replace the placeholders:

   ```python
   CLIENT_ID = "<your_client_id>"
   ACCESS_TOKEN = "<your_access_token>"
   REFRESH_TOKEN = "<your_refresh_token>"
   WEBHOOK_URL = "<your_discord_webhook_url>"
   BROADCASTER_ID = "<twitch_broadcaster_id>"
   ```

   * `BROADCASTER_ID` = The Twitch user ID of the streamer you want to monitor (not username).
     You can find it using the Twitch API or tools like [streamweasels.com/tools/convert-twitch-username-to-user-id](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/).

5. **Run the script**

   ```bash
   python clip.py
   ```

---

## Configuration

* **Check interval** (default: `60` seconds):

  ```python
  CHECK_INTERVAL = 60
  ```

* **Message template** (customizable, default: `New clip created by: [{creator_name}]({url})`):

  ```python
  MESSAGE_TEMPLATE = "🎬 New clip from {creator_name}: [{title}]({url})"
  ```

  Available placeholders:

  * `{creator_name}` → Name of the person who created the clip
  * `{broadcaster_name}` → Streamer’s name
  * `{title}` → Clip title
  * `{url}` → Clip URL
  * `{id}` → Clip ID

---

## Example Discord Message

```
🎬 New clip from Alice: [Epic Gameplay](https://clips.twitch.tv/abcd1234)
```

---

## Notes

* The script stores the last seen clip ID in `lastclip.txt`. Delete this file if you want the bot to re-detect the latest clip.
* If you share this script publicly, **do not commit your tokens or webhook URL**.
* You may want to run this script in the background using `screen`, `tmux`, or as a systemd service.

---

## License

MIT License – free to use and modify.
