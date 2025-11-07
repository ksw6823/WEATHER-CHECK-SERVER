from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from typing import Union
import traceback


class ErrorResponse:
    """표준 에러 응답 형식"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        details: Union[str, dict, list, None] = None,
        status_code: int = 500
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.status_code = status_code
    
    def to_dict(self):
        response = {
            "success": False,
            "error": {
                "code": self.error_code,
                "message": self.message
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    유효성 검사 에러 핸들러 (422)
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        message="입력값이 올바르지 않습니다",
        details=errors,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )


async def http_exception_handler(request: Request, exc):
    """
    HTTP 예외 핸들러 (400, 404, 500 등)
    """
    error_codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        500: "INTERNAL_SERVER_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_response = ErrorResponse(
        error_code=error_codes.get(exc.status_code, "HTTP_ERROR"),
        message=str(exc.detail),
        status_code=exc.status_code
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    데이터베이스 에러 핸들러
    """
    error_response = ErrorResponse(
        error_code="DATABASE_ERROR",
        message="데이터베이스 처리 중 오류가 발생했습니다",
        details=str(exc) if request.app.state.config.DEBUG else None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    일반 예외 핸들러 (모든 예외의 폴백)
    """
    # 로깅
    print(f"Unhandled exception: {type(exc).__name__}")
    print(f"Error: {str(exc)}")
    if request.app.state.config.DEBUG:
        traceback.print_exc()
    
    error_response = ErrorResponse(
        error_code="INTERNAL_ERROR",
        message="서버 내부 오류가 발생했습니다",
        details=str(exc) if request.app.state.config.DEBUG else None,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )


# 커스텀 예외 클래스들
class WeatherAPIError(Exception):
    """기상청 API 호출 실패"""
    pass


class AIServiceError(Exception):
    """AI 서비스 호출 실패"""
    pass


class UserNotFoundError(Exception):
    """사용자를 찾을 수 없음"""
    pass


async def weather_api_exception_handler(request: Request, exc: WeatherAPIError):
    """기상청 API 에러 핸들러"""
    error_response = ErrorResponse(
        error_code="WEATHER_API_ERROR",
        message="날씨 정보를 가져오는데 실패했습니다",
        details=str(exc) if request.app.state.config.DEBUG else None,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )


async def ai_service_exception_handler(request: Request, exc: AIServiceError):
    """AI 서비스 에러 핸들러"""
    error_response = ErrorResponse(
        error_code="AI_SERVICE_ERROR",
        message="AI 조언 생성에 실패했습니다",
        details=str(exc) if request.app.state.config.DEBUG else None,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )
    
    return JSONResponse(
        status_code=error_response.status_code,
        content=error_response.to_dict()
    )
