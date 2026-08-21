import os
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

NOTION_VERSION = "2022-06-28"

def _get_headers() -> Dict[str, str]:
    api_key = os.getenv("NOTION_API_KEY", "").strip()
    if not api_key:
        raise ValueError("NOTION_API_KEY가 설정되지 않았습니다. .env 또는 설정에서 노션 API 키를 입력해주세요.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }

def create_notion_page(title: str, content: str, parent_page_id: Optional[str] = None) -> str:
    """노션에 새로운 페이지를 생성하고 마크다운 형식의 본문을 작성합니다.
    Args:
        title: 페이지 제목
        content: 페이지 내용 (줄바꿈 포함 텍스트)
        parent_page_id: 상위 페이지 ID (생략 시 NOTION_DEFAULT_PAGE_ID 사용)
    """
    try:
        headers = _get_headers()
        target_parent = parent_page_id or os.getenv("NOTION_DEFAULT_PAGE_ID", "").strip()
        
        if not target_parent:
            return "[ERROR] 상위 페이지 ID가 지정되지 않았습니다. NOTION_DEFAULT_PAGE_ID를 설정하거나 parent_page_id를 전달해주세요."

        # Clean dashes if needed
        clean_parent = target_parent.replace("-", "")

        # Build blocks from content lines
        children_blocks = []
        for line in content.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            if line_str.startswith("# "):
                children_blocks.append({
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {"rich_text": [{"type": "text", "text": {"content": line_str[2:]}}]}
                })
            elif line_str.startswith("## "):
                children_blocks.append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"type": "text", "text": {"content": line_str[3:]}}]}
                })
            elif line_str.startswith("### "):
                children_blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": line_str[4:]}}]}
                })
            elif line_str.startswith("- ") or line_str.startswith("* "):
                children_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line_str[2:]}}]}
                })
            elif line_str.startswith("1. ") or line_str.startswith("2. ") or line_str.startswith("3. "):
                children_blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": line_str[3:]}}]}
                })
            else:
                children_blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"type": "text", "text": {"content": line_str}}]}
                })

        payload = {
            "parent": {"page_id": clean_parent},
            "properties": {
                "title": {
                    "title": [{"type": "text", "text": {"content": title}}]
                }
            },
            "children": children_blocks[:95] # Notion max 100 children per request
        }

        resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload, timeout=12)
        if resp.status_code == 200:
            data = resp.json()
            page_url = data.get("url", "")
            return f"✅ **노션 페이지 생성 완료!**\n- 제목: **{title}**\n- 링크: [노션에서 보기]({page_url})"
        else:
            return f"[ERROR] 노션 페이지 생성 실패 ({resp.status_code}): {resp.text}"

    except Exception as e:
        return f"[ERROR] 노션 연동 오류: {e}"

def search_notion_pages(query: str, max_results: int = 5) -> str:
    """노션 워크스페이스 내에서 페이지나 데이터베이스를 검색합니다.
    Args:
        query: 검색어
        max_results: 최대 결과 수
    """
    try:
        headers = _get_headers()
        payload = {
            "query": query,
            "page_size": max_results
        }
        resp = requests.post("https://api.notion.com/v1/search", headers=headers, json=payload, timeout=10)
        if resp.status_code != 200:
            return f"[ERROR] 노션 검색 실패 ({resp.status_code}): {resp.text}"

        results = resp.json().get("results", [])
        if not results:
            return f"🔍 노션에서 '{query}' 검색 결과가 없습니다."

        items = []
        for r in results:
            obj_type = r.get("object", "page")
            url = r.get("url", "")
            title = "제목 없음"
            
            # Extract title
            props = r.get("properties", {})
            for p_name, p_val in props.items():
                if p_val.get("type") == "title":
                    t_list = p_val.get("title", [])
                    if t_list:
                        title = t_list[0].get("plain_text", "제목 없음")
                    break
            
            if title == "제목 없음" and "title" in r:
                # database title
                t_list = r.get("title", [])
                if t_list:
                    title = t_list[0].get("plain_text", "제목 없음")

            items.append(f"• **[{obj_type.upper()}] {title}**\n  - 링크: {url}\n  - ID: `{r.get('id')}`")

        return f"🔍 **노션 '{query}' 검색 결과 (총 {len(items)}건)**:\n\n" + "\n\n".join(items)

    except Exception as e:
        return f"[ERROR] 노션 검색 중 오류: {e}"

def append_to_notion_page(page_id: str, content: str) -> str:
    """기존 노션 페이지의 맨 아래에 텍스트/메모 내용을 추가합니다.
    Args:
        page_id: 추가할 노션 페이지 ID
        content: 추가할 내용
    """
    try:
        headers = _get_headers()
        clean_id = page_id.replace("-", "")
        
        children_blocks = []
        for line in content.split("\n"):
            line_str = line.strip()
            if not line_str:
                continue
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": line_str}}]}
            })

        payload = {"children": children_blocks}
        url = f"https://api.notion.com/v1/blocks/{clean_id}/children"
        resp = requests.patch(url, headers=headers, json=payload, timeout=10)
        
        if resp.status_code == 200:
            return f"✅ **노션 페이지에 내용 추가 완료!** (페이지 ID: `{clean_id}`)"
        else:
            return f"[ERROR] 노션 내용 추가 실패 ({resp.status_code}): {resp.text}"

    except Exception as e:
        return f"[ERROR] 노션 추가 오류: {e}"
