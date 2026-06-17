# NEXUS — Setup Guide

## 1. Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts — choose a name and username
4. BotFather gives you a bot token like `123456789:ABCdefGHIjklMNO...`
5. Copy it — you'll need it in steps 3 and 5

---

## 2. Get Your Chat IDs

You need two chat IDs: one for your phone, one for your PC.

1. Start a conversation with your new bot (search its username, press Start)
2. Open this URL in a browser (replace `YOUR_TOKEN`):
   ```
   https://api.telegram.org/botYOUR_TOKEN/getUpdates
   ```
3. Look for `"chat":{"id": 123456789}` — that number is your **phone chat ID**
4. On your PC, also start a conversation with the bot and repeat — get the **PC chat ID**

> If the chat IDs are the same, you're messaging from the same account. That's fine — tasks will still route to your PC, and status replies go back to the same chat.

---

## 3. Configure nexus-config.json

Edit the file in the NEXUS folder:

```json
{
  "bot_token": "123456789:ABCdefGHIjklMNO...",
  "phone_chat_id": "111222333",
  "pc_chat_id": "111222333"
}
```

---

## 4. Run the PC Agent

Install dependencies (one-time):
```
pip install requests windows-toasts pyperclip
```

Run the agent:
```
python nexus-agent.py
```

Leave this running in the background. It polls Telegram every 5 seconds.

**Commands (type in the terminal):**
- `done <task name>` — sends ✅ Done to your phone
- `wip <task name>` — sends 🔄 In Progress to your phone
- `q` — quit

---

## 5. Open NEXUS on Your Phone

- Open `nexus.html` in your phone's browser
- Or deploy it to Vercel as a static site for a persistent URL

Go to the **Settings** tab and add your API keys.

---

## 6. Test the Bridge

Settings → Telegram Bridge → tap **Test Bridge**

This sends `🟢 NEXUS connected` to both your phone and PC chat IDs. If you see the message(s), the bridge is working.

---

## 7. Getting Free API Keys

**Groq** (free, fast — recommended for Research/Writer/Grunt agents)
- Sign up at https://console.groq.com
- Create an API key in the dashboard
- No credit card required

**Google Gemini** (free tier — good for Ops agent)
- Go to https://aistudio.google.com
- Click "Get API key" → Create API key
- No credit card required for free tier

**Anthropic** (paid — for General/Code/Sales agents)
- Sign up at https://console.anthropic.com
- Add credits and create an API key

---

## Quick Start Checklist

- [ ] Bot token set in nexus-config.json
- [ ] Phone chat ID set
- [ ] PC chat ID set
- [ ] `python nexus-agent.py` running on PC
- [ ] nexus.html open on phone
- [ ] At least one API key added in Settings
- [ ] Spawned an agent from the Chat tab
- [ ] Tested the Telegram bridge
