from sqlalchemy.orm import Session
from models import User, LearningSession
from schemas import user as user_schemas
from datetime import datetime


def get_user_profile(db: Session, openid: str) -> user_schemas.UserProfile:
    """获取用户个人信息及订阅状态"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    return user


def update_user_settings(db: Session, openid: str, settings: user_schemas.UserSettingsUpdate) -> user_schemas.UserSettings:
    """更新用户设置"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    
    user.daily_goal = settings.daily_goal
    db.commit()
    db.refresh(user)
    
    return user


def sync_learning_duration(db: Session, openid: str, duration: int) -> dict:
    """同步学习时长"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise ValueError("用户不存在")
    
    # 更新总学习时长
    user.total_learning_time += duration
    
    # 创建学习会话记录
    learning_session = LearningSession(
        user_id=user.id,
        session_start=datetime.utcnow(),
        session_end=datetime.utcnow(),
        duration=duration
    )
    
    db.add(learning_session)
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "total_learning_time": user.total_learning_time
    }