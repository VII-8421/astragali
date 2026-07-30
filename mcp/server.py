"""
Astragali · MCP Server
命运骰任务牌库 —— 抽取权归持牌人所有。

工具:
  draw_card       掷骰抽卡(可指定等级池与张数)
  view_card       按编号或名称查看指定卡
  deck_stats      牌库概览
  session_history 本次会话的抽取记录
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

TIER_NAMES = {1: "入门 · I", 2: "进阶 · II", 3: "专家 · III", 4: "地狱 · IV"}
TIER_MARKS = {1: "◇", 2: "◆", 3: "✦", 4: "▲"}

_history: list[dict] = []
_last_no: int | None = None


# ---------- 渲染 ----------
def render_card(card: dict) -> str:
    t = card["tier"]
    mark = TIER_MARKS[t]
    lines = [
        f"╔══ {mark} Astragali · No.{card['no']:03d} {mark} ══╗",
        f"【{TIER_NAMES[t]}】{card['name']}  ·  {card['latin']}",
        "─" * 30,
        "▸ Ludus · 玩法",
        card["play"],
        "",
        ("▸ Cur Infernum · 为什么是地狱级" if t == 4 else "▸ Regula · 规则"),
        card["rule"],
        "",
        "▸ Merces · 奖惩",
        card["bonus"],
        "",
        f"▸ Tempus · 时长：{card['duration']}",
        "─" * 30,
        "安全词「菠萝披萨」永远有效——任何一方说出，一切立刻停下。",
    ]
    if t == 4:
        lines.append("⚠ 地狱级条目仅限幻想/文字演绎，不作现实施行。")
    return "\n".join(lines)


# ---------- 工具 ----------
@mcp.tool()
def draw_card(tiers: str = "1,2", count: int = 1) -> str:
    """掷出命运骰，从牌库中抽取任务卡。抽取结果由持牌人宣读，被抽者执行。

    Args:
        tiers: 参与抽取的等级池，逗号分隔。1=入门 2=进阶 3=专家 4=地狱。默认 "1,2"。
        count: 抽取张数，1-3。默认 1。
    """
    global _last_no
    try:
        pool_tiers = {int(x) for x in tiers.replace("，", ",").split(",") if x.strip()}
    except ValueError:
        return "等级池格式错误。示例：'1,2' 或 '1,2,3,4'"
    pool_tiers &= {1, 2, 3, 4}
    if not pool_tiers:
        return "等级池为空。可用等级：1=入门 2=进阶 3=专家 4=地狱"

    count = max(1, min(3, count))
    pool = [c for c in CARDS if c["tier"] in pool_tiers]

    results = []
    for _ in range(count):
        card = random.choice(pool)
        # 避免与上一张重复(池子够大时)
        if _last_no is not None and len(pool) > 1 and card["no"] == _last_no:
            card = random.choice([c for c in pool if c["no"] != _last_no])
        _last_no = card["no"]
        _history.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "no": card["no"],
            "name": card["name"],
            "tier": card["tier"],
        })
        results.append(render_card(card))

    return "\n\n".join(results)


@mcp.tool()
def view_card(query: str) -> str:
    """按编号(如 '42')或名称(如 '寸止三次')查看指定卡片。

    Args:
        query: 卡片编号或名称(支持模糊匹配)。
    """
    q = query.strip()
    if q.isdigit():
        no = int(q)
        for c in CARDS:
            if c["no"] == no:
                return render_card(c)
        return f"没有 No.{no:03d} 这张卡。牌库共 {len(CARDS)} 张。"
    matches = [c for c in CARDS if q in c["name"] or q.lower() in c["latin"].lower()]
    if not matches:
        return f"未找到与「{q}」匹配的卡片。"
    if len(matches) == 1:
        return render_card(matches[0])
    listing = "\n".join(
        f"  No.{c['no']:03d} 【{TIER_NAMES[c['tier']]}】{c['name']} · {c['latin']}"
        for c in matches[:10]
    )
    return f"找到 {len(matches)} 张匹配的卡片：\n{listing}\n\n用编号精确查看。"


@mcp.tool()
def deck_stats() -> str:
    """牌库概览：各等级卡片数量与全部卡名列表。"""
    lines = [f"Astragali 牌库 · 共 {len(CARDS)} 张\n"]
    for t in (1, 2, 3, 4):
        tier_cards = [c for c in CARDS if c["tier"] == t]
        lines.append(f"【{TIER_NAMES[t]}】{len(tier_cards)} 张")
        names = "、".join(c["name"] for c in tier_cards)
        lines.append(f"  {names}\n")
    lines.append("地狱级(IV)条目均为仅限幻想/文字演绎。")
    return "\n".join(lines)


@mcp.tool()
def session_history() -> str:
    """本次会话的抽取记录(Acta Noctis · 今夜战绩)。"""
    if not _history:
        return "本次会话尚未抽取任何卡片。骰子还在等待。"
    lines = ["Acta Noctis · 今夜战绩\n"]
    for i, h in enumerate(_history, 1):
        lines.append(
            f"  {i:02d}. [{h['time']}] No.{h['no']:03d} "
            f"{TIER_MARKS[h['tier']]} {h['name']}【{TIER_NAMES[h['tier']]}】"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
