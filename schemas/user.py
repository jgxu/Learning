from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """用户基础模型"""
    openid: str = Field(..., description="微信用户唯一标识")
    nickname: Optional[str] = Field(None, description="用户昵称")
    avatar: Optional[str] = Field(None, description="用户头像URL")
    
    class Config:
        orm_mode = True

class UserProfile(User):
    """用户个人信息响应模型"""
    subscription_expiry: datetime = Field(..., description="订阅到期时间")
    daily_goal: int = Field(..., description="每日复习目标")
    total_learning_time: int = Field(..., description="总学习时长（秒）")
    
    class Config:
        orm_mode = True

class UserSettingsUpdate(BaseModel):
    """用户设置更新请求模型"""
    daily_goal: int = Field(..., ge=20, le=100, description="每日复习量，范围20-100")

class UserSettings(BaseModel):
    """用户设置响应模型"""
    daily_goal: int = Field(..., description="每日复习目标")
    
    class Config:
        orm_mode = True