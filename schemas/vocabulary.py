from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Example(BaseModel):
    """例句模型"""
    sentence: str = Field(..., description="英文例句")
    translation: str = Field(..., description="例句中文翻译")

class WordAnalysis(BaseModel):
    """单词分析响应模型"""
    word: str = Field(..., description="单词原文")
    phonetic: str = Field(..., description="音标")
    translation: str = Field(..., description="中文释义")
    examples: List[Example] = Field(..., description="例句列表")

class AnalyzeWordRequest(BaseModel):
    """单词分析请求模型"""
    word: str = Field(..., min_length=1, max_length=100, description="要分析的单词")

class SentenceTranslation(BaseModel):
    """句子翻译响应模型"""
    original: str = Field(..., description="原句")
    translation: str = Field(..., description="翻译结果")

class TranslateSentenceRequest(BaseModel):
    """句子翻译请求模型"""
    sentence: str = Field(..., min_length=1, max_length=500, description="要翻译的句子")

class LearningDuration(BaseModel):
    """学习时长请求模型"""
    duration: int = Field(..., ge=1, description="学习时长，单位：秒")