import httpx
from typing import Dict, Any
from datetime import datetime
from app.core.config import settings


class WeatherService:
    """기상청 단기예보 API를 사용하는 날씨 서비스"""
    
    def __init__(self):
        self.api_key = settings.KMA_API_KEY
        self.base_url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    
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
            "serviceKey": self.api_key,
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
            
            return weather_info
            
        except Exception as e:
            print(f"날씨 데이터 파싱 실패: {e}")
            return self._get_dummy_weather_data()
    
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
        return {
            "temperature": 15.0,
            "precipitation": "없음",
            "rain_probability": 30,
            "humidity": 60,
            "sky_condition": "맑음",
            "rain_type": "없음",
            "wind_speed": 2.5,
        }
