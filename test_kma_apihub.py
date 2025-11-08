"""
기상청 API Hub 전용 테스트
https://apihub.kma.go.kr/
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_base_time():
    now = datetime.now()
    base_times = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
    
    current_hour = now.hour
    current_minute = now.minute
    current_time_str = f"{current_hour:02d}{current_minute:02d}"
    
    for base_time in reversed(base_times):
        if current_time_str >= base_time:
            return now.strftime('%Y%m%d'), base_time
    
    yesterday = now - timedelta(days=1)
    return yesterday.strftime('%Y%m%d'), '2300'

print("="*70)
print("  기상청 API Hub 테스트")
print("="*70)

api_key = os.getenv('KMA_API_KEY')
print(f"✅ API 키: {api_key}")

nx, ny = 60, 127
base_date, base_time = get_base_time()

print(f"\n📍 위치: 서울 시청")
print(f"   격자좌표: X={nx}, Y={ny}")
print(f"   발표일자: {base_date}")
print(f"   발표시각: {base_time}")

# 기상청 API Hub 엔드포인트들
endpoints = [
    # 공공데이터포털 (기존)
    ("공공데이터포털", "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"),
    
    # 기상청 API Hub 가능한 엔드포인트
    ("API Hub v1", "https://apihub.kma.go.kr/api/typ01/url/kma_sfct.php"),
    ("API Hub v2", "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"),
]

for name, url in endpoints:
    print("\n" + "="*70)
    print(f"  {name} 테스트")
    print("="*70)
    print(f"URL: {url}")
    
    # API Hub는 authKey 파라미터를 사용할 수 있음
    params = {
        "authKey": api_key,  # API Hub 방식
        "numOfRows": "60",
        "pageNo": "1",
        "dataType": "JSON",
        "base_date": base_date,
        "base_time": base_time,
        "nx": nx,
        "ny": ny
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"HTTP 상태: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ JSON 파싱 성공")
                print(f"응답 키: {list(data.keys())}")
                
                if 'response' in data:
                    result_code = data['response']['header']['resultCode']
                    result_msg = data['response']['header']['resultMsg']
                    print(f"결과코드: {result_code}")
                    print(f"결과메시지: {result_msg}")
                    
                    if result_code == '00':
                        total = data['response']['body']['totalCount']
                        print(f"✅✅✅ 성공! 데이터 {total}개 수신")
                        print(f"\n🎉 {name}이(가) 작동합니다!")
                        
                        # 샘플 데이터 출력
                        items = data['response']['body']['items']['item']
                        print(f"\n샘플 데이터 (처음 3개):")
                        for item in items[:3]:
                            print(f"  - {item['category']}: {item['fcstValue']} (시간: {item['fcstTime']})")
                        break
                else:
                    print(f"응답 구조: {str(data)[:200]}")
            except:
                print(f"응답 (텍스트): {response.text[:200]}")
        elif response.status_code == 404:
            print(f"❌ 404 Not Found - 잘못된 URL")
        elif response.status_code == 401:
            print(f"❌ 401 Unauthorized")
        else:
            print(f"응답: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 에러: {e}")

# serviceKey로도 시도
print("\n" + "="*70)
print("  공공데이터포털 (serviceKey)")
print("="*70)

url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
params = {
    "serviceKey": api_key,  # 표준 방식
    "numOfRows": "60",
    "pageNo": "1",
    "dataType": "JSON",
    "base_date": base_date,
    "base_time": base_time,
    "nx": nx,
    "ny": ny
}

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"HTTP 상태: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            result_code = data['response']['header']['resultCode']
            result_msg = data['response']['header']['resultMsg']
            print(f"결과코드: {result_code}")
            print(f"결과메시지: {result_msg}")
            
            if result_code == '00':
                total = data['response']['body']['totalCount']
                print(f"✅✅✅ 성공! 데이터 {total}개 수신")
except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "="*70)
print("  결론")
print("="*70)
print(f"현재 API 키: {api_key}")
print(f"\n기상청 API Hub를 사용하신다면:")
print(f"  1. API Hub 문서에서 정확한 엔드포인트 URL 확인")
print(f"  2. 인증 파라미터 이름 확인 (authKey vs serviceKey)")
print(f"  3. API Hub 마이페이지에서 키 상태 확인")
print(f"\n또는 공공데이터포털 Decoding 키로 변경하시면")
print(f"공공데이터포털 API가 확실히 작동합니다.")
