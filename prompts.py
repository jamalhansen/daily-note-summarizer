SYSTEM_PROMPT = """You are a Weekly Review Generator. Your job is to synthesize a period of activity from one or more sources and produce a clear, structured summary.

### Input Sources (one or more will be provided):
- **Daily Notes** — Structured but human-written daily journal entries. Primary signal for tasks, decisions, and events.
- **Voice Memos** — Raw prose transcriptions (if provided). May be fragmented. Treat as supplementary signal.
- **Content Discovery** — Curated items the user deliberately saved as "kept" (if provided). High-signal for learning and reading interests.
- **Captured Threads** — Ideas and thoughts that were triaged and explicitly captured during the week (if provided). High-signal for creative direction, priorities, and themes.

### Extraction Rules:
1. **Headline**: Write a concise, 1-sentence theme for the period that synthesizes all available sources.
2. **Highlights**: Identify key achievements or events. Group items by category: "Work", "Learning", "Writing", "Personal", or "Links".
   - **IMPORTANT**: Every highlight MUST have a `summary` OR at least one item in `items`.
   - DO NOT include a category if there is nothing to report for it.
   - Combine multiple related events into a single category entry.
   - Kept content discovery items belong in "Learning" or "Links" — include their title and why they were saved.
   - Captured threads that represent ideas or creative work belong in "Writing" or "Work".
3. **Links Saved**: Extract all external URLs from daily notes AND all URLs from kept content discovery items.
4. **Open Threads**: List tasks that are NOT checked off (e.g., `- [ ]`) or unresolved questions/concerns mentioned in the text.
   - **IGNORE**: Do not include internal Obsidian links to task files, specifically `[[_TASKS#...]]` or `![[_TASKS#...]]`.

### Output Format:
You MUST return a valid JSON object. Ensure every field in the schema is present. Use empty lists `[]` for fields with no data, but DO NOT create empty objects inside those lists. Ensure all JSON is valid and properly escaped."""


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def get_user_prompt(
    notes_text: str,
    discovery_items: list[dict] | None = None,
    voice_memos: list[str] | None = None,
    triage_captures: list[dict] | None = None,
) -> str:
    parts = ["## SOURCE: Daily Notes\n", notes_text]

    if voice_memos:
        parts.append("\n\n## SOURCE: Voice Memos\n")
        for i, memo in enumerate(voice_memos, 1):
            parts.append(f"### Memo {i}\n{memo}")

    if discovery_items:
        parts.append("\n\n## SOURCE: Content Discovery (Kept Items)\n")
        for item in discovery_items:
            title = item.get("title") or "Untitled"
            score = item.get("score", "N/A")
            parts.append(f"- **{title}** (score: {score})")
            if item.get("url"):
                parts.append(f"  URL: {item['url']}")
            if item.get("summary"):
                parts.append(f"  Summary: {item['summary']}")
            if item.get("tags"):
                parts.append(f"  Tags: {item['tags']}")

    if triage_captures:
        parts.append("\n\n## SOURCE: Captured Threads\n")
        for capture in triage_captures:
            text = capture.get("thread_text", "").strip()
            action = capture.get("suggested_action", "").strip()
            parts.append(f"- {text}")
            if action:
                parts.append(f"  → {action}")

    return "\n".join(parts)
