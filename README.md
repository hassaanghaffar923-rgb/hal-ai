
# HAL - Python Dependency Hell, Finally Fixed

**HAL wins where pip struggles.**

`hal add requests` - If there's a conflict, HAL auto-fixes it with AI or heuristics.

### For 50 Million Developers

```bash
pip install hal-ai
hal init
hal add numpy
hal add pandas
hal doctor
```

### Why HAL?
- Normal `pip install` fails on conflicts -> HAL fixes them
- Works WITHOUT AI key (heuristic mode) for 50M users
- Works WITH ANY AI key (Groq free, OpenAI, Gemini, Claude, OpenRouter, Ollama, etc)

### AI Keys (any one, all optional)
```
GROQ_API_KEY=gsk_... (free, fast)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
OR generic:
AI_API_KEY=xxx
AI_BASE_URL=https://api.openrouter.ai/api/v1
AI_MODEL=llama-3.3-70b-versatile
```

### How it beats pip?
pip: "ERROR: Cannot install because..."
HAL: "Conflict detected -> Fixing httpx==0.13.3 -> SUCCESS!"

Built by Hassaan from Bahawalpur for 50M devs.
