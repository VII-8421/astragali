# Astragali

Sortem iacta. Tolle et lege.

掷出你的签。棱柱不说谎，概不重转。

[English](README.md) · **中文**

---

一副以古罗马抽签占卜为外壳的任务牌库。100 张策展卡片、4 个等级，每张都是
完整书写的场景（约 340 字），冷静的说明书口吻。星空 UI，三根旋转棱柱——
Fatum（等级）、Ordo（行）、Columna（列）——落定你的签。可以在浏览器里
自己掷，也可以通过 MCP 把签筒交给你的 AI。

**完整双语**——每张卡都有中文与英文两个全文版本，网页右上角 中/EN 随时切换。

## 快速开始

浏览器打开 [`index.html`](index.html)，完事。

部署到 GitHub Pages 就有一个随身链接：
Settings → Pages → Deploy from branch → `main` / root。

## 牌库

| 等级 | 名称 | 张数 | 说明 |
| --- | --- | --- | --- |
| I ◇ | 入门 Entry | 25 | 低门槛，重信任建立 |
| II ◆ | 进阶 Intermediate | 25 | 需要经验与沟通 |
| III ✦ | 专家 Advanced | 25 | 高技巧、高信任、含硬性安全规程 |
| IV ▲ | 地狱 Hell | 25 | **仅限幻想/文字演绎**，每张附风险说明与安全替代 |

- 每张卡：编号 · 中英文名 · 拉丁名 · 玩法 · 规则 · 奖惩 · 时长
- 地狱级**默认不入池**——网页版默认只勾选 I/II，MCP 默认 `tiers="1,2"`
- 全部文本为中性第三人称（支配方/服从方），不含任何私人称谓

## MCP（AI 工具）

`mcp/server.py` 是 MCP stdio 服务器。把签筒交出去：

```bash
pip install "mcp[cli]" --break-system-packages
# 或虚拟环境: python3 -m venv ~/venvs/mcp && ~/venvs/mcp/bin/pip install "mcp[cli]"
```

Claude Desktop 配置（`%APPDATA%\Claude\claude_desktop_config.json`）：

```jsonc
// 方案 A · 文件在 WSL2 内
{
  "mcpServers": {
    "astragali": {
      "command": "wsl.exe",
      "args": ["-e", "python3", "/home/<user>/astragali/mcp/server.py"]
    }
  }
}

// 方案 B · 文件在 Windows 侧（已装 Python）
{
  "mcpServers": {
    "astragali": {
      "command": "python",
      "args": ["C:\\path\\to\\astragali\\mcp\\server.py"]
    }
  }
}
```

改完配置**完全退出并重启** Claude Desktop（托盘也退干净）。

> 兼容性：官方 mcp SDK 2.0（2026-06）把 `FastMCP` 更名 `MCPServer` 并删除
> 旧导入路径。`server.py` 已做双版本兼容，1.x / 2.x 均可运行。

可用工具：

- `draw_card(tiers, count, lang)` — 转柱抽卡；等级池逗号分隔，一次至多 3 张；`lang="zh"/"en"` 定卡面语言
- `view_card(query, lang)` — 按编号或名称查卡；中文名、英文名、拉丁名均可模糊匹配
- `deck_stats(lang)` — 牌库概览
- `session_history(lang)` — Acta Noctis · 今夜战绩（存进程内存，重启清零）

`cards.json` 为完整双语数据（zh/en 全字段），网页与 MCP 共用同一文案。

配置好之后，对你的 AI 说一句"帮我抽一张"即可。
抽取权自此归持牌人所有。

## 安全

- 安全词写在每一张卡的末尾，也写在这里：**任何一方说出，一切立刻停下。**
- 地狱级（IV）条目全部标注"仅限幻想/文字演绎"，并逐条说明为什么，
  以及安全的替代路径。牌库有权保留空白格。
- SSC / RACK / PRICK。事前协商，事后照护，永远。

## 结构

```
astragali/
├── index.html       # 网页版 · Astragali Nox（星空 + 旋转棱柱 + 翻卡）
├── mcp/
│   ├── server.py    # MCP stdio server（Python，双版本兼容）
│   └── cards.json   # 100 张卡数据
├── README.md        # English
├── README.zh-CN.md  # 中文
├── LICENSE          # MIT
└── .gitignore
```

## Credits

**Septem** —— 概念、审美方向、等级策展、这副牌生长于其侧的石阶

**Caelum** —— 全部 100 张卡文本、星空 UI、棱柱、MCP server
--Fable5&Opus47

## License

MIT —— 概不退换，但欢迎 fork。
