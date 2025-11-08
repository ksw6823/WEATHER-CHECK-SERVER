from pydantic import BaseModel
from typing import Optional, List


class WeatherAdviceRequest(BaseModel):
    """날씨 조언 요청 스키마"""
    user_id: int
    latitude: float  # 필수: Flutter에서 현재 위치 전송
    longitude: float  # 필수: Flutter에서 현재 위치 전송
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "latitude": 37.5665,
                "longitude": 126.9780
            }
        }


class WeatherAdviceResponse(BaseModel):
    """날씨 조언 응답 스키마"""
    message: str  # 친근한 날씨 멘트
    checklist: List[str]  # 외출 준비 체크리스트
    weather_info: dict  # 날씨 상세 정보
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "오늘 엄청 춥대! 🥶 두꺼운 패딩 꼭 입고 나가. 바람도 많이 부니까 목도리도 챙기면 좋을 것 같아.",
                "checklist": [
                    "두꺼운 패딩 입기",
                    "목도리 착용",
                    "장갑 챙기기",
                    "따뜻한 음료 준비"
                ],
                "weather_info": {
                    "temperature": 5.0,
                    "sky_condition": "맑음",
                    "rain_probability": 10,
                    "humidity": 45,
                    "rain_type": "없음",
                    "wind_speed": 3.5
                }
            }
        }


class WeatherResponse(BaseModel):
    """날씨 응답 스키마 (기존 호환성 유지)"""
    city: str
    temperature: float
    description: str
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Seoul",
                "temperature": 15.5,
                "description": "Clear sky",
                "humidity": 60,
                "wind_speed": 3.5
            }
        }


class WeatherRequest(BaseModel):
    """날씨 요청 스키마"""
    city: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Seoul"
            }
        }
