import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

ACCOUNTING_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "accounting"
ACCOUNTING_DATA_DIR.mkdir(parents=True, exist_ok=True)
TRANSACTIONS_FILE = ACCOUNTING_DATA_DIR / "transactions.json"
INVOICES_FILE = ACCOUNTING_DATA_DIR / "invoices.json"

def _load_json(file_path: Path, default_val: Any) -> Any:
    if not file_path.exists():
        file_path.write_text(json.dumps(default_val, ensure_ascii=False, indent=2), encoding="utf-8")
        return default_val
    try:
        return json.loads(file_path.read_text(encoding="utf-8"))
    except Exception:
        return default_val

def _save_json(file_path: Path, data: Any):
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def record_transaction(date: str, description: str, amount: float, category: str, t_type: str = "expense", account: str = "default") -> str:
    """새로운 수입/지출 거래 내역을 기록합니다.
    Args:
        date: 거래 일자 (YYYY-MM-DD 또는 '오늘')
        description: 거래 내용 (예: 'AWS 서버비', '클라이언트 컨설팅비')
        amount: 금액 (원 또는 달러)
        category: 카테고리 (예: '서버/인프라', '매출', '식비', '마케팅')
        t_type: 'income'(수입/매출) 또는 'expense'(지출/비용)
        account: 계좌/카드명
    """
    if not date or date in ["오늘", "today"]:
        date = datetime.now().strftime("%Y-%m-%d")
        
    transactions = _load_json(TRANSACTIONS_FILE, [])
    new_item = {
        "id": f"tx_{int(datetime.now().timestamp() * 1000)}",
        "date": date,
        "description": description,
        "amount": float(amount),
        "category": category,
        "type": t_type.lower(),
        "account": account,
        "created_at": datetime.now().isoformat()
    }
    transactions.append(new_item)
    _save_json(TRANSACTIONS_FILE, transactions)
    
    type_kor = "수입(매출)" if t_type.lower() == "income" else "지출(비용)"
    return f"✅ **거래 기록 완료**: [{date}] {description} | {type_kor}: {amount:,.0f}원 (분류: {category})"

def generate_profit_and_loss(start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """기간별 손익계산서(P&L / Income Statement)를 자동 생성합니다.
    매출(Revenue), 매출원가/직접비용, 운영비용(OPEX), 영업이익(Net Income) 및 이익률(Margin)을 계산합니다.
    """
    transactions = _load_json(TRANSACTIONS_FILE, [])
    
    total_income = 0.0
    total_expense = 0.0
    income_by_category = {}
    expense_by_category = {}
    
    filtered_txs = []
    for tx in transactions:
        t_date = tx.get("date", "")
        if start_date and t_date < start_date:
            continue
        if end_date and t_date > end_date:
            continue
        filtered_txs.append(tx)
        
        amt = float(tx.get("amount", 0))
        cat = tx.get("category", "기타")
        t_type = tx.get("type", "expense")
        
        if t_type == "income":
            total_income += amt
            income_by_category[cat] = income_by_category.get(cat, 0.0) + amt
        else:
            total_expense += amt
            expense_by_category[cat] = expense_by_category.get(cat, 0.0) + amt

    net_income = total_income - total_expense
    margin = (net_income / total_income * 100) if total_income > 0 else 0.0
    
    period_title = f"{start_date or '전체'} ~ {end_date or '현재'}"
    
    lines = [
        f"📊 **손익계산서 (Profit & Loss Statement) — [{period_title}]**",
        "=" * 45,
        "💰 **1. 총 매출 (Total Revenue)**",
    ]
    
    if income_by_category:
        for cat, val in sorted(income_by_category.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  • {cat}: {val:,.0f}원")
    else:
        lines.append("  • 기록된 매출 내역 없음")
    lines.append(f"  ➡️ **매출 합계: {total_income:,.0f}원**\n")
    
    lines.append("📉 **2. 운영 비용 (Operating Expenses)**")
    if expense_by_category:
        for cat, val in sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True):
            pct = (val / total_expense * 100) if total_expense > 0 else 0
            lines.append(f"  • {cat}: {val:,.0f}원 ({pct:.1f}%)")
    else:
        lines.append("  • 기록된 지출 내역 없음")
    lines.append(f"  ➡️ **비용 합계: {total_expense:,.0f}원**\n")
    
    lines.append("-" * 45)
    sign = "+" if net_income >= 0 else ""
    lines.append(f"🏆 **순이익 (Net Income)**: **{sign}{net_income:,.0f}원**")
    lines.append(f"📈 **순이익률 (Net Margin)**: **{margin:.1f}%**")
    lines.append("=" * 45)
    
    return "\n".join(lines)

def calculate_burn_rate_and_runway(current_cash_balance: float) -> str:
    """현재 현금 잔고를 바탕으로 월평균 번레이트(Burn Rate)와 런웨이(Runway: 남은 생존 기간)를 산출합니다."""
    transactions = _load_json(TRANSACTIONS_FILE, [])
    if not transactions:
        return f"현재 기록된 거래 내역이 없어 런웨이 계산을 진행할 수 없습니다. (현재 잔고: {current_cash_balance:,.0f}원)"
    
    # 최근 30일/월별 지출 집계
    monthly_expenses = {}
    for tx in transactions:
        if tx.get("type") == "expense":
            month_key = tx.get("date", "")[:7] # YYYY-MM
            if month_key:
                monthly_expenses[month_key] = monthly_expenses.get(month_key, 0.0) + float(tx.get("amount", 0))
                
    if not monthly_expenses:
        return f"기록된 지출 내역이 없습니다. (현재 현금 잔고: {current_cash_balance:,.0f}원)"
        
    avg_monthly_burn = sum(monthly_expenses.values()) / len(monthly_expenses)
    
    if avg_monthly_burn <= 0:
        runway_months = "무한 (지출 없음)"
    else:
        months = current_cash_balance / avg_monthly_burn
        runway_months = f"{months:.1f}개월 ({round(months * 30.4)}일)"
        
    return f"""🔥 **런웨이 & 번레이트 분석 (Runway Calculator)**
━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 💵 현재 보유 현금 잔고: **{current_cash_balance:,.0f}원**
• 🔥 월평균 소진 금액 (Burn Rate): **{avg_monthly_burn:,.0f}원/월**
• ⏱️ **예상 생존 런웨이 (Runway)**: **{runway_months}**
• 💡 진단: {'안정적 런웨이 유지 중' if (isinstance(runway_months, str) and '무한' in runway_months) or (isinstance(months, float) and months >= 6) else '⚠️ 지출 최적화 또는 추가 자금 확보 필요'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def query_transactions(keyword: Optional[str] = None, category: Optional[str] = None, t_type: Optional[str] = None, limit: int = 15) -> str:
    """저장된 회계 거래 내역을 검색/조회합니다."""
    transactions = _load_json(TRANSACTIONS_FILE, [])
    if not transactions:
        return "기록된 회계 거래 내역이 없습니다."
        
    results = []
    for tx in reversed(transactions):
        if keyword and (keyword.lower() not in tx.get("description", "").lower()):
            continue
        if category and (category.lower() not in tx.get("category", "").lower()):
            continue
        if t_type and (tx.get("type", "").lower() != t_type.lower()):
            continue
            
        results.append(tx)
        if len(results) >= limit:
            break
            
    if not results:
        return f"검색 조건(키워드: {keyword or '전체'}, 분류: {category or '전체'})과 일치하는 거래 내역이 없습니다."
        
    lines = [f"📋 **회계 거래 내역 조회 (최근 {len(results)}건)**:"]
    for r in results:
        t_icon = "📈" if r.get("type") == "income" else "📉"
        lines.append(f"{t_icon} [{r.get('date')}] {r.get('description')} : {float(r.get('amount', 0)):,.0f}원 ({r.get('category', '미분류')})")
        
    return "\n".join(lines)
