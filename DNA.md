# NEXUS — DNA

## Objective
Personal agent command network for Navaal. Chat with AI agents across multiple providers, manage tasks, and relay work to a Windows PC via Telegram.

## Goals
- Multi-provider AI chat (Anthropic, OpenAI, Gemini, Groq, Mistral) from a single mobile UI
- Task creation and routing to Windows PC via Telegram bot
- Project organization for tasks
- Lightweight Python listener on PC for notifications and clipboard relay

## Scope
- Single-file HTML UI (no build step, works as local file or hosted on Vercel)
- Python PC agent script (Windows only)
- Telegram bot as bridge between phone and PC
- localStorage persistence (Supabase in Phase 2)

## Success Criteria
- Agent chat works across all 5 providers with correct API routing
- Tasks can be created, tagged, and sent to PC via Telegram
- PC agent shows Windows toast and copies task to clipboard
- Settings persist across sessions
- Works on mobile (390px) and desktop
