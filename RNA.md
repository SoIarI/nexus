# NEXUS — RNA

## Tech Stack
| Layer       | Technology                        | Version / Notes              |
|-------------|-----------------------------------|------------------------------|
| UI          | Single-file HTML/CSS/JS           | No framework, no build step  |
| Font        | Inter (Google Fonts)              | 400 / 500 / 600 / 700        |
| AI Primary  | Anthropic — claude-sonnet-4-6     | Direct browser API call      |
| AI Free     | Groq — llama-3.3-70b-versatile    | OpenAI-compatible            |
| AI Free     | Gemini — gemini-1.5-flash         | generativelanguage API       |
| AI Optional | OpenAI — gpt-4o-mini              | Standard chat completions    |
| AI Optional | Mistral — mistral-small-latest    | OpenAI-compatible            |
| Persistence | localStorage                      | Phase 1; Supabase in Phase 2 |
| Bridge      | Telegram Bot API                  | Raw HTTP, no SDK             |
| PC Agent    | Python 3.x                        | Windows only                 |
| Hosting     | Vercel (static) or local file     | Single file, works either way|

## Python Dependencies
```
pip install requests windows-toasts pyperclip
```

## Environment / Config
- All API keys stored in localStorage under `nexus_key_<provider>`
- Telegram config stored in localStorage under `nexus_tg_*`
- PC agent reads from `nexus-config.json` in same directory

## Build & Run
```
# UI — open nexus.html in browser (or deploy to Vercel as static site)

# PC Agent
pip install requests windows-toasts pyperclip
python nexus-agent.py
```

## Notes
- Anthropic requires `anthropic-dangerous-direct-browser-access: true` header for direct browser calls
- Gemini system prompt injected as first user/model turn pair (API doesn't support system role)
- Groq and Mistral are OpenAI-compatible — same request format
- Token budget tracked only for Anthropic and OpenAI (paid providers)
