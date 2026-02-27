from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """用户基础模型"""
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    
    class Config:
        orm_mode = True

class UserProfile(User):
    """用户个人信息响应模型"""
    subscription_expiry: datetime
    daily_goal: int
    total_learning_time: int
    
    class Config:
        orm_mode = True

class UserSettingsUpdate(BaseModel):
    """用户设置更新请求模型"""
    daily_goal: int = Field(..., ge=20, le=100, description="每日复习量，范围20-100")

class UserSettings(BaseModel):
    """用户设置响应模型"""
    daily_goal: int
    
    class Config:
        orm_mode = True