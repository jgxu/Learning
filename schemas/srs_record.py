from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class FeedbackType(str):
    """复习反馈类型"""
    EASY = "easy"  # 认识
    MEDIUM = "medium"  # 模糊
    HARD = "hard"  # 忘记

class SRSRecord(BaseModel):
    """SRS记录模型"""
    id: int
    vocabulary_id: int
    easiness_factor: float
    interval: int
    repetitions: int
    next_review_date: datetime
    last_review_date: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ReviewItem(BaseModel):
    """复习项模型"""
    srs_record_id: int
    word: str
    phonetic: str
    translation: str

class FeedbackRequest(BaseModel):
    """复习反馈请求模型"""
    srs_record_id: int
    feedback: FeedbackType = Field(..., description="反馈类型：easy(认识), medium(模糊), hard(忘记)")