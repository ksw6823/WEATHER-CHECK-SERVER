"""
서버의 좌표 변환 로직 테스트
"""
import sys
import math

def convert_to_grid_server_logic(lat, lon):
    """서버에서 사용하는 좌표 변환 로직"""
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136
    
    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi
    
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    
    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    
    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    
    return nx, ny

# 테스트 케이스
test_locations = [
    ("서울 시청", 37.5665, 126.9780),
    ("부산 시청", 35.1796, 129.0756),
    ("대구 시청", 35.8714, 128.6014),
    ("인천 시청", 37.4563, 126.7052),
]

print("="*70)
print("  서버 좌표 변환 로직 테스트")
print("="*70)

for name, lat, lon in test_locations:
    nx, ny = convert_to_grid_server_logic(lat, lon)
    print(f"\n📍 {name}")
    print(f"   위경도: ({lat}, {lon})")
    print(f"   격자좌표: X={nx}, Y={ny}")
    
    if nx < 0 or ny < 0:
        print(f"   ⚠️ 경고: 음수 좌표 발견!")
    elif nx > 200 or ny > 200:
        print(f"   ⚠️ 경고: 비정상적으로 큰 좌표!")
    else:
        print(f"   ✅ 정상 범위")

print("\n" + "="*70)
print("  기상청 API 실제 호출 테스트")
print("="*70)

import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

api_key = os.getenv('KMA_API_KEY')
lat, lon = 37.5665, 126.9780
nx, ny = convert_to_grid_server_logic(lat, lon)

# 현재 시간 기준 base_time 설정
now = datetime.now()
base_date = now.strftime("%Y%m%d")
hour = now.hour

if hour < 2:
    base_time = "2300"
    base_date = (now.replace(hour=0, minute=0, second=0, microsecond=0) - 
                 datetime.timedelta(days=1)).strftime("%Y%m%d")
elif hour < 5:
    base_time = "0200"
elif hour < 8:
    base_time = "0500"
elif hour < 11:
    base_time = "0800"
elif hour < 14:
    base_time = "1100"
elif hour < 17:
    base_time = "1400"
elif hour < 20:
    base_time = "1700"
elif hour < 23:
    base_time = "2000"
else:
    base_time = "2300"

print(f"\n📍 테스트 위치: 서울 시청")
print(f"   격자좌표: X={nx}, Y={ny}")
print(f"   발표일자: {base_date}")
print(f"   발표시각: {base_time}")

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

print(f"\n🔄 API 호출 중...")
try:
    response = requests.get(url, params=params, timeout=10)
    print(f"✅ HTTP 상태: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if 'response' in data:
            header = data['response']['header']
            result_code = header['resultCode']
            result_msg = header['resultMsg']
            
            print(f"✅ 결과코드: {result_code}")
            print(f"✅ 결과메시지: {result_msg}")
            
            if result_code == '00':
                body = data['response']['body']
                total_count = body['totalCount']
                print(f"✅ 데이터 수신 성공! (총 {total_count}개 항목)")
                print("\n🎉 기상청 API가 정상 작동합니다!")
            else:
                print(f"❌ API 에러: {result_msg}")
    elif response.status_code == 401:
        print("❌ 401 Unauthorized")
        print("   API 키를 확인하세요. Decoding 키를 사용해야 합니다.")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"   응답: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 호출 실패: {e}")
