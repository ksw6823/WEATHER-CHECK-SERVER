from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.weather import WeatherAdviceRequest, WeatherAdviceResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.weather_service import WeatherService
from app.services.ai_service import AIService
from app.core.database import get_db
from app.models.user import User

router = APIRouter()
weather_service = WeatherService()
ai_service = AIService()


@router.post("/advice", response_model=WeatherAdviceResponse)
async def get_weather_advice(
    request: WeatherAdviceRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 위치 기반 날씨 조언 생성
    
    Flutter 앱에서 호출하는 메인 엔드포인트
    - 사용자 확인용으로만 user_id 사용
    - 위치는 항상 Flutter에서 실시간으로 전송받음
    """
    # 1. 사용자 존재 여부만 확인
    result = await db.execute(select(User).where(User.id == request.user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 2. 요청에 포함된 실시간 위치 사용
    lat = request.latitude
    lon = request.longitude
    
    # 3. 기상청 API로 날씨 정보 가져오기
    weather_data = await weather_service.get_weather_forecast(lat, lon)
    
    # 4. GPT로 조언 생성 (message + checklist)
    advice_data = await ai_service.generate_weather_advice(
        weather_data=weather_data,
        user_name=user.username
    )
    
    return WeatherAdviceResponse(
        message=advice_data["message"],
        checklist=advice_data["checklist"],
        weather_info=weather_data
    )


@router.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 사용자 생성 (이름과 이메일만)
    """
    # 중복 체크
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다")
    
    # 사용자 생성 (위치 정보 없이)
    db_user = User(
        username=user.username,
        email=user.email
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    
    return db_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 정보 조회
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    사용자 정보 업데이트 (이름, 이메일)
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    # 업데이트 (제공된 필드만)
    if user_update.username is not None:
        # 중복 체크
        result = await db.execute(
            select(User).where(User.username == user_update.username, User.id != user_id)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="이미 존재하는 사용자 이름입니다")
        user.username = user_update.username
    
    if user_update.email is not None:
        user.email = user_update.email
    
    await db.commit()
    await db.refresh(user)
    
    return user
