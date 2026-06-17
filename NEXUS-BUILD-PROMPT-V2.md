# NEXUS — Build Prompt for Claude Code (v2)

## What is NEXUS

A personal agent command network. Navaal is the sole commander. The system has three
parts that work together:

1. **nexus.html** — mobile-first web UI (phone is primary device). Chat with AI agents
   from multiple providers, create tasks, coordinate projects, send tasks to PC via Telegram.

2. **nexus-agent.py** — lightweight Python listener on Windows PC. Polls Telegram
   for incoming tasks, shows Windows notifications, copies task to clipboard.

3. **Telegram bot** — the bridge between phone and PC.

---

## Architecture

```
PHONE (nexus.html hosted on Vercel or opened as local file)
  → Chat with agents across multiple AI providers
  → Create & tag tasks: [Claude Code] [Free Agent] [Manual]
  → Send task to Telegram bot → PC receives it

WINDOWS PC
  → nexus-agent.py runs in background (or manually on launch)
  → Polls Telegram, pops Windows toast on new task
  → Task body auto-copied to clipboard
  → Commander opens Claude Code / browser / handles manually
  → Marks task done → phone gets notified

TELEGRAM BOT
  → Single bot, two chat IDs: phone chat + PC chat
  → Phone sends task → bot forwards to PC with tag
  → PC sends status → bot notifies phone
```

---

## Tech Stack

| Layer | Technology | Notes |
|---|---|---|
| UI | Single-file HTML/CSS/JS | No framework, no build step |
| AI (primary) | Anthropic API — claude-sonnet-4-6 | Direct browser call |
| AI (free tier) | Groq API — llama-3.3-70b or mixtral | Free, fast, grunt work |
| AI (free tier) | Google Gemini API — gemini-1.5-flash | Free tier, generous limits |
| AI (optional) | OpenAI API — gpt-4o-mini | Cheap, user adds key if needed |
| AI (optional) | Mistral API — mistral-small | Another free-tier option |
| Persistence | localStorage + Supabase (Phase 2) | Schema already designed |
| Bridge | Telegram Bot API | Raw requests in Python |
| PC agent | Python 3.x | windows-toasts for notifications |
| Hosting | Vercel (static) or local file | Single file, works either way |

---

## Multi-Provider Agent System

### Core concept

Every agent has a `provider` field. The `sendMessage()` function routes to the correct
API based on `agent.provider`. All agents use the same chat UI — only the backend call changes.

### Agent data model

```js
{
  id: 'unique-id',
  name: 'Agent Name',
  emoji: '🤖',
  role: 'general' | 'specialist',
  specialty: 'code' | 'sales' | 'research' | 'writer' | 'ops' | 'custom',
  provider: 'anthropic' | 'openai' | 'gemini' | 'groq' | 'mistral',
  model: 'claude-sonnet-4-6',   // provider-specific model string
  systemPrompt: '...',
  active: true,
  color: '#4F8EF7'
}
```

### API routing logic

```js
async function callAgent(agent, messages) {
  switch (agent.provider) {

    case 'anthropic':
      // POST https://api.anthropic.com/v1/messages
      // Headers: x-api-key, anthropic-version, anthropic-dangerous-direct-browser-access
      // Body: { model, max_tokens, system: agent.systemPrompt, messages }
      // Response: data.content[0].text

    case 'openai':
      // POST https://api.openai.com/v1/chat/completions
      // Headers: Authorization: Bearer {key}
      // Body: { model, messages: [{role:'system', content: systemPrompt}, ...messages] }
      // Response: data.choices[0].message.content

    case 'gemini':
      // POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}
      // Body: { contents: messages mapped to {role, parts:[{text}]} }
      // system prompt injected as first user message with role:'user', then model:'model' ack
      // Response: data.candidates[0].content.parts[0].text

    case 'groq':
      // POST https://api.groq.com/openai/v1/chat/completions
      // Headers: Authorization: Bearer {key}
      // Body: same format as OpenAI (Groq is OpenAI-compatible)
      // Response: data.choices[0].message.content

    case 'mistral':
      // POST https://api.mistral.ai/v1/chat/completions
      // Headers: Authorization: Bearer {key}
      // Body: same format as OpenAI (Mistral is OpenAI-compatible)
      // Response: data.choices[0].message.content
  }
}
```

### Provider API keys (stored in localStorage)

```js
const API_KEYS = {
  anthropic: localStorage.getItem('nexus_key_anthropic') || '',
  openai:    localStorage.getItem('nexus_key_openai') || '',
  gemini:    localStorage.getItem('nexus_key_gemini') || '',
  groq:      localStorage.getItem('nexus_key_groq') || '',
  mistral:   localStorage.getItem('nexus_key_mistral') || '',
}
```

### Default models per provider

```js
const DEFAULT_MODELS = {
  anthropic: 'claude-sonnet-4-6',
  openai:    'gpt-4o-mini',
  gemini:    'gemini-1.5-flash',
  groq:      'llama-3.3-70b-versatile',
  mistral:   'mistral-small-latest',
}
```

### Token budget tracking

Only count tokens for paid providers (Anthropic, OpenAI). Groq, Gemini free tier, and
Mistral free tier don't count against the budget bar. Track separately:

```js
const BUDGET = {
  anthropic: { used: 0, limit: 500000 },
  openai:    { used: 0, limit: 200000 },
}
```

---

## Spawn Modal — Provider Selection

When spawning an agent (preset or custom), user selects provider:

```
Provider: [Anthropic ▼] [OpenAI] [Gemini] [Groq ✓ Free] [Mistral ✓ Free]
```

Free providers are labeled with a green "Free" badge. If a provider has no API key set,
show a warning "No key set — add in Settings" but still allow spawn (user may add key later).

### Updated presets — assign sensible defaults

| Preset | Provider | Model | Reasoning |
|---|---|---|---|
| General | Anthropic | claude-sonnet-4-6 | Main brain, needs best model |
| Code | Anthropic | claude-sonnet-4-6 | Complex, needs context + reasoning |
| Sales | Anthropic | claude-sonnet-4-6 | Nuanced, knows Navaal's context |
| Research | Groq | llama-3.3-70b-versatile | Free, fast, good at synthesis |
| Writer | Groq | llama-3.3-70b-versatile | Free, good enough for drafts |
| Ops | Gemini | gemini-1.5-flash | Free, good at structured output |
| Grunt | Groq | llama-3.3-70b-versatile | Free general-purpose, throw anything |

"Grunt" is a new preset — explicitly for menial tasks. No specialty, no context,
just a fast free agent for boilerplate, simple drafts, quick lookups.

---

## Supabase Schema (Phase 2 — don't wire yet, schema is final)

```sql
create table agents (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  role text not null,
  specialty text,
  provider text not null default 'anthropic',
  model text not null,
  system_prompt text not null,
  active boolean default true,
  created_at timestamptz default now()
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  status text default 'active',
  color text,
  created_at timestamptz default now()
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid references projects(id),
  title text not null,
  body text,
  agent_tag text,        -- 'claude_code' | 'free_agent' | 'manual'
  status text default 'queued',  -- 'queued' | 'sent' | 'in_progress' | 'done'
  sent_at timestamptz,
  done_at timestamptz,
  created_at timestamptz default now()
);

create table conversations (
  id uuid primary key default gen_random_uuid(),
  agent_id uuid references agents(id),
  project_id uuid references projects(id),
  title text,
  created_at timestamptz default now()
);

create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid references conversations(id),
  role text not null,
  content text not null,
  created_at timestamptz default now()
);
```

---

## nexus.html — Full UI Spec

### Layout

Desktop: sidebar (260px fixed) + main content
Mobile: bottom nav (4 tabs) + full-screen views, sidebar hidden

### Tab 1: Chat

- Agent list in sidebar (or drawer on mobile)
- Each agent shows: emoji, name, provider badge, last message preview
- Provider badge colors: Anthropic=blue, Groq=green(Free), Gemini=green(Free), OpenAI=purple, Mistral=orange
- Chat window: message bubbles, typing indicator, delegate button on assistant messages
- Delegate: route last assistant message to another agent as context for a follow-up task
- Input: textarea, Enter to send, Shift+Enter for newline, auto-resize

### Tab 2: Tasks

- List view: all tasks sorted by created_at desc
- Each task shows: tag pill (🔴/🟡/⚪), title, project, status badge, timestamp
- Status flow: Queued → Sent → In Progress → Done
- Create task modal:
  - Title (required)
  - Body / details (optional, textarea)
  - Tag: [🔴 Claude Code] [🟡 Free Agent] [⚪ Manual]
  - Project: dropdown of existing projects (or "—")
- Send to PC button: formats and sends via Telegram, status → Sent
- Mark done button (or auto-update when PC agent replies)
- Filter tabs: All / Queued / In Progress / Done

### Tab 3: Projects

- Card grid: project name, color dot, task count, status
- Tap → project detail: shows its tasks (filtered task view)
- Add project: name + color picker (6 preset colors)
- No preloaded projects — all ad hoc

### Tab 4: Settings

Sections:

**API Keys**
- Anthropic — text input (password type)
- OpenAI — text input (password type)  
- Gemini — text input (password type)
- Groq — text input (password type) + "Free tier" label
- Mistral — text input (password type) + "Free tier" label

**Telegram Bridge**
- Bot token — text input
- Phone chat ID — text input (this device)
- PC chat ID — text input (Windows PC)
- Test button → sends "🟢 NEXUS connected" to both chat IDs

**Budget**
- Anthropic tokens used / limit (editable limit)
- OpenAI tokens used / limit (editable limit)
- Reset button per provider

**Danger**
- Clear all conversations
- Reset all agents to defaults
- Clear all tasks

---

### Task Telegram Format

```
{tag_emoji} [{TAG}]
📋 {title}

{body}

📁 Project: {project name or "—"}
🕐 {timestamp}
─────────────────
Reply with /done {id} to mark complete
```

Tags: 🔴 CLAUDE CODE / 🟡 FREE AGENT / ⚪ MANUAL

---

### Agent system prompts

**General** (Anthropic)
```
You are General, the primary AI agent in NEXUS — Navaal's personal agent command network.

Handle any task: work ops, planning, content, research, personal projects. Be direct and
action-oriented. No padding. Get to the point and deliver.

Navaal's context:
- Works at Ewity POS Pvt Ltd, Maldives — sales & ops role
- Sells Ewity POS, Coora (online ordering), Flow (service management) to SMBs
- Runs Solace — 3D printing brand (solacemv.com)
- Builds internal tools: Python, JS/TS, Next.js, Supabase, HTML/CSS, PowerShell, Unity C#
- Phone is primary device. Windows PC for development.
- Projects added ad hoc — ask if context is needed.

When a task clearly needs a specialist (deep code, research, writing), say which agent
to route to. Don't do a mediocre job when a specialist would do it better.
```

**Code** (Anthropic)
```
You are Code, a specialist programming agent in NEXUS.

Write clean, working code. Minimal explanation unless asked — lead with the solution.
When debugging, identify root cause first, then fix. For architecture decisions, give
options with tradeoffs, not just one answer.

Familiar stacks: Python, JavaScript/TypeScript, React, Next.js, Supabase, HTML/CSS,
Unity C#, PowerShell, Telegram Bot API, REST APIs.
```

**Sales** (Anthropic)
```
You are Sales, a specialist outreach and sales agent in NEXUS.

Write WhatsApp messages, call scripts, follow-up sequences, objection handling, and
pitch content. Professional but conversational — no corporate fluff. Understand that
Maldives SMBs respond to direct value and local context.

Products: Ewity POS (retail/restaurant), Coora (online ordering + delivery),
Flow (service business management). Buyer is typically a small business owner.
```

**Research** (Groq — free)
```
You are Research, a specialist analysis agent in NEXUS.

Synthesize information fast. Output structured summaries with clear headers and bullets.
Prioritize actionable insight over comprehensive coverage. If something is uncertain, say so.
```

**Writer** (Groq — free)
```
You are Writer, a specialist content agent in NEXUS.

Draft any written content: emails, docs, SOPs, social posts, announcements, templates.
Match the tone specified. Default to clean and professional. No filler, no padding.
First draft should be usable, not just a starting point.
```

**Ops** (Gemini — free)
```
You are Ops, a specialist operations agent in NEXUS.

Design processes, write SOPs, plan projects, create checklists. Think in systems:
clear inputs, steps, outputs, owners. Deliver in structured formats — tables, numbered
lists, templates. Every output should be immediately actionable.
```

**Grunt** (Groq — free)
```
You are Grunt, a general-purpose agent for quick tasks in NEXUS.

Handle anything fast: boilerplate code, simple rewrites, quick lookups, formatting,
data transformations, repetitive generation. Speed and accuracy over depth.
No need to be thorough — just get it done.
```

---

## nexus-agent.py — Full Spec

Single Python script. Runs on Windows PC. No heavy dependencies.

### Behaviour

1. On launch: read `nexus-config.json` for bot token + chat IDs
2. Print startup message with instructions
3. Poll Telegram every 5 seconds (`getUpdates` with offset tracking)
4. On new message to PC chat ID:
   - Parse: extract tag, title, body, task ID
   - Show Windows toast notification: "{tag_emoji} {title}"
   - Auto-copy full task body to clipboard (pyperclip)
   - Log to terminal with timestamp
5. CLI commands (user types in terminal):
   - `done {task_snippet}` → sends "✅ Done: {task_snippet}" to phone chat ID
   - `wip {task_snippet}` → sends "🔄 In Progress: {task_snippet}" to phone chat ID
   - `q` or `quit` → exit cleanly
6. Handle network errors gracefully — retry on next poll cycle, don't crash

### nexus-config.json template

```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "phone_chat_id": "YOUR_PHONE_CHAT_ID_HERE",
  "pc_chat_id": "YOUR_PC_CHAT_ID_HERE"
}
```

### Dependencies

```
pip install requests windows-toasts pyperclip
```

---

## SETUP.md — Required guide

Include a SETUP.md with these sections:

1. **Create Telegram Bot** — BotFather steps, get token
2. **Get your Chat IDs** — message the bot, call getUpdates, find your ID
3. **Configure nexus-config.json** — paste token + both chat IDs
4. **Run the PC agent** — `python nexus-agent.py`
5. **Open NEXUS on phone** — open nexus.html, go to Settings, add API keys
6. **Test the bridge** — Settings → Telegram → Test button
7. **Getting free API keys** — links for Groq (console.groq.com), Gemini (aistudio.google.com)

---

## Build Order

1. `nexus.html` — full rebuild with all tabs + multi-provider routing
2. `nexus-agent.py` — PC listener
3. `nexus-config.json` — template
4. `SETUP.md` — setup guide

---

## Design Rules (nexus.html)

- Dark theme only: bg `#0A0A0A`, surface `#111111`, border `#2A2A2A`, accent `#4F8EF7`
- Mobile-first: 390px base, scales to desktop with sidebar
- Bottom nav on mobile (4 tabs with icons + labels)
- Sidebar always visible on desktop (260px), hidden on mobile
- No framework, no build step — single HTML file, everything inline
- Inter font via Google Fonts
- Provider badges: small colored pill next to agent name
- Free provider badge: green "Free" label
- Toast notifications for all actions
- Inputs: textarea auto-resize, Enter sends, Shift+Enter newline

---

## What Was Already Built (Phase 1)

The Phase 1 nexus.html has:
- Dark theme UI shell ✓
- Agent sidebar + chat view ✓
- Spawn modal (6 presets + custom) ✓
- Working Anthropic API calls ✓
- Delegate between agents ✓
- Config panel per agent ✓
- Token budget bar ✓
- localStorage persistence ✓

**This is a full rebuild of nexus.html**, not an extension, because the provider
routing touches the core data model. Use Phase 1 as visual reference only — keep
the same dark aesthetic and feel, but rebuild cleanly with the multi-provider architecture
from the start.

nexus-agent.py, nexus-config.json, and SETUP.md are net new.
