from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    openid = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(100))
    avatar = Column(String(255))
    subscription_expiry = Column(DateTime, default=datetime.utcnow)
    daily_goal = Column(Integer, default=50)  # 默认每日复习量50个
    total_learning_time = Column(Integer, default=0)  # 总学习时长，单位：秒
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    documents = relationship("Document", backref="user")
    vocabularies = relationship("Vocabulary", backref="user")
    srs_records = relationship("SRSRecord", backref="user")
    learning_sessions = relationship("LearningSession", backref="user")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(255))
    file_type = Column(String(50))  # word, pdf, txt, image, link
    file_path = Column(String(255))  # 如果是文件上传，存储文件路径
    source_link = Column(String(500))  # 如果是链接，存储链接
    content = Column(Text)  # 解析后的文本内容
    ai_analysis_cache = Column(Text)  # AI分析结果缓存（JSON格式）
    is_parsed = Column(Boolean, default=False)  # 是否已解析
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Vocabulary(Base):
    __tablename__ = "vocabulary"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String(100), index=True)
    phonetic = Column(String(100))  # 音标
    translation = Column(Text)  # 翻译
    examples = Column(Text)  # 例句（JSON格式）
    frequency = Column(Integer, default=1)  # 出现频率
    is_favorite = Column(Boolean, default=False)  # 是否收藏
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SRSRecord(Base):
    __tablename__ = "srs_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    vocabulary_id = Column(Integer, ForeignKey("vocabulary.id"), unique=True)
    easiness_factor = Column(Numeric(4, 2), default=2.5)  # 难度系数
    interval = Column(Integer, default=1)  # 间隔天数
    repetitions = Column(Integer, default=0)  # 重复次数
    next_review_date = Column(DateTime, default=datetime.utcnow)  # 下次复习日期
    last_review_date = Column(DateTime)  # 上次复习日期
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime)
    duration = Column(Integer)  # 学习时长，单位：秒
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建数据库引擎
from sqlalchemy import create_engine
from config import settings

engine = create_engine(settings.DATABASE_URL)