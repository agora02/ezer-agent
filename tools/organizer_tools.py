import os
import shutil
from pathlib import Path

CATEGORY_MAPPING = {
    "PDFs_and_Docs": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".hwp"],
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".heic"],
    "Archives": [".zip", ".tar", ".gz", ".7z", ".rar", ".dmg", ".pkg"],
    "Code_and_Data": [".py", ".json", ".js", ".html", ".css", ".sql", ".sh", ".yaml", ".yml"],
    "Audio_and_Video": [".mp3", ".wav", ".mp4", ".mov", ".m4a", ".avi", ".mkv"]
}

def organize_downloads_folder(target_folder: str = "~/Downloads") -> str:
    """Auto-organizes loose files in Downloads directory into clean subfolders."""
    folder_path = Path(os.path.expanduser(target_folder))
    if not folder_path.exists():
        return f"[ERROR] Directory does not exist: {target_folder}"

    moved_count = 0
    moved_details = []

    for item in folder_path.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue

        ext = item.suffix.lower()
        destination_cat = "Others"

        for cat_name, extensions in CATEGORY_MAPPING.items():
            if ext in extensions:
                destination_cat = cat_name
                break

        dest_dir = folder_path / destination_cat
        dest_dir.mkdir(exist_ok=True)
        dest_file = dest_dir / item.name

        try:
            shutil.move(str(item), str(dest_file))
            moved_count += 1
            moved_details.append(f"📁 [{destination_cat}] {item.name}")
        except Exception as e:
            print(f"Failed to move {item.name}: {e}")

    if moved_count == 0:
        return f"정리할 파일이 없습니다 ({target_folder})."
    return f"총 {moved_count}개 파일 자동 정리 완료 ({target_folder}):\n" + "\n".join(moved_details[:15])
