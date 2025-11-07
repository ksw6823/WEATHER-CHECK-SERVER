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
| GET | `/` | 서버 상태 확인 |
| GET | `/health` | 헬스 체크 |

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

사용자의 위치 정보를 기반으로 기상청 날씨 데이터와 GPT를 활용하여 친근한 날씨 조언을 생성합니다.

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
| `latitude` | float | ❌ 선택 | 위도 (없으면 사용자 기본 위치 사용) |
| `longitude` | float | ❌ 선택 | 경도 (없으면 사용자 기본 위치 사용) |

#### Response (200 OK)

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

| Field | Type | Description |
|-------|------|-------------|
| `advice` | string | GPT가 생성한 친근한 날씨 조언 (2-3문장) |
| `weather_info` | object | 날씨 상세 정보 |
| `weather_info.temperature` | float | 기온 (°C) |
| `weather_info.precipitation` | string | 강수량 ("없음", "1mm", "5mm" 등) |
| `weather_info.rain_probability` | integer | 강수확률 (0-100%) |
| `weather_info.humidity` | integer | 습도 (0-100%) |
| `weather_info.sky_condition` | string | 하늘 상태 ("맑음", "구름많음", "흐림") |
| `weather_info.rain_type` | string | 강수 형태 ("없음", "비", "눈", "비/눈", "소나기") |
| `weather_info.wind_speed` | float | 풍속 (m/s) |

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

class WeatherInfo {
  final double temperature;
  final String precipitation;
  final int rainProbability;
  final int humidity;
  final String skyCondition;
  final String rainType;
  final double windSpeed;

  WeatherInfo({
    required this.temperature,
    required this.precipitation,
    required this.rainProbability,
    required this.humidity,
    required this.skyCondition,
    required this.rainType,
    required this.windSpeed,
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
    );
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
  int userId, {
  double? latitude,
  double? longitude,
}) async {
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

새로운 사용자를 생성합니다.

#### Request Body

```json
{
  "username": "홍길동",
  "email": "hong@example.com",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "서울시 중구"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | ✅ 필수 | 사용자명 (중복 불가) |
| `email` | string | ❌ 선택 | 이메일 (중복 불가, 이메일 형식) |
| `latitude` | float | ✅ 필수 | 위도 |
| `longitude` | float | ✅ 필수 | 경도 |
| `location_name` | string | ❌ 선택 | 지역명 (예: "서울시 강남구") |

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "홍길동",
  "email": "hong@example.com",
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "서울시 중구",
  "is_active": true,
  "created_at": "2025-11-07T12:34:56.789Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | 생성된 사용자 ID |
| `username` | string | 사용자명 |
| `email` | string\|null | 이메일 |
| `latitude` | float | 위도 |
| `longitude` | float | 경도 |
| `location_name` | string\|null | 지역명 |
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
  final double latitude;
  final double longitude;
  final String? locationName;

  UserCreateRequest({
    required this.username,
    this.email,
    required this.latitude,
    required this.longitude,
    this.locationName,
  });

  Map<String, dynamic> toJson() => {
    'username': username,
    if (email != null) 'email': email,
    'latitude': latitude,
    'longitude': longitude,
    if (locationName != null) 'location_name': locationName,
  };
}

class UserResponse {
  final int id;
  final String username;
  final String? email;
  final double latitude;
  final double longitude;
  final String? locationName;
  final bool isActive;
  final DateTime createdAt;

  UserResponse({
    required this.id,
    required this.username,
    this.email,
    required this.latitude,
    required this.longitude,
    this.locationName,
    required this.isActive,
    required this.createdAt,
  });

  factory UserResponse.fromJson(Map<String, dynamic> json) {
    return UserResponse(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      latitude: json['latitude'].toDouble(),
      longitude: json['longitude'].toDouble(),
      locationName: json['location_name'],
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
  "latitude": 37.5665,
  "longitude": 126.9780,
  "location_name": "서울시 중구",
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

## 4️⃣ 서버 상태 확인

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

## 5️⃣ 헬스 체크

### **GET** `/health`

서버의 헬스 상태를 확인합니다.

#### Response (200 OK)

```json
{
  "status": "healthy"
}
```

---

## 🔐 인증 (Authentication)

현재 버전(MVP)에서는 인증이 없습니다. 향후 JWT 토큰 기반 인증을 추가할 예정입니다.

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

### 날씨 데이터
- **출처**: 기상청 단기예보 API
- **업데이트**: 3시간마다 (02:00, 05:00, 08:00, 11:00, 14:00, 17:00, 20:00, 23:00)
- **범위**: 전국 (대한민국)

### GPT 조언
- **모델**: GPT-4o
- **톤**: 친근한 반말
- **길이**: 2-3문장
- **특징**: 구체적인 행동 조언 포함

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
