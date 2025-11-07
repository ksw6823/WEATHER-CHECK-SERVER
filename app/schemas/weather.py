from pydantic import BaseModel
from typing import Optional


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
    advice: str
    weather_info: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "advice": "오늘 날씨 딱 좋다! 편하게 입고 나가도 될 것 같아. 혹시 모르니 우산 가져가는 게 좋을 것 같아.",
                "weather_info": {
                    "temperature": 15.0,
                    "sky_condition": "맑음",
                    "rain_probability": 30,
                    "humidity": 60
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
