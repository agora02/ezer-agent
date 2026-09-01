import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.sqlite_store import db_store

def record_transaction(date: str, description: str, amount: float, category: str, t_type: str = "expense", account: str = "주계좌") -> str:
    """새로운 수입/지출 거래 내역을 SQLite 및 장부에 기록합니다."""
    if not date or date in ["오늘", "today"]:
        date = datetime.now().strftime("%Y-%m-%d")

    tx_id = f"tx_{int(datetime.now().timestamp() * 1000)}"
    amt = float(amount)
    
    # Save to SQLite
    db_store.add_transaction(
        tx_id=tx_id,
        date=date,
        description=description,
        amount=amt,
        category=category,
        t_type=t_type,
        account=account
    )

    type_kor = "수입(매출)" if t_type.lower() == "income" else "지출(비용)"
    return f"✅ **거래 기록 완료 (SQLite 저장)**: [{date}] {description} | {type_kor}: {amt:,.0f}원 (분류: {category})"

def generate_profit_and_loss(start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """기간별 손익계산서(P&L / Income Statement)를 SQLite 데이터 기반으로 자동 생성합니다."""
    transactions = db_store.get_transactions(start_date=start_date, end_date=end_date, limit=500)

    total_income = 0.0
    total_expense = 0.0
    income_by_category = {}
    expense_by_category = {}

    for tx in transactions:
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
    """현재 현금 잔고를 바탕으로 월평균 번레이트(Burn Rate)와 런웨이(Runway)를 산출합니다."""
    transactions = db_store.get_transactions(limit=500)
    if not transactions:
        return f"현재 기록된 거래 내역이 없어 런웨이 계산을 진행할 수 없습니다. (현재 잔고: {current_cash_balance:,.0f}원)"

    monthly_expenses = {}
    for tx in transactions:
        if tx.get("type") == "expense":
            month_key = str(tx.get("date", ""))[:7]
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
    """저장된 회계 거래 내역을 SQLite에서 고속 검색합니다."""
    results = db_store.get_transactions(category=category, t_type=t_type, limit=limit)
    if keyword:
        results = [r for r in results if keyword.lower() in str(r.get("description", "")).lower()]

    if not results:
        return f"검색 조건(키워드: {keyword or '전체'}, 분류: {category or '전체'})과 일치하는 거래 내역이 없습니다."

    lines = [f"📋 **회계 거래 내역 조회 (SQLite 고속 쿼리, 최근 {len(results)}건)**:"]
    for r in results:
        t_icon = "📈" if r.get("type") == "income" else "📉"
        lines.append(f"{t_icon} [{r.get('date')}] {r.get('description')} : {float(r.get('amount', 0)):,.0f}원 ({r.get('category', '미분류')})")

    return "\n".join(lines)
