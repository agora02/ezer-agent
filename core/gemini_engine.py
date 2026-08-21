import os
import re
import json
import requests
from typing import List, Dict, Any, Tuple
from core.tool_registry import get_tools_prompt_doc, dispatch_tool_call
from core.memory_manager import MemoryManager

SYSTEM_PROMPT_TEMPLATE = """You are AE, a world-class AI personal assistant and engineering architect.
You are powered by Google Gemini intelligence and possess direct control over the user's macOS host, Notion workspaces, files, and development bridges.

### CRITICAL INSTRUCTIONS:
1. Always communicate in natural, friendly, and professional Korean (한국어).
2. For casual talk, greetings, jokes, or conceptual questions, converse naturally with high warmth and intelligence without calling tools.
3. When the user requests ANY action, real-time query, Notion creation/update, file search, file deletion, shopping price comparison, weather, or coding task:
   You MUST output a single JSON action block:
```json
{
  "tool": "tool_name",
  "args": {"param1": "value"}
}
```

### AVAILABLE TOOLS SCHEMA:
__TOOLS_DOC__

### EXAMPLES:
- "제로콜라 500ml 최저가 찾아줘" -> {"tool": "compare_product_deals", "args": {"query": "제로콜라 500ml"}}
- "오늘 회의록 노션에 정리해줘" -> {"tool": "create_notion_page", "args": {"title": "회의록", "content": "# 회의록\n..."}}
- "서울 내일 날씨 어때?" -> {"tool": "get_korea_weather", "args": {"query": "서울 내일"}}
- "바탕화면 106MSDCF 폴더에서 raw 파일 지워줘" -> {"tool": "delete_mac_file", "args": {"keyword": ".ARW", "target_dir": "106MSDCF"}}

4. After tool execution, synthesize observations into clear, beautifully formatted markdown answers.
"""

class GeminiAEAgent:
    """High-Intelligence Autonomous Agent powered by Google Gemini with Tool Calling & ReAct Loop."""

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.memory = MemoryManager()
        self.tools_doc = get_tools_prompt_doc()
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("__TOOLS_DOC__", self.tools_doc)
        print(f"🚀 [Gemini Engine] Initialized Gemini Agent with API Key ({self.api_key[:8]}...)")

    def _extract_tool_call(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extracts JSON tool call from LLM response."""
        json_matches = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_matches:
            try:
                data = json.loads(json_matches[0])
                if "tool" in data:
                    return data["tool"], data.get("args", {})
            except Exception:
                pass

        raw_matches = re.findall(r'(\{\s*"tool"\s*:\s*"[^"]+".*?\})', text, re.DOTALL)
        if raw_matches:
            try:
                data = json.loads(raw_matches[0])
                if "tool" in data:
                    return data["tool"], data.get("args", {})
            except Exception:
                pass

        return "", {}

    def _call_gemini_api(self, prompt: str) -> str:
        """Calls Gemini API with the most cost-effective and high-intelligence models."""
        models_to_try = [
            "gemini-3.6-flash",       # 최신 1위 가성비 + 초고속
            "gemini-3.7-flash",       # 초고속 최신
            "gemini-3.5-flash"        # 백업
        ]

        last_error = None
        for model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 2048
                }
            }
            try:
                resp = requests.post(url, json=payload, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        return "".join([p.get("text", "") for p in parts])
                last_error = f"{model} error ({resp.status_code}): {resp.text[:200]}"
            except Exception as e:
                last_error = str(e)

        raise RuntimeError(f"All Gemini models failed. Last: {last_error}")

    def chat(self, user_prompt: str, session_id: str = "discord_default") -> str:
        """Executes full ReAct loop with Gemini."""
        history = self.memory.get_history(session_id)
        
        # Build prompt with history and long-term memory
        memory_facts = self.memory.get_memory_context_prompt()
        history_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history[-6:]])
        current_prompt = f"{self.system_prompt}\n\n{memory_facts}\n\n### DIALOGUE HISTORY:\n{history_text}\n\nUSER: {user_prompt}\nASSISTANT:"

        try:
            # 1. First Pass
            llm_response = self._call_gemini_api(current_prompt)
            tool_name, tool_args = self._extract_tool_call(llm_response)

            if tool_name:
                print(f"⚡ [Gemini Tool Action] Triggering `{tool_name}` with args: {tool_args}")
                obs = dispatch_tool_call(tool_name, tool_args)
                print(f"🔍 [Tool Observation] {str(obs)[:150]}...")

                # 2. Observation synthesis pass
                synthesis_prompt = f"{current_prompt}\n{llm_response}\n\n[Tool Execution Observation for {tool_name}]:\n{obs}\n\nASSISTANT (Final response incorporating observation):"
                final_response = self._call_gemini_api(synthesis_prompt)
            else:
                final_response = llm_response

            self.memory.add_turn(session_id, "user", user_prompt)
            self.memory.add_turn(session_id, "assistant", final_response)
            return final_response.strip()

        except Exception as e:
            print(f"⚠️ [Gemini Engine Error] {e}")
            return f"[ERROR] Gemini 응답 처리 중 오류 발생: {e}"
