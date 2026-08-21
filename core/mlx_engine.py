import re
import json
from typing import List, Dict, Any, Tuple
from mlx_lm import load, generate
from config import MLX_MAIN_MODEL, MLX_AUX_MODEL
from core.tool_registry import get_tools_prompt_doc, dispatch_tool_call
from core.memory_manager import MemoryManager

SYSTEM_PROMPT = """You are AE, a highly intelligent autonomous personal assistant powered natively on Apple MLX Metal GPU.

### INSTRUCTIONS:
1. Always respond in natural Korean (한국어).
2. For casual greetings, jokes, or general small talk ("안녕", "반가워", "뭐해", "너 누구야"), converse warmly without calling any tools.
3. For ANY factual queries, real-time lookups, calculations, pricing/shopping, weather, file operations, Mac controls, or coding tasks:
   You MUST trigger the appropriate tool by outputting a JSON action block:
```json
{
  "tool": "tool_name",
  "args": {"param1": "value"}
}
```

Examples:
- "제로콜라 500ml 얼마야?" or "닭가슴살 싼거 찾아줘" -> {"tool": "compare_product_deals", "args": {"query": "제로콜라 500ml"}}
- "홍천 16일 날씨 어때?" or "내일 비오나?" -> {"tool": "get_korea_weather", "args": {"query": "홍천 16일"}}
- "바탕화면에서 106MSDCF 폴더 .ARW 파일 지워줘" -> {"tool": "delete_mac_file", "args": {"keyword": ".ARW", "target_dir": "106MSDCF"}}
- "수련회 관련 파일 찾아줘" -> {"tool": "find_mac_files", "args": {"keyword": "수련회"}}
- "lign app 상단 헤더 수정해줘" -> {"tool": "execute_dev_task", "args": {"instruction": "lign app 상단 헤더 수정해줘"}}

4. Analyze tool execution observations to give comprehensive, clear answers.
5. NEVER output Chinese characters under any circumstances.
"""

class MLXAEAgent:
    """100% LLM-Driven Autonomous Personal Assistant with Native Tool Calling & ReAct Loop."""

    def __init__(self, main_model_path: str = MLX_MAIN_MODEL, aux_model_path: str = MLX_AUX_MODEL):
        print(f"🚀 [Apple MLX Engine] Loading Qwen Coder 14B ({main_model_path}) ...")
        self.main_model, self.main_tokenizer = load(main_model_path)
        print("✅ [Apple MLX Engine] Qwen Coder 14B loaded into Metal GPU Unified Memory!")
        
        self.memory = MemoryManager()
        self.tools_doc = get_tools_prompt_doc()

    def _extract_tool_call(self, text: str) -> Tuple[str, Dict[str, Any]]:
        """Extracts JSON tool call from LLM response."""
        # 1. Match ```json { ... } ```
        json_matches = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_matches:
            try:
                data = json.loads(json_matches[0])
                if "tool" in data:
                    return data["tool"], data.get("args", {})
            except Exception:
                pass

        # 2. Match raw JSON object with "tool"
        raw_matches = re.findall(r'(\{\s*"tool"\s*:\s*"[^"]+".*?\})', text, re.DOTALL)
        if raw_matches:
            try:
                data = json.loads(raw_matches[0])
                if "tool" in data:
                    return data["tool"], data.get("args", {})
            except Exception:
                pass

        return None, {}

    def chat(self, prompt: str, session_id: str = "default") -> str:
        """Processes any user prompt purely through LLM Natural Language Understanding & ReAct Tool Loop."""
        print(f"[Apple MLX ReAct Agent] 🧠 Processing natural language prompt: '{prompt}'")

        system_instruction = f"""{SYSTEM_PROMPT}

{self.memory.get_memory_context_prompt()}

### Available Tools:
{self.tools_doc}
"""
        # Multi-turn conversation context
        history = self.memory.get_history(session_id)
        messages = [{"role": "system", "content": system_instruction}]
        for turn in history[-6:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": prompt})

        # ReAct Autonomous Execution Loop (Max 5 turns)
        max_loops = 5
        final_answer = ""

        for loop_idx in range(max_loops):
            if hasattr(self.main_tokenizer, "apply_chat_template"):
                formatted_prompt = self.main_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                formatted_prompt = f"<|im_start|>system\n{system_instruction}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"

            response = generate(
                self.main_model,
                self.main_tokenizer,
                prompt=formatted_prompt,
                max_tokens=512,
                verbose=False
            ).strip()

            tool_name, tool_args = self._extract_tool_call(response)

            # If no tool requested by LLM, response is the final conversational answer
            if not tool_name:
                final_answer = response
                break

            # Execute tool requested by LLM
            print(f"🔧 [LLM Autonomous Action - Turn {loop_idx + 1}] Invoking tool: '{tool_name}' with args: {tool_args}")
            observation = dispatch_tool_call(tool_name, tool_args)
            print(f"👁️ [Observation - Turn {loop_idx + 1}] Received {len(observation)} bytes from tool.")

            # Feed observation back to LLM for final analysis / next action
            messages.append({"role": "assistant", "content": response})
            messages.append({
                "role": "user",
                "content": f"Tool Execution Observation:\n{observation}\n\nBased on the above observation, provide the final user answer in Korean or call another tool if needed."
            })

        if not final_answer:
            final_answer = response or "작업 처리가 완료되었습니다."

        # Save to session memory
        self.memory.add_turn(session_id, "user", prompt)
        self.memory.add_turn(session_id, "assistant", final_answer)

        return final_answer
