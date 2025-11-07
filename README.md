# WEATHER-CHECK-SERVER 🌤️
코딩마라톤 간단 프로젝트 웨더체크 입니다.

기상청 단기예보 API와 GPT를 활용한 날씨 기반 AI 조언 서비스

## 📋 프로젝트 개요

사용자의 위치 정보를 기반으로 기상청 단기예보 데이터를 받아와서, GPT가 친근하고 실용적인 날씨 조언을 생성하는 백엔드 서버입니다.

### 주요 기능
- 🌍 사용자 위치 기반 날씨 정보 조회 (기상청 단기예보 API)
- 🤖 GPT-5를 활용한 친근한 날씨 조언 생성
- 📱 Flutter 앱 연동을 위한 RESTful API
- 💾 AWS RDS PostgreSQL 데이터베이스 지원
- 🎯 정확한 좌표 변환 (Lambert Conformal Conic 투영법)

## 🏗️ 기술 스택

- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL (AWS RDS)
- **ORM**: SQLAlchemy 2.0 (Async)
- **AI**: OpenAI GPT-5
- **Weather API**: 기상청 단기예보 API (공공데이터포털)
- **Client**: Flutter Mobile App

## 📁 프로젝트 구조

```
WEATHER-CHECK-SERVER/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # API 라우터 통합
│   │       └── endpoints/
│   │           └── weather.py      # 날씨 조언 엔드포인트
│   ├── core/
│   │   ├── config.py               # 설정 관리
│   │   └── database.py             # DB 연결 설정
│   ├── models/
│   │   └── user.py                 # User 모델
│   ├── schemas/
│   │   ├── user.py                 # User 스키마
│   │   └── weather.py              # Weather 스키마
│   └── services/
│       ├── weather_service.py      # 기상청 API 서비스
│       └── ai_service.py           # OpenAI GPT 서비스
├── tests/
│   └── test_weather.py             # 테스트 코드
├── main.py                         # FastAPI 애플리케이션
├── requirements.txt                # 패키지 의존성
├── .env.example                    # 환경변수 예시
├── API_SPEC.md                     # 📖 API 명세서
└── README.md
```

## 🚀 시작하기

### 준비물
- Python 3.10 이상
- Git
- AWS RDS PostgreSQL 인스턴스 (미리 생성 필요)
- 기상청 API 키
- OpenAI API 키

---

## 📦 로컬 환경에서 서버 실행하기

### 1단계: 레포지토리 클론

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
git clone https://github.com/ksw6823/WEATHER-CHECK-SERVER.git
cd WEATHER-CHECK-SERVER
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
git clone https://github.com/ksw6823/WEATHER-CHECK-SERVER.git
cd WEATHER-CHECK-SERVER
```
</details>

---

### 2단계: Python 가상환경 생성 및 활성화

<details>
<summary><b>🪟 Windows (PowerShell)</b></summary>

```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화
.\venv\Scripts\Activate.ps1

# 만약 스크립트 실행 오류가 발생하면:
# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
# 명령어 실행 후 다시 시도
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate
```
</details>

---

### 3단계: 패키지 설치

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
pip install -r requirements.txt
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
pip install -r requirements.txt
```
</details>

---

### 4단계: 환경변수 파일 생성

<details>
<summary><b>🪟 Windows (PowerShell)</b></summary>

```powershell
# .env.example을 .env로 복사
Copy-Item .env.example .env

# 또는 CMD에서
# copy .env.example .env
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
# .env.example을 .env로 복사
cp .env.example .env
```
</details>

---

### 5단계: .env 파일 설정

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# 메모장으로 .env 파일 열기
notepad .env

# 또는 VS Code로 열기
code .env
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

```bash
# 기본 텍스트 편집기로 열기
open -e .env

# 또는 VS Code로 열기
code .env

# 또는 vim으로 열기
vim .env
```
</details>

`.env` 파일에 다음 정보를 입력합니다:

```env
# Application
PROJECT_NAME=Weather Check Server
API_V1_STR=/api/v1
DEBUG=True

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://localhost:*"]

# Database (AWS RDS PostgreSQL)
DATABASE_URL=postgresql+asyncpg://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/weather_db
# 예시: postgresql+asyncpg://admin:mypassword@weather-db.abc123.ap-northeast-2.rds.amazonaws.com:5432/weather_db

# 기상청 단기예보 API
KMA_API_KEY=your_kma_api_key_here

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
```

#### 5-1. AWS RDS PostgreSQL 설정

**RDS 인스턴스 생성:**
1. AWS Console → RDS 이동
2. PostgreSQL 데이터베이스 생성 (버전 15 권장)
3. 설정 정보 입력:
   - **DB 인스턴스 식별자**: `weather-db` (원하는 이름)
   - **마스터 사용자 이름**: `admin` (또는 원하는 이름)
   - **마스터 암호**: 안전한 비밀번호 설정 (최소 8자)
4. **퍼블릭 액세스**: 예 (로컬 개발용)
5. **보안 그룹 설정**: 
   - 인바운드 규칙 추가
   - 유형: PostgreSQL
   - 포트: 5432
   - 소스: 내 IP 또는 0.0.0.0/0 (개발용)

**연결 정보 확인:**
1. RDS 대시보드에서 생성한 데이터베이스 클릭
2. **연결 & 보안** 탭에서 정보 확인:
   - **엔드포인트**: `weather-db.abc123.ap-northeast-2.rds.amazonaws.com`
   - **포트**: `5432`
   - **마스터 사용자 이름**: 생성 시 설정한 이름

**DATABASE_URL 형식:**
```
postgresql+asyncpg://유저명:비밀번호@엔드포인트:포트/데이터베이스명
```

**실제 예시:**
```bash
# 설정값 예시:
# - 유저명: admin
# - 비밀번호: MySecurePass123
# - 엔드포인트: weather-db.abc123.ap-northeast-2.rds.amazonaws.com
# - 포트: 5432
# - 데이터베이스명: weather_db

DATABASE_URL=postgresql+asyncpg://admin:MySecurePass123@weather-db.abc123.ap-northeast-2.rds.amazonaws.com:5432/weather_db
```

**⚠️ 비밀번호에 특수문자가 있는 경우 URL 인코딩 필요:**
- `@` → `%40`
- `#` → `%23`
- `%` → `%25`
- `/` → `%2F`

예시: 비밀번호가 `P@ssw0rd#123` 인 경우
```bash
DATABASE_URL=postgresql+asyncpg://admin:P%40ssw0rd%23123@weather-db.abc123.ap-northeast-2.rds.amazonaws.com:5432/weather_db
```

#### 5-2. 기상청 API 키 발급

1. [공공데이터포털](https://data.go.kr/) 접속
2. 회원가입 및 로그인
3. 검색창에 "기상청_단기예보" 검색
4. "기상청_단기예보 ((구)_동네예보) 조회서비스" 클릭
5. 우측 "활용신청" 버튼 클릭
6. 일반 인증키(Decoding) 선택하여 발급
7. 발급된 키를 `.env`의 `KMA_API_KEY`에 입력
   - **주의**: 키 발급 후 1-2시간 후부터 사용 가능

#### 5-3. OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 로그인 (계정 없으면 가입)
3. 우측 상단 프로필 → "View API keys" 클릭
4. "Create new secret key" 버튼 클릭
5. 생성된 키를 **즉시 복사** (다시 볼 수 없음)
6. `.env`의 `OPENAI_API_KEY`에 입력
   - **주의**: 유료 API이므로 크레딧 충전 필요 (~$5 추천)

### 6단계: 데이터베이스 연결 확인

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# Python으로 DB 연결 테스트
python -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
# Python으로 DB 연결 테스트
python3 -c "from app.core.database import engine; import asyncio; asyncio.run(engine.connect())"
```
</details>

만약 연결 오류가 발생하면:
- AWS RDS 보안 그룹에서 내 IP가 허용되었는지 확인
- `DATABASE_URL`이 정확한지 확인
- RDS 인스턴스가 실행 중인지 확인

---

### 7단계: 서버 실행

<details>
<summary><b>🪟 Windows</b></summary>

```powershell
# 개발 모드로 실행 (자동 재시작)
uvicorn main:app --reload

# 또는 특정 포트로 실행
uvicorn main:app --reload --port 8000

# 백그라운드로 실행하려면
# Start-Process -NoNewWindow uvicorn main:app
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

```bash
# 개발 모드로 실행 (자동 재시작)
uvicorn main:app --reload

# 또는 특정 포트로 실행
uvicorn main:app --reload --port 8000

# 백그라운드로 실행하려면
# nohup uvicorn main:app &
```
</details>

---

### 8단계: 서버 동작 확인

브라우저에서 다음 URL에 접속:

- **API 문서 (Swagger UI)**: http://localhost:8000/docs
- **API 문서 (ReDoc)**: http://localhost:8000/redoc  
- **서버 상태**: http://localhost:8000/
- **헬스 체크**: http://localhost:8000/health

---

## ✅ 설치 확인

다음 순서대로 API를 테스트해보세요:

### 1. 사용자 생성 테스트

Swagger UI (http://localhost:8000/docs)에서:

1. `POST /weather/users` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. 다음 JSON 입력:

```json
{
  "username": "테스트유저",
  "email": "test@example.com",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "서울"
}
```

4. "Execute" 버튼 클릭
5. 응답에서 `id` 값 확인 (예: 1)

### 2. 날씨 조언 받기 테스트

1. `POST /weather/advice` 엔드포인트 클릭
2. "Try it out" 버튼 클릭
3. 다음 JSON 입력 (위에서 받은 `id` 사용):

```json
{
  "user_id": 1,
  "latitude": 37.5665,
  "longitude": 126.9780
}
```

4. "Execute" 버튼 클릭
5. 응답에서 `advice`와 `weather_info` 확인

**성공 응답 예시:**
```json
{
  "advice": "오늘 날씨 딱 좋다! 😊 가벼운 자켓만 걸쳐도 될 것 같아.",
  "weather_info": {
    "temperature": 15.0,
    "sky_condition": "맑음",
    "rain_probability": 20,
    ...
  }
}
```

---

## 🔧 트러블슈팅

## 📡 API 엔드포인트

### 주요 API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/weather/advice` | 날씨 조언 생성 (메인) |
| POST | `/weather/users` | 사용자 생성 |
| GET | `/weather/users/{id}` | 사용자 조회 |

### 사용 예시

#### 1. 사용자 생성

```bash
curl -X POST "http://localhost:8000/weather/users" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "홍길동",
    "email": "hong@example.com",
    "latitude": 37.5665,
    "longitude": 126.9780,
    "location_name": "서울시 중구"
  }'
```

#### 2. 날씨 조언 받기 (메인 기능)

```bash
curl -X POST "http://localhost:8000/weather/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "latitude": 37.5665,
    "longitude": 126.9780
  }'
```

**응답 예시:**
```json
{
  "advice": "오늘 엄청 춥대! 🥶 두꺼운 패딩 꼭 입고 나가. 목도리도 있으면 좋을 것 같아.",
  "weather_info": {
    "temperature": 5.0,
    "precipitation": "없음",
    "rain_probability": 10,
    "humidity": 45,
    "sky_condition": "맑음",
    "rain_type": "없음",
    "wind_speed": 2.3
  }
}
```

**📖 자세한 API 명세는 [API_SPEC.md](./API_SPEC.md) 참고**

## 🔄 서비스 플로우

```
┌─────────────┐
│ Flutter App │
└──────┬──────┘
       │ 1. POST /weather/advice
       │    (user_id, lat, lon)
       ▼
┌─────────────────┐
│   FastAPI 백엔드   │
│                 │
│  2. 사용자 조회   │
│     (PostgreSQL) │
│                 │
│  3. 위경도 →     │
│     격자 변환     │
│                 │
│  4. 기상청 API   │
│     호출 및 파싱  │
│                 │
│  5. GPT-4o      │
│     조언 생성    │
└──────┬──────────┘
       │ 6. Response
       │    (advice + weather_info)
       ▼
┌─────────────┐
│ Flutter App │
│ (화면 표시)  │
└─────────────┘
```

## 🗄️ 데이터베이스 스키마

### `users` 테이블

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | Integer | Primary Key | 사용자 ID |
| username | String | Unique, Not Null | 사용자명 |
| email | String | Unique | 이메일 |
| latitude | Float | Not Null | 위도 |
| longitude | Float | Not Null | 경도 |
| location_name | String | Nullable | 지역명 |
| is_active | Boolean | Default: True | 활성 상태 |
| created_at | DateTime | Auto | 생성 시간 |
| updated_at | DateTime | Auto | 수정 시간 |

## 🌐 외부 API

### 1. 기상청 단기예보 API
- **URL**: http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst
- **발급처**: [공공데이터포털](https://data.go.kr/)
- **좌표계**: 기상청 격자 좌표 (Lambert Conformal Conic)
- **업데이트**: 3시간마다 (02:00, 05:00, 08:00, 11:00, 14:00, 17:00, 20:00, 23:00)
- **제공 데이터**: 
  - TMP (기온)
  - POP (강수확률)
  - PTY (강수형태)
  - REH (습도)
  - SKY (하늘상태)
  - WSD (풍속)

### 2. OpenAI API
- **Model**: GPT-5
- **Temperature**: 0.7
- **Max Tokens**: 150
- **용도**: 날씨 데이터 기반 친근한 조언 생성
- **톤**: 친근한 반말, 이모지 1-2개

## 📱 Flutter 연동 가이드

### HTTP 패키지 설치

```yaml
# pubspec.yaml
dependencies:
  http: ^1.1.0
```

### 모델 클래스

```dart
// lib/models/weather_advice.dart
class WeatherAdviceRequest {
  final int userId;
  final double? latitude;
  final double? longitude;

  WeatherAdviceRequest({
    required this.userId,
    this.latitude,
    this.longitude,
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    if (latitude != null) 'latitude': latitude,
    if (longitude != null) 'longitude': longitude,
  };
}

class WeatherAdviceResponse {
  final String advice;
  final WeatherInfo weatherInfo;

  WeatherAdviceResponse({
    required this.advice,
    required this.weatherInfo,
  });

  factory WeatherAdviceResponse.fromJson(Map<String, dynamic> json) {
    return WeatherAdviceResponse(
      advice: json['advice'],
      weatherInfo: WeatherInfo.fromJson(json['weather_info']),
    );
  }
}
```

### API 서비스

```dart
// lib/services/weather_api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class WeatherApiService {
  static const String baseUrl = 'http://your-server.com';

  Future<WeatherAdviceResponse> getWeatherAdvice({
    required int userId,
    double? latitude,
    double? longitude,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/weather/advice'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        if (latitude != null) 'latitude': latitude,
        if (longitude != null) 'longitude': longitude,
      }),
    );

    if (response.statusCode == 200) {
      return WeatherAdviceResponse.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to get weather advice');
    }
  }
}
```

**전체 Flutter 연동 예시는 [API_SPEC.md](./API_SPEC.md) 참고**

## 🧪 테스트

```powershell
# 전체 테스트 실행
pytest tests/ -v

# 특정 테스트 파일 실행
pytest tests/test_weather.py -v

# 커버리지 포함
pytest tests/ --cov=app --cov-report=html
```

## 🔧 트러블슈팅

### 문제 1: 가상환경 활성화 오류

<details>
<summary><b>🪟 Windows (PowerShell)</b></summary>

**증상:**
```
.\venv\Scripts\Activate.ps1 : 이 시스템에서 스크립트를 실행할 수 없으므로...
```

**해결:**
```powershell
# PowerShell을 관리자 권한으로 실행 후
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 다시 가상환경 활성화 시도
.\venv\Scripts\Activate.ps1
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

**증상:**
```
-bash: venv/bin/activate: Permission denied
```

**해결:**
```bash
# 실행 권한 부여
chmod +x venv/bin/activate

# 다시 활성화 시도
source venv/bin/activate
```
</details>

---

### 문제 2: 데이터베이스 연결 오류

**증상:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결 방법 (공통):**
1. AWS RDS 보안 그룹 확인
   - 인바운드 규칙에 5432 포트가 열려있는지 확인
   - 내 IP 주소가 허용되었는지 확인
   
2. RDS 퍼블릭 액세스 확인
   - RDS 인스턴스 → "연결 & 보안" 탭
   - "퍼블릭 액세스 가능" 여부 확인
   
3. DATABASE_URL 형식 확인
   ```
   postgresql+asyncpg://username:password@endpoint:5432/dbname
   ```

4. RDS 인스턴스 상태 확인
   - "사용 가능" 상태인지 확인

<details>
<summary><b>🪟 Windows - 방화벽 확인</b></summary>

```powershell
# PostgreSQL 포트(5432) 방화벽 확인
netsh advfirewall firewall show rule name=all | Select-String "5432"

# 필요시 방화벽 규칙 추가
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Outbound -LocalPort 5432 -Protocol TCP -Action Allow
```
</details>

<details>
<summary><b>🍎 macOS - 방화벽 확인</b></summary>

```bash
# macOS 방화벽 상태 확인
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate

# 방화벽이 활성화되어 있다면 Python 허용
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/python3
```
</details>

---

### 문제 3: 기상청 API 오류

**증상:**
```
기상청 API 호출 실패
```

**해결 방법 (공통):**
1. API 키가 활성화되었는지 확인 (발급 후 1-2시간 소요)
2. [공공데이터포털 마이페이지](https://www.data.go.kr/mypage/my)에서 키 상태 확인
3. API 키에 특수문자가 포함되어 있다면 URL 인코딩 필요 없음 (그대로 사용)
4. 더미 데이터로 테스트 가능 (API 없어도 서버 동작)

---

### 문제 4: OpenAI API 오류

**증상:**
```
OpenAI API 호출 실패 / Rate limit exceeded
```

**해결 방법 (공통):**
1. [OpenAI 계정](https://platform.openai.com/account/billing)에서 크레딧 확인
2. API 키가 올바른지 확인
3. 크레딧이 없으면 규칙 기반 폴백으로 동작 (간단한 조언 생성)

---

### 문제 5: 포트 충돌

<details>
<summary><b>🪟 Windows</b></summary>

**증상:**
```
Error: [Errno 10048] Only one usage of each socket address
```

**해결:**
```powershell
# 8000 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8000

# 프로세스 종료 (PID 확인 후)
taskkill /PID [프로세스ID] /F

# 또는 다른 포트로 실행
uvicorn main:app --reload --port 8001
```
</details>

<details>
<summary><b>🍎 macOS / Linux</b></summary>

**증상:**
```
Error: [Errno 48] Address already in use
```

**해결:**
```bash
# 8000 포트 사용 중인 프로세스 확인
lsof -i :8000

# 프로세스 종료 (PID 확인 후)
kill -9 [PID]

# 또는 다른 포트로 실행
uvicorn main:app --reload --port 8001
```
</details>

---

### 문제 6: 패키지 설치 오류

<details>
<summary><b>🪟 Windows</b></summary>

**증상:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**해결:**
```powershell
# pip 업그레이드
python -m pip install --upgrade pip

# requirements.txt 재설치
pip install -r requirements.txt --no-cache-dir

# Visual C++ 빌드 도구가 필요한 경우
# https://visualstudio.microsoft.com/downloads/ 에서 
# "Build Tools for Visual Studio" 다운로드 및 설치
```
</details>

<details>
<summary><b>🍎 macOS</b></summary>

**증상:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**해결:**
```bash
# pip 업그레이드
python3 -m pip install --upgrade pip

# requirements.txt 재설치
pip install -r requirements.txt --no-cache-dir

# Xcode Command Line Tools가 필요한 경우
xcode-select --install
```
</details>

---

### 문제 7: Python 버전 오류

<details>
<summary><b>🪟 Windows</b></summary>

**Python 버전 확인:**
```powershell
python --version
```

**Python 3.10 이상이 아니라면:**
1. [Python 공식 사이트](https://www.python.org/downloads/)에서 최신 버전 다운로드
2. 설치 시 "Add Python to PATH" 체크박스 선택
3. 명령 프롬프트 재시작 후 버전 확인
</details>

<details>
<summary><b>🍎 macOS</b></summary>

**Python 버전 확인:**
```bash
python3 --version
```

**Python 3.10 이상이 아니라면:**
```bash
# Homebrew로 Python 설치
brew install python@3.11

# 또는 pyenv 사용
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```
</details>

## 📝 MVP 특징

이 프로젝트는 **빠른 프로토타이핑**을 위한 MVP입니다:

- ✅ 핵심 기능에 집중 (날씨 조언 생성)
- ✅ 간단한 사용자 관리 (인증 없음)
- ✅ 에러 처리 및 폴백 메커니즘
- ✅ 외부 API 실패시에도 동작
- ❌ 사용자 인증/권한 없음 (JWT 등)
- ❌ 날씨 조언 히스토리 저장 없음
- ❌ 캐싱 없음

## 🚀 향후 개선 사항

- [ ] JWT 기반 사용자 인증
- [ ] 날씨 조언 히스토리 저장
- [ ] Redis 캐싱 (기상청 API 응답)
- [ ] 푸시 알림 (아침 날씨 조언)
- [ ] 다중 위치 즐겨찾기
- [ ] 관리자 대시보드
- [ ] Sentry 에러 모니터링
- [ ] 로깅 개선

## 📄 라이센스

MIT License

## 👨‍💻 개발자

Weather Check Server - 코딩마라톤 프로젝트

## 📚 참고 문서

- [API 명세서](./API_SPEC.md)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [기상청 API 가이드](https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15084084)
- [OpenAI API 문서](https://platform.openai.com/docs/)

## 📁 프로젝트 구조

```
WEATHER-CHECK-SERVER/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # API 라우터 통합
│   │       └── endpoints/
│   │           └── weather.py      # 날씨 조언 엔드포인트
│   ├── core/
│   │   ├── config.py               # 설정 관리
│   │   └── database.py             # DB 연결 설정
│   ├── models/
│   │   └── user.py                 # User 모델
│   ├── schemas/
│   │   ├── user.py                 # User 스키마
│   │   └── weather.py              # Weather 스키마
│   └── services/
│       ├── weather_service.py      # 기상청 API 서비스
│       └── ai_service.py           # OpenAI GPT 서비스
├── tests/
├── main.py                         # FastAPI 애플리케이션
├── requirements.txt
└── .env.example
```

## 🚀 시작하기

### 1. 환경 설정

```powershell
# 가상환경 생성 및 활성화
python -m venv venv
.\venv\Scripts\Activate.ps1

# 패키지 설치
pip install -r requirements.txt

# 환경변수 설정
Copy-Item .env.example .env
```

### 2. 환경 변수 설정 (.env)

```env
# Application
PROJECT_NAME=Weather Check Server
API_V1_STR=/api/v1
DEBUG=True

# Database (AWS RDS PostgreSQL)
DATABASE_URL=postgresql+asyncpg://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/weather_db

# 기상청 단기예보 API
KMA_API_KEY=your_kma_api_key_here
# 발급: https://data.go.kr/

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
# 발급: https://platform.openai.com/
```

### 3. 서버 실행

```powershell
uvicorn main:app --reload
```

서버 접속: http://localhost:8000  
API 문서: http://localhost:8000/docs

## 📡 API 엔드포인트

### 1. 날씨 조언 받기 (메인 기능)

```http
POST /api/v1/weather/advice
```

**Request Body:**
```json
{
  "user_id": 1,
  "latitude": 37.5665,
  "longitude": 126.9780
}
```

**Response:**
```json
{
  "advice": "오늘 날씨 딱 좋다! 😊 편하게 입고 나가도 될 것 같아. 혹시 모르니 우산 가져가는 게 좋을 것 같아.",
  "weather_info": {
    "temperature": 15.0,
    "sky_condition": "맑음",
    "rain_probability": 30,
    "humidity": 60,
    "rain_type": "없음",
    "wind_speed": 2.5
  }
}
```

### 2. 사용자 생성

```http
POST /api/v1/weather/users
```

**Request Body:**
```json
{
  "username": "홍길동",
  "email": "user@example.com",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "서울시 중구"
}
```

### 3. 사용자 조회

```http
GET /api/v1/weather/users/{user_id}
```

## 🔄 서비스 플로우

1. **Flutter 앱** → 사용자 위치 정보와 함께 `/weather/advice` 호출
2. **백엔드** → 사용자 정보 조회 (PostgreSQL)
3. **백엔드** → 기상청 단기예보 API 호출 및 데이터 정제
4. **백엔드** → 정제된 날씨 데이터를 GPT에 전달
5. **GPT** → 친근하고 실용적인 날씨 조언 생성
6. **백엔드** → Flutter 앱에 조언 및 날씨 정보 반환

## 🗄️ 데이터베이스

### User 테이블

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary Key |
| username | String | 사용자명 |
| email | String | 이메일 |
| latitude | Float | 위도 |
| longitude | Float | 경도 |
| location_name | String | 지역명 |
| is_active | Boolean | 활성 상태 |
| created_at | DateTime | 생성일 |
| updated_at | DateTime | 수정일 |

## 🌐 외부 API

### 1. 기상청 단기예보 API
- **URL**: https://data.go.kr/
- **서비스**: 동네예보 조회서비스
- **제공 데이터**: 기온, 강수확률, 습도, 풍속, 하늘상태 등

### 2. OpenAI API
- **Model**: GPT-4o (또는 GPT-4-turbo)
- **용도**: 날씨 데이터 기반 친근한 조언 생성

## 📱 Flutter 앱 연동 예시

```dart
// Dart/Flutter 예시
Future<WeatherAdvice> getWeatherAdvice(int userId, double lat, double lon) async {
  final response = await http.post(
    Uri.parse('http://your-server.com/api/v1/weather/advice'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'user_id': userId,
      'latitude': lat,
      'longitude': lon,
    }),
  );
  
  return WeatherAdvice.fromJson(jsonDecode(response.body));
}
```

## 🔧 개발 팁

### 로컬 PostgreSQL 설정 (개발용)

```powershell
# Docker로 PostgreSQL 실행
docker run --name weather-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=weather_db -p 5432:5432 -d postgres:15

# .env 파일 설정
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/weather_db
```

## 📝 MVP 특징

- 최소한의 기능으로 빠른 프로토타입 개발
- 간단한 위경도 → 격자 변환 (정확도보다 속도 우선)
- GPT 조언 생성 실패시 규칙 기반 폴백
- 기상청 API 실패시 더미 데이터 제공
