"""
API 허브 방식으로 기상청 API 테스트
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_base_time():
    """현재 시간 기준으로 적절한 base_time 계산"""
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
print("  API 허브 방식 테스트")
print("="*70)

api_key = os.getenv('KMA_API_KEY')
print(f"✅ API 키: {api_key[:10]}... (길이: {len(api_key)})")

# 서울 시청 격자 좌표 (정확한 값)
nx, ny = 60, 127
base_date, base_time = get_base_time()

print(f"\n📍 위치: 서울 시청")
print(f"   격자좌표: X={nx}, Y={ny}")
print(f"   발표일자: {base_date}")
print(f"   발표시각: {base_time}")

# 방법 1: serviceKey를 쿼리 파라미터로 (일반적인 방식)
print("\n" + "="*70)
print("  방법 1: Query Parameter 방식")
print("="*70)

url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
params = {
    "serviceKey": api_key,
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
                print(f"✅ 성공! 데이터 {total}개 수신")
            else:
                print(f"❌ 실패: {result_msg}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"응답: {response.text[:200]}")
except Exception as e:
    print(f"❌ 에러: {e}")

# 방법 2: Header 방식 (API Hub 스타일)
print("\n" + "="*70)
print("  방법 2: Authorization Header 방식")
print("="*70)

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

params_without_key = {
    "numOfRows": "60",
    "pageNo": "1",
    "dataType": "JSON",
    "base_date": base_date,
    "base_time": base_time,
    "nx": nx,
    "ny": ny
}

try:
    response = requests.get(url, params=params_without_key, headers=headers, timeout=10)
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
                print(f"✅ 성공! 데이터 {total}개 수신")
            else:
                print(f"❌ 실패: {result_msg}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"응답: {response.text[:200]}")
except Exception as e:
    print(f"❌ 에러: {e}")

# 방법 3: URL 인코딩 없이 직접 전달
print("\n" + "="*70)
print("  방법 3: URL 직접 구성 방식")
print("="*70)

url_direct = (f"{url}?"
              f"serviceKey={api_key}&"
              f"numOfRows=60&pageNo=1&dataType=JSON&"
              f"base_date={base_date}&base_time={base_time}&"
              f"nx={nx}&ny={ny}")

print(f"URL (처음 100자): {url_direct[:100]}...")

try:
    response = requests.get(url_direct, timeout=10)
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
                print(f"✅ 성공! 데이터 {total}개 수신")
            else:
                print(f"❌ 실패: {result_msg}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"응답: {response.text[:200]}")
except Exception as e:
    print(f"❌ 에러: {e}")

print("\n" + "="*70)
print("  API 허브 키 정보 확인")
print("="*70)
print(f"현재 키: {api_key}")
print(f"키 길이: {len(api_key)} 문자")
print(f"\n💡 참고:")
print(f"   - 공공데이터포털 Decoding 키: 보통 80-100자 이상")
print(f"   - 공공데이터포털 Encoding 키: 보통 20-30자")
print(f"   - API Hub 키: 형식이 다를 수 있음")
print(f"\n현재 키 형식 추정:")
if len(api_key) < 30:
    print(f"   ⚠️ Encoding 키로 보임 → Decoding 키 필요")
elif len(api_key) > 80:
    print(f"   ✅ Decoding 키로 보임")
else:
    print(f"   ❓ API Hub 전용 키일 수 있음")
