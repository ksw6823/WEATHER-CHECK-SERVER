"""
실제 기상청 API Hub 데이터로 날씨 조언 테스트
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("="*70)
print("  실제 기상청 데이터 테스트")
print("="*70)

# 기존 사용자 ID 1번으로 테스트 (김철수)
user_id = 1

weather_request = {
    "user_id": user_id,
    "latitude": 37.5665,  # 서울 시청
    "longitude": 126.9780
}

print(f"\n📍 위치: 서울 시청")
print(f"🔄 실제 기상청 API Hub 데이터로 조회 중...")
print(f"⏳ AI 조언 생성 중 (최대 15초)...")

try:
    response = requests.post(
        f"{BASE_URL}/weather/advice",
        json=weather_request,
        timeout=15
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n" + "="*70)
        print("  💬 AI 날씨 조언")
        print("="*70)
        print(result['message'])
        
        print("\n" + "="*70)
        print("  ✅ 외출 준비 체크리스트")
        print("="*70)
        for i, item in enumerate(result['checklist'], 1):
            print(f"{i}. {item}")
        
        print("\n" + "="*70)
        print("  🌤️ 실제 기상청 날씨 정보")
        print("="*70)
        weather = result['weather_info']
        
        print(f"📊 기본 정보:")
        print(f"   기온: {weather['display_temperature']} ({weather['temp_feeling']})")
        print(f"   체감: {weather.get('temp_description', 'N/A')}")
        
        print(f"\n☁️ 하늘 상태:")
        print(f"   상태: {weather['sky_condition']}")
        print(f"   강수확률: {weather['display_rain_probability']}")
        print(f"   강수형태: {weather.get('rain_type', 'N/A')}")
        print(f"   {weather.get('rain_status', '')} - {weather.get('rain_description', '')}")
        
        print(f"\n💧 습도/바람:")
        print(f"   습도: {weather['display_humidity']} ({weather['humidity_feeling']})")
        print(f"   풍속: {weather['display_wind_speed']} ({weather['wind_feeling']})")
        
        print(f"\n🎯 종합 평가:")
        print(f"   {weather['overall_emoji']} {weather['overall_status']}")
        
        print("\n" + "="*70)
        print("  🎭 캐릭터별 날씨 반응")
        print("="*70)
        moods = weather['character_moods']
        
        char_names = {
            'sunny': '🌞 맑음이',
            'cloudy': '☁️  구름이',
            'rainy': '🌧️  비',
            'snowy': '❄️  눈',
            'warm': '🌸 따뜻이'
        }
        
        for char_type, mood_data in moods.items():
            char_display = char_names.get(char_type, char_type)
            mood_emoji = mood_data['emoji']
            mood = mood_data['mood']
            preference = mood_data['preference']
            
            mood_kr = {
                'very_happy': '매우 행복',
                'happy': '행복',
                'normal': '보통',
                'sad': '슬픔'
            }.get(mood, mood)
            
            print(f"{char_display:10} {mood_emoji} {mood_kr:8} - {preference}")
        
        print("\n" + "="*70)
        print("  🎉 테스트 완료!")
        print("="*70)
        print("✅ 기상청 API Hub와 연동 성공!")
        print("✅ 실제 날씨 데이터 수신 완료!")
        print("✅ AI 조언 및 체크리스트 생성 완료!")
        print("✅ 캐릭터 무드 시스템 작동 완료!")
        
    else:
        print(f"\n❌ 응답 코드: {response.status_code}")
        print(f"응답: {response.text}")
        
except Exception as e:
    print(f"\n❌ 테스트 실패: {e}")
