"""
OpenAI API 상세 진단
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()

print("="*70)
print("  OpenAI API 상세 진단")
print("="*70)

api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("❌ API 키가 설정되지 않았습니다")
    exit(1)

print(f"\n✅ API 키 확인")
print(f"   길이: {len(api_key)} 문자")
print(f"   시작: {api_key[:20]}...")
print(f"   끝: ...{api_key[-20:]}")

# API 키 형식 확인
if api_key.startswith('sk-proj-'):
    print(f"   형식: Project API Key ✅")
elif api_key.startswith('sk-'):
    print(f"   형식: Standard API Key ✅")
else:
    print(f"   형식: 알 수 없는 형식 ⚠️")

print("\n" + "="*70)
print("  테스트 1: 간단한 채팅 완성")
print("="*70)

try:
    client = OpenAI(api_key=api_key)
    
    print("🔄 OpenAI API 호출 중 (간단한 테스트)...")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": "안녕! 간단하게 '테스트 성공'이라고만 답해줘"}
        ],
        max_tokens=50
    )
    
    answer = response.choices[0].message.content
    
    print(f"✅✅✅ OpenAI API 성공!")
    print(f"\n응답: {answer}")
    print(f"모델: {response.model}")
    print(f"토큰 사용: {response.usage.total_tokens}개")
    print(f"   - 입력: {response.usage.prompt_tokens}")
    print(f"   - 출력: {response.usage.completion_tokens}")
    
    test1_success = True
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    test1_success = False
    
    # 에러 상세 분석
    error_str = str(e)
    if "insufficient_quota" in error_str:
        print("\n💡 진단: 할당량 부족")
        print("   - OpenAI 대시보드에서 크레딧 확인")
        print("   - https://platform.openai.com/account/billing")
    elif "invalid_api_key" in error_str:
        print("\n💡 진단: 잘못된 API 키")
        print("   - API 키가 만료되었거나 삭제됨")
    elif "rate_limit" in error_str:
        print("\n💡 진단: 요청 속도 제한")
        print("   - 잠시 후 다시 시도")
    else:
        print(f"\n💡 전체 에러 메시지:")
        print(f"   {error_str}")

if test1_success:
    print("\n" + "="*70)
    print("  테스트 2: JSON 응답 모드")
    print("="*70)
    
    try:
        print("🔄 JSON 형식 응답 테스트...")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "JSON 형식으로만 응답하세요"},
                {"role": "user", "content": '{"test": "success"} 형식으로 응답해주세요'}
            ],
            max_tokens=50,
            response_format={"type": "json_object"}
        )
        
        answer = response.choices[0].message.content
        data = json.loads(answer)
        
        print(f"✅✅✅ JSON 모드 성공!")
        print(f"응답: {data}")
        print(f"토큰 사용: {response.usage.total_tokens}개")
        
        test2_success = True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        test2_success = False

if test1_success:
    print("\n" + "="*70)
    print("  테스트 3: 실제 날씨 조언 생성")
    print("="*70)
    
    try:
        print("🔄 실제 날씨 조언 생성 테스트...")
        
        system_prompt = """당신은 친근한 날씨 도우미입니다.
JSON 형식으로 응답하세요:
{
  "message": "친근한 날씨 멘트 (2-3문장, 반말)",
  "checklist": ["준비물1", "준비물2", "준비물3"]
}"""
        
        user_prompt = """오늘의 날씨:
- 기온: 17°C
- 하늘: 흐림
- 강수확률: 30%

친근한 조언과 체크리스트를 JSON으로 생성해주세요."""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        answer = response.choices[0].message.content
        data = json.loads(answer)
        
        print(f"✅✅✅ 날씨 조언 생성 성공!")
        print(f"\n💬 메시지:")
        print(f"   {data['message']}")
        print(f"\n✅ 체크리스트:")
        for i, item in enumerate(data['checklist'], 1):
            print(f"   {i}. {item}")
        print(f"\n토큰 사용: {response.usage.total_tokens}개")
        
        test3_success = True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        test3_success = False

print("\n" + "="*70)
print("  최종 결과")
print("="*70)

if test1_success:
    print("\n✅ OpenAI API가 정상 작동합니다!")
    print("✅ 기본 채팅 완성: 성공")
    if 'test2_success' in locals() and test2_success:
        print("✅ JSON 응답 모드: 성공")
    if 'test3_success' in locals() and test3_success:
        print("✅ 날씨 조언 생성: 성공")
    print("\n🎉 OpenAI API를 사용할 수 있습니다!")
else:
    print("\n❌ OpenAI API에 문제가 있습니다")
    print("\n해결 방법:")
    print("1. https://platform.openai.com/account/billing 에서 크레딧 확인")
    print("2. API 키가 활성화되어 있는지 확인")
    print("3. 새 API 키 생성 시도")
    print("\n서버는 폴백 로직으로 계속 작동합니다.")
