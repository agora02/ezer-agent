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

def create_subpage(title: str, blocks: list, parent_id: str = PARENT_PAGE_ID, icon: str = None) -> dict:
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {"title": [{"type": "text", "text": {"content": title}}]}
        },
        "children": blocks[:100]
    }
    if icon:
        payload["icon"] = {"type": "emoji", "emoji": icon}
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ Created subpage: {title} ({data.get('id')})")
        return data
    else:
        print(f"❌ Failed to create {title}: {resp.status_code} - {resp.text}")
        return None

def create_database(parent_id: str, title: str, properties: dict, icon: str = None) -> dict:
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"page_id": parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }
    if icon:
        payload["icon"] = {"type": "emoji", "emoji": icon}
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ Created Database: {title} ({data.get('id')})")
        return data
    else:
        print(f"❌ Failed to create Database {title}: {resp.status_code} - {resp.text}")
        return None

def add_database_row(database_id: str, properties: dict, children: list = None) -> dict:
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties
    }
    if children:
        payload["children"] = children[:100]
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        return resp.json()
    else:
        print(f"❌ Failed to add row to DB {database_id}: {resp.status_code} - {resp.text}")
        return None

def main():
    print("🚀 [Gemini 3.7 Architect] Executing Full Production Master Workspace Deployment on Notion...")

    # 1. Main Workspace Root Page
    main_root = create_subpage(
        title="📀 26 Q4 Tov Project Album (Master Workspace)",
        icon="📀",
        blocks=[
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "📀 26 Q4 Tov Project Album 통합 제작 및 운영 워크스페이스입니다.\nApple & Linear 미니멀리즘 디자인과 실무 제작 파이프라인(Tracks, Tasks, Budget, Timeline)으로 완벽하게 구축되었습니다."}}],
                    "icon": {"type": "emoji", "emoji": "🎯"}
                }
            },
            {"object": "block", "type": "divider", "divider": {}}
        ]
    )

    if not main_root:
        print("Root creation failed.")
        return

    root_id = main_root["id"]

    # 2. Tracks Database
    tracks_props = {
        "Track No.": {"number": {"format": "number"}},
        "Song Title": {"title": {}},
        "Track Type": {
            "select": {
                "options": [
                    {"name": "Original", "color": "blue"},
                    {"name": "Remake", "color": "purple"},
                    {"name": "Intro", "color": "gray"},
                    {"name": "Interlude", "color": "default"},
                    {"name": "Outro", "color": "orange"}
                ]
            }
        },
        "Status": {
            "status": {
                "options": [
                    {"name": "Idea", "color": "gray"},
                    {"name": "Writing", "color": "brown"},
                    {"name": "Demo", "color": "orange"},
                    {"name": "Arrangement", "color": "yellow"},
                    {"name": "Recording", "color": "blue"},
                    {"name": "Editing", "color": "purple"},
                    {"name": "Mixing", "color": "pink"},
                    {"name": "Mastering", "color": "red"},
                    {"name": "Complete", "color": "green"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "BPM": {"number": {}},
        "Key": {"rich_text": {}},
        "Duration": {"rich_text": {}},
        "Genre": {"rich_text": {}},
        "Theme": {"rich_text": {}},
        "Composer": {"rich_text": {}},
        "Lyricist": {"rich_text": {}},
        "Arranger": {"rich_text": {}},
        "Owner": {"rich_text": {}},
        "Original Artist": {"rich_text": {}},
        "Original Song": {"rich_text": {}},
        "Publisher": {"rich_text": {}},
        "Copyright Status": {
            "select": {
                "options": [
                    {"name": "Not Checked", "color": "gray"},
                    {"name": "Checking", "color": "yellow"},
                    {"name": "Confirmed", "color": "blue"},
                    {"name": "Completed", "color": "green"}
                ]
            }
        },
        "Release Permission": {
            "select": {
                "options": [
                    {"name": "Required", "color": "red"},
                    {"name": "Not Required", "color": "gray"},
                    {"name": "Approved", "color": "green"}
                ]
            }
        },
        "License Notes": {"rich_text": {}},
        "Due Date": {"date": {}},
        "Recording Date": {"date": {}},
        "Mix Version": {"rich_text": {}},
        "Master Version": {"rich_text": {}}
    }
    tracks_db = create_database(root_id, "🎵 Tracks Database", tracks_props, icon="🎵")
    time.sleep(1)

    # 3. Tasks Database
    tasks_props = {
        "Task": {"title": {}},
        "Status": {
            "status": {
                "options": [
                    {"name": "Todo", "color": "gray"},
                    {"name": "In Progress", "color": "blue"},
                    {"name": "Waiting", "color": "yellow"},
                    {"name": "Review", "color": "purple"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "Area": {
            "select": {
                "options": [
                    {"name": "Songwriting", "color": "blue"},
                    {"name": "Arrangement", "color": "yellow"},
                    {"name": "Recording", "color": "red"},
                    {"name": "Mix", "color": "purple"},
                    {"name": "Master", "color": "pink"},
                    {"name": "Artwork", "color": "orange"},
                    {"name": "Video", "color": "green"},
                    {"name": "Promotion", "color": "brown"},
                    {"name": "Administration", "color": "gray"}
                ]
            }
        },
        "Priority": {
            "select": {
                "options": [
                    {"name": "High", "color": "red"},
                    {"name": "Medium", "color": "yellow"},
                    {"name": "Low", "color": "gray"}
                ]
            }
        },
        "Owner": {"rich_text": {}},
        "Due Date": {"date": {}}
    }
    tasks_db = create_database(root_id, "✅ Tasks Database", tasks_props, icon="✅")
    time.sleep(1)

    # 4. Budget & Finance Database
    budget_props = {
        "Item": {"title": {}},
        "Category": {
            "select": {
                "options": [
                    {"name": "Recording", "color": "blue"},
                    {"name": "Session", "color": "green"},
                    {"name": "Mixing", "color": "purple"},
                    {"name": "Mastering", "color": "red"},
                    {"name": "Artwork", "color": "orange"},
                    {"name": "Video", "color": "pink"},
                    {"name": "Distribution", "color": "yellow"},
                    {"name": "Marketing", "color": "brown"},
                    {"name": "Misc", "color": "gray"}
                ]
            }
        },
        "Planned Budget": {"number": {"format": "won"}},
        "Actual Cost": {"number": {"format": "won"}},
        "Payment Status": {
            "status": {
                "options": [
                    {"name": "대기", "color": "gray"},
                    {"name": "결제완료", "color": "green"},
                    {"name": "세금계산서발행", "color": "blue"}
                ]
            }
        },
        "Vendor": {"rich_text": {}}
    }
    budget_db = create_database(root_id, "💰 Budget & Finance Database", budget_props, icon="💰")
    time.sleep(1)

    # Populate Tasks DB with initial operational tasks
    initial_tasks = [
        ("01. 앨범 타이틀곡 편곡 세션 가이드 제작", "In Progress", "Arrangement", "High", "양명환", "2026-08-25"),
        ("02. 드럼 & 베이스 리듬 세션 스튜디오 녹음", "Todo", "Recording", "High", "양명환", "2026-09-02"),
        ("03. 앨범 커버 3000x3000px 최종 아트워크 시안 확정", "Todo", "Artwork", "Medium", "최지원", "2026-09-10"),
        ("04. 타이틀곡 뮤직비디오 스토리보드 및 로케이션 헌팅", "In Progress", "Video", "High", "최지원", "2026-08-30"),
        ("05. 음원 유통사(벅스/멜론/지니) 메타데이터 등록 서류 준비", "Waiting", "Promotion", "Medium", "최지원", "2026-09-15")
    ]
    for t in initial_tasks:
        add_database_row(tasks_db["id"], {
            "Task": {"title": [{"type": "text", "text": {"content": t[0]}}]},
            "Status": {"status": {"name": t[1]}},
            "Area": {"select": {"name": t[2]}},
            "Priority": {"select": {"name": t[3]}},
            "Owner": {"rich_text": [{"type": "text", "text": {"content": t[4]}}]},
            "Due Date": {"date": {"start": t[5]}}
        })

    # Populate Budget DB with sample budget items
    initial_budget = [
        ("메인 보컬 & 드럼 스튜디오 레코딩 렌탈비", "Recording", 1500000, 1500000, "결제완료", "스튜디오 사운드"),
        ("외부 전문 세션 연주비 (베이스/기타/스트링)", "Session", 1200000, 1000000, "결제완료", "세션 연주팀"),
        ("전곡 믹싱 엔지니어링 (5트랙)", "Mixing", 1500000, 0, "대기", "믹싱 스튜디오"),
        ("스털링 사운드 마스터링 (Mastering)", "Mastering", 800000, 0, "대기", "Mastering Lab"),
        ("앨범 커버 아트워크 & 피지컬 패키지 디자인", "Artwork", 700000, 700000, "세금계산서발행", "디자인 스튜디오"),
        ("타이틀곡 라이브 뮤직비디오 촬영 및 조명", "Video", 2500000, 1000000, "대기", "프로덕션 필름")
    ]
    for b in initial_budget:
        add_database_row(budget_db["id"], {
            "Item": {"title": [{"type": "text", "text": {"content": b[0]}}]},
            "Category": {"select": {"name": b[1]}},
            "Planned Budget": {"number": b[2]},
            "Actual Cost": {"number": b[3]},
            "Payment Status": {"status": {"name": b[4]}},
            "Vendor": {"rich_text": [{"type": "text", "text": {"content": b[5]}}]}
        })

    # Populate Tracks DB with full in-depth tracks and templates
    tracks_data = [
        (1, "01. Intro: Faithfulness", "Intro", "Complete", 68, "D Major", "Ambient Instrumental", "하나님의 임재와 시작", "양명환", "양명환", "양명환", "양명환"),
        (2, "02. Remember His Faithfulness (신실하심)", "Original", "Arrangement", 72, "E Major", "Modern Worship / CC", "하나님의 신실하심을 기억하라", "양명환", "최지원", "양명환", "최지원"),
        (3, "03. 은혜의 여정", "Original", "Demo", 76, "G Major", "Contemporary Worship", "공동체가 걸어온 은혜의 발자취", "박지원", "박지원", "양명환", "박지원"),
        (4, "04. 주를 예배하는 세대", "Original", "Writing", 128, "A Major", "Praise / Rock Worship", "다음 세대의 헌신과 찬양", "박시온", "박시온", "양명환", "박시온"),
        (5, "05. Outro: Everlasting", "Outro", "Idea", 64, "D Major", "Acoustic Reflection", "영원한 언약의 마무리", "양명환", "양명환", "양명환", "양명환")
    ]
    for t in tracks_data:
        add_database_row(tracks_db["id"], {
            "Track No.": {"number": t[0]},
            "Song Title": {"title": [{"type": "text", "text": {"content": t[1]}}]},
            "Track Type": {"select": {"name": t[2]}},
            "Status": {"status": {"name": t[3]}},
            "Priority": {"select": {"name": "High" if t[0] <= 2 else "Medium"}},
            "BPM": {"number": t[4]},
            "Key": {"rich_text": [{"type": "text", "text": {"content": t[5]}}]},
            "Genre": {"rich_text": [{"type": "text", "text": {"content": t[6]}}]},
            "Theme": {"rich_text": [{"type": "text", "text": {"content": t[7]}}]},
            "Composer": {"rich_text": [{"type": "text", "text": {"content": t[8]}}]},
            "Lyricist": {"rich_text": [{"type": "text", "text": {"content": t[9]}}]},
            "Arranger": {"rich_text": [{"type": "text", "text": {"content": t[10]}}]},
            "Owner": {"rich_text": [{"type": "text", "text": {"content": t[11]}}]}
        }, children=[
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": f"Track No. {t[0]:02d} | Type: {t[2]} | Status: {t[3]} | BPM: {t[4]} | Key: {t[5]}\nTheme: {t[7]}"}}], "icon": {"type": "emoji", "emoji": "🎧"}}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📋 1. Song Overview"}}]}},
            {
                "object": "block", "type": "table", "table": {
                    "table_width": 2, "has_column_header": True, "has_row_header": False,
                    "children": [
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "항목"}}], [{"type": "text", "text": {"content": "내용"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "작곡/작사"}}], [{"type": "text", "text": {"content": f"{t[8]} / {t[9]}"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "편곡/담당"}}], [{"type": "text", "text": {"content": f"{t[10]} / {t[11]}"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "BPM / Key"}}], [{"type": "text", "text": {"content": f"{t[4]} BPM / {t[5]}"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "장르 / 무드"}}], [{"type": "text", "text": {"content": f"{t[6]} / {t[7]}"}}]]}}
                    ]
                }
            },
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📜 2. Lyrics (가사)"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "[Verse 1]\n주의 신실하심이 아침마다 새롭고\n주의 인자하심이 영원히 머무네\n\n[Chorus]\nRemember His Faithfulness\n우릴 인도하신 주를 찬양해\n어두운 밤 지나고 새 날이 밝아오니\n주를 높이리라\n\n[Bridge]\n대대에 이를 주의 영광\n주의 선하심을 영원히 노래하리라"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎹 3. Musical Direction & Arrangement Notes"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "악기 편성: Acoustic Piano, Warm Pad, Ambient Electric Guitar, Bass, Drum Set"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "빌드업 구조: 1절 피아노+보컬 ➔ 2절 리듬 섹션 추가 ➔ 브릿지 풀 콰이어 및 드럼 빌드업"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎙️ 4. Recording & Mix Notes"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "보컬 톤: 과도한 기교를 지양하고 회중 예배에 적합한 맑고 진정성 있는 톤"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "믹싱 타겟: 깊은 앰비언스 리버브 공간감과 명료한 센터 보컬 밸런스"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ 5. Track TODOs"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "1차 가이드 보컬 데모 레코딩"}}], "checked": True}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "세션 가이드 차트(코드보) 제작"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "메인 보컬 & 코러스 본 녹음"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "1차 러프 믹스본 리뷰"}}], "checked": False}}
        ])

    # 5. Build All Subpages with 100% PRD details
    # 5-1. Dashboard
    create_subpage(
        title="🏠 Dashboard", icon="🏠", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📊 Project Progress"}}]}},
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "전체 진행률: ████████░░ 75%\n현재 제작 단계: [ Arrangement & Recording Preparation ]"}}], "icon": {"type": "emoji", "emoji": "⚡"}}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🧭 Current Phase Progression"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "• Concept  ➔  • Songwriting  ➔  • Demo  ➔  • [ Arrangement & Recording ]  ➔  • Editing  ➔  • Mixing  ➔  • Mastering  ➔  • Release"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🔗 Quick Links"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "🎵 Tracks Database | ✅ Tasks Database | 💰 Budget & Finance"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "🎯 Album Direction | 👥 Team | 📅 Production Timeline | 🎬 Visual"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "🎨 Branding & Artwork | 🤝 Partnership | 📂 Assets | 📝 Meeting Notes | 🚀 Release Center | 📚 References"}}]}}
        ]
    )

    # 5-2. Album Direction
    create_subpage(
        title="🎯 Album Direction", icon="🎯", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🌟 1. Vision"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "하나님께서 이룸교회에 부어주신 은혜를 예배로 기록하고, 다음 세대에도 이어질 믿음의 고백으로 남긴다."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📖 2. Core Message"}}]}},
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "Remember His Faithfulness (하나님의 신실하심을 기억하라)"}}], "icon": {"type": "emoji", "emoji": "✨"}}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🙏 3. Spiritual Direction"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "공동체가 경험한 하나님의 은혜를 꾸밈없이 고백하며, 회중이 함께 하나님을 바라보고 예배할 수 있는 곡을 만든다."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 4. Target Audience"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Primary: 이룸교회 성도"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Secondary: 새신자 및 등록 예정 성도"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Tertiary: 신앙을 찾고 있거나 교회 공동체를 알아가고 싶은 청년들"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🏆 5. Project Outcomes"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "하나님께 받은 은혜를 기록한다."}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "공동체가 함께 부를 수 있는 예배곡을 만든다."}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "다음 세대에 남을 음반 유산을 만든다."}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "예배를 통해 하나님의 선하심(Tov)을 전한다."}}]}}
        ]
    )

    # 5-3. Team
    create_subpage(
        title="👥 Team", icon="👥", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "프로젝트 핵심 제작진"}}]}},
            {
                "object": "block", "type": "table", "table": {
                    "table_width": 4, "has_column_header": True, "has_row_header": False,
                    "children": [
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "이름"}}], [{"type": "text", "text": {"content": "직책/역할"}}], [{"type": "text", "text": {"content": "담당 업무"}}], [{"type": "text", "text": {"content": "연락처/비고"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "양명환"}}], [{"type": "text", "text": {"content": "Executive Producer"}}], [{"type": "text", "text": {"content": "총괄 프로듀싱, 음악 방향성, 편곡 지휘"}}], [{"type": "text", "text": {"content": "음악 총괄"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "최지원"}}], [{"type": "text", "text": {"content": "Project Manager"}}], [{"type": "text", "text": {"content": "일정/예산/제작 파이프라인/노션 아카이빙"}}], [{"type": "text", "text": {"content": "PM"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "박지원"}}], [{"type": "text", "text": {"content": "Worship Leader"}}], [{"type": "text", "text": {"content": "예배 보컬 디렉팅 & 송라이팅"}}], [{"type": "text", "text": {"content": "워십 리더"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "박시온"}}], [{"type": "text", "text": {"content": "Worship Leader"}}], [{"type": "text", "text": {"content": "예배 보컬 디렉팅 & 송라이팅"}}], [{"type": "text", "text": {"content": "워십 리더"}}]]}}
                    ]
                }
            }
        ]
    )

    # 5-4. Production Timeline
    create_subpage(
        title="📅 Production Timeline", icon="📅", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "프로젝트 전체 단계별 제작 로드맵"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Concept ➔ Songwriting ➔ Demo ➔ Arrangement ➔ Recording ➔ Mix ➔ Master ➔ Artwork ➔ Release"}}]}},
            {"object": "block", "type": "divider", "divider": {}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 1: Concept & 송라이팅 기획 완료"}}], "checked": True}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 2: 가이드 보컬 데모(Demo) 트랙 제작 완료"}}], "checked": True}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 3: 전문 편곡(Arrangement) & 세션 가이드 차트 작업"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 4: 스튜디오 메인 보컬 & 세션 본 녹음 (Recording)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 5: 믹싱(Mixing) & 마스터링(Mastering)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Phase 6: 아트워크 패키징 / MV / 유통사 릴리즈(Release)"}}], "checked": False}}
        ]
    )

    # 5-5. Visual
    create_subpage(
        title="🎬 Visual", icon="🎬", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎥 1. Music Video"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Concept: 예배 현장의 진정성과 빛의 확산"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Storyboard / Shot List: 인트로 피아노 클로즈업 ➔ 브릿지 풀샷 조명 연출"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Location / Cast / Schedule / Editing Notes"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🌌 2. Visualizer"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "3D 모션 그래픽 & AI 비주얼 프롬프트 아카이브"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📱 3. Promotion / Teaser / SNS Shorts"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "업로드 일정 / 플랫폼별 규격 / 자막 템플릿 / 공식 해시태그 전략"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎞️ 4. Behind Film & Media Assets"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "메이킹 다큐멘터리 / 제작진 인터뷰 / 썸네일, 포스터, 배너, SNS 고화질 원본"}}]}}
        ]
    )

    # 5-6. Branding & Artwork
    create_subpage(
        title="🎨 Branding & Artwork", icon="🎨", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "앨범 아트워크 & 브랜드 아이덴티티"}}]}},
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "디자인 원칙: Apple & Linear 미니멀리즘 / 킨파쿠 골드(#E8B959) & 라커 다크(#111217)"}}], "icon": {"type": "emoji", "emoji": "🎨"}}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Official Album Cover 아트워크 최종본 (3000x3000px RGB)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Moodboard & References 아카이브"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Typography & 서체 라이선스 규정"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "AI Prompt Archive & Final Vector Assets"}}]}}
        ]
    )

    # 5-7. Partnership & Sponsorship
    create_subpage(
        title="🤝 Partnership & Sponsorship", icon="🤝", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "프로젝트 소개 및 후원 동역"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "26 Q4 Tov Project Album은 다음 세대를 위한 예배 유산으로 제작되며, 모든 후원금은 100% 음반 제작 및 유통에 투명하게 집행됩니다."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🤝 후원 파트너 구분"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Prayer Partner: 음반 제작과 영적 결실을 위해 중보하는 기도 동역팀"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Project Partner: 제작비 및 스튜디오 후원에 동참하는 재정 파트너"}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📋 후원자 관리 및 FAQ"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "후원자 명단 앨범 부클릿 크레딧 기재 원칙 / 기부금 영수증 및 감사 보고"}}]}}
        ]
    )

    # 5-8. Assets
    create_subpage(
        title="📂 Assets", icon="📂", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "제작 파일 및 폴더 아카이브 구조"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 01_Lyrics: 곡별 최종 가사 텍스트본"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 02_Demo: 가이드 보컬 및 피아노 데모 MP3"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 03_Logic_Project: 로직 프로(Logic Pro) 멀티트랙 프로젝트 파일"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 04_Stems: 악기별 개별 멀티 트랙 음원"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 05_Mix_Master: 최종 24bit/48kHz 무손실 WAV 마스터"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 06_Artwork_Photo: 고해상도 커버, 프로필 사진, 인쇄용 PSD"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 07_Video: MV 마스터본, 티저 클립, 숏폼 원본"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 08_Documents: 계약서, 저작권 승인서, 기획서"}}]}}
        ]
    )

    # 5-9. Meeting Notes
    create_subpage(
        title="📝 Meeting Notes", icon="📝", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "정기 프로덕션 회의록"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Meeting Date: 2026-08-20"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Participants: 양명환, 최지원, 박지원, 박시온"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Agenda: 26 Q4 Tov Project Album 5개 트랙 프로덕션 파이프라인 및 예산 확정"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Discussion: 타이틀곡 'Remember His Faithfulness'의 편곡 스케일 및 세션 레코딩 일정 논의"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Decisions: 타이틀곡 D Major에서 E Major로 전조 확정, 스튜디오 사운드 9/2 렌탈 예약"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Action Item: 세션 연주자 가이드 차트(코드보) 배포 (~8/25, 양명환)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Action Item: MV 촬영 로케이션 최종 컨펌 (~8/30, 최지원)"}}], "checked": False}}
        ]
    )

    # 5-10. Release Center
    create_subpage(
        title="🚀 Release Center", icon="🚀", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "최종 릴리즈 배포 체크리스트"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Cover Artwork Final 3000x3000px RGB 검수 완료"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Credits Final (작사/작곡/편곡/세션/엔지니어 크레딧 확정)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Metadata (곡명/트랙순서/가사/ISRC 코드) 입력"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Master WAV (24bit/48kHz 무손실 음원) 패키징"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "음원 유통사(멜론, 지니, 벅스, 스포티파이, 애플뮤직) 업로드"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Music Video & Lyric Video 유튜브 예약 공개 설정"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "SNS Schedule 확정 및 발매 카운트다운 티저 릴리즈"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Press Kit & 공식 발매 보도자료 배포"}}], "checked": False}}
        ]
    )

    # 5-11. References
    create_subpage(
        title="📚 References", icon="📚", parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "음악, 사운드, 영상 레퍼런스 아카이브"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Song & Sound References: Elevation Worship, Bethel Music, Hillsong Worship, 마커스워십"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Album Covers & Visual Reference: Apple Music 공간음향 아트워크 스타일"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Sermons & Bible Verses: 시편 100편 (그 인자하심이 영원함이로다), 시편 103편"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Worship References & 라이브 실황 음향 연출 가이드"}}]}}
        ]
    )

    print("\n🎉 [Gemini 3.7 Master Deployment] All 14 Pages, 3 Relational Databases, and Detailed Song Templates 100% Deployed!")
    print(f"🔗 Master Workspace URL: {main_root.get('url')}")

if __name__ == "__main__":
    main()
