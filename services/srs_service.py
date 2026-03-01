from sqlalchemy.orm import Session
from models import SRSRecord, Vocabulary, User
from schemas.srs_record import FeedbackRequest, ReviewItem, FeedbackType
from datetime import datetime, timedelta
from utils.logging import app_logger


def get_today_review_list(db: Session, openid: str) -> list[ReviewItem]:
    """获取今日到期需复习的单词列表"""
    app_logger.info(f"获取今日复习列表，openid: {openid}")
    
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        app_logger.error(f"用户不存在，openid: {openid}")
        raise ValueError("用户不存在")
    
    # 获取今日到期的SRS记录
    today = datetime.utcnow().date()
    app_logger.info(f"获取用户今日到期的SRS记录，用户ID: {user.id}，每日目标: {user.daily_goal}")
    
    srs_records = db.query(SRSRecord).filter(
        SRSRecord.user_id == user.id,
        SRSRecord.next_review_date <= datetime.utcnow()
    ).limit(user.daily_goal).all()
    
    # 构建复习列表
    review_list = []
    for record in srs_records:
        if record.vocabulary:
            review_list.append(ReviewItem(
                srs_record_id=record.id,
                word=record.vocabulary.word,
                phonetic=record.vocabulary.phonetic,
                translation=record.vocabulary.translation
            ))
    
    app_logger.info(f"获取复习列表成功，用户ID: {user.id}，复习数量: {len(review_list)}")
    return review_list


def submit_feedback(db: Session, openid: str, request: FeedbackRequest) -> SRSRecord:
    """提交单词复习反馈，更新SRS参数"""
    app_logger.info(f"提交复习反馈，openid: {openid}，SRS记录ID: {request.srs_record_id}，反馈类型: {request.feedback}")
    
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        app_logger.error(f"用户不存在，openid: {openid}")
        raise ValueError("用户不存在")
    
    # 获取SRS记录
    srs_record = db.query(SRSRecord).filter(
        SRSRecord.id == request.srs_record_id,
        SRSRecord.user_id == user.id
    ).first()
    
    if not srs_record:
        app_logger.error(f"SRS记录不存在，记录ID: {request.srs_record_id}，用户ID: {user.id}")
        raise ValueError("SRS记录不存在")
    
    # 记录更新前的参数
    old_params = {
        "repetitions": srs_record.repetitions,
        "easiness_factor": float(srs_record.easiness_factor),
        "interval": srs_record.interval,
        "next_review_date": srs_record.next_review_date
    }
    
    # 根据反馈类型更新SRS参数
    if request.feedback == FeedbackType.HARD:
        # 忘记：重新开始学习
        app_logger.info(f"反馈类型：忘记，重置学习进度，记录ID: {request.srs_record_id}")
        srs_record.repetitions = 0
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor - 0.2)
        srs_record.interval = 1
    elif request.feedback == FeedbackType.MEDIUM:
        # 模糊：降低难度系数，缩短间隔
        app_logger.info(f"反馈类型：模糊，降低难度系数，记录ID: {request.srs_record_id}")
        srs_record.repetitions = max(0, srs_record.repetitions - 1)
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor - 0.1)
        srs_record.interval = max(1, srs_record.interval // 2)
    elif request.feedback == FeedbackType.EASY:
        # 认识：增加重复次数，调整难度系数，延长间隔
        app_logger.info(f"反馈类型：认识，增加重复次数，延长间隔，记录ID: {request.srs_record_id}")
        srs_record.repetitions += 1
        srs_record.easiness_factor = max(1.3, srs_record.easiness_factor + 0.1)
        
        if srs_record.repetitions == 1:
            srs_record.interval = 1
        elif srs_record.repetitions == 2:
            srs_record.interval = 6
        else:
            srs_record.interval = int(srs_record.interval * srs_record.easiness_factor)
    
    # 更新复习日期
    srs_record.last_review_date = datetime.utcnow()
    srs_record.next_review_date = datetime.utcnow() + timedelta(days=srs_record.interval)
    
    # 记录更新后的参数
    new_params = {
        "repetitions": srs_record.repetitions,
        "easiness_factor": float(srs_record.easiness_factor),
        "interval": srs_record.interval,
        "next_review_date": srs_record.next_review_date
    }
    
    app_logger.info(f"SRS参数更新，记录ID: {request.srs_record_id}，旧参数: {old_params}，新参数: {new_params}")
    
    db.commit()
    db.refresh(srs_record)
    
    return srs_record


def add_word_to_srs(db: Session, user_id: int, vocabulary_id: int) -> SRSRecord:
    """将单词添加到SRS系统"""
    # 检查是否已存在
    existing_record = db.query(SRSRecord).filter(
        SRSRecord.user_id == user_id,
        SRSRecord.vocabulary_id == vocabulary_id
    ).first()
    
    if existing_record:
        return existing_record
    
    # 创建新的SRS记录
    srs_record = SRSRecord(
        user_id=user_id,
        vocabulary_id=vocabulary_id,
        easiness_factor=2.5,
        interval=1,
        repetitions=0,
        next_review_date=datetime.utcnow()
    )
    
    db.add(srs_record)
    db.commit()
    db.refresh(srs_record)
    
    return srs_record