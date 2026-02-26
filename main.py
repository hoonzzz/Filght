import os
import requests
import json

# 환경 변수
AMADEUS_KEY = os.environ.get('6oRB72lKYI6pmICcdYxFgaa6cvVpewRG')
AMADEUS_SECRET = os.environ.get('tzrrGCjQMMkGyowa')
SLACK_WEBHOOK_URL = os.environ.get('https://hooks.slack.com/services/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')

def send_slack(message):
    """슬랙 전송 후 결과 로그를 출력합니다."""
    payload = {"text": message}
    res = requests.post(SLACK_URL, json=payload)
    if res.status_code == 200:
        print(f"✅ 슬랙 전송 성공: {message}")
    else:
        print(f"❌ 슬랙 전송 실패 (에러코드: {res.status_code}): {res.text}")

def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {"grant_type": "client_credentials", "client_id": AMADEUS_KEY, "client_secret": AMADEUS_SECRET}
    response = requests.post(url, data=data)
    return response.json().get('access_token')

def check_emirates():
    # [테스트] 실행 시작하자마자 슬랙으로 신호 보내기
    send_slack("🚀 에미레이트 감시 시스템이 정상적으로 가동되었습니다! 가격을 조회합니다.")

    token = get_token()
    if not token:
        print("❌ 토큰 발급 실패")
        return

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
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
            print(f"✈️ 조회된 가격: {price:,.0f}원")
            send_slack(f"🔔 현재 최저가 포착: {price:,.0f}원")
        else:
            print("조회 결과가 없습니다. (날짜/구간에 에미레이트 항공편이 없을 수 있습니다)")
    else:
        print(f"❌ API 에러: {res.text}")

if __name__ == "__main__":
    check_emirates()
