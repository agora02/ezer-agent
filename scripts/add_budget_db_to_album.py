import os
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NOTION_API_KEY")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

ALBUM_ID = "3c14e6a9-b256-817c-ab72-d1435abe4bc8"

def main():
    print(f"🚀 Creating 💰 Budget & Finance Database inside 26 Q4 Tov Project Album ({ALBUM_ID})...")
    url = "https://api.notion.com/v1/databases"
    
    budget_props = {
        "항목명 / 내역": {"title": {}},
        "구분 (Type)": {
            "select": {
                "options": [
                    {"name": "💵 후원금 (수입)", "color": "green"},
                    {"name": "💳 지출 (Expense)", "color": "red"},
                    {"name": "🏛️ 교회 지원금", "color": "blue"},
                    {"name": "📦 기타 수입", "color": "purple"}
                ]
            }
        },
        "카테고리": {
            "select": {
                "options": [
                    {"name": "후원금 (개인 성도)", "color": "green"},
                    {"name": "후원금 (기업/단체)", "color": "blue"},
                    {"name": "Recording", "color": "yellow"},
                    {"name": "Session", "color": "orange"},
                    {"name": "Mixing", "color": "purple"},
                    {"name": "Mastering", "color": "pink"},
                    {"name": "Artwork & Design", "color": "brown"},
                    {"name": "Video & MV", "color": "red"},
                    {"name": "Distribution & Marketing", "color": "gray"},
                    {"name": "기타 (Misc)", "color": "default"}
                ]
            }
        },
        "금액 (Amount)": {"number": {"format": "won"}},
        "예산안 (Planned)": {"number": {"format": "won"}},
        "후원자 / 거래처": {"rich_text": {}},
        "후원 파트너 구분": {
            "select": {
                "options": [
                    {"name": "Prayer Partner", "color": "purple"},
                    {"name": "Project Partner", "color": "blue"},
                    {"name": "Special Sponsor", "color": "yellow"},
                    {"name": "일반 후원", "color": "green"},
                    {"name": "해당 없음 (지출)", "color": "gray"}
                ]
            }
        },
        "입금 / 결제 상태": {
            "status": {
                "options": [
                    {"name": "대기", "color": "gray"},
                    {"name": "입금완료", "color": "green"},
                    {"name": "결제완료", "color": "blue"},
                    {"name": "세금계산서/영수증발행", "color": "purple"}
                ]
            }
        },
        "기부금영수증": {
            "select": {
                "options": [
                    {"name": "발행 필요", "color": "yellow"},
                    {"name": "발행 완료", "color": "green"},
                    {"name": "미발행 (불필요)", "color": "gray"}
                ]
            }
        },
        "일자": {"date": {}},
        "비고": {"rich_text": {}}
    }

    payload = {
        "parent": {"page_id": ALBUM_ID},
        "title": [{"type": "text", "text": {"content": "💰 Budget & Finance Database"}}],
        "icon": {"type": "emoji", "emoji": "💰"},
        "properties": budget_props
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ Successfully created 💰 Budget & Finance Database inside 26 Q4 Tov Project Album! ID: {data.get('id')}")
        print(f"🔗 URL: {data.get('url')}")
    else:
        print(f"❌ Failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    main()
