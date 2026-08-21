import re
import json
import requests
from collections import defaultdict
from bs4 import BeautifulSoup

CITY_COORDINATES = {
    "홍천": {"lat": 37.6970, "lon": 127.8887, "name": "강원도 홍천군"},
    "강원도": {"lat": 37.6970, "lon": 127.8887, "name": "강원도 홍천군"},
    "서울": {"lat": 37.5665, "lon": 126.9780, "name": "서울특별시"},
    "seoul": {"lat": 37.5665, "lon": 126.9780, "name": "서울특별시"},
    "부산": {"lat": 35.1796, "lon": 129.0756, "name": "부산광역시"},
    "인천": {"lat": 37.4563, "lon": 126.7052, "name": "인천광역시"},
    "대구": {"lat": 35.8714, "lon": 128.6014, "name": "대구광역시"},
    "대전": {"lat": 36.3504, "lon": 127.3845, "name": "대전광역시"},
    "광주": {"lat": 35.1595, "lon": 126.8526, "name": "광주광역시"},
    "제주": {"lat": 33.4996, "lon": 126.5312, "name": "제주특별자치도"},
    "수원": {"lat": 37.2636, "lon": 127.0286, "name": "수원시"},
    "성남": {"lat": 37.4200, "lon": 127.1265, "name": "성남시"},
}

SKY_CODES = {"1": "☀️ 맑음", "3": "⛅ 구름많음", "4": "☁️ 흐림"}
PTY_CODES = {"0": "없음", "1": "☔ 비", "2": "🌧️ 비/눈", "3": "❄️ 눈", "4": "🌧️ 소나기"}

def get_realtime_weather(query: str) -> str:
    """Fetches official KMA (대한민국 기상청 k-skill) forecast, filtered by exact requested dates if specified."""
    target_city = "서울"
    for city_name in CITY_COORDINATES:
        if city_name in query.lower():
            target_city = city_name
            break

    coords = CITY_COORDINATES[target_city]

    # Extract specific target day numbers from query (e.g. '16일' -> '16', '15일' -> '15')
    matched_days = re.findall(r'(\d+)\s*일', query)

    try:
        url = f"https://k-skill-proxy.nomadamas.org/v1/korea-weather/forecast?lat={coords['lat']}&lon={coords['lon']}"
        resp = requests.get(url, timeout=5).json()
        
        items = resp.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            raise ValueError("KMA Proxy Data Empty")

        daily_data = defaultdict(lambda: {"tmps": [], "sky": "맑음", "pty": "없음", "max_pop": 0, "day_num": ""})

        for item in items:
            date_str = item.get("fcstDate")
            if not date_str or len(date_str) != 8:
                continue

            day_num = str(int(date_str[6:8]))
            formatted_date = f"{int(date_str[4:6])}월 {day_num}일"
            cat = item.get("category")
            val = item.get("fcstValue")

            daily_data[formatted_date]["day_num"] = day_num

            try:
                if cat in ["TMP", "TMX", "TMN"]:
                    daily_data[formatted_date]["tmps"].append(float(val))
                elif cat == "SKY":
                    daily_data[formatted_date]["sky"] = SKY_CODES.get(str(val), "맑음")
                elif cat == "PTY" and str(val) != "0":
                    daily_data[formatted_date]["pty"] = PTY_CODES.get(str(val), "비/소나기")
                elif cat == "POP":
                    pop_val = int(val)
                    if pop_val > daily_data[formatted_date]["max_pop"]:
                        daily_data[formatted_date]["max_pop"] = pop_val
            except Exception:
                pass

        lines = [f"🌤️ **대한민국 기상청 (KMA k-skill) 예보 - {coords['name']}**:\n"]
        
        # Filter matching dates if user specified specific day numbers
        matching_entries = []
        for date_key, d_info in daily_data.items():
            if matched_days:
                if d_info["day_num"] in matched_days:
                    matching_entries.append((date_key, d_info))
            else:
                matching_entries.append((date_key, d_info))

        if not matching_entries:
            matching_entries = list(daily_data.items())[:4]

        for date_key, d_info in matching_entries[:4]:
            min_t = int(min(d_info["tmps"])) if d_info["tmps"] else "N/A"
            max_t = int(max(d_info["tmps"])) if d_info["tmps"] else "N/A"
            pty_text = f" ({d_info['pty']})" if d_info['pty'] != "없음" else ""
            
            lines.append(
                f"📅 **{date_key}**: 기온 **{min_t}°C ~ {max_t}°C** | 상태 **{d_info['sky']}{pty_text}** | 강수확률 **{d_info['max_pop']}%**"
            )

        lines.append("\n- 제공 출처: 대한민국 기상청 단기예보 (k-skill official proxy)")
        return "\n".join(lines)

    except Exception as e:
        try:
            open_url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&current_weather=true"
            r = requests.get(open_url, timeout=5).json()
            curr = r.get("current_weather", {})
            return f"🌤️ **{coords['name']} 실시간 날씨**: 기온 {curr.get('temperature')}°C, 풍속 {curr.get('windspeed')}km/h"
        except Exception:
            return f"[ERROR] 날씨 조회 실패: {e}"

def search_web_duckduckgo(query: str, max_results: int = 5) -> str:
    if any(kw in query.lower() for kw in ["날씨", "기온", "weather", "예보"]):
        return get_realtime_weather(query)

    try:
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        }
        data = {"q": query}
        resp = requests.post(url, headers=headers, data=data, timeout=8)
        soup = BeautifulSoup(resp.text, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result__body")[:max_results]:
            title_tag = result.find("a", class_="result__url")
            snippet_tag = result.find("a", class_="result__snippet")
            
            title = title_tag.get_text(strip=True) if title_tag else ""
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            
            if title and snippet:
                results.append({"title": title, "snippet": snippet})
            
        if not results:
            return f"실시간 검색 결과: '{query}' 관련 정보를 검색했습니다."
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[ERROR] 웹 검색 실패: {e}"
