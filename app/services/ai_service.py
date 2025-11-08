from openai import AsyncOpenAI
from typing import Dict, Any, List
from app.core.config import settings
import json


class AIService:
    """OpenAI GPT를 사용하여 날씨 기반 조언 생성"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # GPT-4o 또는 gpt-4-turbo 사용
    
    async def generate_weather_advice(
        self, 
        weather_data: Dict[str, Any],
        user_name: str = "사용자"
    ) -> Dict[str, Any]:
        """
        날씨 정보를 기반으로 친근한 조언과 체크리스트 생성
        
        Returns:
            {
                "message": "친근한 날씨 멘트",
                "checklist": ["체크리스트 항목1", "체크리스트 항목2", ...]
            }
        """
        # 날씨 정보를 텍스트로 변환
        weather_summary = self._format_weather_info(weather_data)
        
        # GPT에게 전달할 프롬프트 (체크리스트 추가)
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
4. 불필요한 인사말이나 부연설명 금지
5. 날씨를 단순 반복하지 말고, 그에 따른 느낌이나 행동을 말해주세요

checklist 작성 규칙:
1. 외출 시 꼭 필요한 준비물이나 행동 3-5개
2. 각 항목은 간결하게 (예: "두꺼운 외투 챙기기", "우산 필수")
3. 날씨에 따라 실용적이고 구체적으로

좋은 예시:
{
  "message": "오늘 엄청 춥대! 🥶 두꺼운 패딩 꼭 입고 나가. 바람도 많이 부니까 목도리도 챙기면 좋을 것 같아.",
  "checklist": ["두꺼운 패딩 입기", "목도리 착용", "장갑 챙기기", "따뜻한 음료 준비"]
}

{
  "message": "비 올 확률 높네 ☔ 우산 꼭 챙기고, 미끄러운 데 조심해! 신발도 방수 되는 걸로 신는 게 좋을 것 같아.",
  "checklist": ["우산 챙기기", "방수 신발 착용", "여벌 양말 준비", "미끄럼 주의"]
}

{
  "message": "날씨 딱 좋다! 😊 가벼운 자켓만 걸쳐도 될 것 같아. 산책하기 딱 좋은 날씨야.",
  "checklist": ["가벼운 자켓 착용", "선글라스 챙기기", "물 한 병 준비", "편한 신발 신기"]
}"""

        user_prompt = f"""오늘의 날씨:
{weather_summary}

{user_name}님에게 친근한 메시지와 외출 준비 체크리스트를 JSON 형식으로 생성해주세요."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                response_format={"type": "json_object"}  # JSON 응답 강제
            )
            
            advice_json = response.choices[0].message.content.strip()
            advice_data = json.loads(advice_json)
            
            # 응답 검증
            if "message" not in advice_data or "checklist" not in advice_data:
                raise ValueError("Invalid response format")
            
            return advice_data
            
        except Exception as e:
            print(f"OpenAI API 호출 실패: {e}")
            # 폴백: 간단한 규칙 기반 조언
            return self._generate_fallback_advice(weather_data)
    
    def _format_weather_info(self, weather_data: Dict[str, Any]) -> str:
        """날씨 정보를 읽기 쉬운 텍스트로 변환"""
        lines = []
        
        if weather_data.get("temperature") is not None:
            lines.append(f"- 기온: {weather_data['temperature']}°C")
        
        if weather_data.get("sky_condition"):
            lines.append(f"- 하늘 상태: {weather_data['sky_condition']}")
        
        if weather_data.get("rain_type") and weather_data["rain_type"] != "없음":
            lines.append(f"- 강수 형태: {weather_data['rain_type']}")
        
        if weather_data.get("rain_probability") is not None:
            lines.append(f"- 강수 확률: {weather_data['rain_probability']}%")
        
        if weather_data.get("humidity") is not None:
            lines.append(f"- 습도: {weather_data['humidity']}%")
        
        if weather_data.get("wind_speed") is not None:
            lines.append(f"- 풍속: {weather_data['wind_speed']}m/s")
        
        return "\n".join(lines)
    
    def _generate_fallback_advice(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        API 실패시 사용할 간단한 규칙 기반 조언
        """
        temp = weather_data.get("temperature", 15)
        rain_type = weather_data.get("rain_type", "없음")
        rain_prob = weather_data.get("rain_probability", 0)
        
        message_parts = []
        checklist = []
        
        # 기온 기반 조언
        if temp < 5:
            message_parts.append("오늘 정말 춥네! 🥶 따뜻한 패딩 꼭 입고 나가~")
            checklist.extend(["두꺼운 패딩 입기", "목도리 착용", "장갑 챙기기", "따뜻한 음료 준비"])
        elif temp < 10:
            message_parts.append("쌀쌀한 날씨야. 두꺼운 외투 챙기는 거 잊지마!")
            checklist.extend(["두꺼운 외투 입기", "목도리나 스카프", "따뜻한 신발"])
        elif temp < 15:
            message_parts.append("선선한 날씨네. 가벼운 자켓 정도면 딱 좋을 것 같아 😊")
            checklist.extend(["가벼운 자켓 착용", "긴팔 옷 준비", "편한 신발"])
        elif temp < 25:
            message_parts.append("오늘 날씨 딱 좋다! 편하게 입고 나가도 될 것 같아.")
            checklist.extend(["편한 옷차림", "선글라스", "물 한 병"])
        else:
            message_parts.append("오늘 덥네! 🌞 시원한 옷차림으로 가자.")
            checklist.extend(["시원한 옷 입기", "선글라스 착용", "물 충분히 준비", "자외선 차단제"])
        
        # 강수 기반 조언
        if rain_type != "없음" or rain_prob > 60:
            message_parts.append("우산 꼭 챙겨! ☔")
            checklist.insert(0, "우산 필수")
            checklist.append("방수 신발 착용")
        elif rain_prob > 30:
            message_parts.append("혹시 모르니 우산 가져가는 게 좋을 것 같아.")
            checklist.append("우산 챙기기")
        
        return {
            "message": " ".join(message_parts),
            "checklist": checklist[:5]  # 최대 5개
        }
