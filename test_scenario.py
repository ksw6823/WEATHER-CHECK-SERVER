"""
테스트 시나리오: 서울 김철수의 아침 날씨 체크
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_scenario():
    print_section("🧪 테스트 시나리오: 서울 김철수의 아침 날씨 체크")
    
    # Step 1: 서버 헬스 체크
    print_section("Step 1: 서버 연결 확인")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"✅ 서버 상태: {response.status_code}")
        print(f"응답: {response.json()}")
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("서버가 실행 중인지 확인하세요: uvicorn main:app --reload")
        return
    
    # Step 2: 사용자 생성
    print_section("Step 2: 사용자 '김철수' 생성")
    user_data = {
        "username": "김철수",
        "email": "chulsoo@example.com"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/weather/users",
            json=user_data,
            timeout=5
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ 사용자 생성 성공!")
            print(f"ID: {user['id']}")
            print(f"이름: {user['username']}")
            print(f"이메일: {user['email']}")
            print(f"생성일: {user['created_at']}")
            user_id = user['id']
        else:
            print(f"⚠️ 응답 코드: {response.status_code}")
            print(f"응답: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 사용자 생성 실패: {e}")
        return
    
    # Step 3: 날씨 조언 요청 (서울 시청 좌표)
    print_section("Step 3: 날씨 조언 요청 (서울 시청)")
    
    weather_request = {
        "user_id": user_id,
        "latitude": 37.5665,  # 서울 시청 위도
        "longitude": 126.9780  # 서울 시청 경도
    }
    
    print(f"📍 위치: 서울특별시 중구 (37.5665°N, 126.9780°E)")
    print(f"⏳ AI 조언 생성 중... (최대 10초 소요)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/weather/advice",
            json=weather_request,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # 메시지 출력
            print_section("💬 AI 날씨 조언")
            print(result['message'])
            
            # 체크리스트 출력
            print_section("✅ 외출 준비 체크리스트")
            for i, item in enumerate(result['checklist'], 1):
                print(f"{i}. {item}")
            
            # 날씨 정보 출력
            print_section("🌤️ 상세 날씨 정보")
            weather = result['weather_info']
            print(f"기온: {weather['display_temperature']} ({weather['temp_feeling']})")
            print(f"하늘: {weather['sky_condition']}")
            print(f"강수확률: {weather['display_rain_probability']}")
            print(f"습도: {weather['display_humidity']} ({weather['humidity_feeling']})")
            print(f"풍속: {weather['display_wind_speed']} ({weather['wind_feeling']})")
            print(f"전체 상태: {weather['overall_emoji']} {weather['overall_status']}")
            
            # 캐릭터 무드 출력
            print_section("🎭 캐릭터별 날씨 반응")
            moods = weather['character_moods']
            for char_name, mood_data in moods.items():
                emoji = mood_data['emoji']
                mood = mood_data['mood']
                print(f"{char_name.upper():8} {emoji} - {mood:12} ({mood_data['preference']})")
            
            print_section("✅ 테스트 완료!")
            print("모든 기능이 정상 작동합니다! 🎉")
            
        else:
            print(f"⚠️ 응답 코드: {response.status_code}")
            print(f"응답: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 요청 타임아웃 (15초 초과)")
        print("OpenAI API 키가 설정되어 있는지 확인하세요.")
    except Exception as e:
        print(f"❌ 날씨 조언 요청 실패: {e}")

if __name__ == "__main__":
    test_scenario()
