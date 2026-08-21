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

TRACKS_DB_ID = "3c14e6a9-b256-810c-9cef-d9ad98d49027"
TASKS_DB_ID = "3c14e6a9-b256-8119-877f-f84a712d3573"
DASHBOARD_PAGE_ID = "3c14e6a9-b256-81ee-aaeb-d61d8e4d2ecd"

def main():
    print("🛠️ [Real-time Notion Dashboard] Upgrading Tracks with native Formula & Embedding Live Tracker...")

    # 1. Add Formula to Tracks DB
    url = f"https://api.notion.com/v1/databases/{TRACKS_DB_ID}"
    formula_payload = {
        "properties": {
            "Track Progress": {
                "formula": {
                    "expression": "if(prop(\"Status\") == \"Complete\", 100, if(prop(\"Status\") == \"Mastering\", 90, if(prop(\"Status\") == \"Mixing\", 80, if(prop(\"Status\") == \"Recording\", 60, if(prop(\"Status\") == \"Arrangement\", 40, if(prop(\"Status\") == \"Demo\", 25, if(prop(\"Status\") == \"Writing\", 15, 5)))))))"
                }
            }
        }
    }
    resp = requests.patch(url, headers=headers, json=formula_payload)
    if resp.status_code == 200:
        print("✅ Tracks DB now has native 'Track Progress' Formula!")
    else:
        print(f"⚠️ Formula error: {resp.status_code} - {resp.text}")

    # 2. Create Live Metric Tracker DB inside Dashboard Page
    tracker_url = "https://api.notion.com/v1/databases"
    tracker_payload = {
        "parent": {"page_id": DASHBOARD_PAGE_ID},
        "title": [{"type": "text", "text": {"content": "⚡ Real-time Project Health & Metric Tracker"}}],
        "properties": {
            "Metric": {"title": {}},
            "Current Phase": {
                "select": {
                    "options": [
                        {"name": "Concept", "color": "gray"},
                        {"name": "Songwriting", "color": "brown"},
                        {"name": "Demo", "color": "orange"},
                        {"name": "Arrangement & Recording", "color": "yellow"},
                        {"name": "Mixing & Mastering", "color": "purple"},
                        {"name": "Release", "color": "green"}
                    ]
                }
            },
            "Tracks Linked": {
                "relation": {
                    "database_id": TRACKS_DB_ID,
                    "single_property": {}
                }
            },
            "Album Progress": {
                "rollup": {
                    "relation_property_name": "Tracks Linked",
                    "rollup_property_name": "Track Progress",
                    "function": "percent_per_group"
                }
            },
            "Target Release Date": {"date": {}},
            "Production Notes": {"rich_text": {}}
        }
    }

    tracker_res = requests.post(tracker_url, headers=headers, json=tracker_payload)
    if tracker_res.status_code in [200, 201]:
        tracker_data = tracker_res.json()
        tracker_id = tracker_data["id"]
        print(f"✅ Real-time Tracker Database created inside Dashboard! ({tracker_id})")

        # 3. Query all Track IDs to link them into the Tracker
        tracks_query = requests.post(f"https://api.notion.com/v1/databases/{TRACKS_DB_ID}/query", headers=headers).json()
        track_ids = [{"id": item["id"]} for item in tracks_query.get("results", [])]

        # 4. Insert 1-row Live Metric Item
        row_url = "https://api.notion.com/v1/pages"
        row_payload = {
            "parent": {"database_id": tracker_id},
            "properties": {
                "Metric": {"title": [{"type": "text", "text": {"content": "📀 26 Q4 Tov Project Album"}}]},
                "Current Phase": {"select": {"name": "Arrangement & Recording"}},
                "Tracks Linked": {"relation": track_ids},
                "Target Release Date": {"date": {"start": "2026-11-20"}},
                "Production Notes": {"rich_text": [{"type": "text", "text": {"content": "5개 트랙 연동 완료. 트랙 상태 변경 시 전체 앨범 진행률 및 프로그레스 바가 실시간으로 자동 재계산됩니다."}}]}
            }
        }
        r_resp = requests.post(row_url, headers=headers, json=row_payload)
        if r_resp.status_code in [200, 201]:
            print("✅ Live Tracker Row populated and linked to all 5 tracks!")
        else:
            print(f"⚠️ Row error: {r_resp.status_code} - {r_resp.text}")

    print("\n🎉 [Real-Time Dashboard Setup Complete] Real-Time Rollup & Formula Engine is now LIVE!")

if __name__ == "__main__":
    main()
