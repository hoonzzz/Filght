import os
import requests
import json

# 1. 환경 변수 가져오기 (이름 오타 방지를 위해 통일)
AMADEUS_KEY = os.environ.get('6oRB72lKYI6pmICcdYxFgaa6cvVpewRG')
AMADEUS_SECRET = os.environ.get('tzrrGCjQMMkGyowa')
SLACK_URL = os.environ.get('https://hooks.slack.com/services/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')

# 2. 목표 금액 설정 (테스트를 위해 일단 높게 설정 - 알림 오는지 확인용)
TARGET_PRICE = 3000000  # 1,000만원 이하일 때 무조건 알림

def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {"grant_type": "client_credentials", "client_id": AMADEUS_KEY, "client_secret": AMADEUS_SECRET}
    response = requests.post(url, data=data)
    return response.json().get('access_token')

def check_emirates():
    token = get_token()
    if not token:
        print("❌ Amadeus 토큰 발급 실패. API 키를 확인하세요.")
        return

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 다구간 조회 본문 (인천-두바이-몰디브-인천)
    payload = {
        "currencyCode": "KRW",
        "originDestinations": [
            {"id": "1", "originLocationCode": "ICN", "destinationLocationCode": "DXB", "departureDateTimeRange": {"date": "2026-11-15"}},
            {"id": "2", "originLocationCode": "DXB", "destinationLocationCode": "MLE", "departureDateTimeRange": {"date": "2026-11-18"}},
            {"id": "3", "originLocationCode": "MLE", "destinationLocationCode": "ICN", "departureDateTimeRange": {"date": "2026-11-22"}}
        ],
        "travelers": [{"id": "1", "travelerType": "ADULT"}, {"id": "2", "travelerType": "ADULT"}],
        "sources": ["GDS"],
        "searchCriteria": {"flightFilters": {"airlineRestrictions": {"includedAirlineCodes": ["EK"]}}}
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 200:
        data = res.json().get('data', [])
        if data:
            price = float(data[0]['price']['total'])
            print(f"✈️ 현재 에미레이트 최저가: {price:,.0f}원")
            
            if price <= TARGET_PRICE:
                msg = f"🔔 **에미레이트 알림!**\n총액: {price:,.0f}원\n스케줄: 11/15 ICN-DXB | 11/18 DXB-MLE | 11/22 MLE-ICN"
                requests.post(SLACK_URL, json={"text": msg})
                print("✅ 슬랙 알림 전송 완료!")
        else:
            print("조회 결과가 없습니다.")
    else:
        print(f"❌ API 호출 에러: {res.text}")

if __name__ == "__main__":
    check_emirates()
