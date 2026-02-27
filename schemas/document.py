from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class Document(BaseModel):
    """文档模型"""
    id: int
    title: str
    file_type: str
    content: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class DocumentUploadResponse(Document):
    """文档上传响应模型"""
    is_parsed: bool
    
    class Config:
        orm_mode = True