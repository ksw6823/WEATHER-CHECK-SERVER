from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.core.exceptions import (
    validation_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
    weather_api_exception_handler,
    ai_service_exception_handler,
    WeatherAPIError,
    AIServiceError
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="날씨 기반 AI 조언 서비스 API",
    version="1.0.0"
)

# 설정을 앱 상태에 저장 (에러 핸들러에서 DEBUG 모드 확인용)
app.state.config = settings

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 에러 핸들러 등록
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(WeatherAPIError, weather_api_exception_handler)
app.add_exception_handler(AIServiceError, ai_service_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작시 실행"""
    # 데이터베이스 테이블 생성 (개발용 - 프로덕션에서는 Alembic 사용)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# API 라우터 포함 (프리픽스 없음)
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "Weather Check Server API",
        "version": "1.0.0",
        "description": "기상청 데이터와 GPT를 활용한 날씨 조언 서비스"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
