import os
import re
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv()

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

def get_notion_headers() -> Dict[str, str]:
    token = os.getenv("NOTION_API_KEY", "").strip()
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

def parse_inline_rich_text(text: str) -> List[Dict[str, Any]]:
    """Converts bold (**bold**) and inline code (`code`) into Notion rich_text objects."""
    parts = []
    # Simple regex parsing for bold and code
    pattern = r'(\*\*[^*]+\*\*|`[^`]+`)'
    tokens = re.split(pattern, text)

    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            parts.append({
                "type": "text",
                "text": {"content": token[2:-2]},
                "annotations": {"bold": True}
            })
        elif token.startswith("`") and token.endswith("`"):
            parts.append({
                "type": "text",
                "text": {"content": token[1:-1]},
                "annotations": {"code": True}
            })
        else:
            parts.append({
                "type": "text",
                "text": {"content": token}
            })

    return parts or [{"type": "text", "text": {"content": text}}]

def markdown_to_notion_blocks(markdown_text: str) -> List[Dict[str, Any]]:
    """Converts rich Markdown text into full-featured Notion Blocks:
    - Headings (H1, H2, H3)
    - Callouts (💡, ⚠️, 📌, 🚀)
    - To-Do Checklists (- [ ] / - [x])
    - Toggle Lists (▶ Toggle)
    - Dividers (---)
    - Code Blocks (```python ... ```)
    - Numbered & Bulleted Lists
    - 2D Tables (| col1 | col2 |)
    """
    blocks = []
    lines = markdown_text.splitlines()
    i = 0

    while i < len(lines):
        line_str = lines[i].strip()
        if not line_str:
            i += 1
            continue

        # 1. Divider (--- or ***)
        if line_str in ["---", "***", "___"]:
            blocks.append({"object": "block", "type": "divider", "divider": {}})
            i += 1
            continue

        # 2. Code Block (```lang ... ```)
        if line_str.startswith("```"):
            lang = line_str[3:].strip() or "plain text"
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({
                "object": "block",
                "type": "code",
                "code": {
                    "rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)}}],
                    "language": lang.lower() if lang.lower() in ["python", "javascript", "typescript", "html", "css", "json", "sql", "bash", "markdown"] else "plain text"
                }
            })
            i += 1
            continue

        # 3. Table (| col1 | col2 |)
        if line_str.startswith("|") and line_str.endswith("|"):
            table_rows = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                row_str = lines[i].strip()
                # Skip divider row |---|---|
                if not re.match(r'^\|[\s\-:|]+\|$', row_str):
                    cells = [c.strip() for c in row_str.strip("|").split("|")]
                    row_block = {
                        "type": "table_row",
                        "table_row": {
                            "cells": [[{"type": "text", "text": {"content": c}}] for c in cells]
                        }
                    }
                    table_rows.append(row_block)
                i += 1

            if table_rows:
                table_width = len(table_rows[0]["table_row"]["cells"])
                blocks.append({
                    "object": "block",
                    "type": "table",
                    "table": {
                        "table_width": table_width,
                        "has_column_header": True,
                        "has_row_header": False,
                        "children": table_rows
                    }
                })
            continue

        # 4. Headings (H1, H2, H3)
        if line_str.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": parse_inline_rich_text(line_str[2:])}
            })
        elif line_str.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": parse_inline_rich_text(line_str[3:])}
            })
        elif line_str.startswith("### "):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": parse_inline_rich_text(line_str[4:])}
            })

        # 5. To-Do Checklist (- [ ] / - [x])
        elif line_str.startswith("- [ ] ") or line_str.startswith("- [x] ") or line_str.startswith("- [X] "):
            checked = line_str.startswith("- [x] ") or line_str.startswith("- [X] ")
            blocks.append({
                "object": "block",
                "type": "to_do",
                "to_do": {
                    "rich_text": parse_inline_rich_text(line_str[6:]),
                    "checked": checked
                }
            })

        # 6. Toggle List (▶ or >+ )
        elif line_str.startswith("▶ ") or line_str.startswith(">+ "):
            toggle_text = line_str[2:].strip() if line_str.startswith("▶ ") else line_str[3:].strip()
            blocks.append({
                "object": "block",
                "type": "toggle",
                "toggle": {"rich_text": parse_inline_rich_text(toggle_text)}
            })

        # 7. Callout / Quote (> Quote)
        elif line_str.startswith("> "):
            callout_text = line_str[2:].strip()
            emoji_icon = "💡"
            if "⚠️" in callout_text or "주의" in callout_text or "경고" in callout_text:
                emoji_icon = "⚠️"
            elif "📌" in callout_text or "중요" in callout_text:
                emoji_icon = "📌"
            elif "🚀" in callout_text or "목표" in callout_text:
                emoji_icon = "🚀"

            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": parse_inline_rich_text(callout_text),
                    "icon": {"type": "emoji", "emoji": emoji_icon}
                }
            })

        # 8. Bullet & Numbered List
        elif line_str.startswith("- ") or line_str.startswith("* "):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline_rich_text(line_str[2:])}
            })
        elif re.match(r'^\d+\.\s+', line_str):
            item_text = re.sub(r'^\d+\.\s+', '', line_str)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline_rich_text(item_text)}
            })

        # 9. Paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": parse_inline_rich_text(line_str)}
            })

        i += 1

    return blocks

def create_notion_page(title: str, content: str, parent_page_id: str = "") -> str:
    """[Pro Notion AI Engine] Creates a beautifully formatted Notion page utilizing full Notion block capabilities."""
    token = os.getenv("NOTION_API_KEY", "").strip()
    if not token:
        return "[설정 필요] `NOTION_API_KEY`가 `.env`에 설정되지 않았습니다."

    target_parent_id = parent_page_id or os.getenv("NOTION_DEFAULT_PAGE_ID", "").strip()
    target_parent_id = target_parent_id.replace("-", "").strip()

    headers = get_notion_headers()
    blocks = markdown_to_notion_blocks(content)

    payload = {
        "parent": {"page_id": target_parent_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": blocks[:100]
    }

    try:
        url = f"{NOTION_API_URL}/pages"
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            page_url = data.get("url", "")
            return f"✅ **노션 프로 페이지 생성 완료!**\n📄 **제목**: `{title}`\n🔗 [노션 페이지 바로가기]({page_url})"
        else:
            return f"[ERROR] 노션 페이지 생성 실패 ({resp.status_code}):\n```json\n{resp.text}\n```"
    except Exception as e:
        return f"[ERROR] 노션 API 호출 중 오류: {e}"

def read_notion_page(page_id: str) -> str:
    """Reads all blocks from a Notion page to summarize or edit."""
    token = os.getenv("NOTION_API_KEY", "").strip()
    if not token:
        return "[설정 필요] `NOTION_API_KEY`가 설정되지 않았습니다."

    clean_id = (page_id or os.getenv("NOTION_DEFAULT_PAGE_ID", "")).replace("-", "").strip()
    headers = get_notion_headers()

    try:
        url = f"{NOTION_API_URL}/blocks/{clean_id}/children?page_size=100"
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            lines = []
            for b in results:
                b_type = b.get("type", "")
                rich_text = b.get(b_type, {}).get("rich_text", [])
                text = "".join([t.get("text", {}).get("content", "") for t in rich_text])
                if text:
                    lines.append(text)
            return "\n".join(lines) or "노션 페이지가 비어 있습니다."
        else:
            return f"[ERROR] 노션 페이지 읽기 실패 ({resp.status_code})"
    except Exception as e:
        return f"[ERROR] 노션 읽기 오류: {e}"

def append_to_notion_page(page_id: str, content: str) -> str:
    """Appends markdown blocks to an existing Notion page."""
    token = os.getenv("NOTION_API_KEY", "").strip()
    clean_id = (page_id or os.getenv("NOTION_DEFAULT_PAGE_ID", "")).replace("-", "").strip()
    headers = get_notion_headers()
    blocks = markdown_to_notion_blocks(content)

    try:
        url = f"{NOTION_API_URL}/blocks/{clean_id}/children"
        resp = requests.patch(url, headers=headers, json={"children": blocks[:100]}, timeout=10)
        if resp.status_code in [200, 201]:
            return f"✅ **노션 페이지 업데이트 완료!**\n새로운 내용이 성공적으로 추가되었습니다."
        else:
            return f"[ERROR] 노션 업데이트 실패 ({resp.status_code}): {resp.text}"
    except Exception as e:
        return f"[ERROR] 노션 업데이트 오류: {e}"
