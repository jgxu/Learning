from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Example(BaseModel):
    """例句模型"""
    sentence: str
    translation: str

class WordAnalysis(BaseModel):
    """单词分析响应模型"""
    word: str
    phonetic: str
    translation: str
    examples: List[Example]

class AnalyzeWordRequest(BaseModel):
    """单词分析请求模型"""
    word: str = Field(..., min_length=1, max_length=100)

class SentenceTranslation(BaseModel):
    """句子翻译响应模型"""
    original: str
    translation: str

class TranslateSentenceRequest(BaseModel):
    """句子翻译请求模型"""
    sentence: str = Field(..., min_length=1, max_length=500)

class LearningDuration(BaseModel):
    """学习时长请求模型"""
    duration: int = Field(..., ge=1, description="学习时长，单位：秒")