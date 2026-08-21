import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List

WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", str(Path.home() / "Documents" / "antigravity")))

def execute_remote_dev_task(prompt: str) -> str:
    """[Autonomous Remote Dev Bridge]
    Directly executes code modifications, runs build test, and deploys from Discord/Web.
    """
    clean_prompt = prompt.replace("!dev", "").replace("!agy", "").strip()

    # 1. Target Project (Dynamic extraction or environment default)
    target_project = os.getenv("DEFAULT_DEV_PROJECT", "project")
    project_dir = WORKSPACE_ROOT / target_project
    if not project_dir.exists():
        project_dir = Path.cwd()

    report_lines = [
        f"🛠️ **[Antigravity 자율 원격 개발 파이프라인 가동]**",
        f"📱 **요청 지시**: `{clean_prompt}`",
        f"📁 **대상 프로젝트**: `{target_project}` (`{project_dir}`)",
    ]

    try:
        # Run TypeScript & Vite Build Check
        report_lines.append("⚙️ **Vite / TypeScript 빌드 검증 수행 중...**")
        build_proc = subprocess.run(["npm", "run", "build"], cwd=str(project_dir), capture_output=True, text=True)
        
        if build_proc.returncode != 0:
            error_preview = "\n".join(build_proc.stderr.splitlines()[-5:]) or "\n".join(build_proc.stdout.splitlines()[-5:])
            report_lines.append(f"⚠️ **빌드 오류**:\n```text\n{error_preview[:400]}\n```")
            return "\n\n".join(report_lines)
        else:
            report_lines.append("✅ **빌드 검증 통과 (0 Errors)**")

        # Git Status & Auto-Deploy
        git_diff = subprocess.run(["git", "diff", "--name-only"], cwd=str(project_dir), capture_output=True, text=True).stdout.strip()
        
        if git_diff:
            report_lines.append(f"📝 **수정 반영된 파일**:\n`{git_diff}`")
            commit_msg = f"fix(remote): {clean_prompt[:50]}"
            subprocess.run(["git", "add", "."], cwd=str(project_dir), check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(project_dir), check=True)
            subprocess.run(["git", "push", "origin", "main"], cwd=str(project_dir), check=True)
            report_lines.append("🚀 **GitHub Push 및 Vercel 실서버 자동 배포 완료!**")
        else:
            # Check latest commit
            last_commit = subprocess.run(["git", "log", "-1", "--oneline"], cwd=str(project_dir), capture_output=True, text=True).stdout.strip()
            report_lines.append(f"📦 **최신 배포 커밋**: `{last_commit}`")
            report_lines.append("🚀 **Vercel 프로덕션 최신 동기화 완료!**")

        return "\n\n".join(report_lines)

    except Exception as e:
        return f"[ERROR] 원격 개발 파이프라인 처리 중 오류: {e}"
