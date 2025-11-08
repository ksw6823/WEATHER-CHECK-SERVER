# API 명세서 (API Specification)

**Base URL**: `http://your-server.com`  
**Version**: 1.0.0  
**Protocol**: REST API  
**Content-Type**: `application/json`

---

## 📡 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/weather/advice` | 날씨 조언 생성 (메인 기능) |
| POST | `/weather/users` | 사용자 생성 |
| GET | `/weather/users/{user_id}` | 사용자 조회 |
| PUT | `/weather/users/{user_id}` | 사용자 정보 수정 |

---

## 🚨 에러 응답 형식

모든 에러는 다음과 같은 일관된 형식으로 응답됩니다:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "사용자에게 표시할 에러 메시지",
    "details": "추가 상세 정보 (선택사항, DEBUG 모드에서만)"
  }
}
```

### 에러 코드 목록

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `BAD_REQUEST` | 잘못된 요청 |
| 400 | `CONFLICT` | 중복된 리소스 |
| 404 | `NOT_FOUND` | 리소스를 찾을 수 없음 |
| 422 | `VALIDATION_ERROR` | 입력값 유효성 검사 실패 |
| 500 | `INTERNAL_ERROR` | 서버 내부 오류 |
| 500 | `DATABASE_ERROR` | 데이터베이스 오류 |
| 503 | `WEATHER_API_ERROR` | 기상청 API 호출 실패 |
| 503 | `AI_SERVICE_ERROR` | AI 서비스 호출 실패 |

---

## 1️⃣ 날씨 조언 생성 (메인 API)

### **POST** `/weather/advice`

사용자의 현재 위치 정보를 기반으로 기상청 날씨 데이터와 GPT를 활용하여 친근한 날씨 조언을 생성합니다.

#### Request Body

```json
{
  "user_id": 1,
  "latitude": 37.5665,
  "longitude": 126.9780
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | integer | ✅ 필수 | 사용자 ID |
| `latitude` | float | ✅ 필수 | 위도 (현재 위치) |
| `longitude` | float | ✅ 필수 | 경도 (현재 위치) |

#### Response (200 OK)

```json
{
  "message": "오늘 엄청 춥대! 🥶 두꺼운 패딩 꼭 입고 나가. 바람도 많이 부니까 목도리도 챙기면 좋을 것 같아.",
  "checklist": [
    "두꺼운 패딩 입기",
    "목도리 착용",
    "장갑 챙기기",
    "따뜻한 음료 준비"
  ],
  "weather_info": {
    "temperature": 5.0,
    "precipitation": "없음",
    "rain_probability": 10,
    "humidity": 45,
    "sky_condition": "맑음",
    "rain_type": "없음",
    "wind_speed": 2.3,
    "temp_feeling": "추움",
    "temp_description": "쌀쌀한 날씨예요. 두꺼운 옷이 필요해요.",
    "rain_status": "강수없음",
    "rain_description": "비 올 걱정 없어요!",
    "humidity_feeling": "쾌적",
    "humidity_description": "쾌적한 습도예요.",
    "wind_feeling": "약간",
    "wind_description": "약한 바람이 불어요.",
    "overall_status": "sunny",
    "overall_emoji": "☀️",
    "display_temperature": "5°C",
    "display_rain_probability": "10%",
    "display_humidity": "45%",
    "display_wind_speed": "2.3m/s",
    "character_moods": {
      "sunny": {
        "mood": "happy",
        "emoji": "🙂",
        "preference": "맑은 날씨를 좋아해요 ☀️"
      },
      "cloudy": {
        "mood": "sad",
        "emoji": "😢",
        "preference": "구름 낀 날씨를 좋아해요 ☁️"
      },
      "rainy": {
        "mood": "sad",
        "emoji": "😢",
        "preference": "비 오는 날씨를 좋아해요 🌧️"
      },
      "snowy": {
        "mood": "happy",
        "emoji": "🙂",
        "preference": "추운 날씨를 좋아해요 ❄️"
      },
      "warm": {
        "mood": "normal",
        "emoji": "😐",
        "preference": "따뜻한 날씨를 좋아해요 🌸"
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | GPT가 생성한 친근한 날씨 멘트 (2-3문장, 이모지 포함) |
| `checklist` | array[string] | 외출 준비 체크리스트 (3-5개 항목) |
| `weather_info` | object | 날씨 상세 정보 |

#### weather_info 상세 필드

**기본 기상 데이터:**
| Field | Type | Description |
|-------|------|-------------|
| `temperature` | float | 기온 (°C) |
| `precipitation` | string | 강수량 ("없음", "1mm", "5mm" 등) |
| `rain_probability` | integer | 강수확률 (0-100%) |
| `humidity` | integer | 습도 (0-100%) |
| `sky_condition` | string | 하늘 상태 ("맑음", "구름많음", "흐림") |
| `rain_type` | string | 강수 형태 ("없음", "비", "눈", "비/눈", "소나기") |
| `wind_speed` | float | 풍속 (m/s) |

**프론트엔드 표시용 추가 정보:**
| Field | Type | Description |
|-------|------|-------------|
| `temp_feeling` | string | 기온 느낌 ("매우추움", "추움", "선선", "쾌적", "따뜻", "더움") |
| `temp_description` | string | 기온 설명 (예: "쌀쌀한 날씨예요. 두꺼운 옷이 필요해요.") |
| `rain_status` | string | 강수 상태 ("강수중", "강수예정", "강수가능", "강수없음") |
| `rain_description` | string | 강수 설명 (예: "비 올 확률 30%. 우산 챙기면 좋아요.") |
| `humidity_feeling` | string | 습도 느낌 ("건조", "쾌적", "습함", "매우습함") |
| `humidity_description` | string | 습도 설명 (예: "쾌적한 습도예요.") |
| `wind_feeling` | string | 바람 느낌 ("약함", "약간", "보통", "강함", "매우강함") |
| `wind_description` | string | 바람 설명 (예: "약한 바람이 불어요.") |
| `overall_status` | string | 종합 날씨 상태 ("sunny", "cloudy", "overcast", "rainy") |
| `overall_emoji` | string | 날씨 이모지 (☀️, ⛅, ☁️, 🌧️) |
| `display_temperature` | string | UI 표시용 기온 (예: "5°C") |
| `display_rain_probability` | string | UI 표시용 강수확률 (예: "10%") |
| `display_humidity` | string | UI 표시용 습도 (예: "45%") |
| `display_wind_speed` | string | UI 표시용 풍속 (예: "2.3m/s") |
| `character_moods` | object | 캐릭터별 감정 상태 (5가지 캐릭터) |

#### character_moods 상세 구조

각 캐릭터는 날씨에 따라 다르게 반응합니다:

**캐릭터 타입:**
- `sunny`: 햇살이 (맑은 날 선호)
- `cloudy`: 구름이 (흐린 날 선호)
- `rainy`: 비방울 (비 오는 날 선호)
- `snowy`: 눈송이 (추운 날/눈 오는 날 선호)
- `warm`: 따스이 (따뜻한 날 선호)

**각 캐릭터 필드:**
| Field | Type | Description |
|-------|------|-------------|
| `mood` | string | 감정 상태 ("very_happy", "happy", "normal", "sad") |
| `emoji` | string | 감정 이모지 (😊, 🙂, 😐, 😢) |
| `preference` | string | 캐릭터 선호 설명 |

#### Error Responses

**404 Not Found** - 사용자를 찾을 수 없음
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다"
  }
}
```

**503 Service Unavailable** - 기상청 API 오류
```json
{
  "success": false,
  "error": {
    "code": "WEATHER_API_ERROR",
    "message": "날씨 정보를 가져오는데 실패했습니다"
  }
}
```

**503 Service Unavailable** - AI 서비스 오류
```json
{
  "success": false,
  "error": {
    "code": "AI_SERVICE_ERROR",
    "message": "AI 조언 생성에 실패했습니다"
  }
}
```

**500 Internal Server Error** - 서버 오류
```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "서버 내부 오류가 발생했습니다"
  }
}
```

#### Flutter/Dart 예시 코드

```dart
class WeatherAdviceRequest {
  final int userId;
  final double latitude;
  final double longitude;

  WeatherAdviceRequest({
    required this.userId,
    required this.latitude,
    required this.longitude,
  });

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'latitude': latitude,
    'longitude': longitude,
  };
}

class WeatherAdviceResponse {
  final String message;
  final List<String> checklist;
  final WeatherInfo weatherInfo;

  WeatherAdviceResponse({
    required this.message,
    required this.checklist,
    required this.weatherInfo,
  });

  factory WeatherAdviceResponse.fromJson(Map<String, dynamic> json) {
    return WeatherAdviceResponse(
      message: json['message'],
      checklist: List<String>.from(json['checklist']),
      weatherInfo: WeatherInfo.fromJson(json['weather_info']),
    );
  }
}

class WeatherInfo {
  // 기본 기상 데이터
  final double temperature;
  final String precipitation;
  final int rainProbability;
  final int humidity;
  final String skyCondition;
  final String rainType;
  final double windSpeed;
  
  // 프론트엔드 표시용 추가 정보
  final String tempFeeling;
  final String tempDescription;
  final String rainStatus;
  final String rainDescription;
  final String humidityFeeling;
  final String humidityDescription;
  final String windFeeling;
  final String windDescription;
  final String overallStatus;
  final String overallEmoji;
  final String displayTemperature;
  final String displayRainProbability;
  final String displayHumidity;
  final String displayWindSpeed;

  WeatherInfo({
    required this.temperature,
    required this.precipitation,
    required this.rainProbability,
    required this.humidity,
    required this.skyCondition,
    required this.rainType,
    required this.windSpeed,
    required this.tempFeeling,
    required this.tempDescription,
    required this.rainStatus,
    required this.rainDescription,
    required this.humidityFeeling,
    required this.humidityDescription,
    required this.windFeeling,
    required this.windDescription,
    required this.overallStatus,
    required this.overallEmoji,
    required this.displayTemperature,
    required this.displayRainProbability,
    required this.displayHumidity,
    required this.displayWindSpeed,
  });

  factory WeatherInfo.fromJson(Map<String, dynamic> json) {
    return WeatherInfo(
      temperature: json['temperature']?.toDouble() ?? 0.0,
      precipitation: json['precipitation'] ?? '없음',
      rainProbability: json['rain_probability'] ?? 0,
      humidity: json['humidity'] ?? 0,
      skyCondition: json['sky_condition'] ?? '알수없음',
      rainType: json['rain_type'] ?? '없음',
      windSpeed: json['wind_speed']?.toDouble() ?? 0.0,
      tempFeeling: json['temp_feeling'] ?? '',
      tempDescription: json['temp_description'] ?? '',
      rainStatus: json['rain_status'] ?? '',
      rainDescription: json['rain_description'] ?? '',
      humidityFeeling: json['humidity_feeling'] ?? '',
      humidityDescription: json['humidity_description'] ?? '',
      windFeeling: json['wind_feeling'] ?? '',
      windDescription: json['wind_description'] ?? '',
      overallStatus: json['overall_status'] ?? 'sunny',
      overallEmoji: json['overall_emoji'] ?? '☀️',
      displayTemperature: json['display_temperature'] ?? '',
      displayRainProbability: json['display_rain_probability'] ?? '',
      displayHumidity: json['display_humidity'] ?? '',
      displayWindSpeed: json['display_wind_speed'] ?? '',
    );
  }
  
  // 프론트에서 사용자가 선택한 캐릭터의 감정 상태 가져오기
  String getCharacterMood(String characterType) {
    // characterType: "sunny", "cloudy", "rainy", "snowy", "warm"
    final characterData = json['character_moods'][characterType];
    return characterData['mood'];  // "very_happy", "happy", "normal", "sad"
  }
  
  String getCharacterEmoji(String characterType) {
    final characterData = json['character_moods'][characterType];
    return characterData['emoji'];  // 😊, 🙂, 😐, 😢
  }
  
  String getCharacterPreference(String characterType) {
    final characterData = json['character_moods'][characterType];
    return characterData['preference'];
  }
  
  // 프론트에서 캐릭터 선택에 사용
  String getWeatherCharacter() {
    // overall_status 사용하면 더 간단!
    switch (overallStatus) {
      case 'rainy':
        return 'rainy';  // 우산 든 캐릭터
      case 'sunny':
        return 'sunny';  // 밝은 캐릭터
      case 'cloudy':
        return 'cloudy'; // 흐린 캐릭터
      case 'overcast':
        return 'overcast'; // 구름 많은 캐릭터
      default:
        return 'default';
    }
  }
  
  // 기온에 따른 캐릭터 옷차림
  String getCharacterOutfit() {
    if (tempFeeling == '매우추움' || tempFeeling == '추움') {
      return 'winter';  // 패딩 입은 캐릭터
    } else if (tempFeeling == '더움') {
      return 'summer';  // 시원한 옷 캐릭터
    } else {
      return 'normal';  // 일반 옷 캐릭터
    }
  }
}

// 에러 응답 모델
class ApiErrorResponse {
  final bool success;
  final ApiError error;

  ApiErrorResponse({
    required this.success,
    required this.error,
  });

  factory ApiErrorResponse.fromJson(Map<String, dynamic> json) {
    return ApiErrorResponse(
      success: json['success'] ?? false,
      error: ApiError.fromJson(json['error']),
    );
  }
}

class ApiError {
  final String code;
  final String message;
  final dynamic details;

  ApiError({
    required this.code,
    required this.message,
    this.details,
  });

  factory ApiError.fromJson(Map<String, dynamic> json) {
    return ApiError(
      code: json['code'],
      message: json['message'],
      details: json['details'],
    );
  }
}

// API 호출 예시 (에러 처리 포함)
Future<WeatherAdviceResponse> getWeatherAdvice(
  int userId,
  double latitude,
  double longitude,
) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/weather/advice'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(
        WeatherAdviceRequest(
          userId: userId,
          latitude: latitude,
          longitude: longitude,
        ).toJson(),
      ),
    );

    if (response.statusCode == 200) {
      return WeatherAdviceResponse.fromJson(jsonDecode(response.body));
    } else {
      // 에러 응답 파싱
      final errorResponse = ApiErrorResponse.fromJson(jsonDecode(response.body));
      throw ApiException(
        code: errorResponse.error.code,
        message: errorResponse.error.message,
        statusCode: response.statusCode,
      );
    }
  } catch (e) {
    if (e is ApiException) rethrow;
    throw ApiException(
      code: 'NETWORK_ERROR',
      message: '네트워크 오류가 발생했습니다',
      statusCode: 0,
    );
  }
}

// UI 사용 예시
void displayWeatherAdvice(WeatherAdviceResponse response) {
  final weather = response.weatherInfo;
  
  // 사용자가 선택한 캐릭터 타입 (앱 설정에서 가져옴)
  String selectedCharacter = userSettings.characterType;  // "sunny", "cloudy", "rainy", "snowy", "warm"
  
  // 1. 선택한 캐릭터의 감정 상태 가져오기
  String characterMood = weather.getCharacterMood(selectedCharacter);
  String characterEmoji = weather.getCharacterEmoji(selectedCharacter);
  String characterPreference = weather.getCharacterPreference(selectedCharacter);
  
  // 2. 캐릭터 애니메이션/이미지 표시
  Widget characterWidget;
  switch (characterMood) {
    case 'very_happy':
      characterWidget = Image.asset('assets/characters/${selectedCharacter}_very_happy.gif');
      break;
    case 'happy':
      characterWidget = Image.asset('assets/characters/${selectedCharacter}_happy.png');
      break;
    case 'normal':
      characterWidget = Image.asset('assets/characters/${selectedCharacter}_normal.png');
      break;
    case 'sad':
      characterWidget = Image.asset('assets/characters/${selectedCharacter}_sad.png');
      break;
  }
  
  // 3. 캐릭터 말풍선 (감정에 따라 다른 멘트)
  String characterSpeech;
  if (characterMood == 'very_happy') {
    characterSpeech = "오늘 날씨 완전 좋아! 😊";
  } else if (characterMood == 'happy') {
    characterSpeech = "오늘 날씨 괜찮네! 🙂";
  } else if (characterMood == 'normal') {
    characterSpeech = "그냥 그래... 😐";
  } else {
    characterSpeech = "오늘 날씨 별로야... 😢";
  }
  
  // 4. UI 구성
  Column(
    children: [
      // 캐릭터 표시
      Stack(
        children: [
          characterWidget,
          // 말풍선
          Positioned(
            top: 20,
            right: 20,
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 8)],
              ),
              child: Text(characterSpeech, style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
      
      SizedBox(height: 16),
      
      // 친근한 메시지
      Text(response.message, style: TextStyle(fontSize: 18)),
      
      SizedBox(height: 16),
      
      // 날씨 종합 정보
      Row(
        children: [
          Text(weather.overallEmoji, style: TextStyle(fontSize: 48)),
          SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(weather.displayTemperature, 
                   style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
              Text(weather.tempFeeling, 
                   style: TextStyle(fontSize: 14, color: Colors.grey)),
            ],
          ),
        ],
      ),
      
      // ... 나머지 UI
    ],
  );
}
  
  // 3. 상세 날씨 정보 카드
  Card(
    child: Padding(
      padding: EdgeInsets.all(16),
      child: Column(
        children: [
          // 기온 정보
          ListTile(
            leading: Icon(Icons.thermostat),
            title: Text(weather.tempDescription),
          ),
          // 강수 정보
          ListTile(
            leading: Icon(Icons.water_drop),
            title: Text(weather.rainDescription),
            subtitle: Text(weather.displayRainProbability),
          ),
          // 습도 정보
          ListTile(
            leading: Icon(Icons.opacity),
            title: Text(weather.humidityDescription),
            subtitle: Text(weather.displayHumidity),
          ),
          // 바람 정보
          ListTile(
            leading: Icon(Icons.air),
            title: Text(weather.windDescription),
            subtitle: Text(weather.displayWindSpeed),
          ),
        ],
      ),
    ),
  );
  
  // 4. 체크리스트
  Card(
    child: ListView.builder(
      shrinkWrap: true,
      physics: NeverScrollableScrollPhysics(),
      itemCount: response.checklist.length,
      itemBuilder: (context, index) {
        return CheckboxListTile(
          title: Text(response.checklist[index]),
          value: false,
          onChanged: (value) {
            // 체크박스 상태 관리
          },
        );
      },
    ),
  );
  
  // 5. 날씨에 따른 캐릭터 표시
  String characterType = weather.getWeatherCharacter();
  String outfit = weather.getCharacterOutfit();
  Image.asset('assets/characters/${characterType}_$outfit.png');
}

// 커스텀 예외 클래스
class ApiException implements Exception {
  final String code;
  final String message;
  final int statusCode;

  ApiException({
    required this.code,
    required this.message,
    required this.statusCode,
  });

  @override
  String toString() => message;
}
```

---

## 2️⃣ 사용자 생성

### **POST** `/weather/users`

새로운 사용자를 생성합니다. (이름과 이메일만 저장)

#### Request Body

```json
{
  "username": "홍길동",
  "email": "hong@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✅ 필수 | 사용자명 (중복 불가) |
| `email` | string | ❌ 선택 | 이메일 (중복 불가, 이메일 형식) |

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "홍길동",
  "email": "hong@example.com",
  "is_active": true,
  "created_at": "2025-11-07T12:34:56.789Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | 생성된 사용자 ID |
| `username` | string | 사용자명 |
| `email` | string\|null | 이메일 |
| `is_active` | boolean | 활성 상태 |
| `created_at` | string | 생성 시간 (ISO 8601) |

#### Error Responses

**400 Bad Request** - 중복된 사용자
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "이미 존재하는 사용자입니다"
  }
}
```

**422 Unprocessable Entity** - 유효성 검사 실패
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다",
    "details": [
      {
        "field": "body -> latitude",
        "message": "field required",
        "type": "value_error.missing"
      }
    ]
  }
}
```

#### Flutter/Dart 예시 코드

```dart
class UserCreateRequest {
  final String username;
  final String? email;

  UserCreateRequest({
    required this.username,
    this.email,
  });

  Map<String, dynamic> toJson() => {
    'username': username,
    if (email != null) 'email': email,
  };
}

class UserResponse {
  final int id;
  final String username;
  final String? email;
  final bool isActive;
  final DateTime createdAt;

  UserResponse({
    required this.id,
    required this.username,
    this.email,
    required this.isActive,
    required this.createdAt,
  });

  factory UserResponse.fromJson(Map<String, dynamic> json) {
    return UserResponse(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      isActive: json['is_active'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

// API 호출 예시
Future<UserResponse> createUser(UserCreateRequest request) async {
  final response = await http.post(
    Uri.parse('$baseUrl/weather/users'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    return UserResponse.fromJson(jsonDecode(response.body));
  } else {
    throw Exception('Failed to create user');
  }
}
```

---

## 3️⃣ 사용자 조회

### **GET** `/weather/users/{user_id}`

특정 사용자의 정보를 조회합니다.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ✅ 필수 | 사용자 ID |

#### Request Example

```
GET /weather/users/1
```

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "홍길동",
  "email": "hong@example.com",
  "is_active": true,
  "created_at": "2025-11-07T12:34:56.789Z"
}
```

응답 필드는 사용자 생성과 동일합니다.

#### Error Responses

**404 Not Found** - 사용자를 찾을 수 없음
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다"
  }
}
```

#### Flutter/Dart 예시 코드

```dart
Future<UserResponse> getUser(int userId) async {
  final response = await http.get(
    Uri.parse('$baseUrl/weather/users/$userId'),
    headers: {'Content-Type': 'application/json'},
  );

  if (response.statusCode == 200) {
    return UserResponse.fromJson(jsonDecode(response.body));
  } else if (response.statusCode == 404) {
    throw Exception('User not found');
  } else {
    throw Exception('Failed to get user');
  }
}
```

---

## 4️⃣ 사용자 정보 수정

### **PUT** `/weather/users/{user_id}`

사용자의 이름이나 이메일을 수정합니다.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | integer | ✅ 필수 | 사용자 ID |

#### Request Body

```json
{
  "username": "새이름",
  "email": "new@example.com"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ❌ 선택 | 새 사용자명 (중복 불가) |
| `email` | string | ❌ 선택 | 새 이메일 (중복 불가) |

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "새이름",
  "email": "new@example.com",
  "is_active": true,
  "created_at": "2025-11-07T12:34:56.789Z"
}
```

#### Error Responses

**400 Bad Request** - 중복된 사용자명
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "이미 존재하는 사용자 이름입니다"
  }
}
```

**404 Not Found** - 사용자를 찾을 수 없음
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다"
  }
}
```

#### Flutter/Dart 예시 코드

```dart
class UserUpdateRequest {
  final String? username;
  final String? email;

  UserUpdateRequest({
    this.username,
    this.email,
  });

  Map<String, dynamic> toJson() => {
    if (username != null) 'username': username,
    if (email != null) 'email': email,
  };
}

Future<UserResponse> updateUser(int userId, UserUpdateRequest request) async {
  final response = await http.put(
    Uri.parse('$baseUrl/weather/users/$userId'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode(request.toJson()),
  );

  if (response.statusCode == 200) {
    return UserResponse.fromJson(jsonDecode(response.body));
  } else if (response.statusCode == 404) {
    throw Exception('User not found');
  } else if (response.statusCode == 400) {
    throw Exception('Username already exists');
  } else {
    throw Exception('Failed to update user');
  }
}
```

---

## 5️⃣ 서버 상태 확인 (미구현)

### **GET** `/`

서버의 기본 정보를 확인합니다.

#### Response (200 OK)

```json
{
  "message": "Weather Check Server API",
  "version": "1.0.0",
  "description": "기상청 데이터와 GPT를 활용한 날씨 조언 서비스"
}
```

---

## 5️⃣ 서버 상태 확인 (미구현)

### **GET** `/`

> ⚠️ **MVP 버전에서는 미구현**

---

## 6️⃣ 헬스 체크 (미구현)

### **GET** `/health`

> ⚠️ **MVP 버전에서는 미구현**

---

## 🔐 인증 (Authentication)

현재 버전(MVP)에서는 인증이 없습니다. `user_id`만으로 사용자를 식별합니다.

---

## ⚠️ 에러 코드

| Status Code | Description |
|-------------|-------------|
| 200 | 성공 |
| 400 | 잘못된 요청 (Bad Request) |
| 404 | 리소스를 찾을 수 없음 (Not Found) |
| 422 | 유효성 검사 실패 (Unprocessable Entity) |
| 500 | 서버 내부 오류 (Internal Server Error) |

---

## 📝 참고사항

### 좌표계
- **입력**: WGS84 좌표계 (GPS 표준)
  - 위도(latitude): -90 ~ 90
  - 경도(longitude): -180 ~ 180
- **내부 변환**: 기상청 격자 좌표계 (Lambert Conformal Conic)
- **위치 저장**: 사용자 위치는 DB에 저장하지 않음 (매 요청 시 전송)

### 날씨 데이터
- **출처**: 기상청 단기예보 API
- **업데이트**: 3시간마다 (02:00, 05:00, 08:00, 11:00, 14:00, 17:00, 20:00, 23:00)
- **범위**: 전국 (대한민국)

### GPT 조언
- **모델**: GPT-4o
- **톤**: 친근한 반말
- **길이**: 2-3문장
- **특징**: 구체적인 행동 조언 포함

### 캐릭터 시스템
- **캐릭터 종류**: 5가지 (햇살이, 구름이, 비방울, 눈송이, 따스이)
- **감정 상태**: 날씨에 따라 캐릭터마다 다르게 반응
- **기분**: very_happy, happy, normal, sad (4단계)
- **활용**: 사용자가 선택한 캐릭터의 `character_moods`에서 해당 감정 표시

---

## 🧪 Swagger UI

개발 중에는 자동 생성된 API 문서를 사용할 수 있습니다:

```
http://localhost:8000/docs
```

또는 ReDoc 형식:

```
http://localhost:8000/redoc
```
