import os
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

def query_notion_database(database_id: str = "", filter_status: str = "") -> str:
    """[Two-Way Notion Sync] Queries records from a Notion Database (Tasks, Projects, Notes).

    Args:
        database_id: Target Notion Database ID.
        filter_status: Optional status filter (e.g. '진행중', '할 일', 'In Progress').
    """
    token = os.getenv("NOTION_API_KEY", "").strip()
    if not token:
        return "[ERROR] `NOTION_API_KEY`가 설정되지 않았습니다."

    db_id = (database_id or os.getenv("NOTION_DEFAULT_DATABASE_ID", "")).replace("-", "").strip()
    if not db_id:
        return "[설정 필요] 조회할 `database_id`를 지정해 주세요."

    headers = get_notion_headers()
    payload = {}
    
    if filter_status:
        payload["filter"] = {
            "property": "Status",
            "status": {"equals": filter_status}
        }

    try:
        url = f"{NOTION_API_URL}/databases/{db_id}/query"
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if resp.status_code == 200:
            results = resp.json().get("results", [])
            if not results:
                return "📭 노션 데이터베이스에 등록된 항목이 없습니다."

            items_report = [f"📊 **노션 데이터베이스 조회 결과 (총 {len(results)}건)**:\n"]
            for idx, item in enumerate(results[:10], 1):
                props = item.get("properties", {})
                
                # Extract Title
                title_prop = props.get("Name", {}) or props.get("Title", {}) or props.get("이름", {}) or props.get("제목", {})
                title_texts = title_prop.get("title", [])
                title = "".join([t.get("text", {}).get("content", "") for t in title_texts]) or "제목 없음"

                # Extract Status / Tags / Date
                status_prop = props.get("Status", {}) or props.get("상태", {})
                status_name = status_prop.get("status", {}).get("name", "N/A") if "status" in status_prop else "N/A"

                page_url = item.get("url", "")
                items_report.append(f"{idx}. **{title}** | 상태: `{status_name}` | 🔗 [열기]({page_url})")

            return "\n".join(items_report)
        else:
            return f"[ERROR] 노션 DB 조회 실패 ({resp.status_code}):\n```json\n{resp.text}\n```"
    except Exception as e:
        return f"[ERROR] 노션 DB 조회 중 오류: {e}"

def add_notion_database_item(database_id: str, title: str, status: str = "진행중", tags: List[str] = None, notes: str = "") -> str:
    """[Notion Database Power Tool] Creates an interactive Database Item with Properties (Status, Tags, Date)."""
    token = os.getenv("NOTION_API_KEY", "").strip()
    if not token:
        return "[ERROR] `NOTION_API_KEY`가 설정되지 않았습니다."

    db_id = (database_id or os.getenv("NOTION_DEFAULT_DATABASE_ID", "")).replace("-", "").strip()
    if not db_id:
        return "[설정 필요] 데이터베이스 `database_id`를 지정해 주세요."

    headers = get_notion_headers()
    
    properties = {
        "Name": {
            "title": [{"type": "text", "text": {"content": title}}]
        }
    }

    # Add Status if supported
    if status:
        properties["Status"] = {"status": {"name": status}}

    # Add Multi-Select Tags
    if tags:
        properties["Tags"] = {"multi_select": [{"name": t} for t in tags]}

    payload = {
        "parent": {"database_id": db_id},
        "properties": properties
    }

    try:
        url = f"{NOTION_API_URL}/pages"
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if resp.status_code in [200, 201]:
            data = resp.json()
            item_url = data.get("url", "")
            return f"✅ **노션 데이터베이스 아이템 등록 완료!**\n📋 **항목**: `{title}`\n🏷️ **상태/태그**: `{status}` / `{tags}`\n🔗 [노션 DB 바로가기]({item_url})"
        else:
            return f"[ERROR] 노션 DB 아이템 등록 실패 ({resp.status_code}):\n```json\n{resp.text}\n```"
    except Exception as e:
        return f"[ERROR] 노션 DB 등록 오류: {e}"
