import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("NOTION_API_KEY")
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
PARENT_PAGE_ID = "3bf4e6a9b256809f9569ffd78d95438a"

def main():
    print("🚀 [Budget & Sponsorship DB] Creating Project Tov2 and Comprehensive Finance Database...")

    # 1. Create Project Tov2 Page
    url = "https://api.notion.com/v1/pages"
    tov2_payload = {
        "parent": {"page_id": PARENT_PAGE_ID},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": "Project Tov2"}}]}
        },
        "icon": {"type": "emoji", "emoji": "💰"},
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "💰 Project Tov2 재정 및 후원금 관리 통합 시스템입니다.\n지출(녹음/세션/믹싱/마스터링/영상)뿐만 아니라 개인/단체 후원금, 기부금 영수증, 입금 상태를 한눈에 관리할 수 있습니다."}}],
                    "icon": {"type": "emoji", "emoji": "📊"}
                }
            },
            {"object": "block", "type": "divider", "divider": {}}
        ]
    }

    tov2_res = requests.post(url, headers=headers, json=tov2_payload)
    if tov2_res.status_code not in [200, 201]:
        print(f"❌ Failed to create Project Tov2: {tov2_res.status_code} - {tov2_res.text}")
        return

    tov2_data = tov2_res.json()
    tov2_id = tov2_data["id"]
    tov2_url = tov2_data.get("url", "")
    print(f"✅ Created Project Tov2 ({tov2_id})")

    # 2. Create Budget, Sponsorship & Finance Database inside Project Tov2
    db_url = "https://api.notion.com/v1/databases"
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

    db_payload = {
        "parent": {"page_id": tov2_id},
        "title": [{"type": "text", "text": {"content": "💰 Budget, Sponsorship & Finance Database"}}],
        "icon": {"type": "emoji", "emoji": "💰"},
        "properties": budget_props
    }

    db_res = requests.post(db_url, headers=headers, json=db_payload)
    if db_res.status_code not in [200, 201]:
        print(f"❌ Failed to create DB: {db_res.status_code} - {db_res.text}")
        return

    db_data = db_res.json()
    db_id = db_data["id"]
    print(f"✅ Created Budget & Sponsorship Database ({db_id})")

    # 3. Populate Sample Records (Sponsorship & Expenses)
    records = [
        # Sponsorship Income
        ("이룸교회 청년부 앨범 제작 지정 후원금", "💵 후원금 (수입)", "후원금 (개인 성도)", 1000000, 1000000, "익명 성도", "Project Partner", "입금완료", "발행 완료", "2026-08-15", "음반 제작 및 녹음비 지정 후원"),
        ("Tov 프로젝트 서포터즈 1차 모금", "💵 후원금 (수입)", "후원금 (개인 성도)", 2500000, 3000000, "서포터즈 12명", "일반 후원", "입금완료", "발행 필요", "2026-08-18", "부클릿 크레딧 기재 예정"),
        ("협력 기업 사역 후원금", "💵 후원금 (수입)", "후원금 (기업/단체)", 2000000, 2000000, "(주)선한기업", "Special Sponsor", "입금완료", "발행 완료", "2026-08-19", "세금계산서 발행 완료"),
        # Production Expenses
        ("스튜디오 사운드 메인 보컬 녹음실 대관", "💳 지출 (Expense)", "Recording", 1500000, 1500000, "스튜디오 사운드", "해당 없음 (지출)", "결제완료", "미발행 (불필요)", "2026-08-20", "9/2 녹음 예약금 포함"),
        ("전문 세션 연주비 (베이스/일렉/드럼)", "💳 지출 (Expense)", "Session", 1200000, 1200000, "세션팀", "해당 없음 (지출)", "결제완료", "미발행 (불필요)", "2026-08-20", "코드보 배포 완료"),
        ("5트랙 전문 믹싱 & 사운드 디자인", "💳 지출 (Expense)", "Mixing", 1500000, 1500000, "믹싱 엔지니어", "해당 없음 (지출)", "대기", "미발행 (불필요)", "2026-09-05", "1차 러프본 수령 후 잔금 집행"),
        ("앨범 커버 및 피지컬 패키지 디자인", "💳 지출 (Expense)", "Artwork & Design", 700000, 700000, "디자인 스튜디오", "해당 없음 (지출)", "세금계산서/영수증발행", "미발행 (불필요)", "2026-08-19", "3000px 커버 및 폰트 라이선스")
    ]

    row_url = "https://api.notion.com/v1/pages"
    for r in records:
        row_payload = {
            "parent": {"database_id": db_id},
            "properties": {
                "항목명 / 내역": {"title": [{"type": "text", "text": {"content": r[0]}}]},
                "구분 (Type)": {"select": {"name": r[1]}},
                "카테고리": {"select": {"name": r[2]}},
                "금액 (Amount)": {"number": r[3]},
                "예산안 (Planned)": {"number": r[4]},
                "후원자 / 거래처": {"rich_text": [{"type": "text", "text": {"content": r[5]}}]},
                "후원 파트너 구분": {"select": {"name": r[6]}},
                "입금 / 결제 상태": {"status": {"name": r[7]}},
                "기부금영수증": {"select": {"name": r[8]}},
                "일자": {"date": {"start": r[9]}},
                "비고": {"rich_text": [{"type": "text", "text": {"content": r[10]}}]}
            }
        }
        requests.post(row_url, headers=headers, json=row_payload)
        time.sleep(0.3)

    print("\n🎉 [Project Tov2 Finance DB Complete] Created successfully under Project Tov2!")
    print(f"🔗 Project Tov2 URL: {tov2_url}")

if __name__ == "__main__":
    main()
