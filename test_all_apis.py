"""
기상청 API Hub + OpenAI API 종합 테스트
"""
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

print_section("🧪 API 종합 테스트")

# ============================================================
# 1. 기상청 API Hub 테스트
# ============================================================
print_section("1️⃣ 기상청 API Hub 테스트")

kma_key = os.getenv('KMA_API_KEY')
print(f"✅ API 키: {kma_key[:10]}... (길이: {len(kma_key)})")

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

nx, ny = 60, 127  # 서울 시청
base_date, base_time = get_base_time()

print(f"📍 테스트 위치: 서울 시청 (X={nx}, Y={ny})")
print(f"⏰ 발표일시: {base_date} {base_time}")

url = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"
params = {
    "authKey": kma_key,
    "numOfRows": "60",
    "pageNo": "1",
    "dataType": "JSON",
    "base_date": base_date,
    "base_time": base_time,
    "nx": nx,
    "ny": ny
}

print(f"\n🔄 기상청 API 호출 중...")
try:
    response = requests.get(url, params=params, timeout=10)
    print(f"HTTP 상태: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        result_code = data['response']['header']['resultCode']
        result_msg = data['response']['header']['resultMsg']
        
        print(f"결과 코드: {result_code}")
        print(f"결과 메시지: {result_msg}")
        
        if result_code == '00':
            items = data['response']['body']['items']['item']
            total_count = data['response']['body']['totalCount']
            
            print(f"✅✅✅ 기상청 API 성공!")
            print(f"총 {total_count}개 데이터 수신")
            
            # 날씨 데이터 추출
            weather_data = {}
            for item in items[:30]:
                category = item['category']
                value = item['fcstValue']
                time = item['fcstTime']
                
                if time not in weather_data:
                    weather_data[time] = {}
                weather_data[time][category] = value
            
            # 가장 가까운 시간 데이터 출력
            if weather_data:
                first_time = sorted(weather_data.keys())[0]
                data_point = weather_data[first_time]
                
                print(f"\n🌤️ 현재 날씨 정보 (예보시각: {first_time})")
                if 'TMP' in data_point:
                    print(f"   🌡️  기온: {data_point['TMP']}°C")
                if 'SKY' in data_point:
                    sky_map = {'1': '맑음', '3': '구름많음', '4': '흐림'}
                    print(f"   ☁️  하늘: {sky_map.get(data_point['SKY'], data_point['SKY'])}")
                if 'POP' in data_point:
                    print(f"   ☔ 강수확률: {data_point['POP']}%")
                if 'PTY' in data_point:
                    pty_map = {'0': '없음', '1': '비', '2': '비/눈', '3': '눈', '4': '소나기'}
                    print(f"   🌧️  강수형태: {pty_map.get(data_point['PTY'], data_point['PTY'])}")
                if 'REH' in data_point:
                    print(f"   💧 습도: {data_point['REH']}%")
                if 'WSD' in data_point:
                    print(f"   💨 풍속: {data_point['WSD']}m/s")
                
                kma_success = True
                kma_weather = data_point
        else:
            print(f"❌ 기상청 API 오류: {result_msg}")
            kma_success = False
            kma_weather = None
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"응답: {response.text[:200]}")
        kma_success = False
        kma_weather = None
        
except Exception as e:
    print(f"❌ 기상청 API 실패: {e}")
    kma_success = False
    kma_weather = None

# ============================================================
# 2. OpenAI API 테스트
# ============================================================
print_section("2️⃣ OpenAI API 테스트")

openai_key = os.getenv('OPENAI_API_KEY')
if openai_key:
    print(f"✅ API 키: {openai_key[:20]}... (길이: {len(openai_key)})")
else:
    print(f"❌ OpenAI API 키가 설정되지 않았습니다")

if openai_key and kma_success and kma_weather:
    print(f"\n🔄 OpenAI GPT-4o 호출 중...")
    print(f"📝 기상청 데이터를 바탕으로 조언 생성...")
    
    # 날씨 데이터를 텍스트로 변환
    weather_text = f"""오늘의 날씨:
- 기온: {kma_weather.get('TMP', 'N/A')}°C
- 하늘 상태: {kma_weather.get('SKY', 'N/A')}
- 강수확률: {kma_weather.get('POP', 'N/A')}%
- 강수형태: {kma_weather.get('PTY', 'N/A')}
- 습도: {kma_weather.get('REH', 'N/A')}%
- 풍속: {kma_weather.get('WSD', 'N/A')}m/s"""
    
    system_prompt = """당신은 친근하고 따뜻한 날씨 도우미입니다.
아침에 외출하는 친구에게 카톡으로 날씨 조언을 보내듯이 말해주세요.

응답은 반드시 다음 JSON 형식으로만 제공하세요:
{
  "message": "친근한 날씨 멘트",
  "checklist": ["체크리스트 항목1", "체크리스트 항목2", ...]
}

message 작성 규칙:
1. 반말 사용 (친구처럼 편하게)
2. 정확히 2-3문장으로 간결하게
3. 이모지는 딱 1-2개만 자연스럽게
4. 날씨에 따른 느낌이나 행동을 말해주세요

checklist 작성 규칙:
1. 외출 시 꼭 필요한 준비물이나 행동 3-5개
2. 각 항목은 간결하게 (예: "두꺼운 외투 챙기기", "우산 필수")
3. 날씨에 따라 실용적이고 구체적으로"""
    
    user_prompt = f"""{weather_text}

사용자님에게 친근한 메시지와 외출 준비 체크리스트를 JSON 형식으로 생성해주세요."""
    
    try:
        client = OpenAI(api_key=openai_key)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        advice_json = response.choices[0].message.content
        
        import json
        advice_data = json.loads(advice_json)
        
        print(f"✅✅✅ OpenAI API 성공!")
        print(f"모델: {response.model}")
        print(f"토큰 사용: {response.usage.total_tokens}개")
        
        print(f"\n💬 생성된 조언:")
        print(f"{advice_data['message']}")
        
        print(f"\n✅ 생성된 체크리스트:")
        for i, item in enumerate(advice_data['checklist'], 1):
            print(f"{i}. {item}")
        
        openai_success = True
        
    except Exception as e:
        print(f"❌ OpenAI API 실패: {e}")
        openai_success = False
else:
    if not openai_key:
        print("⚠️ OpenAI API 키가 없어 테스트를 건너뜁니다")
    elif not kma_success:
        print("⚠️ 기상청 데이터가 없어 OpenAI 테스트를 건너뜁니다")
    openai_success = False

# ============================================================
# 3. 서버 통합 테스트
# ============================================================
print_section("3️⃣ 서버 전체 통합 테스트")

print("🔄 실제 서버 API 호출 중...")
print("   (기상청 + OpenAI + 캐릭터 무드 + 상세 정보)")

try:
    server_response = requests.post(
        "http://127.0.0.1:8000/weather/advice",
        json={
            "user_id": 1,
            "latitude": 37.5665,
            "longitude": 126.9780
        },
        timeout=20
    )
    
    if server_response.status_code == 200:
        result = server_response.json()
        
        print("✅✅✅ 서버 통합 테스트 성공!")
        
        print(f"\n💬 서버 응답 - 조언:")
        print(f"{result['message']}")
        
        print(f"\n✅ 서버 응답 - 체크리스트:")
        for i, item in enumerate(result['checklist'], 1):
            print(f"{i}. {item}")
        
        weather_info = result['weather_info']
        print(f"\n🌤️ 서버 응답 - 날씨 정보:")
        print(f"   기온: {weather_info['display_temperature']}")
        print(f"   상태: {weather_info['overall_emoji']} {weather_info['overall_status']}")
        
        print(f"\n🎭 서버 응답 - 캐릭터 무드:")
        moods = weather_info['character_moods']
        for char, mood in list(moods.items())[:2]:
            print(f"   {char}: {mood['emoji']} {mood['mood']}")
        
        server_success = True
    else:
        print(f"❌ 서버 오류: HTTP {server_response.status_code}")
        print(f"응답: {server_response.text[:200]}")
        server_success = False
        
except Exception as e:
    print(f"❌ 서버 테스트 실패: {e}")
    server_success = False

# ============================================================
# 최종 결과
# ============================================================
print_section("📊 최종 테스트 결과")

print(f"\n{'항목':<30} {'상태':<10} {'비고'}")
print("-" * 70)
print(f"{'1. 기상청 API Hub':<30} {'✅ 성공' if kma_success else '❌ 실패':<10} {'실제 날씨 데이터 수신' if kma_success else '연결 실패'}")
print(f"{'2. OpenAI GPT-4o API':<30} {'✅ 성공' if openai_success else '❌ 실패':<10} {'AI 조언 생성' if openai_success else 'API 키 확인 필요'}")
print(f"{'3. 서버 통합 API':<30} {'✅ 성공' if server_success else '❌ 실패':<10} {'전체 기능 작동' if server_success else '서버 확인 필요'}")

print("\n" + "="*70)
if kma_success and openai_success and server_success:
    print("  🎉🎉🎉 모든 API가 정상 작동합니다! 🎉🎉🎉")
    print("="*70)
    print("\n✅ 기상청 실제 데이터 수신")
    print("✅ OpenAI로 실시간 조언 생성")
    print("✅ 캐릭터 무드 시스템 작동")
    print("✅ 상세 날씨 정보 제공")
    print("\n프로덕션 준비 완료! 🚀")
elif kma_success and server_success:
    print("  ⚠️ 기상청 API는 작동하지만 OpenAI는 폴백 사용 중")
    print("="*70)
    print("\n✅ 기상청 실제 데이터 수신")
    print("⚠️ OpenAI API 키 확인 필요 (현재는 규칙 기반 폴백)")
    print("✅ 기본 기능은 모두 작동")
else:
    print("  ⚠️ 일부 API에 문제가 있습니다")
    print("="*70)
    if not kma_success:
        print("\n❌ 기상청 API: API Hub 키 확인 필요")
    if not openai_success:
        print("❌ OpenAI API: API 키 확인 필요")
    if not server_success:
        print("❌ 서버: uvicorn main:app --reload 실행 확인")
