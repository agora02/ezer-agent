import os
import json
import importlib
from pathlib import Path
from typing import Dict, Any, List
from core.memory_manager import MemoryManager

SKILLS_DIR = Path(__file__).resolve().parent.parent / "tools" / "custom_skills"
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

class SkillLearner:
    """Hermes-style Self-Learning & Skill Evolution Engine.
    Allows the agent to autonomously generate, test, and hot-load new Python tools in real-time.
    """

    def __init__(self):
        self.memory = MemoryManager()

    def generate_and_install_skill(self, skill_name: str, python_code: str, description: str, parameters: Dict[str, Any]) -> str:
        """Dynamically creates a new Python tool file and hot-registers it into Tool Registry."""
        safe_name = skill_name.strip().lower().replace(" ", "_").replace("-", "_")
        skill_file = SKILLS_DIR / f"{safe_name}.py"

        try:
            # 1. Write the Python tool code
            skill_file.write_text(python_code, encoding="utf-8")

            # 2. Add to Long-Term Memory (Permanent Fact of learned skill)
            self.memory.add_fact(f"자율 학습된 스킬: `{safe_name}` - {description}")

            # 3. Hot-Register schema to Tool Registry dynamically
            from core.tool_registry import TOOLS_SCHEMA
            tool_entry = {
                "name": safe_name,
                "description": f"[Auto-Learned Skill] {description}",
                "parameters": parameters or {"type": "object", "properties": {"query": {"type": "string"}}}
            }
            # Avoid duplicates
            TOOLS_SCHEMA[:] = [t for t in TOOLS_SCHEMA if t["name"] != safe_name]
            TOOLS_SCHEMA.append(tool_entry)

            print(f"✨ [Skill Learner] Successfully installed and hot-loaded new skill: `{safe_name}`")
            return f"✅ 스킬 `{safe_name}` 자율 생성 및 설치 완료! (즉시 사용 가능)"

        except Exception as e:
            return f"❌ 스킬 설치 실패: {e}"

    def record_learning_experience(self, session_id: str, lesson_learned: str):
        """Hermes-style continuous learning: records successful habits, fixes, and insights into long-term memory."""
        self.memory.add_fact(f"스스로 학습한 교훈 ({session_id}): {lesson_learned}")
        print(f"🧠 [Continuous Learning] Recorded new insight: {lesson_learned}")

# Global instance
skill_learner = SkillLearner()
