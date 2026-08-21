import json
import os
from pathlib import Path
from typing import Dict, Any, List, Callable

# ============================================================
# ALL tool imports are LAZY (inside dispatch function) to avoid
# crashing on Linux/Docker where macOS commands don't exist.
# ============================================================

# Core Built-in Capabilities (Always built into Ezer Agent by default)
DEFAULT_CORE_TOOLS = [
    {
        "name": "search_web",
        "description": "실시간 최신 인터넷 정보, 뉴스, 검색, 연구 조사를 수행합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색 쿼리"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_korea_weather",
        "description": "대한민국 기상청(KMA) 공식 실시간 및 날짜별(오늘, 내일, 특정 날짜) 날씨 예보를 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "지역명 및 날짜 (예: '서울 오늘 날씨', '제주 주말 날씨')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "find_mac_files",
        "description": "컴퓨터 파일시스템에서 특정 키워드나 확장자(PDF, 이미지, 문서 등)를 가진 파일을 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "검색할 파일 이름, 키워드 또는 확장자"
                },
                "target_dir": {
                    "type": "string",
                    "description": "시작 검색 디렉토리 (기본값: ~)",
                    "default": "~"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "delete_mac_file",
        "description": "특정 폴더에서 파일 또는 특정 확장자를 안전하게 휴지통(~/.Trash)으로 이동시킵니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "삭제할 파일 이름 또는 확장자"
                },
                "target_dir": {
                    "type": "string",
                    "description": "대상 폴더 경로",
                    "default": "~/Desktop"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "organize_mac_folder",
        "description": "바탕화면(Desktop) 또는 다운로드(Downloads) 폴더 내 흩어진 파일들을 카테고리별로 자동 정리합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "정리할 폴더 경로",
                    "default": "~/Downloads"
                }
            }
        }
    },
    {
        "name": "read_mac_file",
        "description": "로컬 텍스트, 문서, 코드 파일의 내용을 직접 읽고 분석합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "읽을 파일 경로"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "open_mac_app",
        "description": "컴퓨터의 애플리케이션(Finder, Safari, Chrome 등)을 실행합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "실행할 앱 이름"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "manage_emails",
        "description": "이메일(Gmail) 받은편지함을 조회하거나 스팸 광고 메일을 안전하게 정리합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["fetch", "delete_spam"],
                    "description": "'fetch'(이메일 목록 조회) 또는 'delete_spam'(스팸 광고만 삭제)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "get_system_status",
        "description": "호스트의 실시간 CPU, 메모리(RAM), 디스크 여유 공간 및 GPU 상태를 확인합니다.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    # OpenAccountant Financial & Accounting Core Tools
    {
        "name": "record_transaction",
        "description": "[회계] 수입(매출) 또는 지출(비용) 내역을 장부에 새로 기록합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "거래 일자 (YYYY-MM-DD 또는 '오늘')"},
                "description": {"type": "string", "description": "거래 내용 (예: 'AWS 서버비', '외주 용역비')"},
                "amount": {"type": "number", "description": "금액 (숫자)"},
                "category": {"type": "string", "description": "카테고리 (예: '서버비', '인건비', '식대', '매출')"},
                "t_type": {"type": "string", "enum": ["income", "expense"], "description": "'income'(수입/매출) 또는 'expense'(지출/비용)"},
                "account": {"type": "string", "description": "계좌/카드명 (기본값: '주계좌')", "default": "주계좌"}
            },
            "required": ["description", "amount", "category", "t_type"]
        }
    },
    {
        "name": "generate_profit_and_loss",
        "description": "[회계] 지정된 기간의 손익계산서(P&L / Income Statement), 총매출, 총비용, 순이익 및 마진율을 산출합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "시작 일자 (YYYY-MM-DD, 옵션)"},
                "end_date": {"type": "string", "description": "종료 일자 (YYYY-MM-DD, 옵션)"}
            }
        }
    },
    {
        "name": "calculate_burn_rate_and_runway",
        "description": "[회계] 현재 현금 잔고를 바탕으로 월평균 소진액(Burn Rate)과 남은 생존 기간(Runway)을 계산합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "current_cash_balance": {"type": "number", "description": "현재 보유한 총 현금/통장 잔고"}
            },
            "required": ["current_cash_balance"]
        }
    },
    {
        "name": "query_transactions",
        "description": "[회계] 기록된 수입/지출 내역을 검색하고 최근 거래 목록을 확인합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "검색할 거래 키워드"},
                "category": {"type": "string", "description": "특정 카테고리 필터"},
                "t_type": {"type": "string", "enum": ["income", "expense"], "description": "'income' 또는 'expense'"}
            }
        }
    }
]

TOOLS_SCHEMA = list(DEFAULT_CORE_TOOLS)

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Dispatches and executes the requested built-in capability.
    All imports are lazy to ensure Cloud Run (Linux) doesn't crash on macOS-only modules.
    """
    try:
        if tool_name == "get_korea_weather":
            from tools.browser_tools import get_realtime_weather
            query = arguments.get("query", "서울")
            return get_realtime_weather(query)

        elif tool_name == "find_mac_files":
            from tools.mac_control_tools import find_mac_files
            kw = arguments.get("keyword", "")
            target_dir = arguments.get("target_dir", "~")
            return find_mac_files(keyword=kw, target_dir=target_dir)

        elif tool_name == "delete_mac_file":
            from tools.mac_control_tools import delete_mac_file
            kw = arguments.get("keyword", "")
            target_dir = arguments.get("target_dir", "~/Desktop")
            return delete_mac_file(keyword=kw, target_dir=target_dir)

        elif tool_name == "organize_mac_folder":
            from tools.mac_control_tools import organize_mac_folder
            folder = arguments.get("folder_path", "~/Downloads")
            return organize_mac_folder(folder_path=folder)

        elif tool_name == "read_mac_file":
            from tools.mac_control_tools import read_mac_file_summary
            path = arguments.get("file_path", "")
            return read_mac_file_summary(file_path=path)

        elif tool_name == "open_mac_app":
            from tools.mac_control_tools import open_mac_app
            app = arguments.get("app_name", "Finder")
            return open_mac_app(app_name=app)

        elif tool_name == "search_web":
            from tools.browser_tools import search_web_duckduckgo
            query = arguments.get("query", "")
            return search_web_duckduckgo(query=query)

        elif tool_name == "manage_emails":
            from tools.email_tools import fetch_recent_emails, delete_spam_only_emails
            action = arguments.get("action", "fetch")
            tab = arguments.get("tab", "primary")
            if action == "delete_spam":
                return delete_spam_only_emails(tab=tab)
            else:
                return fetch_recent_emails(max_count=10, tab=tab)

        elif tool_name == "get_system_status":
            from tools.system_tools import get_system_status
            return get_system_status()

        # OpenAccountant Tool Handlers
        elif tool_name == "record_transaction":
            from tools.accounting_tools import record_transaction
            return record_transaction(
                date=arguments.get("date", "오늘"),
                description=arguments.get("description", ""),
                amount=float(arguments.get("amount", 0)),
                category=arguments.get("category", "기타"),
                t_type=arguments.get("t_type", "expense"),
                account=arguments.get("account", "주계좌")
            )

        elif tool_name == "generate_profit_and_loss":
            from tools.accounting_tools import generate_profit_and_loss
            return generate_profit_and_loss(
                start_date=arguments.get("start_date"),
                end_date=arguments.get("end_date")
            )

        elif tool_name == "calculate_burn_rate_and_runway":
            from tools.accounting_tools import calculate_burn_rate_and_runway
            return calculate_burn_rate_and_runway(
                current_cash_balance=float(arguments.get("current_cash_balance", 0))
            )

        elif tool_name == "query_transactions":
            from tools.accounting_tools import query_transactions
            return query_transactions(
                keyword=arguments.get("keyword"),
                category=arguments.get("category"),
                t_type=arguments.get("t_type")
            )

        elif tool_name == "install_new_skill":
            from core.skill_learner import skill_learner
            s_name = arguments.get("skill_name", "")
            s_code = arguments.get("python_code", "")
            s_desc = arguments.get("description", "")
            s_params = arguments.get("parameters", {})
            return skill_learner.generate_and_install_skill(s_name, s_code, s_desc, s_params)

        elif tool_name == "record_learning_insight":
            from core.skill_learner import skill_learner
            insight = arguments.get("insight", "")
            session_id = arguments.get("session_id", "default")
            skill_learner.record_learning_experience(session_id, insight)
            return f"✅ 지식/교훈이 장기 기억에 영구 반영되었습니다: {insight}"

        else:
            custom_skill_file = Path(__file__).resolve().parent.parent / "tools" / "custom_skills" / f"{tool_name}.py"
            if custom_skill_file.exists():
                import importlib.util
                spec = importlib.util.spec_from_file_location(tool_name, str(custom_skill_file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "run"):
                    return module.run(**arguments)
                elif hasattr(module, "main"):
                    return module.main(**arguments)
                return f"✅ 기능 `{tool_name}` 실행 완료"

            return f"[ERROR] 알 수 없는 기능입니다: '{tool_name}'"

    except Exception as e:
        return f"[ERROR] 기능 '{tool_name}' 실행 중 오류 발생: {e}"

def get_tools_prompt_doc() -> str:
    """Returns the formatted JSON tool schema documentation to inject into LLM system prompt."""
    return json.dumps(TOOLS_SCHEMA, ensure_ascii=False, indent=2)
