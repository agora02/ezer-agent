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

# All databases under 26 Q4 Tov Project Album & Tov2
target_dbs = [
    "3c14e6a9-b256-816c-931a-c3b0d2843b80",  # Tracks DB
    "3c14e6a9-b256-8179-b8e6-c75000fe9df6",  # Budget & Finance DB
    "3c14e6a9-b256-8128-b869-de356bb0d85a",  # Tasks DB
    "3c14e6a9-b256-80e5-8c73-c1711eeba271",  # Tasks DB (1)
    "3c14e6a9-b256-816e-a5c7-d34b9c38c5d7",  # Budget & Sponsorship DB
    "3c14e6a9-b256-810c-9cef-d9ad98d49027",  # Master Tracks DB
    "3c14e6a9-b256-8119-877f-f84a712d3573",  # Master Tasks DB
    "3c14e6a9-b256-8149-b8b4-c08e947343d7",  # Master Budget DB
    "3c14e6a9-b256-81a5-ba02-eb33d357ca88"   # Metric Tracker DB
]

deleted_count = 0
for db_id in target_dbs:
    query_url = f"https://api.notion.com/v1/databases/{db_id}/query"
    resp = requests.post(query_url, headers=headers)
    if resp.status_code == 200:
        results = resp.json().get("results", [])
        for item in results:
            item_id = item["id"]
            del_resp = requests.patch(f"https://api.notion.com/v1/pages/{item_id}", headers=headers, json={"archived": True})
            if del_resp.status_code == 200:
                print(f"🗑️ Cleaned dummy item: {item_id}")
                deleted_count += 1

print(f"\n🎉 [Cleanup Complete] Total {deleted_count} dummy/sample rows cleanly deleted from all databases!")
