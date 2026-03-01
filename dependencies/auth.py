from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from config import settings
from models import User, engine
from sqlalchemy.orm import sessionmaker

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 从请求头获取openid
def get_openid(x_wx_openid: Optional[str] = Header(None)) -> str:
    """从微信云托管自动注入的请求头获取openid"""
    if not x_wx_openid:
        raise HTTPException(
            status_code=401,
            detail="未提供有效的openid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return x_wx_openid

# 获取当前用户
def get_current_user(x_wx_openid: str = Depends(get_openid), db: Session = Depends(get_db)):
    """根据openid获取当前用户，若不存在则创建"""
    # 导入日志记录器
    from utils.logging import app_logger
    
    app_logger.info(f"获取当前用户，openid: {x_wx_openid}")
    
    user = db.query(User).filter(User.openid == x_wx_openid).first()
    
    # 如果用户不存在，则自动创建
    if not user:
        app_logger.info(f"用户不存在，创建新用户，openid: {x_wx_openid}")
        user = User(openid=x_wx_openid)
        db.add(user)
        db.commit()
        db.refresh(user)
        app_logger.info(f"新用户创建成功，用户ID: {user.id}")
    else:
        app_logger.info(f"用户已存在，用户ID: {user.id}")
    
    return user
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from config import settings
from models import User, engine
from sqlalchemy.orm import sessionmaker

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 从请求头获取openid
def get_openid(x_wx_openid: Optional[str] = Header(None)) -> str:
    """从微信云托管自动注入的请求头获取openid"""
    if not x_wx_openid:
        raise HTTPException(
            status_code=401,
            detail="未提供有效的openid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return x_wx_openid

# 获取当前用户
def get_current_user(x_wx_openid: str = Depends(get_openid), db: Session = Depends(get_db)):
    """根据openid获取当前用户，若不存在则创建"""
    # 导入日志记录器
    from utils.logging import app_logger
    
    app_logger.info(f"获取当前用户，openid: {x_wx_openid}")
    
    user = db.query(User).filter(User.openid == x_wx_openid).first()
    
    # 如果用户不存在，则自动创建
    if not user:
        app_logger.info(f"用户不存在，创建新用户，openid: {x_wx_openid}")
        user = User(openid=x_wx_openid)
        db.add(user)
        db.commit()
        db.refresh(user)
        app_logger.info(f"新用户创建成功，用户ID: {user.id}")
    else:
        app_logger.info(f"用户已存在，用户ID: {user.id}")
    
    return user