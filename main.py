import time
import requests
from bs4 import BeautifulSoup

# Telegram 설정
TELEGRAM_TOKEN = "8158643755:AAFM5mUDGlc6DRlwQe4Dloebi4fd6qCPTHg"
TELEGRAM_CHAT_ID = "7438061345"

# 추적할 코인 심볼
symbols = {
    "BTC": "비트코인",
    "ETH": "이더리움",
    "XRP": "리플",
    "DOGE": "도지코인",
    "PEPE": "페페",
    "SUI": "수이",
    "SHIB": "시바이누"
}

# 환율 조회
def get_usd_krw_rate():
    url = "https://finance.naver.com/marketindex/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    rate_text = soup.select_one("div.head_info > span.value").text
    return float(rate_text.replace(",", ""))

# 업비트 가격 조회
def get_upbit_price(symbol):
    url = f"https://api.upbit.com/v1/ticker?markets=KRW-{symbol}"
    res = requests.get(url)
    if res.status_code == 200 and res.json():
        return res.json()[0]['trade_price']
    return None

# 바이낸스 가격 조회
def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    res = requests.get(url)
    if res.status_code == 200 and res.json():
        return float(res.json()['price'])
    return None

# 김치 프리미엄 계산
def calculate_kimchi_premium(upbit_price, binance_price, usd_krw):
    try:
        global_price_krw = binance_price * usd_krw
        premium = ((upbit_price - global_price_krw) / global_price_krw) * 100
        return premium
    except:
        return None

# 텔레그램 메시지 전송
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# 메인 함수
def main():
    usd_krw = get_usd_krw_rate()
    message = f"[김치 프리미엄 추적 📊]\n(USD/KRW: {usd_krw:.2f})\n\n"
    alert_triggered = False

    for symbol, name in symbols.items():
        try:
            upbit = get_upbit_price(symbol)
            binance = get_binance_price(symbol)
            if upbit and binance:
                premium = calculate_kimchi_premium(upbit, binance, usd_krw)
                message += f"{name} ({symbol}): {premium:.2f}%\n"
                if premium >= 3.2:
                    alert_triggered = True
        except Exception as e:
            message += f"{name} ({symbol}): 데이터 오류 발생\n"

    if alert_triggered:
        send_telegram_message(message)

# 루프: 30초마다 실행
if __name__ == "__main__":
    while True:
        print("[Loop] 김치 프리미엄 확인 중...")
        main()
        print("[Loop] 30초 후 다시 확인합니다...\n")
        time.sleep(30)
