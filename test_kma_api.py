"""
기상청 단기예보 API 호출 테스트
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def convert_to_grid(lat, lon):
    """위경도를 기상청 격자 좌표로 변환 (간단한 버전)"""
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136
    
    DEGRAD = 3.141592653589793 / 180.0
    
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD
    
    sn = (slat1 ** 2 - slat2 ** 2) / 2
    sf = slat1 / sn
    ro = re * sf / (slat1 ** 2)
    
    ra = re * sf / ((lat * DEGRAD) ** 2)
    theta = lon * DEGRAD - olon
    
    x = ra * theta / DEGRAD
    y = ro - ra
    
    nx = int(x + XO + 0.5)
    ny = int(y + YO + 0.5)
    
    return nx, ny

def get_base_time():
    """현재 시간 기준으로 적절한 base_time 계산"""
    now = datetime.now()
    
    # API 발표 시각: 02:10, 05:10, 08:10, 11:10, 14:10, 17:10, 20:10, 23:10
    base_times = ['0200', '0500', '0800', '1100', '1400', '1700', '2000', '2300']
    
    current_hour = now.hour
    current_minute = now.minute
    
    # 현재 시각을 4자리 문자열로 변환
    current_time_str = f"{current_hour:02d}{current_minute:02d}"
    
    # 가장 최근의 발표 시각 찾기
    for base_time in reversed(base_times):
        if current_time_str >= base_time:
            return now.strftime('%Y%m%d'), base_time
    
    # 모든 base_time보다 이른 경우 전날 마지막 발표 시각 사용
    yesterday = now - timedelta(days=1)
    return yesterday.strftime('%Y%m%d'), '2300'

def test_kma_api():
    print_section("🌤️ 기상청 단기예보 API 테스트")
    
    # API 키 확인
    api_key = os.getenv('KMA_API_KEY')
    
    if not api_key:
        print("❌ .env 파일에 KMA_API_KEY가 설정되지 않았습니다.")
        return
    
    print(f"✅ API 키 확인: {api_key[:10]}...")
    print(f"   전체 길이: {len(api_key)} 문자")
    
    # 테스트할 위치: 서울 시청
    lat, lon = 37.5665, 126.9780
    nx, ny = convert_to_grid(lat, lon)
    
    print(f"\n📍 테스트 위치: 서울 시청")
    print(f"   위도/경도: {lat}, {lon}")
    print(f"   격자 좌표: X={nx}, Y={ny}")
    
    # API 호출 시간 계산
    base_date, base_time = get_base_time()
    print(f"\n⏰ API 조회 시간")
    print(f"   발표 일자: {base_date}")
    print(f"   발표 시각: {base_time}")
    
    # API URL 구성
    url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
    params = {
        'serviceKey': api_key,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': str(nx),
        'ny': str(ny)
    }
    
    print_section("🔄 API 호출 중...")
    print(f"URL: {url}")
    print(f"파라미터:")
    for key, value in params.items():
        if key == 'serviceKey':
            print(f"  {key}: {value[:10]}...")
        else:
            print(f"  {key}: {value}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        print(f"\n📊 응답 상태")
        print(f"   HTTP 상태 코드: {response.status_code}")
        print(f"   응답 크기: {len(response.content)} bytes")
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # 응답 구조 확인
                if 'response' in data:
                    header = data['response']['header']
                    result_code = header['resultCode']
                    result_msg = header['resultMsg']
                    
                    print(f"\n✅ API 응답 헤더")
                    print(f"   결과 코드: {result_code}")
                    print(f"   결과 메시지: {result_msg}")
                    
                    if result_code == '00':
                        # 정상 응답
                        body = data['response']['body']
                        items = body['items']['item']
                        total_count = body['totalCount']
                        
                        print(f"\n✅ 데이터 조회 성공!")
                        print(f"   총 {total_count}개 항목 수신")
                        
                        # 주요 날씨 정보 추출
                        print_section("🌡️ 날씨 정보 샘플 (최신 3시간)")
                        
                        weather_data = {}
                        for item in items[:50]:  # 처음 50개만 확인
                            category = item['category']
                            fcst_value = item['fcstValue']
                            fcst_time = item['fcstTime']
                            
                            if fcst_time not in weather_data:
                                weather_data[fcst_time] = {}
                            
                            weather_data[fcst_time][category] = fcst_value
                        
                        # 가장 가까운 시간 정보 출력
                        if weather_data:
                            first_time = sorted(weather_data.keys())[0]
                            data_point = weather_data[first_time]
                            
                            print(f"\n⏰ 예보 시각: {first_time[:2]}:{first_time[2:]}시")
                            
                            if 'TMP' in data_point:
                                print(f"   🌡️  기온: {data_point['TMP']}°C")
                            if 'POP' in data_point:
                                print(f"   ☔ 강수확률: {data_point['POP']}%")
                            if 'SKY' in data_point:
                                sky_code = data_point['SKY']
                                sky_map = {'1': '맑음', '3': '구름많음', '4': '흐림'}
                                print(f"   ☁️  하늘상태: {sky_map.get(sky_code, sky_code)}")
                            if 'PTY' in data_point:
                                pty_code = data_point['PTY']
                                pty_map = {'0': '없음', '1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
                                print(f"   🌧️  강수형태: {pty_map.get(pty_code, pty_code)}")
                            if 'REH' in data_point:
                                print(f"   💧 습도: {data_point['REH']}%")
                            if 'WSD' in data_point:
                                print(f"   💨 풍속: {data_point['WSD']}m/s")
                        
                        print_section("✅ 기상청 API 테스트 성공!")
                        print("실제 날씨 데이터를 정상적으로 받아올 수 있습니다! 🎉")
                        
                    elif result_code == '01':
                        print(f"\n❌ API 오류: APPLICATION_ERROR")
                        print(f"   메시지: {result_msg}")
                        print(f"\n💡 해결 방법:")
                        print(f"   - API 키가 승인되었는지 확인")
                        print(f"   - 공공데이터포털에서 활용신청 상태 확인")
                        
                    elif result_code == '03':
                        print(f"\n❌ API 오류: NODATA_ERROR")
                        print(f"   메시지: {result_msg}")
                        print(f"\n💡 해결 방법:")
                        print(f"   - base_date, base_time 확인")
                        print(f"   - 격자 좌표(nx, ny) 확인")
                        
                    else:
                        print(f"\n⚠️ 알 수 없는 결과 코드: {result_code}")
                        print(f"   메시지: {result_msg}")
                        
                else:
                    print(f"\n❌ 예상치 못한 응답 형식")
                    print(f"응답 내용 (처음 500자):")
                    print(response.text[:500])
                    
            except Exception as e:
                print(f"\n❌ JSON 파싱 실패: {e}")
                print(f"응답 내용 (처음 500자):")
                print(response.text[:500])
                
        elif response.status_code == 401:
            print(f"\n❌ 401 Unauthorized - 인증 실패")
            print(f"\n💡 원인:")
            print(f"   1. API 키가 잘못되었거나 만료됨")
            print(f"   2. Encoding 키 대신 Decoding 키를 사용해야 함")
            print(f"   3. 활용신청이 승인되지 않음 (1-2시간 소요)")
            print(f"\n💡 해결 방법:")
            print(f"   1. 공공데이터포털(data.go.kr) 접속")
            print(f"   2. 마이페이지 → 활용신청 현황")
            print(f"   3. '일반 인증키 (Decoding)' 복사")
            print(f"   4. .env 파일의 KMA_API_KEY에 붙여넣기")
            
        elif response.status_code == 429:
            print(f"\n❌ 429 Too Many Requests - 트래픽 초과")
            print(f"   일일 호출 제한(1,000건)을 초과했습니다.")
            
        else:
            print(f"\n⚠️ 예상치 못한 HTTP 상태 코드")
            print(f"응답 내용 (처음 500자):")
            print(response.text[:500])
            
    except requests.exceptions.Timeout:
        print(f"\n❌ 요청 타임아웃 (10초 초과)")
        print(f"   네트워크 연결을 확인하세요.")
        
    except Exception as e:
        print(f"\n❌ API 호출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kma_api()
