import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List

CATEGORY_MAPPING = {
    "PDFs_and_Docs": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx", ".csv", ".hwp", ".pages"],
    "Images": [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".heic", ".psd"],
    "Archives": [".zip", ".tar", ".gz", ".7z", ".rar", ".dmg", ".pkg"],
    "Code_and_Data": [".py", ".json", ".js", ".html", ".css", ".sql", ".sh", ".yaml", ".yml", ".ts", ".tsx"],
    "Audio_and_Video": [".mp3", ".wav", ".mp4", ".mov", ".m4a", ".avi", ".mkv"]
}

def find_mac_files(keyword: str, target_dir: str = "~") -> str:
    """[Mac System Control] Searches for files matching keyword across Mac filesystem.

    Args:
        keyword: File name or search keyword (e.g. '보고서', '수련회', 'pdf').
        target_dir: Starting search directory (default: ~).
    """
    root_path = Path(os.path.expanduser(target_dir))
    if not root_path.exists():
        return f"[ERROR] 경로가 존재하지 않습니다: {target_dir}"

    found_files = []
    keyword_lower = keyword.lower()

    try:
        for path in root_path.rglob(f"*{keyword}*"):
            if any(part.startswith(".") for part in path.parts):
                continue
            if len(found_files) >= 15:
                break
            found_files.append({
                "name": path.name,
                "path": str(path),
                "size_mb": round(path.stat().st_size / (1024 * 1024), 2) if path.is_file() else "Directory"
            })

        if not found_files:
            return f"🔍 '{keyword}' 검색어와 일치하는 맥북 파일을 찾지 못했습니다."

        return json.dumps(found_files, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[ERROR] 파일 검색 중 오류: {e}"

def organize_mac_folder(folder_path: str = "~/Downloads") -> str:
    """[Mac System Control] Auto-organizes loose files in any Mac folder into subfolders.

    Args:
        folder_path: Target Mac directory (e.g. ~/Downloads, ~/Desktop).
    """
    target = Path(os.path.expanduser(folder_path))
    if not target.exists():
        return f"[ERROR] 폴더 경로가 존재하지 않습니다: {folder_path}"

    moved_count = 0
    moved_details = []

    for item in target.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue

        ext = item.suffix.lower()
        destination_cat = "Others"

        for cat_name, extensions in CATEGORY_MAPPING.items():
            if ext in extensions:
                destination_cat = cat_name
                break

        dest_dir = target / destination_cat
        dest_dir.mkdir(exist_ok=True)
        dest_file = dest_dir / item.name

        try:
            shutil.move(str(item), str(dest_file))
            moved_count += 1
            moved_details.append(f"📁 [{destination_cat}] {item.name}")
        except Exception as e:
            print(f"Failed to move {item.name}: {e}")

    if moved_count == 0:
        return f"정리할 파일이 없습니다 ({folder_path})."
    return f"✨ 총 {moved_count}개 맥북 파일 자동 정리 완료 ({folder_path}):\n" + "\n".join(moved_details[:15])

def open_mac_app(app_name: str) -> str:
    """[Mac System Control] Launches any application on Mac OS (e.g. Finder, Safari, Preview).

    Args:
        app_name: Name of application to open.
    """
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"🚀 맥북 앱 '{app_name}' 실행 완료!"
    except Exception as e:
        return f"[ERROR] 앱 실행 실패: {e}"

def delete_mac_file(keyword: str, target_dir: str = "~/Desktop") -> str:
    """[Mac System Control] Safely moves matching files/extensions to macOS Trash (~/.Trash).

    Args:
        keyword: File name, keyword, or extension (e.g. '.ARW', '박효신', '106MSDCF').
        target_dir: Starting search directory or folder name (default: ~/Desktop).
    """
    trash_path = Path(os.path.expanduser("~/.Trash"))
    trash_path.mkdir(exist_ok=True)

    base_dir = Path(os.path.expanduser(target_dir))
    
    # If target_dir is a folder name (like '106MSDCF'), check Desktop/Downloads first
    if not base_dir.exists():
        candidates = list(Path(os.path.expanduser("~/Desktop")).glob(f"*{target_dir}*"))
        if not candidates:
            candidates = list(Path(os.path.expanduser("~/Downloads")).glob(f"*{target_dir}*"))
        if candidates and candidates[0].is_dir():
            base_dir = candidates[0]
        else:
            base_dir = Path(os.path.expanduser("~/Desktop"))

    keyword_clean = keyword.lower().strip().lstrip(".")
    deleted_items = []

    # Search for matching extension or keyword
    pattern_list = [f"*.{keyword_clean}", f"*.{keyword_clean.upper()}", f"*{keyword_clean}*"]
    
    found_files = set()
    for pat in pattern_list:
        for p in base_dir.rglob(pat):
            if p.is_file() and not any(part.startswith(".") for part in p.parts):
                found_files.add(p)

    for file_p in found_files:
        try:
            dest = trash_path / file_p.name
            if dest.exists():
                dest = trash_path / f"{file_p.stem}_{int(dest.stat().st_mtime)}{file_p.suffix}"
            shutil.move(str(file_p), str(dest))
            deleted_items.append(f"🗑️ [휴지통 이동] {file_p.name} (폴더: {file_p.parent.name})")
        except Exception as e:
            print(f"Failed to move {file_p}: {e}")

    if not deleted_items:
        return f"🔍 '{base_dir}' 경로에서 '{keyword}' 관련 확장자/파일을 찾지 못했습니다."

    return f"✅ **맥북 파일 안전 삭제 완료 ({base_dir.name} 폴더 내 총 {len(deleted_items)}개 .Trash 이동)**:\n" + "\n".join(deleted_items[:15])

def read_mac_file_summary(file_path: str) -> str:
    """[Mac System Control] Reads and summarizes text content of a local Mac file."""
    path = Path(os.path.expanduser(file_path))
    if not path.exists() or not path.is_file():
        return f"[ERROR] 읽을 수 있는 파일이 아닙니다: {file_path}"

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        preview = "\n".join(lines[:25])
        return f"📄 **파일 읽기 성공 ({path.name})**:\n{preview[:1500]}"
    except Exception as e:
        return f"[ERROR] 파일 읽기 실패: {e}"

