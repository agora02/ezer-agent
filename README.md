# 🛡️ Ezer Agent (에제르 에이전트)

> **Autonomous Ministry & Project Management AI OS**  
> 이룸교회 사역 관리, 노션(Notion) 완전 자동화 및 실시간 프로젝트 제어를 위한 차세대 자율 AI 비서 프레임워크

---

## ✨ 주요 기능 (Key Features)

- 🧠 **Google Gemini 3.6 Flash / Pro 하이브리드 엔진**: 1초 미만의 초고속 응답과 복잡한 기획/추론 능력
- 🖥️ **Ezer Studio 웹 제어 센터 (`http://localhost:8888`)**: 세션별 대화 관리 및 실시간 시스템 대시보드
- 🤖 **24/7 디스코드 봇 게이트웨이**: 모바일 어디서나 스마트폰으로 원격 제어
- 📝 **노션(Notion) 완전 자동화**: 14개 서브페이지 생성, 데이터베이스 양방향 쿼리, Formula 수식 연동
- 💰 **사역 및 재정/후원금 관리**: 지출 및 후원금 DB 자동 적재, 기부금 영수증 상태 트래킹
- 🛠️ **13개 고성능 독립 툴킷**: 기상청 날씨, 실시간 최저가 단가 비교, macOS 파일 자동 정리

---

## 🚀 빠른 시작 (Quick Start)

### 1. 환경 설정 및 의존성 설치
```bash
./setup.sh
```

### 2. `.env` 파일에 API 키 입력
```env
GEMINI_API_KEY=your_gemini_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
NOTION_API_KEY=your_notion_api_key
NOTION_DEFAULT_PAGE_ID=your_notion_page_id
```

### 3. 서버 실행
* **Ezer Studio 웹 제어 센터**:
  ```bash
  source venv/bin/activate && python -m uvicorn gateways.web_ui:app --host 0.0.0.0 --port 8888
  ```
* **디스코드 봇 실행**:
  ```bash
  source venv/bin/activate && python scripts/auto_reloader.py
  ```

---

## 📜 License
MIT License
