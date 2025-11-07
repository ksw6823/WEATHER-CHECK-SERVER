from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """사용자 기본 스키마"""
    username: str
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    """사용자 생성 스키마 - 이름과 이메일만"""
    pass


class UserUpdate(BaseModel):
    """사용자 수정 스키마"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
