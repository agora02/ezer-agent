import os
import json
import imaplib
import email
from email.header import decode_header
from typing import Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

PROTECTED_KEYWORDS = [
    "영수증", "receipt", "invoice", "결제", "승인", "로그인", "보안", "code",
    "riot", "notion", "유니클로", "uniqlo", "비밀번호", "인증", "티켓", "예매", "항공권"
]

SPAM_KEYWORDS = [
    "(광고)", "[광고]", "discount", "sale", "newsletter", "deals", "promotions",
    "특가", "무료", "쿠폰", "혜택", "이벤트", "마케팅"
]

def get_imap_connection():
    server = os.getenv("IMAP_SERVER", "imap.gmail.com").strip()
    user = os.getenv("EMAIL_USER", "").strip()
    password = os.getenv("EMAIL_PASS", "").strip()
    port = int(os.getenv("IMAP_PORT", "993"))

    if not user or not password:
        raise ValueError("EMAIL_USER and EMAIL_PASS must be configured in mlx_agent/.env")

    mail = imaplib.IMAP4_SSL(server, port)
    mail.login(user, password)
    return mail

def decode_mime_header(header_value: str) -> str:
    if not header_value:
        return ""
    parts = decode_header(header_value)
    decoded_str = ""
    for part, enc in parts:
        if isinstance(part, bytes):
            decoded_str += part.decode(enc or "utf-8", errors="ignore")
        else:
            decoded_str += str(part)
    return decoded_str

def fetch_recent_emails(max_count: int = 10, tab: str = "primary") -> str:
    """Fetches recent emails specifically from Gmail Tabs."""
    try:
        mail = get_imap_connection()
        mail.select("inbox")

        tab_str = tab.lower()
        if "기본" in tab_str or "primary" in tab_str:
            search_query = 'X-GM-RAW "category:primary"'
        elif "프로모션" in tab_str or "promo" in tab_str:
            search_query = 'X-GM-RAW "category:promotions"'
        else:
            search_query = 'ALL'

        status, messages = mail.search(None, search_query)
        if status != "OK" or not messages[0]:
            status, messages = mail.search(None, 'ALL')

        if status != "OK" or not messages[0]:
            mail.logout()
            return f"'{tab}' 탭에 메일이 없습니다."

        email_ids = messages[0].split()
        
        fetched_emails = []
        for e_id in reversed(email_ids):
            if len(fetched_emails) >= max_count:
                break

            res, msg_data = mail.fetch(e_id, "(RFC822.HEADER)")
            if res != "OK" or not msg_data or not msg_data[0]:
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subj_str = decode_mime_header(msg.get("Subject", "제목 없음"))
                    from_str = decode_mime_header(msg.get("From", "알 수 없음"))

                    subj_lower = subj_str.lower()
                    from_lower = from_str.lower()
                    
                    is_protected = any(kw in subj_lower or kw in from_lower for kw in PROTECTED_KEYWORDS)
                    is_spam = any(kw in subj_lower or kw in from_lower for kw in SPAM_KEYWORDS)
                    
                    category = "PROTECTED (보안/영수증)" if is_protected else "SPAM (광고/프로모션)" if is_spam else "GENERAL"

                    fetched_emails.append({
                        "id": e_id.decode("utf-8"),
                        "sender": from_str,
                        "subject": subj_str,
                        "category": category,
                        "date": msg.get("Date", "N/A")
                    })

        mail.logout()
        return json.dumps(fetched_emails, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"[ERROR] IMAP 탭 조회 실패: {e}"

def delete_spam_only_emails(tab: str = "primary") -> str:
    """[STRICT SAFE DELETION] Scans inbox and ONLY deletes confirmed SPAM/ADVERTISEMENT emails while PROTECTING receipts, logins, and invoices."""
    try:
        mail = get_imap_connection()
        mail.select("inbox")

        status, messages = mail.search(None, 'X-GM-RAW "category:primary"')
        if status != "OK" or not messages[0]:
            status, messages = mail.search(None, 'ALL')

        if status != "OK" or not messages[0]:
            mail.logout()
            return "삭제할 메일이 없습니다."

        email_ids = messages[0].split()
        latest_ids = email_ids[-20:]
        
        deleted_details = []
        skipped_protected = []

        for e_id in latest_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822.HEADER)")
            if res != "OK":
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subj_str = decode_mime_header(msg.get("Subject", ""))
                    from_str = decode_mime_header(msg.get("From", ""))
                    
                    subj_lower = subj_str.lower()
                    from_lower = from_str.lower()

                    if any(kw in subj_lower or kw in from_lower for kw in PROTECTED_KEYWORDS):
                        skipped_protected.append(f"🛡️ [보호됨] {subj_str} (보안/영수증)")
                        continue

                    if any(kw in subj_lower or kw in from_lower for kw in SPAM_KEYWORDS):
                        mail.store(e_id, "+FLAGS", "\\Deleted")
                        deleted_details.append(f"🗑️ [삭제완료] {subj_str} (발신: {from_str})")

        mail.expunge()
        mail.logout()

        report = []
        if deleted_details:
            report.append("✅ **[Apple MLX 안전 스팸 삭제 결과]**\n" + "\n".join(deleted_details))
        else:
            report.append("ℹ️ 삭제 조건에 맞는 광고/스팸 메일이 없습니다.")
            
        if skipped_protected:
            report.append("\n🛡️ **[보호된 중요한 메일 목록 - 삭제 안함]**\n" + "\n".join(skipped_protected[:5]))

        return "\n\n".join(report)

    except Exception as e:
        return f"[ERROR] 안전 스팸 삭제 실패: {e}"
