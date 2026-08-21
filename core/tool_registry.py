import json
from typing import Dict, Any, List, Callable
from tools.browser_tools import get_realtime_weather, search_web_duckduckgo
from tools.mac_control_tools import find_mac_files, organize_mac_folder, open_mac_app, read_mac_file_summary, delete_mac_file
from tools.email_tools import fetch_recent_emails, delete_spam_only_emails
from tools.system_tools import get_system_status
from tools.dev_bridge_tools import execute_remote_dev_task
from tools.shopping_tools import compare_product_deals
from tools.notion_tools import create_notion_page, append_to_notion_page

TOOLS_SCHEMA = [
    {
        "name": "get_korea_weather",
        "description": "대한민국 기상청(KMA) 공식 실시간 및 날짜별(오늘, 내일, 특정 날짜) 날씨 예보를 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "지역명 및 날짜 (예: '홍천 16일 날씨', '서울 오늘 날씨', '제주 주말 날씨')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "find_mac_files",
        "description": "맥북 컴퓨터 파일시스템에서 특정 키워드나 확장자(PDF, 이미지, 코드 등)를 가진 파일을 검색합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "검색할 파일 이름, 키워드 또는 확장자 (예: '수련회', '보고서', 'pdf')"
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
        "description": "맥북의 특정 폴더에서 파일 또는 특정 확장자(.ARW, .mp4 등)를 안전하게 맥북 휴지통(~/.Trash)으로 이동시킵니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "삭제할 파일 이름, 키워드 또는 확장자 (예: '.ARW', '박효신', 'test.txt')"
                },
                "target_dir": {
                    "type": "string",
                    "description": "대상 폴더 경로 또는 폴더명 (예: '~/Desktop', '106MSDCF', '~/Downloads')",
                    "default": "~/Desktop"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "organize_mac_folder",
        "description": "맥북의 바탕화면(Desktop) 또는 다운로드(Downloads) 폴더 내 흩어진 파일들을 카테고리별 하위 폴더로 자동 정리합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {
                    "type": "string",
                    "description": "정리할 맥북 폴더 경로 (예: '~/Desktop', '~/Downloads')",
                    "default": "~/Downloads"
                }
            }
        }
    },
    {
        "name": "read_mac_file",
        "description": "맥북 로컬 파일(텍스트, 소스코드, 마크다운 등)의 내용을 읽고 요약합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "읽을 맥북 파일 경로 (예: '~/Desktop/notes.txt', '/Users/jeewonchoi/Documents/...')"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "open_mac_app",
        "description": "맥북의 애플리케이션(Finder, Safari, Chrome, 미리보기 등)을 실행합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "실행할 앱 이름 (예: 'Finder', 'Safari', 'Preview')"
                }
            },
            "required": ["app_name"]
        }
    },
    {
        "name": "search_web",
        "description": "실시간 최신 인터넷 정보, 뉴스, 환율, 지식 검색을 수행합니다.",
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
        "name": "manage_emails",
        "description": "사용자의 지메일(Gmail) 받은편지함을 조회하거나 스팸 광고 메일을 안전하게 정리합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["fetch", "delete_spam"],
                    "description": "'fetch'(이메일 목록 조회) 또는 'delete_spam'(스팸 광고만 안전 삭제)"
                },
                "tab": {
                    "type": "string",
                    "enum": ["primary", "promotions"],
                    "description": "대상 탭 ('primary' 또는 'promotions')",
                    "default": "primary"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "execute_dev_task",
        "description": "프로젝트의 소스코드를 원격으로 수정, 빌드 검증 및 Vercel/GitHub에 자동 배포합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "instruction": {
                    "type": "string",
                    "description": "개발 또는 코드 수정 지시사항 (예: '상단 헤더 AI 바 이름을 이룸 AI로 변경해줘')"
                }
            },
            "required": ["instruction"]
        }
    },
    {
        "name": "compare_product_deals",
        "description": "생필품/식품/전자기기(닭가슴살, 보충제, 음료, 생수 등)의 실시간 가격, 총 중량, 100g/개당 단가(가성비)를 비교 분석하고 추천 순위표를 제공합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "비교할 상품명 (예: '냉동 닭가슴살', '제로콜라 355ml', '단백질 보충제')"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_notion_page",
        "description": "사용자의 노션(Notion) 워크스페이스에 제목과 마크다운 본문(헤더, 글머리기호, 콜아웃 등)을 가진 새로운 노션 페이지를 자동 생성합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "노션 페이지 제목"
                },
                "content": {
                    "type": "string",
                    "description": "정리된 마크다운 본문 내용 (요약, 회의록, 자료 정리 등)"
                },
                "parent_page_id": {
                    "type": "string",
                    "description": "노션 부모 페이지 ID (선택사항, 생략 시 기본 페이지에 생성)",
                    "default": ""
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "append_to_notion_page",
        "description": "기존에 존재하는 특정 노션(Notion) 페이지에 새로운 내용을 추가(업데이트)합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "page_id": {
                    "type": "string",
                    "description": "대상 노션 페이지 ID"
                },
                "content": {
                    "type": "string",
                    "description": "추가할 마크다운 본문 내용"
                }
            },
            "required": ["page_id", "content"]
        }
    },
    {
        "name": "get_system_status",
        "description": "맥북 호스트의 실시간 CPU, 메모리(RAM), 디스크 여유 공간 및 GPU 상태를 확인합니다.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Dispatches and executes the requested tool call, returning the observation string."""
    try:
        if tool_name == "get_korea_weather":
            query = arguments.get("query", "서울")
            return get_realtime_weather(query)

        elif tool_name == "find_mac_files":
            kw = arguments.get("keyword", "")
            target_dir = arguments.get("target_dir", "~")
            return find_mac_files(keyword=kw, target_dir=target_dir)

        elif tool_name == "delete_mac_file":
            kw = arguments.get("keyword", "")
            target_dir = arguments.get("target_dir", "~/Desktop")
            return delete_mac_file(keyword=kw, target_dir=target_dir)

        elif tool_name == "organize_mac_folder":
            folder = arguments.get("folder_path", "~/Downloads")
            return organize_mac_folder(folder_path=folder)

        elif tool_name == "read_mac_file":
            path = arguments.get("file_path", "")
            return read_mac_file_summary(file_path=path)

        elif tool_name == "open_mac_app":
            app = arguments.get("app_name", "Finder")
            return open_mac_app(app_name=app)

        elif tool_name == "search_web":
            query = arguments.get("query", "")
            return search_web_duckduckgo(query=query)

        elif tool_name == "manage_emails":
            action = arguments.get("action", "fetch")
            tab = arguments.get("tab", "primary")
            if action == "delete_spam":
                return delete_spam_only_emails(tab=tab)
            else:
                return fetch_recent_emails(max_count=10, tab=tab)

        elif tool_name == "execute_dev_task":
            instruction = arguments.get("instruction", "")
            return execute_remote_dev_task(prompt=instruction)

        elif tool_name == "compare_product_deals":
            query = arguments.get("query", "냉동 닭가슴살")
            return compare_product_deals(query=query)

        elif tool_name == "create_notion_page":
            title = arguments.get("title", "자료 정리")
            content = arguments.get("content", "")
            parent_id = arguments.get("parent_page_id", "")
            return create_notion_page(title=title, content=content, parent_page_id=parent_id)

        elif tool_name == "append_to_notion_page":
            page_id = arguments.get("page_id", "")
            content = arguments.get("content", "")
            return append_to_notion_page(page_id=page_id, content=content)

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
            return f"✅ 자율 학습된 지식/교훈이 장기 기억에 영구 반영되었습니다: {insight}"

        else:
            # Check dynamic custom skills directory
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
                return f"✅ 스킬 `{tool_name}` 실행 완료"

            return f"[ERROR] 알 수 없는 도구 이름입니다: '{tool_name}'"

    except Exception as e:
        return f"[ERROR] 도구 '{tool_name}' 실행 중 오류 발생: {e}"

def get_tools_prompt_doc() -> str:
    """Returns the formatted JSON tool schema documentation to inject into LLM system prompt."""
    return json.dumps(TOOLS_SCHEMA, ensure_ascii=False, indent=2)
