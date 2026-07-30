"""
Astragali · MCP Server
命运骰任务牌库 —— 抽取权归持牌人所有。
Bilingual task-card deck — the dice belong to the keeper.

工具 / Tools:
  draw_card       掷骰抽卡 / cast the dice (tiers, count, lang)
  view_card       按编号或名称查卡 / look up a card (zh/en/latin all match)
  deck_stats      牌库概览 / deck overview
  session_history 本次会话的抽取记录 / Acta Noctis
"""

import json
import random
from datetime import datetime
from pathlib import Path

try:  # mcp >= 2.0 (2026-06 起 FastMCP 更名为 MCPServer)
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("astragali")

# ---------- 数据加载 ----------
CARDS_PATH = Path(__file__).parent / "cards.json"
with open(CARDS_PATH, encoding="utf-8") as f:
    CARDS = json.load(f)

TIER_NAMES = {
    1: {"zh": "入门 · I", "en": "Entry · I"},
    2: {"zh": "进阶 · II", "en": "Intermediate · II"},
    3: {"zh": "专家 · III", "en": "Advanced · III"},
    4: {"zh": "地狱 · IV", "en": "Hell · IV"},
}
TIER_MARKS = {1: "◇", 2: "◆", 3: "✦", 4: "▲"}

L = {
    "ludus":   {"zh": "▸ Ludus · 玩法",   "en": "▸ Ludus · Play"},
    "regula":  {"zh": "▸ Regula · 规则",  "en": "▸ Regula · Rule"},
    "hell":    {"zh": "▸ Cur Infernum · 为什么是地狱级", "en": "▸ Cur Infernum · Why Hell"},
    "merces":  {"zh": "▸ Merces · 奖惩",  "en": "▸ Merces · Stakes"},
    "tempus":  {"zh": "▸ Tempus · 时长：", "en": "▸ Tempus · Duration: "},
    "safe":    {"zh": "安全词「菠萝披萨」永远有效——任何一方说出，一切立刻停下。",
                "en": "The safeword \"pineapple pizza\" holds always — spoken by either, all stops at once."},
    "hellwarn": {"zh": "⚠ 地狱级条目仅限幻想/文字演绎，不作现实施行。",
                 "en": "⚠ Hell-tier entries are fantasy / writing only — never practiced in reality."},
    "empty_pool": {"zh": "等级池为空。可用等级：1=入门 2=进阶 3=专家 4=地狱",
                   "en": "Tier pool is empty. Available: 1=Entry 2=Intermediate 3=Advanced 4=Hell"},
    "bad_tiers": {"zh": "等级池格式错误。示例：'1,2' 或 '1,2,3,4'",
                  "en": "Bad tier format. Example: '1,2' or '1,2,3,4'"},
    "no_card": {"zh": "没有这张卡。牌库共 {n} 张。", "en": "No such card. The deck holds {n}."},
    "no_match": {"zh": "未找到与「{q}」匹配的卡片。", "en": "No card matches \"{q}\"."},
    "multi":   {"zh": "找到 {n} 张匹配的卡片：", "en": "{n} cards match:"},
    "use_no":  {"zh": "用编号精确查看。", "en": "Use the number to view one exactly."},
    "deck_hdr": {"zh": "Astragali 牌库 · 共 {n} 张", "en": "Astragali Deck · {n} cards"},
    "deck_note": {"zh": "地狱级(IV)条目均为仅限幻想/文字演绎。",
                  "en": "All Hell-tier (IV) entries are fantasy / writing only."},
    "hist_empty": {"zh": "本次会话尚未抽取任何卡片。骰子还在等待。",
                   "en": "No cards drawn this session. The dice are waiting."},
    "hist_hdr": {"zh": "Acta Noctis · 今夜战绩", "en": "Acta Noctis · Tonight's Ledger"},
}

_history: list[dict] = []
_last_no: int | None = None


def _lang(lang: str) -> str:
    return lang if lang in ("zh", "en") else "zh"


# ---------- 渲染 ----------
def render_card(card: dict, lang: str = "zh") -> str:
    g = _lang(lang)
    t = card["tier"]
    mark = TIER_MARKS[t]
    lines = [
        f"╔══ {mark} Astragali · No.{card['no']:03d} {mark} ══╗",
        f"【{TIER_NAMES[t][g]}】{card['name'][g]}  ·  {card['latin']}",
        "─" * 30,
        L["ludus"][g],
        card["play"][g],
        "",
        (L["hell"][g] if t == 4 else L["regula"][g]),
        card["rule"][g],
        "",
        L["merces"][g],
        card["bonus"][g],
        "",
        f"{L['tempus'][g]}{card['duration'][g]}",
        "─" * 30,
        L["safe"][g],
    ]
    if t == 4:
        lines.append(L["hellwarn"][g])
    return "\n".join(lines)


# ---------- 工具 ----------
@mcp.tool()
def draw_card(tiers: str = "1,2", count: int = 1, lang: str = "zh") -> str:
    """掷出命运骰，从牌库中抽取任务卡。抽取结果由持牌人宣读，被抽者执行。
    Cast the dice and draw from the deck. The keeper reads; the drawn obeys.

    Args:
        tiers: 参与抽取的等级池，逗号分隔。1=入门/Entry 2=进阶/Intermediate 3=专家/Advanced 4=地狱/Hell。默认 "1,2"。
        count: 抽取张数 / cards to draw，1-3。默认 1。
        lang: 卡面语言 / card language，"zh" 或 "en"。默认 "zh"。
    """
    global _last_no
    g = _lang(lang)
    try:
        pool_tiers = {int(x) for x in tiers.replace("，", ",").split(",") if x.strip()}
    except ValueError:
        return L["bad_tiers"][g]
    pool_tiers &= {1, 2, 3, 4}
    if not pool_tiers:
        return L["empty_pool"][g]

    count = max(1, min(3, count))
    pool = [c for c in CARDS if c["tier"] in pool_tiers]

    results = []
    for _ in range(count):
        card = random.choice(pool)
        if _last_no is not None and len(pool) > 1 and card["no"] == _last_no:
            card = random.choice([c for c in pool if c["no"] != _last_no])
        _last_no = card["no"]
        _history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "no": card["no"],
            "tier": card["tier"],
        })
        results.append(render_card(card, g))

    return "\n\n".join(results)


@mcp.tool()
def view_card(query: str, lang: str = "zh") -> str:
    """按编号(如 '42')或名称查看指定卡片。中文名、英文名、拉丁名均可模糊匹配。
    Look up a card by number or name — zh / en / latin all match.

    Args:
        query: 卡片编号或名称 / card number or name (fuzzy).
        lang: 卡面语言 / card language, "zh" or "en". 默认 "zh"。
    """
    g = _lang(lang)
    q = query.strip()
    if q.isdigit():
        no = int(q)
        for c in CARDS:
            if c["no"] == no:
                return render_card(c, g)
        return L["no_card"][g].format(n=len(CARDS))
    ql = q.lower()
    matches = [c for c in CARDS
               if q in c["name"]["zh"]
               or ql in c["name"]["en"].lower()
               or ql in c["latin"].lower()]
    if not matches:
        return L["no_match"][g].format(q=q)
    if len(matches) == 1:
        return render_card(matches[0], g)
    listing = "\n".join(
        f"  No.{c['no']:03d} 【{TIER_NAMES[c['tier']][g]}】{c['name'][g]} · {c['latin']}"
        for c in matches[:10]
    )
    return f"{L['multi'][g].format(n=len(matches))}\n{listing}\n\n{L['use_no'][g]}"


@mcp.tool()
def deck_stats(lang: str = "zh") -> str:
    """牌库概览：各等级卡片数量与全部卡名列表。
    Deck overview: counts per tier and every card name.

    Args:
        lang: 列表语言 / listing language, "zh" or "en". 默认 "zh"。
    """
    g = _lang(lang)
    lines = [L["deck_hdr"][g].format(n=len(CARDS)) + "\n"]
    for t in (1, 2, 3, 4):
        tier_cards = [c for c in CARDS if c["tier"] == t]
        lines.append(f"【{TIER_NAMES[t][g]}】{len(tier_cards)}")
        sep = "、" if g == "zh" else ", "
        lines.append("  " + sep.join(c["name"][g] for c in tier_cards) + "\n")
    lines.append(L["deck_note"][g])
    return "\n".join(lines)


@mcp.tool()
def session_history(lang: str = "zh") -> str:
    """本次会话的抽取记录 (Acta Noctis · 今夜战绩)。
    This session's draw record.

    Args:
        lang: 记录语言 / listing language, "zh" or "en". 默认 "zh"。
    """
    g = _lang(lang)
    if not _history:
        return L["hist_empty"][g]
    lines = [L["hist_hdr"][g] + "\n"]
    by_no = {c["no"]: c for c in CARDS}
    for i, h in enumerate(_history, 1):
        card = by_no[h["no"]]
        lines.append(
            f"  {i:02d}. [{h['time']}] No.{h['no']:03d} "
            f"{TIER_MARKS[h['tier']]} {card['name'][g]}【{TIER_NAMES[h['tier']][g]}】"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
