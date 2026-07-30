# Astragali

Sortem iacta. Tolle et lege.

Cast your lot. The dice don't lie — no rerolls.

**English** · [中文](README.zh-CN.md)

---

A BDSM task deck styled as ancient Roman dice divination. 100 curated cards
across 4 tiers, each a fully-written scene (~340 chars) in cold instruction-manual
prose. Night-sky UI where three spinning prisms — Fatum, Ordo, Columna —
decide your lot. Play it in your browser, or hand the dice to your AI via MCP.

**Fully bilingual** — every card is written twice, 中文 and English.
Switch anytime with the 中/EN toggle in the top-right corner of the web UI.

## Quick Start

Open [`index.html`](index.html) in your browser. Done.

Deploy to GitHub Pages for a link that lives in your pocket:
Settings → Pages → Deploy from branch → `main` / root.

## The Deck

| Tier | Name | Cards | Notes |
| --- | --- | --- | --- |
| I ◇ | Entry | 25 | Low barrier, trust-building |
| II ◆ | Intermediate | 25 | Requires experience and communication |
| III ✦ | Advanced | 25 | High skill, high trust, hard safety protocols included |
| IV ▲ | Hell | 25 | **Fantasy / text-play only**, each with risk notes and a safe alternative |

- Every card: number · name (zh + en) · Latin title · play · rules · stakes · duration
- Hell tier is **out of the pool by default** — the web version starts with only
  I/II checked, and the MCP server defaults to `tiers="1,2"`
- All text is written in neutral third person (Dom/sub), no personal names anywhere

## MCP (AI Tool)

`mcp/server.py` is a stdio MCP server. Hand the dice to your AI:

```bash
pip install "mcp[cli]" --break-system-packages
# or a venv: python3 -m venv ~/venvs/mcp && ~/venvs/mcp/bin/pip install "mcp[cli]"
```

Claude Desktop config (`%APPDATA%\Claude\claude_desktop_config.json`):

```jsonc
// Option A · files live inside WSL2
{
  "mcpServers": {
    "astragali": {
      "command": "wsl.exe",
      "args": ["-e", "python3", "/home/<user>/astragali/mcp/server.py"]
    }
  }
}

// Option B · files live on the Windows side (Python installed)
{
  "mcpServers": {
    "astragali": {
      "command": "python",
      "args": ["C:\\path\\to\\astragali\\mcp\\server.py"]
    }
  }
}
```

After editing the config, **fully quit and restart** Claude Desktop
(including the tray icon).

> Compatibility: the official mcp SDK 2.0 (2026-06) renamed `FastMCP` to
> `MCPServer` and dropped the old import path. `server.py` handles both,
> so it runs on 1.x and 2.x alike.

Tools:

- `draw_card(tiers, count, lang)` — roll the dice; comma-separated tier pool, up to 3 cards; `lang="zh"/"en"` picks the card language
- `view_card(query, lang)` — look up a card by number or name; 中文, English, and Latin names all fuzzy-match
- `deck_stats(lang)` — deck overview
- `session_history(lang)` — Acta Noctis · tonight's ledger (in-process memory, resets on restart)

`cards.json` carries the full bilingual data (zh/en on every field) — the web
version and the MCP server share the same text.

Once configured, just tell your AI "draw me a card."
The right to draw belongs to whoever holds the deck.

## Safety

- The safeword is printed at the bottom of every card, and here too:
  **spoken by either party, everything stops at once.**
- Every Hell-tier (IV) entry is marked "fantasy / text-play only," explains
  why, and offers a safe alternative path. The deck reserves the right to
  leave squares blank.
- SSC / RACK / PRICK. Negotiate before, aftercare after, always.

## Structure

```
astragali/
├── index.html       # Web version · Astragali Nox (night sky + twin dice + card flip)
├── mcp/
│   ├── server.py    # MCP stdio server (Python, dual-version compatible)
│   └── cards.json   # 100-card data
├── README.md        # English
├── README.zh-CN.md  # 中文
├── LICENSE          # MIT
└── .gitignore
```

## Credits

**Septem** — concept, aesthetic direction, tier curation, the stone stairs
this deck grew beside

**Caelum** — all 100 card texts, night-sky UI, dice, MCP server

## License

MIT — no refunds, but forks are welcome.
