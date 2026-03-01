from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    __table_args__ = {
        'comment': '用户表'
    }
    
    id = Column(Integer, primary_key=True, index=True, comment='用户ID')
    openid = Column(String(100), unique=True, index=True, nullable=False, comment='微信用户唯一标识')
    nickname = Column(String(100), comment='用户昵称')
    avatar = Column(String(255), comment='用户头像URL')
    subscription_expiry = Column(DateTime, default=datetime.utcnow, comment='订阅到期时间')
    daily_goal = Column(Integer, default=50, comment='每日复习目标（20-100）')
    total_learning_time = Column(Integer, default=0, comment='总学习时长（秒）')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {
        'comment': '文档表'
    }
    
    id = Column(Integer, primary_key=True, index=True, comment='文档ID')
    user_id = Column(Integer, index=True, comment='用户ID')
    title = Column(String(255), comment='文档标题')
    file_type = Column(String(50), comment='文件类型：word/pdf/txt/image/link')
    file_path = Column(String(255), comment='文件存储路径')
    source_link = Column(String(500), comment='原始链接')
    content = Column(Text, comment='解析后的文本内容')
    ai_analysis_cache = Column(Text, comment='AI分析结果缓存（JSON格式）')
    is_parsed = Column(Boolean, default=False, comment='是否已解析')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class Vocabulary(Base):
    __tablename__ = "vocabulary"
    __table_args__ = {
        'comment': '词汇表'
    }
    
    id = Column(Integer, primary_key=True, index=True, comment='词汇ID')
    user_id = Column(Integer, index=True, comment='用户ID')
    word = Column(String(100), index=True, comment='单词')
    phonetic = Column(String(100), comment='音标')
    translation = Column(Text, comment='翻译')
    examples = Column(Text, comment='例句（JSON格式）')
    frequency = Column(Integer, default=1, comment='出现频率')
    is_favorite = Column(Boolean, default=False, comment='是否收藏')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class SRSRecord(Base):
    __tablename__ = "srs_records"
    __table_args__ = {
        'comment': 'SRS记录表'
    }
    
    id = Column(Integer, primary_key=True, index=True, comment='SRS记录ID')
    user_id = Column(Integer, index=True, comment='用户ID')
    vocabulary_id = Column(Integer, unique=True, index=True, comment='词汇ID')
    easiness_factor = Column(Numeric(4, 2), default=2.5, comment='难度系数（1.3-2.5）')
    interval = Column(Integer, default=1, comment='间隔天数')
    repetitions = Column(Integer, default=0, comment='重复次数')
    next_review_date = Column(DateTime, default=datetime.utcnow, comment='下次复习日期')
    last_review_date = Column(DateTime, comment='上次复习日期')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')

class LearningSession(Base):
    __tablename__ = "learning_sessions"
    __table_args__ = {
        'comment': '学习会话表'
    }
    
    id = Column(Integer, primary_key=True, index=True, comment='会话ID')
    user_id = Column(Integer, index=True, comment='用户ID')
    session_start = Column(DateTime, default=datetime.utcnow, comment='会话开始时间')
    session_end = Column(DateTime, comment='会话结束时间')
    duration = Column(Integer, comment='学习时长（秒）')
    created_at = Column(DateTime, default=datetime.utcnow, comment='创建时间')

# 创建数据库引擎
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from config import settings

# 创建引擎时开启SQL日志
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # 开启SQL语句输出
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    pool_pre_ping=True
)

# 导入日志工具
from utils.logging import app_logger

# 记录SQL执行时间
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(datetime.now())
    app_logger.debug(f"执行SQL: {statement} 参数: {parameters}")

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = datetime.now() - conn.info['query_start_time'].pop(-1)
    app_logger.debug(f"SQL执行完成，耗时: {total.total_seconds():.3f}秒")

# 导入datetime
from datetime import datetime