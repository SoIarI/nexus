# NEXUS — GENE

## Overview
NEXUS is a personal agent command network for Navaal. A single-file mobile-first HTML UI lets you chat with AI agents across 5 providers, create tagged tasks, and send them to a Windows PC via Telegram. A Python listener on the PC receives tasks, shows toast notifications, and copies to clipboard.

## Architecture Summary
- `nexus.html` — all UI, state, and API calls in one self-contained file
- `nexus-agent.py` — Python script, polls Telegram every 5s, handles PC-side actions
- `nexus-config.json` — Telegram credentials for the PC agent
- `SETUP.md` — human-readable setup guide

## Function Index

### nexus.html

| Function | Purpose |
|---|---|
| `init()` | App bootstrap: load state, render all views, select first agent |
| `load()` / `save()` | localStorage persistence for agents, convos, tasks, projects, budget |
| `saveKey(p, v)` | Persist individual API key to localStorage |
| `saveTG()` | Persist Telegram config to localStorage |
| `callAgent(agent, msgs)` | Route message to correct provider API; update budget for paid providers |
| `spawnPreset(pid)` | Spawn an agent from a built-in preset |
| `spawnCustom()` | Spawn a custom agent from the spawn modal form |
| `selectAgent(id)` | Switch active agent; show chat view |
| `deleteAgent(id)` | Remove agent + conversation |
| `sendMessage()` | Send user input to active agent via callAgent(); render response |
| `renderMessages(showTyping)` | Re-render the chat message list |
| `md(text)` | Lightweight markdown → HTML renderer |
| `copyMsg(idx)` | Copy message to clipboard |
| `openDelegate(idx)` / `delegateTo(agentId)` | Route assistant message to another agent |
| `createTask()` | Create task from modal form |
| `sendToPC(taskId)` | Format task and send to PC via Telegram bot |
| `updateStatus(taskId, status)` | Update task status |
| `deleteTask(taskId)` | Remove task |
| `setFilter(f, btn)` | Filter task list by status |
| `renderTaskList()` | Re-render task list with active filter |
| `createProject()` | Create project from modal |
| `openProject(id)` | Show tasks for a specific project |
| `showAllProjects()` | Return to full project grid |
| `renderProjects()` | Render project card grid |
| `renderSettings()` | Build settings view HTML |
| `testBridge()` | Send test message to both Telegram chat IDs |
| `dangerClearConvos()` / `dangerResetAgents()` / `dangerClearTasks()` | Danger zone actions |
| `toggleConfigPanel()` / `renderConfigPanel()` | Per-agent inline config panel |
| `patchAgent(id, field, val)` | Update agent field in state and re-render |
| `renderAgentList()` | Re-render sidebar agent list |
| `renderBudget()` | Re-render sidebar budget mini-bars |
| `switchTab(tab, navBtn)` | Switch between Chat / Tasks / Projects / Settings |
| `openSpawnModal()` / `openCreateTask()` / `openAddProject()` | Open modals |
| `selectTag(tag, btn)` | Select task tag in modal |
| `toast(msg, icon)` | Show temporary notification |
| `esc(s)` | HTML escape helper |
| `autoResize(el)` | Auto-grow textarea |
| `uid()` | Generate short unique ID |

### nexus-agent.py

| Function | Purpose |
|---|---|
| `load_config()` | Load nexus-config.json; exit on error |
| `tg_send(token, chat_id, text)` | Send Telegram message |
| `tg_get_updates(token, offset)` | Poll Telegram getUpdates |
| `show_toast(title, body)` | Windows toast notification |
| `extract_title(text)` | Parse task title from message body |
| `poll_loop()` | Background thread: poll + notify every 5s |
| `main()` | Entry point: validate config, start poll thread, handle CLI commands |

## Capabilities
- Chat with agents across Anthropic, OpenAI, Gemini, Groq, Mistral
- 7 built-in agent presets with tuned system prompts and provider defaults
- Custom agent spawn with any provider
- Per-agent config panel (name, emoji, provider, model, system prompt)
- Delegate assistant responses to other agents with a follow-up prompt
- Token budget tracking for paid providers (Anthropic, OpenAI)
- Task creation with tags (🔴 Claude Code / 🟡 Free Agent / ⚪ Manual)
- Send tasks to Windows PC via Telegram
- Task status flow: Queued → Sent → In Progress → Done
- Project organization for tasks
- Windows PC toast notifications + clipboard relay via nexus-agent.py
- Telegram bridge test from Settings
- All data persists in localStorage
- Works on mobile (390px) and desktop; mobile uses bottom nav

## Known Errors / Bugs
None at initial build.

## TODO / Needs Implementation
- [ ] Supabase persistence (Phase 2 — schema already in build prompt)
- [ ] Streaming responses (currently waits for full response)
- [ ] Message search
- [ ] Export conversation

## Changelog
| Date       | Change                          |
|------------|---------------------------------|
| 2026-06-17 | Initial build — V2 full rebuild |
