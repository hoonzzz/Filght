import os
import requests
import json

# [1] 환경 변수 정의 - 이 이름들이 GitHub Secrets와 같아야 합니다.
# os.environ.get('이름')에서 '이름'은 GitHub의 Secret Name과 일치해야 함!
AMADEUS_KEY = os.environ.get('AMADEUS_KEY')
AMADEUS_SECRET = os.environ.get('AMADEUS_SECRET')
SLACK_URL = os.environ.get('SLACK_WEBHOOK_URL')

# [2] 목표 가격 설정 (예: 400만원)
TARGET_PRICE = 3000000

def send_slack(message):
    """슬랙으로 메시지를 보냅니다."""
    # 위에서 정의한 SLACK_URL이 비어있는지 다시 확인
    if not SLACK_URL:
        print("❌ 에러: 슬랙 주소가 설정되지 않았습니다.")
        return

    payload = {"text": message}
    try:
        res = requests.post(SLACK_URL, json=payload)
        if res.status_code == 200:
            print(f"✅ 슬랙 전송 성공: {message}")
        else:
            print(f"❌ 슬랙 전송 실패 (코드: {res.status_code})")
    except Exception as e:
        print(f"❌ 슬랙 연결 중 오류 발생: {e}")

def get_token():
    """Amadeus API 토큰을 가져옵니다."""
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_KEY,
        "client_secret": AMADEUS_SECRET
    }
    try:
        response = requests.post(url, data=data)
        return response.json().get('access_token')
    except:
        return None

def check_emirates():
    """항공권을 조회하고 조건에 맞으면 슬랙을 보냅니다."""
    print("🚀 에미레이트 항공권 감시 시작...")
    
    # 시작 알림 (테스트용)
    send_slack("✈️ 에미레이트 항공권 감시 시스템이 정상 가동되었습니다.")

    token = get_token()
    if not token:
        print("❌ API 토큰 발급 실패")
        return

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 2026년 11월 일정 페이로드
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

    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            data = res.json().get('data', [])
            if data:
                price = float(data[0]['price']['total'])
                print(f"현재 가격: {price:,.0f}원")
                
                if price <= TARGET_PRICE:
                    send_slack(f"🔥 **특가 발견!** 총액 {price:,.0f}원\n지금 확인하세요!")
                else:
                    print(f"목표가({TARGET_PRICE:,.0f}원)보다 비쌈. 대기 중...")
            else:
                print("조회된 항공권이 없습니다.")
        else:
            print(f"조회 에러: {res.text}")
    except Exception as e:
        print(f"조회 중 예외 발생: {e}")

if __name__ == "__main__":
    check_emirates()
