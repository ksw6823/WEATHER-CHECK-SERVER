import httpx
from typing import Dict, Any
from datetime import datetime
from app.core.config import settings


class WeatherService:
    """기상청 단기예보 API를 사용하는 날씨 서비스"""
    
    def __init__(self):
        self.api_key = settings.KMA_API_KEY
        # 기상청 API Hub 엔드포인트 사용
        self.base_url = "https://apihub.kma.go.kr/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst"
    
    def _convert_to_grid(self, lat: float, lon: float) -> tuple[int, int]:
        """
        위경도를 기상청 격자 좌표로 변환 (Lambert Conformal Conic 투영법)
        
        기상청 공식 알고리즘 사용
        출처: 기상청 격자 X, Y 좌표 변환 공식
        """
        import math
        
        # 기상청 격자 정보
        RE = 6371.00877     # 지구 반경(km)
        GRID = 5.0          # 격자 간격(km)
        SLAT1 = 30.0        # 투영 위도1(degree)
        SLAT2 = 60.0        # 투영 위도2(degree)
        OLON = 126.0        # 기준점 경도(degree)
        OLAT = 38.0         # 기준점 위도(degree)
        XO = 43             # 기준점 X좌표(GRID)
        YO = 136            # 기준점 Y좌표(GRID)
        
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
    
    async def get_weather_forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        위경도 기반으로 기상청 단기예보 데이터 가져오기
        """
        nx, ny = self._convert_to_grid(lat, lon)
        
        # 현재 시간 기준 base_date, base_time 설정
        now = datetime.now()
        base_date = now.strftime("%Y%m%d")
        
        # 기상청 API는 특정 시간에만 업데이트 (0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300)
        hour = now.hour
        if hour < 2:
            base_time = "2300"
            base_date = (now.replace(hour=0) - datetime.timedelta(days=1)).strftime("%Y%m%d")
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
        
        params = {
            "authKey": self.api_key,  # 기상청 API Hub는 authKey 사용
            "numOfRows": "60",
            "pageNo": "1",
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # 데이터 정제
                return self._parse_weather_data(data)
                
        except Exception as e:
            print(f"기상청 API 호출 실패: {e}")
            # MVP: 실패시 더미 데이터 반환
            return self._get_dummy_weather_data()
    
    def _parse_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        기상청 API 응답을 깔끔하게 정제
        """
        try:
            items = data["response"]["body"]["items"]["item"]
            
            # 필요한 데이터만 추출
            weather_info = {
                "temperature": None,  # TMP (기온)
                "precipitation": None,  # PCP (1시간 강수량)
                "rain_probability": None,  # POP (강수확률)
                "humidity": None,  # REH (습도)
                "sky_condition": None,  # SKY (하늘상태)
                "rain_type": None,  # PTY (강수형태)
                "wind_speed": None,  # WSD (풍속)
            }
            
            # 가장 최근 예보 데이터 파싱
            for item in items[:12]:  # 앞쪽 12개만 (3시간치)
                category = item["category"]
                value = item["fcstValue"]
                
                if category == "TMP" and weather_info["temperature"] is None:
                    weather_info["temperature"] = float(value)
                elif category == "POP" and weather_info["rain_probability"] is None:
                    weather_info["rain_probability"] = int(value)
                elif category == "REH" and weather_info["humidity"] is None:
                    weather_info["humidity"] = int(value)
                elif category == "SKY" and weather_info["sky_condition"] is None:
                    weather_info["sky_condition"] = self._interpret_sky(value)
                elif category == "PTY" and weather_info["rain_type"] is None:
                    weather_info["rain_type"] = self._interpret_rain_type(value)
                elif category == "WSD" and weather_info["wind_speed"] is None:
                    weather_info["wind_speed"] = float(value)
                elif category == "PCP" and weather_info["precipitation"] is None:
                    weather_info["precipitation"] = value
            
            # 프론트엔드용 추가 정보 생성
            return self._enrich_weather_data(weather_info)
            
        except Exception as e:
            print(f"날씨 데이터 파싱 실패: {e}")
            return self._get_dummy_weather_data()
    
    def _enrich_weather_data(self, weather_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        프론트엔드 표시용 추가 정보 생성
        """
        temp = weather_info.get("temperature", 15)
        rain_prob = weather_info.get("rain_probability", 0)
        humidity = weather_info.get("humidity", 50)
        wind_speed = weather_info.get("wind_speed", 0)
        rain_type = weather_info.get("rain_type", "없음")
        sky = weather_info.get("sky_condition", "맑음")
        
        # 기온 느낌 (매우추움, 추움, 선선, 적당, 더움, 매우더움)
        if temp < 0:
            temp_feeling = "매우추움"
            temp_description = "영하의 날씨예요. 따뜻하게 입으세요!"
        elif temp < 5:
            temp_feeling = "추움"
            temp_description = "쌀쌀한 날씨예요. 두꺼운 옷이 필요해요."
        elif temp < 12:
            temp_feeling = "선선"
            temp_description = "선선한 날씨예요. 가벼운 외투를 챙기세요."
        elif temp < 20:
            temp_feeling = "쾌적"
            temp_description = "활동하기 좋은 날씨예요!"
        elif temp < 28:
            temp_feeling = "따뜻"
            temp_description = "따뜻한 날씨예요. 편하게 입으세요."
        else:
            temp_feeling = "더움"
            temp_description = "무더운 날씨예요. 시원하게 입고 수분 섭취하세요."
        
        # 강수 상태
        if rain_type != "없음":
            rain_status = "강수중"
            rain_description = f"{rain_type}이(가) 내리고 있어요. 우산 필수!"
        elif rain_prob > 70:
            rain_status = "강수예정"
            rain_description = f"비 올 확률 {rain_prob}%. 우산 꼭 챙기세요!"
        elif rain_prob > 30:
            rain_status = "강수가능"
            rain_description = f"비 올 확률 {rain_prob}%. 우산 챙기면 좋아요."
        else:
            rain_status = "강수없음"
            rain_description = "비 올 걱정 없어요!"
        
        # 습도 느낌
        if humidity < 30:
            humidity_feeling = "건조"
            humidity_description = "매우 건조해요. 보습에 신경쓰세요."
        elif humidity < 60:
            humidity_feeling = "쾌적"
            humidity_description = "쾌적한 습도예요."
        elif humidity < 80:
            humidity_feeling = "습함"
            humidity_description = "조금 습해요."
        else:
            humidity_feeling = "매우습함"
            humidity_description = "매우 습해요. 불쾌감을 느낄 수 있어요."
        
        # 바람 느낌
        if wind_speed < 1:
            wind_feeling = "약함"
            wind_description = "바람이 거의 없어요."
        elif wind_speed < 4:
            wind_feeling = "약간"
            wind_description = "약한 바람이 불어요."
        elif wind_speed < 9:
            wind_feeling = "보통"
            wind_description = "바람이 조금 불어요."
        elif wind_speed < 14:
            wind_feeling = "강함"
            wind_description = "바람이 강해요. 주의하세요."
        else:
            wind_feeling = "매우강함"
            wind_description = "매우 강한 바람이 불어요! 외출 주의!"
        
        # 종합 날씨 상태
        if rain_type != "없음":
            overall_status = "rainy"
            overall_emoji = "🌧️"
        elif sky == "맑음":
            overall_status = "sunny"
            overall_emoji = "☀️"
        elif sky == "구름많음":
            overall_status = "cloudy"
            overall_emoji = "⛅"
        else:
            overall_status = "overcast"
            overall_emoji = "☁️"
        
        # 캐릭터별 감정 상태 (프론트에서 선택한 캐릭터에 따라 사용)
        character_moods = self._calculate_character_moods(
            temp, rain_type, sky, rain_prob
        )
        
        # 기존 정보에 추가 정보 병합
        weather_info.update({
            # 기온 관련
            "temp_feeling": temp_feeling,
            "temp_description": temp_description,
            
            # 강수 관련
            "rain_status": rain_status,
            "rain_description": rain_description,
            
            # 습도 관련
            "humidity_feeling": humidity_feeling,
            "humidity_description": humidity_description,
            
            # 바람 관련
            "wind_feeling": wind_feeling,
            "wind_description": wind_description,
            
            # 종합 정보
            "overall_status": overall_status,
            "overall_emoji": overall_emoji,
            
            # UI용 숫자 포맷
            "display_temperature": f"{int(temp)}°C",
            "display_rain_probability": f"{rain_prob}%",
            "display_humidity": f"{humidity}%",
            "display_wind_speed": f"{wind_speed}m/s",
            
            # 캐릭터별 감정 상태
            "character_moods": character_moods,
        })
        
        return weather_info
    
    def _calculate_character_moods(
        self, 
        temp: float, 
        rain_type: str, 
        sky: str, 
        rain_prob: int
    ) -> Dict[str, Dict[str, Any]]:
        """
        캐릭터별 날씨에 대한 감정 상태 계산
        프론트에서 사용자가 선택한 캐릭터에 따라 다른 반응 표시 가능
        """
        
        # 각 캐릭터의 선호도 기반 감정 계산
        moods = {
            # 햇살이 - 맑은 날을 좋아하는 캐릭터
            "sunny": {
                "mood": self._get_sunny_character_mood(sky, rain_type, temp),
                "emoji": self._get_mood_emoji(self._get_sunny_character_mood(sky, rain_type, temp)),
                "preference": "맑은 날씨를 좋아해요 ☀️"
            },
            
            # 구름이 - 흐린 날을 좋아하는 캐릭터
            "cloudy": {
                "mood": self._get_cloudy_character_mood(sky, rain_type),
                "emoji": self._get_mood_emoji(self._get_cloudy_character_mood(sky, rain_type)),
                "preference": "구름 낀 날씨를 좋아해요 ☁️"
            },
            
            # 비방울 - 비 오는 날을 좋아하는 캐릭터
            "rainy": {
                "mood": self._get_rainy_character_mood(rain_type, rain_prob),
                "emoji": self._get_mood_emoji(self._get_rainy_character_mood(rain_type, rain_prob)),
                "preference": "비 오는 날씨를 좋아해요 🌧️"
            },
            
            # 눈송이 - 추운 날/눈 오는 날을 좋아하는 캐릭터
            "snowy": {
                "mood": self._get_snowy_character_mood(temp, rain_type),
                "emoji": self._get_mood_emoji(self._get_snowy_character_mood(temp, rain_type)),
                "preference": "추운 날씨를 좋아해요 ❄️"
            },
            
            # 따스이 - 따뜻한 날을 좋아하는 캐릭터
            "warm": {
                "mood": self._get_warm_character_mood(temp),
                "emoji": self._get_mood_emoji(self._get_warm_character_mood(temp)),
                "preference": "따뜻한 날씨를 좋아해요 🌸"
            }
        }
        
        return moods
    
    def _get_sunny_character_mood(self, sky: str, rain_type: str, temp: float) -> str:
        """햇살이의 기분 (맑은 날 선호)"""
        if rain_type != "없음":
            return "sad"  # 비 오면 슬픔
        elif sky == "맑음" and 15 <= temp <= 25:
            return "very_happy"  # 맑고 적당한 기온이면 매우 행복
        elif sky == "맑음":
            return "happy"  # 맑으면 행복
        elif sky == "구름많음":
            return "normal"  # 구름 많으면 보통
        else:
            return "sad"  # 흐리면 슬픔
    
    def _get_cloudy_character_mood(self, sky: str, rain_type: str) -> str:
        """구름이의 기분 (구름 낀 날 선호)"""
        if rain_type != "없음":
            return "normal"  # 비는 그냥 보통
        elif sky == "흐림" or sky == "구름많음":
            return "very_happy"  # 구름 많으면 매우 행복
        elif sky == "맑음":
            return "sad"  # 너무 맑으면 오히려 슬픔
        else:
            return "normal"
    
    def _get_rainy_character_mood(self, rain_type: str, rain_prob: int) -> str:
        """비방울의 기분 (비 오는 날 선호)"""
        if rain_type != "없음":
            return "very_happy"  # 비 오면 매우 행복
        elif rain_prob > 60:
            return "happy"  # 비 올 것 같으면 행복
        elif rain_prob > 30:
            return "normal"  # 비 올 수도 있으면 보통
        else:
            return "sad"  # 비 안 오면 슬픔
    
    def _get_snowy_character_mood(self, temp: float, rain_type: str) -> str:
        """눈송이의 기분 (추운 날/눈 오는 날 선호)"""
        if rain_type == "눈" or rain_type == "비/눈":
            return "very_happy"  # 눈 오면 매우 행복
        elif temp < 5:
            return "happy"  # 추우면 행복
        elif temp < 15:
            return "normal"  # 선선하면 보통
        else:
            return "sad"  # 따뜻하면 슬픔
    
    def _get_warm_character_mood(self, temp: float) -> str:
        """따스이의 기분 (따뜻한 날 선호)"""
        if 20 <= temp <= 28:
            return "very_happy"  # 따뜻하면 매우 행복
        elif 15 <= temp < 20:
            return "happy"  # 적당하면 행복
        elif 10 <= temp < 15 or 28 < temp <= 32:
            return "normal"  # 약간 춥거나 더우면 보통
        else:
            return "sad"  # 너무 춥거나 더우면 슬픔
    
    def _get_mood_emoji(self, mood: str) -> str:
        """기분에 따른 이모지 반환"""
        mood_emojis = {
            "very_happy": "😊",
            "happy": "🙂",
            "normal": "😐",
            "sad": "😢"
        }
        return mood_emojis.get(mood, "😐")
    
    def _interpret_sky(self, code: str) -> str:
        """하늘 상태 코드 해석"""
        sky_codes = {
            "1": "맑음",
            "3": "구름많음",
            "4": "흐림"
        }
        return sky_codes.get(code, "알수없음")
    
    def _interpret_rain_type(self, code: str) -> str:
        """강수 형태 코드 해석"""
        rain_codes = {
            "0": "없음",
            "1": "비",
            "2": "비/눈",
            "3": "눈",
            "4": "소나기"
        }
        return rain_codes.get(code, "없음")
    
    def _get_dummy_weather_data(self) -> Dict[str, Any]:
        """MVP용 더미 데이터"""
        base_data = {
            "temperature": 15.0,
            "precipitation": "없음",
            "rain_probability": 30,
            "humidity": 60,
            "sky_condition": "맑음",
            "rain_type": "없음",
            "wind_speed": 2.5,
        }
        return self._enrich_weather_data(base_data)
