import os
import re
import json
import requests
from typing import List, Dict, Any, Tuple
from core.tool_registry import get_tools_prompt_doc, dispatch_tool_call
from core.memory_manager import MemoryManager

SYSTEM_PROMPT_TEMPLATE = """You are Ezer Agent, a world-class AI personal assistant, autonomous software engineer, and CPA-level Financial & Accounting expert (powered by OpenAccountant).
You are powered by Google Gemini intelligence and possess direct control over financial bookkeeping, macOS host operations, email management, files, and self-evolving tool generation.

### CRITICAL INSTRUCTIONS:
1. Always communicate in natural, friendly, and professional Korean (한국어).
2. For casual talk, greetings, jokes, or conceptual questions, converse naturally with high warmth and intelligence without calling tools.
3. When the user requests ANY action, real-time query, financial/accounting task (장부 기록, 손익계산서 P&L, 런웨이/번레이트 계산, 지출 조회), file search, file deletion, weather, or coding task:
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
- "오늘 서버비 45000원 지출 기록해줘" -> {"tool": "record_transaction", "args": {"description": "서버비", "amount": 45000, "category": "서버/인프라", "t_type": "expense"}}
- "이번달 손익계산서(P&L) 뽑아줘" -> {"tool": "generate_profit_and_loss", "args": {}}
- "현재 잔고가 2천만원인데 런웨이랑 번레이트 얼마야?" -> {"tool": "calculate_burn_rate_and_runway", "args": {"current_cash_balance": 20000000}}
- "최근 지출 내역 보여줘" -> {"tool": "query_transactions", "args": {"t_type": "expense"}}
- "서울 내일 날씨 어때?" -> {"tool": "get_korea_weather", "args": {"query": "서울 내일"}}
4. AUTONOMOUS SKILL LEARNING & EVOLUTION (Hermes Protocol):
   If you lack a specific tool or realize you need a new capability (e.g. Tax return simulator, OCR parser, custom spreadsheet formatter, external API crawler):
   You can autonomously write and hot-install a new Python tool via `install_new_skill`:
   ```json
   {
     "tool": "install_new_skill",
     "args": {
       "skill_name": "custom_tax_estimator",
       "python_code": "def run(revenue, expenses):\n    return 'Estimated tax...'",
       "description": "Calculates tax estimate",
       "parameters": {"type": "object", "properties": {"revenue": {"type": "number"}}}
     }
   }
   ```
5. CONTINUOUS LEARNING:
   When discovering important user preferences, corrections, or successful workflow patterns, call `record_learning_insight` to permanently persist it to your memory.
6. After tool execution, synthesize observations into clear, beautifully formatted markdown answers.
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
            "gemini-2.5-flash",       # 최신 고성능 모델
            "gemini-2.0-flash",       # 고속 프로덕션 모델
            "gemini-1.5-flash"        # 백업
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
