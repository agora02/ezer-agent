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

TRACKS_DB_ID = "3c14e6a9-b256-816c-931a-c3b0d2843b80"
TASKS_DB_ID = "3c14e6a9-b256-8128-b869-de356bb0d85a"

def update_tracks_db_schema():
    print("🛠️ [Notion Upgrade] Updating Tracks Database schema with all PRD properties...")
    url = f"https://api.notion.com/v1/databases/{TRACKS_DB_ID}"
    
    properties_payload = {
        "Genre": {"rich_text": {}},
        "Theme": {"rich_text": {}},
        "Original Artist": {"rich_text": {}},
        "Original Song": {"rich_text": {}},
        "Original Composer": {"rich_text": {}},
        "Original Lyricist": {"rich_text": {}},
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
        "Master Version": {"rich_text": {}},
        "Demo Link": {"url": {}},
        "Logic Project Link": {"url": {}},
        "Mix Master Link": {"url": {}},
        "Related Tasks": {
            "relation": {
                "database_id": TASKS_DB_ID,
                "single_property": {}
            }
        }
    }

    resp = requests.patch(url, headers=headers, json={"properties": properties_payload})
    if resp.status_code == 200:
        print("✅ [Notion Upgrade] Tracks Database Schema fully upgraded!")
    else:
        print(f"⚠️ Schema update error: {resp.status_code} - {resp.text}")

def create_rich_track_page(track_no: int, title: str, track_type: str, status: str, bpm: int, key: str, genre: str, theme: str, composer: str, lyricist: str, arranger: str, owner: str):
    print(f"🎵 Creating rich song page: Track {track_no} - {title}...")
    url = "https://api.notion.com/v1/pages"

    children_blocks = [
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": f"Track No. {track_no:02d} | Type: {track_type} | Status: {status} | BPM: {bpm} | Key: {key}\nTheme: {theme}"}}],
                "icon": {"type": "emoji", "emoji": "🎧"}
            }
        },
        {"object": "block", "type": "divider", "divider": {}},
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📋 1. Song Overview"}}]}},
        {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": 2,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "항목"}}], [{"type": "text", "text": {"content": "내용"}}]]}},
                    {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "작곡/작사"}}], [{"type": "text", "text": {"content": f"{composer} / {lyricist}"}}]]}},
                    {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "편곡/담당"}}], [{"type": "text", "text": {"content": f"{arranger} / {owner}"}}]]}},
                    {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "BPM / Key"}}], [{"type": "text", "text": {"content": f"{bpm} BPM / {key}"}}]]}},
                    {"type": "table_row", "table_row": {"cells": [[{"type": "text", "text": {"content": "장르 / 무드"}}], [{"type": "text", "text": {"content": f"{genre} / {theme}"}}]]}}
                ]
            }
        },
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "📜 2. Lyrics (가사)"}}]}},
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": "[Verse 1]\n주의 신실하심이 아침마다 새롭고\n주의 인자하심이 영원히 머무네\n\n[Chorus]\nRemember His Faithfulness\n우릴 인도하신 주를 찬양해\n어두운 밤 지나고 새 날이 밝아오니\n주를 높이리라\n\n[Bridge]\n대대에 이를 주의 영광\n주의 선하심을 영원히 노래하리라"}}]}
        },
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎹 3. Musical Direction & Arrangement Notes"}}]}},
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "악기 구성: Acoustic Piano, Warm Pad, Ambient Electric Guitar, Bass, Drum Set"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "빌드업: 1절은 피아노+보컬로 담담하게 시작 ➔ 브릿지에서 콰이어와 드럼 빌드업"}}]}
        },
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🎙️ 4. Recording & Mix Notes"}}]}},
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "보컬 디렉팅: 과도한 기교를 배제하고 회중이 함께 부를 수 있는 진정성 있는 톤"}}]}
        },
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "믹싱 타겟: 풍부한 공간감(Ambient Reverb)과 명료한 리드 보컬 센터 배치"}}]}
        },
        {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [{"type": "text", "text": {"content": "✅ 5. Track TODOs"}}]}},
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "1차 가이드 보컬 데모 레코딩"}}], "checked": True}
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "세션 가이드 차트(코드보) 제작"}}], "checked": False}
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "메인 보컬 & 코러스 본 녹음"}}], "checked": False}
        },
        {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": [{"type": "text", "text": {"content": "1차 러프 믹스본 리뷰"}}], "checked": False}
        }
    ]

    payload = {
        "parent": {"database_id": TRACKS_DB_ID},
        "properties": {
            "Track No.": {"number": track_no},
            "Song Title": {"title": [{"type": "text", "text": {"content": title}}]},
            "Track Type": {"select": {"name": track_type}},
            "Status": {"status": {"name": status}},
            "Priority": {"select": {"name": "High" if track_no <= 2 else "Medium"}},
            "BPM": {"number": bpm},
            "Key": {"rich_text": [{"type": "text", "text": {"content": key}}]},
            "Genre": {"rich_text": [{"type": "text", "text": {"content": genre}}]},
            "Theme": {"rich_text": [{"type": "text", "text": {"content": theme}}]},
            "Composer": {"rich_text": [{"type": "text", "text": {"content": composer}}]},
            "Lyricist": {"rich_text": [{"type": "text", "text": {"content": lyricist}}]},
            "Arranger": {"rich_text": [{"type": "text", "text": {"content": arranger}}]},
            "Owner": {"rich_text": [{"type": "text", "text": {"content": owner}}]}
        },
        "children": children_blocks
    }

    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code in [200, 201]:
        print(f"✅ Track {track_no} created successfully!")
    else:
        print(f"❌ Failed to create Track {track_no}: {resp.status_code} - {resp.text}")

def main():
    update_tracks_db_schema()
    time.sleep(1)

    tracks_data = [
        (1, "01. Intro: Faithfulness", "Intro", "Complete", 68, "D Major", "Ambient Instrumental", "하나님의 임재와 시작", "양명환", "양명환", "양명환", "양명환"),
        (2, "02. Remember His Faithfulness (신실하심)", "Original", "Arrangement", 72, "E Major", "Modern Worship / CC", "하나님의 신실하심을 기억하라", "양명환", "최지원", "양명환", "최지원"),
        (3, "03. 은혜의 여정", "Original", "Demo", 76, "G Major", "Contemporary Worship", "공동체가 걸어온 은혜의 발자취", "박지원", "박지원", "양명환", "박지원"),
        (4, "04. 주를 예배하는 세대", "Original", "Writing", 128, "A Major", "Praise / Rock Worship", "다음 세대의 헌신과 찬양", "박시온", "박시온", "양명환", "박시온"),
        (5, "05. Outro: Everlasting", "Outro", "Idea", 64, "D Major", "Acoustic Reflection", "영원한 언약의 마무리", "양명환", "양명환", "양명환", "양명환")
    ]

    for t in tracks_data:
        create_rich_track_page(*t)
        time.sleep(0.5)

    print("\n🎉 [Detailed Tracks Complete] All Tracks and In-depth Song Templates fully populated!")

if __name__ == "__main__":
    main()
