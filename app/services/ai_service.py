from openai import AsyncOpenAI
from typing import Dict, Any
from app.core.config import settings


class AIService:
    """OpenAI GPT를 사용하여 날씨 기반 조언 생성"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # GPT-4o 또는 gpt-4-turbo 사용
    
    async def generate_weather_advice(
        self, 
        weather_data: Dict[str, Any],
        user_name: str = "사용자"
    ) -> str:
        """
        날씨 정보를 기반으로 친근한 조언 생성
        """
        # 날씨 정보를 텍스트로 변환
        weather_summary = self._format_weather_info(weather_data)
        
        # GPT에게 전달할 프롬프트 (개선 버전)
        system_prompt = """당신은 친근하고 따뜻한 날씨 도우미입니다.
아침에 외출하는 친구에게 카톡으로 날씨 조언을 보내듯이 말해주세요.

필수 규칙:
1. 반말 사용 (친구처럼 편하게)
2. 정확히 2-3문장으로 간결하게
3. 구체적인 행동 조언 1-2개 포함 (예: "패딩 입어", "우산 챙겨")
4. 이모지는 딱 1-2개만 자연스럽게
5. 불필요한 인사말이나 부연설명 금지
6. 날씨를 단순 반복하지 말고, 그에 따른 행동을 말해주세요

좋은 예시:
- "오늘 엄청 춥대! 🥶 두꺼운 패딩 꼭 입고 나가. 목도리도 있으면 좋을 것 같아."
- "비 올 확률 높네 ☔ 우산 꼭 챙기고, 미끄러운 데 조심해!"
- "날씨 딱 좋다! 가벼운 자켓만 걸쳐도 될 것 같아. 산책하기 좋은 날씨야 😊"

나쁜 예시:
- "안녕하세요! 오늘 날씨를 알려드리겠습니다. 기온은 15도이고..." (❌ 너무 형식적)
- "오늘은 맑은 날씨입니다. 즐거운 하루 되세요." (❌ 구체적 조언 없음)
- "춥고 바람도 불고 습도도 높고 강수확률도..." (❌ 너무 장황함)"""

        user_prompt = f"""오늘의 날씨:
{weather_summary}

{user_name}님에게 간결하고 실용적인 조언을 해주세요."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=150  # 150으로 줄여서 더 간결하게
            )
            
            advice = response.choices[0].message.content.strip()
            return advice
            
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
    
    def _generate_fallback_advice(self, weather_data: Dict[str, Any]) -> str:
        """
        API 실패시 사용할 간단한 규칙 기반 조언
        """
        temp = weather_data.get("temperature", 15)
        rain_type = weather_data.get("rain_type", "없음")
        rain_prob = weather_data.get("rain_probability", 0)
        
        advice_parts = []
        
        # 기온 기반 조언
        if temp < 5:
            advice_parts.append("오늘 정말 춥네! 🥶 따뜻한 패딩 꼭 입고 나가~")
        elif temp < 10:
            advice_parts.append("쌀쌀한 날씨야. 두꺼운 외투 챙기는 거 잊지마!")
        elif temp < 15:
            advice_parts.append("선선한 날씨네. 가벼운 자켓 정도면 딱 좋을 것 같아 😊")
        elif temp < 25:
            advice_parts.append("오늘 날씨 딱 좋다! 편하게 입고 나가도 될 것 같아.")
        else:
            advice_parts.append("오늘 덥네! 🌞 시원한 옷차림으로 가자.")
        
        # 강수 기반 조언
        if rain_type != "없음" or rain_prob > 60:
            advice_parts.append("우산 꼭 챙겨! ☔")
        elif rain_prob > 30:
            advice_parts.append("혹시 모르니 우산 가져가는 게 좋을 것 같아.")
        
        return " ".join(advice_parts)
