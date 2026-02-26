import os
import requests
import json

# 디버깅: 어떤 환경변수들이 들어왔는지 확인 (보안상 값은 출력 안됨)
print("--- 환경 변수 체크 ---")
print(f"AMADEUS_KEY 존재 여부: {'있음' if os.environ.get('AMADEUS_KEY') else '없음'}")
print(f"AMADEUS_SECRET 존재 여부: {'있음' if os.environ.get('AMADEUS_SECRET') else '없음'}")
print(f"SLACK_URL 존재 여부: {'있음' if os.environ.get('SLACK_WEBHOOK_URL') else '없음'}")
print("--------------------")

# 환경 변수 안전하게 가져오기
AMADEUS_KEY = os.environ.get('6oRB72lKYI6pmICcdYxFgaa6cvVpewRG')
AMADEUS_SECRET = os.environ.get('tzrrGCjQMMkGyowa')
SLACK_WEBHOOK_URL = os.environ.get('https://hooks.slack.com/services/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')

# 키가 제대로 전달되지 않았을 경우 확인
if not AMADEUS_KEY or not AMADEUS_SECRET:
    print("❌ 에러: GitHub Secrets에서 API 키를 가져오지 못했습니다. YAML 설정을 확인하세요.")
    exit(1)

TARGET_PRICE_KRW = 3000000  # 성인 2명 합계 목표가

def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {"grant_type": "client_credentials", "client_id": AMADEUS_KEY, "client_secret": AMADEUS_SECRET}
    return requests.post(url, data=data).json()['access_token']

def check_emirates_multi_city():
    token = get_token()
    # 다구간 조회를 위한 POST 엔드포인트
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 정확한 다구간 조회 페이로드 (인천-두바이-몰디브-인천)
    payload = {
        "currencyCode": "KRW",
        "originDestinations": [
            {"id": "1", "originLocationCode": "ICN", "destinationLocationCode": "DXB", "departureDateTimeRange": {"date": "2026-11-15"}},
            {"id": "2", "originLocationCode": "DXB", "destinationLocationCode": "MLE", "departureDateTimeRange": {"date": "2026-11-18"}},
            {"id": "3", "originLocationCode": "MLE", "destinationLocationCode": "ICN", "departureDateTimeRange": {"date": "2026-11-22"}}
        ],
        "travelers": [{"id": "1", "travelerType": "ADULT"}, {"id": "2", "travelerType": "ADULT"}],
        "sources": ["GDS"],
        "searchCriteria": {
            "flightFilters": {
                "airlineRestrictions": {"includedAirlineCodes": ["EK"]}
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        offers = response.json().get('data', [])
        if not offers:
            print("조회된 항공권이 없습니다.")
            return

        # 가장 저렴한 옵션의 가격 확인
        current_price = float(offers[0]['price']['total'])
        print(f"현재 최저가: {current_price:,.0f}원")

        if current_price <= TARGET_PRICE_KRW:
            send_slack(current_price)
    else:
        print(f"오류 발생: {response.text}")

def send_slack(price):
    payload = {"text": f"🚨 **에미레이트 특가 포착!**\n총액: {price:,.0f}원\n스케줄: ICN-DXB-MLE-ICN (성인 2명)"}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

if __name__ == "__main__":
    check_emirates_multi_city()
