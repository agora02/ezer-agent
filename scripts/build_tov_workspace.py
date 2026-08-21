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
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": blocks[:100]
    }
    if icon:
        payload["icon"] = {"type": "emoji", "emoji": icon}
    
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        data = resp.json()
        print(f"✅ Created page: {title} ({data.get('id')})")
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

def main():
    print("🚀 [Tov Workspace Builder] Constructing '26 Q4 Tov Project Album' Workspace...")

    # 1. Main Workspace Root Page
    main_root = create_subpage(
        title="📀 26 Q4 Tov Project Album",
        icon="📀",
        blocks=[
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "26 Q4 Tov Project Album 음반 제작 및 프로젝트 통합 관리 워크스페이스입니다.\nApple & Linear 스타일의 미니멀리즘과 실무 제작 운영 시스템으로 설계되었습니다."}}],
                    "icon": {"type": "emoji", "emoji": "🎯"}
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    )

    if not main_root:
        print("Failed to create root page. Aborting.")
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
        "Composer": {"rich_text": {}},
        "Lyricist": {"rich_text": {}},
        "Arranger": {"rich_text": {}},
        "Owner": {"rich_text": {}}
    }
    tracks_db = create_database(root_id, "🎵 Tracks Database", tracks_props, icon="🎵")
    time.sleep(1)

    # 3. Tasks Database (Kanban)
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

    # 5. Dashboard
    create_subpage(
        title="🏠 Dashboard",
        icon="🏠",
        parent_id=root_id,
        blocks=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📊 Project Progress"}}]}
            },
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{"type": "text", "text": {"content": "진행률: ████████░░ 75%\n현재 단계: Arrangement & Recording Preparation"}}],
                    "icon": {"type": "emoji", "emoji": "⚡"}
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🧭 Current Phase"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Concept  ➔  Songwriting  ➔  Demo  ➔  [ Arrangement & Recording ]  ➔  Mixing  ➔  Mastering  ➔  Release"}}]}
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            }
        ]
    )

    # 6. Album Direction
    create_subpage(
        title="🎯 Album Direction",
        icon="🎯",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🌟 Vision"}}]}},
            {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "하나님께서 이룸교회에 부어주신 은혜를 예배로 기록하고, 다음 세대에도 이어질 믿음의 고백으로 남긴다."}}]}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📖 Core Message"}}]}},
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "Remember His Faithfulness (하나님의 신실하심을 기억하라)"}}], "icon": {"type": "emoji", "emoji": "✨"}}},
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎯 Target Audience"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Primary: 이룸교회 성도"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Secondary: 새신자 및 등록 예정 성도"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Tertiary: 신앙을 찾고 있거나 교회 공동체를 알아가고 싶은 청년들"}}]}}
        ]
    )

    # 7. Team
    create_subpage(
        title="👥 Team",
        icon="👥",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "프로젝트 핵심 제작진"}}]}},
            {
                "object": "block",
                "type": "table",
                "table": {
                    "table_width": 3,
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": [
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "이름"}}], [{"type": "text", "text": {"content": "역할 (Role)"}}], [{"type": "text", "text": {"content": "책임 영역"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "양명환"}}], [{"type": "text", "text": {"content": "Executive Producer"}}], [{"type": "text", "text": {"content": "총괄 프로듀싱 & 음악 총괄"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "최지원"}}], [{"type": "text", "text": {"content": "Project Manager"}}], [{"type": "text", "text": {"content": "일정/예산/제작 파이프라인 관리"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "박지원"}}], [{"type": "text", "text": {"content": "Worship Leader"}}], [{"type": "text", "text": {"content": "예배 보컬 디렉팅 & 송라이팅"}}]]}},
                        {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "박시온"}}], [{"type": "text", "text": {"content": "Worship Leader"}}], [{"type": "text", "text": {"content": "예배 보컬 디렉팅 & 송라이팅"}}]]}}
                    ]
                }
            }
        ]
    )

    # 8. Production Timeline
    create_subpage(
        title="📅 Production Timeline",
        icon="📅",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "단계별 앨범 제작 로드맵"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "1단계: Concept & 송라이팅 기획"}}], "checked": True}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "2단계: 데모(Demo) 트랙 제작 및 리뷰"}}], "checked": True}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "3단계: 편곡(Arrangement) & 세션 가이드"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "4단계: 보컬 & 악기 레코딩(Recording)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "5단계: 믹싱(Mixing) & 마스터링(Mastering)"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "6단계: 아트워크 / MV / 유통사 릴리즈(Release)"}}], "checked": False}}
        ]
    )

    # 9. Visual
    create_subpage(
        title="🎬 Visual",
        icon="🎬",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎥 Music Video & Visualizer"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "뮤직비디오: 콘셉트 / 스토리보드 / 촬영 로케이션 / 출연진 / 숏리스트"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "비주얼라이저: 3D 모션 & AI 비주얼 레퍼런스 아카이브"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "SNS 숏폼/릴스: 티저 영상 릴리즈 캘린더 & 해시태그 전략"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "비하인드 필름: 메이킹 다큐멘터리 & 인터뷰 클립"}}]}}
        ]
    )

    # 10. Branding & Artwork
    create_subpage(
        title="🎨 Branding & Artwork",
        icon="🎨",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "앨범 커버 및 비주얼 아이덴티티"}}]}},
            {"object": "block", "type": "callout", "callout": {"rich_text": [{"type": "text", "text": {"content": "Linear / Apple 미니멀리즘 스타일 & 킨파쿠 골드(Kinpaku Gold) 포인트 컬러 적용"}}], "icon": {"type": "emoji", "emoji": "🎨"}}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Official Album Cover 아트워크 최종본"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "타이포그래피 및 폰트 라이선스"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "컬러 팔레트: #111217 (라커 다크) / #E8B959 (킨파쿠 골드)"}}]}}
        ]
    )

    # 11. Partnership & Sponsorship
    create_subpage(
        title="🤝 Partnership & Sponsorship",
        icon="🤝",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "동역자 및 후원 파트너십"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Prayer Partners (중보기도 동역팀 명단)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Project Sponsors (음반 제작 재정 후원사 및 성도)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "후원 목적 및 투명한 재정 감사 보고 원칙"}}]}}
        ]
    )

    # 12. Assets
    create_subpage(
        title="📂 Assets",
        icon="📂",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "음원 및 제작 에셋 아카이브"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 01_Lyrics (가사 확정본)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 02_Demo (가이드 보컬 데모)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 03_Logic_Project (로직 프로 세션 파일)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 04_Mix_Master (최종 24bit WAV 마스터 음원)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "📁 05_Artwork_Photo (프로필 및 커버 고화질 원본)"}}]}}
        ]
    )

    # 13. Meeting Notes
    create_subpage(
        title="📝 Meeting Notes",
        icon="📝",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "정기 프로덕션 회의록"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Meeting Date: 2026-08-19"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Participants: 양명환, 최지원, 박지원, 박시온"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Agenda: 26 Q4 Tov Project Album 트랙 선정 및 일정 조율"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Action Item: 1차 데모 트랙 편곡 가이드 작성 (~8/25)"}}], "checked": False}}
        ]
    )

    # 14. Release Center
    create_subpage(
        title="🚀 Release Center",
        icon="🚀",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "최종 릴리즈 점검 체크리스트"}}]}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Cover Artwork Final 3000x3000px 검수"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Metadata (작사/작곡/편곡/참여진 크레딧) 확정"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "Master WAV (24bit/48kHz 무손실 음원) 패키징"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "음원 유통사(멜론, 지니, 스포티파이, 애플뮤직) 업로드"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "유튜브 뮤직비디오 & 리릭 비디오 예약 공개"}}], "checked": False}},
            {"object": "block", "type": "to_do", "to_do": {"rich_text": [{"type": "text", "text": {"content": "교회 및 SNS 공식 발매 공지 배포"}}], "checked": False}}
        ]
    )

    # 15. References
    create_subpage(
        title="📚 References",
        icon="📚",
        parent_id=root_id,
        blocks=[
            {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "음악 및 비주얼 레퍼런스 아카이브"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Sound & Arrangement References (Elevation Worship, Bethel, Hillsong, 마커스)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Sermons & Bible Verses (시편 100편, 시편 103편 신실하심의 고백)"}}]}},
            {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Visual & Lighting Direction"}}]}}
        ]
    )

    print("\n🎉 [Tov Workspace Builder] All 14 Pages and Relational Databases successfully constructed!")
    print(f"🔗 Root Workspace URL: {main_root.get('url')}")

if __name__ == "__main__":
    main()
