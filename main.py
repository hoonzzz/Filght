import os
import requests
import json

# 환경 변수에서 정보 가져오기 (GitHub Secrets 설정 예정)
AMADEUS_KEY = os.environ['AMADEUS_KEY']
AMADEUS_SECRET = os.environ['AMADEUS_SECRET']
SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL']

TARGET_PRICE_KRW = 3000000  # 성인 2명 합계 목표 금액 (예시)

def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": "6oRB72lKYI6pmICcdYxFgaa6cvVpewRG",
        "client_secret": "tzrrGCjQMMkGyowa"
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']

def check_emirates_flights():
    token = get_amadeus_token()
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    
    # 다구간(Multi-city) 조회를 위한 파라미터 구성
    # 실제 구현 시에는 API 문서에 따라 상세 JSON 바디를 구성해야 합니다.
    params = {
        "originLocationCode": "ICN",
        "destinationLocationCode": "DXB",
        "departureDate": "2026-11-15",
        "adults": 2,
        "includedAirlineCodes": "EK", # 에미레이트 항공만 필터링
        "currencyCode": "KRW"
    }
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if not data['data']:
            print("조건에 맞는 항공권이 없습니다.")
            return

        # 최저가 추출 (단순 예시 로직)
        cheapest_offer = data['data'][0]
        total_price = float(cheapest_offer['price']['total'])
        
        if total_price <= TARGET_PRICE_KRW:
            send_slack_alert(total_price)
    else:
        print("API 호출 실패:", response.text)

def send_slack_alert(price):
    msg = {
        "text": f"✈️ **에미레이트 특가 알림!**\n합계 금액: {price:,.0f}원\n지금 확인하세요!"
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(msg))

if __name__ == "__main__":
    check_emirates_flights()
